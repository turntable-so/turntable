import json
import logging
import shlex

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from workflows.utils.debug import run_workflow, get_async_listener

logger = logging.getLogger(__name__)

class DBTCommandConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"WebSocket connected for user: {self.scope['user']}")

        await self.accept()
        logger.info(f"WebSocket connected for user: {self.scope['user']}")

        self.workspace = await sync_to_async(self.scope['user'].current_workspace)()
        if not self.workspace:
            raise ValueError("User does not have a current workspace")
        
        self.dbt_details = await sync_to_async(self.workspace.get_dbt_details)()
        if not self.dbt_details:
            raise ValueError("Workspace does not have a dbt resource")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with close code: {close_code}")
        # TODO: abort the workflow here if it's running

    async def receive(self, text_data):
        # load these inside or else we get "Apps aren't loaded yet" error
        from app.models.git_connections import Branch
        from workflows.dbt_runner import DBTStreamerWorkflow

        print("ws - Received text data: ", text_data)

        data = json.loads(text_data)
        command = data.get("command")
        branch_name = data.get("branch_name")

        if command is None:
            raise ValueError("Command is required")
        else:
            command = shlex.split(command)

        print("ws - command: ", command)
        print("ws - branch_name: ", branch_name)

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

        print("ws - dbt_resource_id: ", dbt_resource_id)
        print("ws - resource_id: ", resource_id)

        input = {
            "command": command,
            "branch_id": str(branch_id) if branch_id else None,
            "resource_id": resource_id,
            "dbt_resource_id": dbt_resource_id,
        }
        workflow_run_id, workflow_run = await run_workflow(workflow=DBTStreamerWorkflow, input=input)

        print("workflow run id: ", workflow_run_id)
        print("workflow run: ", workflow_run)

        listener = await get_async_listener(workflow_run_id, workflow_run)
        print("listener: ", listener)

        async for event in listener:
            print("ws - event: ", event)
            if event.payload and event.type == "STEP_RUN_EVENT_TYPE_STREAM":
                print("ws - sending event: ", event.payload)
                await self.send(text_data=event.payload)
            else:
                logger.info(f"ws - skipped event: {event}")

        print("ws - sending success")

        # Assume success if we've reached the end of the event stream
        await self.send(text_data="PROCESS_STREAM_SUCCESS")
        await self.close()
