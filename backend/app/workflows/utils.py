import inspect
import os
import time

import networkx as nx
import orjson
from celery import Task, _state, current_app, states
from celery import chain as celery_chain
from celery.local import Proxy
from celery.result import AsyncResult
from django.core.cache import cache

ABORTED = "ABORTED"
ABORT_TIMEOUT = 60
ABORT_POLL_INTERVAL = 1
PREABORT_RESULT_KEY = "preabort_result"


ABORTED_MESSAGE = "This task or its child was aborted, causing it to fail."


def get_abort_cache_key(task_id):
    return f"abort:{task_id}"


def get_abort_result_cache_key(task_id):
    return f"abort_result:{task_id}"


class AbortedException(Exception):
    """Raised when a task is aborted."""

    def __init__(self, message="Task was aborted"):
        self.message = message
        super().__init__(self.message)

    def __reduce__(self):
        return (self.__class__, (self.message,))


class CustomTask(Task):
    """
    Custom base class for tasks to override the `apply` method.
    """

    def _adjust_inputs(self, *args, **kwargs):
        # Argsrepr and kwargsrepr are used to ensure correct json serialization of task_args and task_kwargs in the Result backend.
        kwargs["argsrepr"] = args[0] if args else None
        kwargs["kwargsrepr"] = args[1] if args else None
        return args, kwargs

    def apply(self, *args, **kwargs):
        args, kwargs = self._adjust_inputs(*args, **kwargs)
        return super().apply(*args, **kwargs)

    def apply_async(self, *args, **kwargs):
        args, kwargs = self._adjust_inputs(*args, **kwargs)
        res = super().apply_async(*args, **kwargs)
        if os.getenv("CUSTOM_CELERY_EAGER") == "true":
            res.get(disable_sync_subtasks=False)
        return res

    def run_subtasks(self, *tasks):
        if self.request.called_directly:
            return chain(*tasks)._run_directly()
        elif self.request.is_eager:
            return chain(*tasks).apply(*tasks, parent_task=self).get()
        return chain(*tasks).apply_async(parent_task=self).get()


