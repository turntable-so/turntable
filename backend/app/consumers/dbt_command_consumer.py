import asyncio
import json
import logging
import shlex

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from workflows.utils.debug import run_workflow, get_async_listener
from workflows.hatchet import hatchet

logger = logging.getLogger(__name__)

class DBTCommandConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"WebSocket connected for user: {self.scope['user']}")
        await self.accept()

        self.workspace = await sync_to_async(self.scope['user'].current_workspace)()
        if not self.workspace:
            raise ValueError("User does not have a current workspace")
        
        self.dbt_details = await sync_to_async(self.workspace.get_dbt_details)()
        if not self.dbt_details:
            raise ValueError("Workspace does not have a dbt resource")

        self.workflow_task = None
        self.workflow_run_id = None

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with close code: {close_code}")
        if self.workflow_task and not self.workflow_task.done():
            self.workflow_task.cancel()
            if self.workflow_run_id:
                await hatchet.rest.workflow_run_cancel(self.workflow_run_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        print("ws - received action: ", action)

        if action == "start":
            if self.workflow_task and not self.workflow_task.done():
                await self.send(text_data="TASK_ALREADY_RUNNING")
                return

            self.workflow_task = asyncio.create_task(self.run_workflow(data))
        elif action == "cancel":
            if self.workflow_task and not self.workflow_task.done():
                self.workflow_task.cancel()
                if self.workflow_run_id:
                    try:
                        hatchet.rest.workflow_run_cancel(self.workflow_run_id)
                    except Exception as e:
                        logger.error(f"Error cancelling Hatchet workflow: {e}")
                await self.send(text_data="WORKFLOW_CANCELLED")
            else:
                await self.send(text_data="NO_ACTIVE_WORKFLOW")
        else:
            await self.send(text_data="INVALID_ACTION")

    async def run_workflow(self, data):
        from workflows.dbt_runner import DBTStreamerWorkflow
        from app.models.git_connections import Branch

        try:
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

            input_data = {
                "command": command,
                "branch_id": str(branch_id) if branch_id else None,
                "resource_id": resource_id,
                "dbt_resource_id": dbt_resource_id,
            }
            # Start the workflow and get the workflow_run_id
            workflow_run_id, workflow_run = await run_workflow(
                workflow=DBTStreamerWorkflow,
                input=input_data
            )
            self.workflow_run_id = str(workflow_run_id)
            listener = await get_async_listener(workflow_run_id, workflow_run)

            async for event in listener:
                if event.payload and event.type == "STEP_RUN_EVENT_TYPE_STREAM":
                    await self.send(text_data=event.payload)
                else:
                    logger.info(f"ws - skipped event: {event}")

            # Assume success if we've reached the end of the event stream
            await self.send(text_data="PROCESS_STREAM_SUCCESS")
            await self.close()
        except asyncio.CancelledError:
            # Handle cancellation
            print("Workflow run was cancelled.")
            if self.workflow_run_id:
                await hatchet.rest.workflow_run_cancel(self.workflow_run_id)
            await self.send(text_data="WORKFLOW_CANCELLED")
            await self.close()
            # Re-raise the exception to propagate the cancellation
            raise
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            await self.send(text_data=f"ERROR: {str(e)}")
            await self.close()
