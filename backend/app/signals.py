# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# from app.models import WorkflowRun


# @receiver(post_save, sender=WorkflowRun)
# def send_status_update(sender, instance, **kwargs):
#     if "status" in instance.get_dirty_fields().keys():
#         workspace_id = instance.resource.workspace_id
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"workspace_{workspace_id}",
#             {
#                 "type": "workflow_status_update",
#                 "status": instance.status,
#                 "workflow_run_id": str(instance.id),
#             },
#         )
