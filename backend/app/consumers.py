import json
import logging
import shlex

from channels.generic.websocket import AsyncWebsocketConsumer
from workflows.main import hatchet
from asgiref.sync import sync_to_async

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


class DBTCommandConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from app.models.workspace import Workspace

        print(f"WebSocket connected for user: {self.scope['user']}")

        await self.accept()
        logger.info(f"WebSocket connected for user: {self.scope['user']}")

        # TODO: we shouldn't be using the route to get the workspace id cause then
        # anyone can try to connect to it
        # we should be passing in a token to the websocket that has the workspace id in it
        self.workspace_id = self.scope["url_route"]["kwargs"]["workspace_id"]
        if self.workspace_id is None:
            await self.close(code=4001, reason="Workspace ID is required")
            return
        
        self.workspace = await sync_to_async(Workspace.objects.get)(id=self.workspace_id)
        self.dbt_details = await sync_to_async(self.workspace.get_dbt_details)()

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with close code: {close_code}")
        # TODO: abort the workflow here if it's running

    async def receive(self, text_data):
        # load these inside or else we get "Apps aren't loaded yet" error
        from app.models.git_connections import Branch
        from workflows.dbt_runner import DBTStreamerWorkflow

        data = json.loads(text_data)
        command = data.get("command")
        branch_name = data.get("branch_name")

        if command is None:
            raise ValueError("Command is required")
        else:
            command = shlex.split(command)

        if branch_name:
            try:
                branch = await sync_to_async(Branch.objects.get)(
                    workspace=self.workspace,
                    repository=self.dbt_details.repository,
                    branch_name=branch_name,
                )
                branch_id = branch.id
            except Branch.DoesNotExist:
                raise ValueError(f"Branch {branch_name} not found")
        else:
            branch_id = None
        
        dbt_resource_id = await sync_to_async(lambda: str(self.dbt_details.id))()
        resource_id = await sync_to_async(lambda: str(self.dbt_details.resource.id))()

        input = {
            "command": command,
            "branch_id": str(branch_id) if branch_id else None,
            "resource_id": resource_id,
            "dbt_resource_id": dbt_resource_id,
        }
        workflow_run_id = hatchet.admin.run_workflow(
            DBTStreamerWorkflow.__name__,
            input=input,
        )
        listener = hatchet.listener.stream(workflow_run_id)

        async for event in listener:
            if event.payload and event.type == "STEP_RUN_EVENT_TYPE_STREAM":
                await self.send(text_data=event.payload)

                if event.payload.startswith("PROCESS_STREAM_SUCCESS"):
                    await self.close()
                elif event.payload.startswith("PROCESS_STREAM_ERROR"):
                    await self.close(code=4001, reason="Error running dbt command")
