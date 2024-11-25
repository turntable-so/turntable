import inspect
import os

from celery import Task, _state, states
from celery import chain as celery_chain
from celery.local import Proxy


class CustomTask(Task):
    """
    Custom base class for tasks to override the `apply` method.

    """

    def _adjust_inputs(self, *args, **kwargs):
        # Argsrepr and kwargsrepr are used to ensure correct json serialization of task_args and task_kwargs in the Result backend.
        kwargs["argsrepr"] = args[0]
        kwargs["kwargsrepr"] = args[1]
        return args, kwargs

    def apply(self, *args, **kwargs):
        args, kwargs =self._adjust_inputs(*args, **kwargs)
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
        return ChainResult(outs)

    def apply_async(self, *args, **kwargs):
        parent_task = kwargs.pop("parent_task", None)
        if not parent_task:
            raise ValueError("parent_task is required")

        outs = []
        for t in self.tasks:
            res = t.apply_async(*args, **kwargs)
            outs.append(self._process_result(parent_task, res))
        return ChainResult(outs)

    def _run_directly(self):
        outs = []
        for t in self.tasks:
            if isinstance(t, type(self)):
                res = t._run_directly()
            else:
                res = t.type(*t.args, **t.kwargs)
            outs.append(res)
        return ChainResult(outs)
