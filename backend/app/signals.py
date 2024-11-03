import json
import os

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

    task_kwargs = json.loads(instance.task_kwargs)
    if isinstance(task_kwargs, str):
        task_kwargs = task_kwargs.replace("'", '"')
        task_kwargs = json.loads(task_kwargs)

    if "workspace_id" not in task_kwargs:
        raise ValueError("Workspace ID is required as a kwarg on all tasks")

    workspace_id = task_kwargs["workspace_id"]

    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            f"workspace_{workspace_id}",
            {
                "type": "workflow_status_update",
                "status": instance.status,
                "workflow_run_id": str(instance.id),
                **task_kwargs,
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
