import ast
import json
import os
import re

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_celery_results.models import TaskResult

from app.models.workflows import (
    WORKFLOW_STARTED_QUEUE,
    ScheduledWorkflow,
    WorkflowTaskMap,
)


@receiver(pre_save, sender=TaskResult)
def send_status_update(sender, instance, **task_kwargs):
    try:
        old_status = TaskResult.objects.get(pk=instance.pk).status
    except TaskResult.DoesNotExist:
        old_status = None
    new_status = instance.status

    if old_status == new_status:
        return

    ids = {}
    for id in ["workspace_id", "resource_id"]:
        pattern = r"""['"]""" + id + r"""['"]\s*:\s*(['"])(.*?)\1"""
        match = re.search(pattern, instance.task_kwargs)
        if match:
            ids[id] = match.group(2)
        else:
            raise ValueError(f"{id} is required as a kwarg on all tasks")

    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            f"workspace_{ids['workspace_id']}",
            {
                "type": "workflow_status_update",
                "status": instance.status,
                "workflow_run_id": str(instance.id),
                "resource_id": ids["resource_id"]
            },
        )
    except Exception as e:
        print(e)
        print("Error sending status update")


@receiver(pre_save, sender=TaskResult)
def task_result_pre_save(sender, instance, **kwargs):
    if os.getenv("BYPASS_CELERY_BEAT") == "true":
        workflow_id = WorkflowTaskMap.inverse_map.get(instance.task_id)
        if not workflow_id:
            return

        workflow = ScheduledWorkflow.objects.get(id=workflow_id)
        instance.periodic_task_name = workflow.replacement_identifier

    if instance.periodic_task_name:
        WORKFLOW_STARTED_QUEUE.put(
            {
                "periodic_task_name": instance.periodic_task_name,
                "task_id": instance.task_id,
            }
        )