class AbortableAsyncResult(AsyncResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started_task_graph = nx.DiGraph()

    def is_aborted(self):
        cache_key = get_abort_cache_key(self.id)
        cached_value = cache.get(key=cache_key)
        is_cached = cached_value is not None
        if is_cached:
            cache.delete(key=cache_key)
        return is_cached

    def _build_started_task_graph(self, task_id):
        """Recursively add task and its children to the graph."""
        self.started_task_graph.add_node(task_id)
        children = self.backend.get_children(task_id)

        for child in children:
            child_id = child[0][0]
            self.started_task_graph.add_edge(task_id, child_id)
            # Recursively add children of this child
            self._build_started_task_graph(child_id)

    def abort(
        self,
        abort_timeout=ABORT_TIMEOUT,
        abort_poll_interval=ABORT_POLL_INTERVAL,
        wait_for_completion=False,
    ):
        self._build_started_task_graph(self.id)

        leaves = [
            node
            for node in self.started_task_graph.nodes
            if self.started_task_graph.out_degree(node) == 0
        ]
        if not leaves:
            return
        current_app.control.revoke(leaves)

        # only abort the leaf nodes and let errors propagate through the rest
        cache_keys = []
        for leaf in leaves:
            cache_key = get_abort_cache_key(leaf)
            cache_keys.append(cache_key)
            cache.set(key=cache_key, value=leaf, timeout=abort_timeout)

        if wait_for_completion:
            # wait for all tasks to complete or abort
            start_time = time.time()
            while time.time() - start_time < abort_timeout:
                cached_kv = {
                    cache_key: cache.get(key=cache_key) for cache_key in cache_keys
                }
                cached_kvs = {k: v for k, v in cached_kv.items() if v is not None}
                print(cached_kvs)
                if len(cached_kvs) == 0:
                    return True
                for k, v in cached_kvs.items():
                    status = AsyncResult(v).status
                    if status != states.STARTED:
                        cache.delete(key=k)
                time.sleep(abort_poll_interval)

            raise TimeoutError("Abort timed out")

        return True


class CustomAbortableTask(CustomTask):
    def AsyncResult(self, task_id):
        """Return the accompanying AbortableAsyncResult instance."""
        return AbortableAsyncResult(task_id, backend=self.backend)

    def is_aborted(self, raise_exception=True):
        is_aborted = AbortableAsyncResult(self.request.id).is_aborted()
        if is_aborted and raise_exception:
            cache_key = get_abort_result_cache_key(self.request.id)
            cur_result = cache.get(cache_key)

            # exception message use to communicate interim result since celery requires standard exception result to propogate errors
            exception_message = {PREABORT_RESULT_KEY: {self.request.id: cur_result}}
            exception_message = orjson.dumps(exception_message).decode("utf-8")
            raise AbortedException(exception_message)
        return is_aborted

    def run_subtasks(self, *tasks):
        self.is_aborted(raise_exception=True)
        return super().run_subtasks(*tasks)

    def update_state(self, *args, **kwargs):
        if meta := kwargs.get("meta"):
            cache_key = get_abort_result_cache_key(self.request.id)
            cache.set(key=cache_key, value=meta, timeout=None)
        super().update_state(*args, **kwargs)


def _ensure_self(func):
    params = inspect.signature(func).parameters
    if not params or list(params.keys())[0] != "self":
        raise ValueError(
            f"Task function '{func.__name__}' must have 'self' as first parameter when bind=True"
        )


# slightly modified version of celery's shared_task that ensures that the task has a self parameter
def _shared_task(*args, **kwargs):
    def create_shared_task(**options):
        def __inner(fun):
            _ensure_self(fun)
            name = options.get("name")
            # Set as shared task so that unfinalized apps,
            # and future apps will register a copy of this task.
            _state.connect_on_app_finalize(
                lambda app: app._task_from_fun(fun, **options)
            )

            # Force all finalized apps to take this task as well.
            for app in _state._get_active_apps():
                if app.finalized:
                    with app._finalize_mutex:
                        app._task_from_fun(fun, **options)

            # Return a proxy that always gets the task from the current
            # apps task registry.
            def task_by_cons():
                app = _state.get_current_app()
                return app.tasks[
                    name or app.gen_task_name(fun.__name__, fun.__module__)
                ]

            return Proxy(task_by_cons)

        return __inner

    if len(args) == 1 and callable(args[0]):
        return create_shared_task(**kwargs)(args[0])
    return create_shared_task(*args, **kwargs)


def task(*args, **kwargs):
    kwargs.setdefault("bind", True)
    task = CustomAbortableTask if kwargs.get("abortable") else CustomTask
    kwargs.setdefault("base", task)
    return _shared_task(*args, **kwargs)


class ChainResult:
    def __init__(self, ls, parent_task):
        self.ls = ls
        self.parent_task = parent_task

    def _individual_get(self, v, *args, **kwargs):
        if not hasattr(v, "get"):
            return v
        elif isinstance(v, ChainResult):
            return v.get(*args, **kwargs)
        else:
            return v.get(*args, **kwargs, disable_sync_subtasks=False)

    def get(self, *args, **kwargs):
        return [self._individual_get(v, *args, **kwargs) for v in self.ls]


class chain(celery_chain):
    def _process_result(self, parent_task, res):
        # force parent task to update state, which updates its children
        parent_task.update_state(state=states.STARTED)
        res.get(disable_sync_subtasks=False)
        return res

    def apply(self, *args, **kwargs):
        parent_task = kwargs.pop("parent_task", None)
        if not parent_task:
            raise ValueError("parent_task is required")

        outs = []
        for t in self.tasks:
            res = t.apply(*args, **kwargs)
            outs.append(self._process_result(parent_task, res))
        return ChainResult(outs, parent_task)

    def apply_async(self, *args, **kwargs):
        parent_task = kwargs.pop("parent_task", None)
        if not parent_task:
            raise ValueError("parent_task is required")

        outs = []
        for t in self.tasks:
            res = t.apply_async(*args, **kwargs)
            outs.append(self._process_result(parent_task, res))
        return ChainResult(outs, parent_task)

    def _run_directly(self):
        outs = []
        for t in self.tasks:
            if isinstance(t, type(self)):
                res = t._run_directly()
            else:
                res = t.type(*t.args, **t.kwargs)
            outs.append(res)
        return ChainResult(outs)
