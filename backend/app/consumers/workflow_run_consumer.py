import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class WorkflowRunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.workspace_id = self.scope["url_route"]["kwargs"]["workspace_id"]
        self.group_name = f"workspace_{self.workspace_id}"
        logger.info(f"Connecting to WebSocket for workspace: {self.workspace_id}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"Disconnected from WebSocket for workspace: {self.workspace_id} with close code: {close_code}")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def workflow_status_update(self, event):
        logger.info(f"Sending status update for workflow: {event['workflow_run_id']} with status: {event['status']}")
        await self.send(
            text_data=json.dumps(
                {
                    "status": event["status"],
                    "workflow_run_id": event["workflow_run_id"],
                    "resource_id": event["resource_id"],
                }
            )
        )
