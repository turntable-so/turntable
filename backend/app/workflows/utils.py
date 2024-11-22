import json
import os
import uuid

from celery import Task, shared_task, states
from celery import chain as celery_chain
from django_celery_results.models import TaskResult

from app.utils.obj import make_values_serializable


class CustomTask(Task):
    """
    Custom base class for tasks to override the `apply` method.
    """

    def apply(self, *args, **kwargs):
        if os.getenv("CUSTOM_CELERY_EAGER") != "true":
            return super().apply(*args, **kwargs)

        kwargs["task_id"] = kwargs.get("task_id") or str(uuid.uuid4())
        task_id = kwargs["task_id"]
        task_args_json = (
            json.dumps(make_values_serializable(args[0])) if args[0] else None
        )
        task_kwargs_json = (
            json.dumps(make_values_serializable(args[1])) if args[1] else None
        )
        tr = TaskResult.objects.create(
            task_id=task_id,
            status=states.PENDING,
            task_args=task_args_json,
            task_kwargs=task_kwargs_json,
        )
        try:
            res = Task.apply(self, *args, **kwargs)
            tr.result = res.get()
            tr.status = res.status
            tr.save()
            return res
        except Exception as e:
            tr.status = states.FAILURE
            tr.save()
            raise e

    def apply_async(self, *args, **kwargs):
        if os.getenv("CUSTOM_CELERY_EAGER") != "true":
            return super().apply_async(*args, **kwargs)
        return self.apply(*args, **kwargs)


def task(*args, **kwargs):
    kwargs.setdefault("bind", True)
    kwargs.setdefault("base", CustomTask)
    return shared_task(*args, **kwargs)


class chain(celery_chain):
    def do(self, *args, **kwargs):
        res = self.apply_async(*args, **kwargs)

        def recurse_results(res):
            out = res.get(disable_sync_subtasks=False)
            if res.parent is None:
                return [out]
            return recurse_results(res.parent) + [out]

        return recurse_results(res)

    def apply_async(self, *args, **kwargs):
        if os.getenv("CUSTOM_CELERY_EAGER") == "true":
            return celery_chain.apply(self, *args, **kwargs)
        return celery_chain.apply_async(self, *args, **kwargs)
