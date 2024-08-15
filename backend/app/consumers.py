# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class WorkflowRunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.workspace_id = self.scope["url_route"]["kwargs"]["workspace_id"]
        self.group_name = f"workspace_{self.workspace_id}"

        print(f"WorkflowRunCosnumer {self.group_name}", flush=True)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def workflow_status_update(self, event):
        print("sending status update!!! {}".format(event), flush=True)
        await self.send(
            text_data=json.dumps(
                {
                    "status": event["status"],
                    "workflow_run_id": event["workflow_run_id"],
                }
            )
        )
