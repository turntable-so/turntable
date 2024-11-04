import asyncio
import json
import logging
import shlex

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from app.models.resources import DBTResource

logger = logging.getLogger(__name__)


def stream_dbt_command(
    dbt_resource: DBTResource,
    branch_id: str,
    command: str,
):
    with dbt_resource.dbt_transition_context(branch_id=branch_id) as (
        transition,
        project_dir,
        _,
    ):
        yield from transition.after.stream_dbt_command(command)


class DBTCommandConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"WebSocket connected for user: {self.scope['user']}")
        await self.accept()

        self.workspace = await sync_to_async(self.scope["user"].current_workspace)()
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

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start":
            if self.workflow_task and not self.workflow_task.done():
                await self.send(text_data="TASK_ALREADY_RUNNING")
                return

            self.workflow_task = asyncio.create_task(self.run_workflow(data))
        elif action == "cancel":
            if self.workflow_task and not self.workflow_task.done():
                self.workflow_task.cancel()
                await self.send(text_data="WORKFLOW_CANCELLED")
        else:
            raise ValueError(
                f"Invalid action: {action} - only 'start' and 'cancel' are supported"
            )

    async def run_workflow(self, data):
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

            # dbt_resource_id = await sync_to_async(lambda: str(self.dbt_details.id))()
            # resource_id = await sync_to_async(
            #     lambda: str(self.dbt_details.resource.id)
            # )()

            # input_data = {
            #     "command": command,
            #     "branch_id": str(branch_id) if branch_id else None,
            #     "resource_id": resource_id,
            #     "dbt_resource_id": dbt_resource_id,
            # }

            stream_generator = await sync_to_async(stream_dbt_command)(
                self.dbt_details, branch_id, command
            )
            for output_chunk in stream_generator:
                await self.send(text_data=output_chunk)

            # assume success if we've reached the end of the event stream
            await self.send(text_data="PROCESS_STREAM_SUCCESS")
            await self.close()
        except asyncio.CancelledError:
            logger.info("Workflow run was cancelled.")
            await self.send(text_data="WORKFLOW_CANCELLED")
            await self.close()
            raise
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            await self.send(text_data=f"ERROR: {str(e)}")
            await self.close()
