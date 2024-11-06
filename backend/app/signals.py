import os
import re

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_celery_results.models import TaskResult

from app.models.workflows import (
    ScheduledWorkflow,
    WorkflowTaskMap,
    get_periodic_task_key,
)


def signal_periodic_task_started(instance):
    if os.getenv("BYPASS_CELERY_BEAT") == "true":
        workflow_id = WorkflowTaskMap.inverse_map.get(instance.task_id)
        if not workflow_id:
            return

        workflow = ScheduledWorkflow.objects.get(id=workflow_id)
        instance.periodic_task_name = workflow.replacement_identifier

    if instance.periodic_task_name:
        cache.set(
            key=get_periodic_task_key(instance.periodic_task_name),
            value=instance.task_id,
            timeout=500,
        )


@receiver(pre_save, sender=TaskResult)
def task_result_pre_save(sender, instance, **task_kwargs):
    signal_periodic_task_started(instance)
    try:
        old_status = TaskResult.objects.get(pk=instance.pk).status
    except TaskResult.DoesNotExist:
        old_status = None
    new_status = instance.status

    if old_status == new_status:
        return

    ids_to_fetch = {"workspace_id": True, "resource_id": False}
    ids = {}
    for id, mandatory in ids_to_fetch.items():
        pattern = r"""['"]""" + id + r"""['"]\s*:\s*(['"])(.*?)\1"""
        match = re.search(pattern, instance.task_kwargs)
        if match:
            ids[id] = match.group(2)
        elif mandatory:
            raise ValueError(f"{id} is required as a kwarg on all tasks")

    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            f"workspace_{ids['workspace_id']}",
            {
                "type": "workflow_status_update",
                "status": instance.status,
                "task_id": str(instance.id),
                **ids,
            },
        )
    except Exception as e:
        print(e)
        print("Error sending status update")
