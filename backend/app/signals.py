from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save
from django.dispatch import receiver

from app.models import WorkflowRun


@receiver(pre_save, sender=WorkflowRun)
def send_status_update(sender, instance, **kwargs):
    try:
        old_status = WorkflowRun.objects.get(pk=instance.pk).status
    except WorkflowRun.DoesNotExist:
        old_status = None
    new_status = instance.status

    if old_status == new_status:
        return
    workspace_id = instance.resource.workspace_id
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            f"workspace_{workspace_id}",
            {
                "type": "workflow_status_update",
                "status": instance.status,
                "workflow_run_id": str(instance.id),
                "resource_id": str(instance.resource.id),
            },
        )
    except Exception as e:
        print(e)
        print("Error sending status update")
