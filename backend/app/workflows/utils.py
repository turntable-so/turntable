import inspect
import os

from celery import Task, _state, states
from celery import chain as celery_chain
from celery.local import Proxy


class CustomTask(Task):
    """
    Custom base class for tasks to override the `apply` method.

    Argsrepr and kwargsrepr are used to ensure correct serialization of task_args and task_kwargs in the Result backend

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._called_directly = False

    def __call__(self, *args, **kwargs):
        self._called_directly = True
        return super().__call__(*args, **kwargs)

    def apply(self, *args, **kwargs):
        if os.getenv("CUSTOM_CELERY_EAGER") != "true":
            return super().apply(
                *args,
                **kwargs,
                argsrepr=args[0],
                kwargsrepr=args[1],
            )
        return self.apply_async(*args, **kwargs)

    def apply_async(self, *args, **kwargs):
        res = super().apply_async(
            *args,
            **kwargs,
            argsrepr=args[0],
            kwargsrepr=args[1],
        )
        if os.getenv("CUSTOM_CELERY_EAGER") == "true":
            res.get(disable_sync_subtasks=False)
        return res

    def run_subtasks(self, *tasks):
        if self.request.is_eager:
            f = chain(*tasks).apply
        elif hasattr(self, "_called_directly") and self._called_directly:
            f = chain(*tasks)._call_directly
        else:
            f = chain(*tasks).apply_async
        return f(parent_task=self).get()


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
    kwargs.setdefault("base", CustomTask)
    return _shared_task(*args, **kwargs)


class ChainResult(list):
    def get(self, *args, **kwargs):
        kwargs["disable_sync_subtasks"] = False
        return [
            res.get(*args, **kwargs) if hasattr(res, "get") else res for res in self
        ]


class BaseChainExecutor:
    uses_celery = True

    def __init__(self, chain, update_state=True):
        self.chain = chain

    def _validate_parent_task(self, kwargs):
        parent_task = kwargs.get("parent_task")
        if not parent_task:
            raise ValueError("parent_task is required")
        return parent_task

    def _process_result(self, parent_task, res):
        if self.uses_celery:
            parent_task.update_state(state=states.STARTED)
            return res.get(disable_sync_subtasks=False)
        else:
            return res

    def execute_single_task(self, task, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement execute_single_task")

    def _process_tasks(self, args, kwargs):
        parent_task = self._validate_parent_task(kwargs)
        outs = []
        for t in self.chain.tasks:
            result = self.execute_single_task(t, *args, **kwargs)
            outs.append(self._process_result(parent_task, result))
        return ChainResult(outs)

    def execute(self, *args, **kwargs):
        return self._process_tasks(args, kwargs)


class SyncChainExecutor(BaseChainExecutor):
    def execute_single_task(self, task, *args, **kwargs):
        return task.apply(*args, **kwargs)


class AsyncChainExecutor(BaseChainExecutor):
    def execute_single_task(self, task, *args, **kwargs):
        return task.apply_async(*args, **kwargs)


class DirectChainExecutor(BaseChainExecutor):
    uses_celery = False

    def execute_single_task(self, task, *args, **kwargs):
        if isinstance(task, type(self.chain)):
            return task._call_directly(*task.args, **task.kwargs)
        return task.type(*task.args, **task.kwargs)


class chain(celery_chain):
    def apply(self, *args, **kwargs):
        executor = SyncChainExecutor(self)
        return executor.execute(*args, **kwargs)

    def apply_async(self, *args, **kwargs):
        if os.getenv("CUSTOM_CELERY_EAGER") == "true":
            return self.apply(*args, **kwargs)
        executor = AsyncChainExecutor(self)
        return executor.execute(*args, **kwargs)

    def _call_directly(self, *args, **kwargs):
        executor = DirectChainExecutor(self)
        return executor.execute(*args, **kwargs)
