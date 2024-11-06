import json
import logging
import shlex
import threading

from channels.generic.websocket import WebsocketConsumer

from app.workflows.orchestration import stream_dbt_command

logger = logging.getLogger(__name__)

DBT_COMMAND_STREAM_TIMEOUT = 120
DBT_COMMAND_STREAM_POLL_INTERVAL = 0.01


class DBTCommandConsumer(WebsocketConsumer):
    def connect(self):
        logger.info(f"WebSocket connected for user: {self.scope['user']}")
        self.accept()

        self.workspace = self.scope["user"].current_workspace()
        if not self.workspace:
            raise ValueError("User does not have a current workspace")

        self.dbt_details = self.workspace.get_dbt_dev_details()
        if not self.dbt_details:
            raise ValueError("Workspace does not have a dbt resource")

        self.started = False

        self.terminate_event = threading.Event()

    def disconnect(self, close_code):
        self.terminate_event.set()
        logger.info(f"WebSocket disconnected with close code: {close_code}")

    def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start":
            if self.started:
                self.send(text_data="TASK_ALREADY_RUNNING")
                return
            self.started = True
            self.send(text_data="WORKFLOW_STARTED")
            my_thread = threading.Thread(target=lambda: self.run_workflow(data))
            my_thread.start()

        elif action == "cancel":
            self.send(text_data="WORKFLOW_CANCEL_REQUESTED")
            if self.started:
                self.terminate_event.set()
                self.send(text_data="WORKFLOW_CANCELLED")
        else:
            raise ValueError(
                f"Invalid action: {action} - only 'start' and 'cancel' are supported"
            )

    def run_workflow(self, data):
        from app.models.git_connections import Branch

        try:
            command = data.get("command")
            branch_name = data.get("branch_name")
            defer = data.get("defer", True)

            if command is None:
                raise ValueError("Command is required")
            else:
                command = shlex.split(command)

            if branch_name:
                try:
                    branch = Branch.objects.get(
                        workspace=self.workspace,
                        repository=self.dbt_details.repository,
                        branch_name=branch_name,
                    )
                    branch_id = branch.id
                except Branch.DoesNotExist:
                    raise ValueError(f"Branch {branch_name} not found")
            else:
                branch_id = None

            for output_chunk in stream_dbt_command(
                workspace_id=self.workspace.id,
                resource_id=self.dbt_details.resource.id,
                dbt_resource_id=self.dbt_details.id,
                command=command,
                branch_id=branch_id,
                defer=defer,
                should_terminate=self.terminate_event.is_set,
            ):
                self.send(text_data=output_chunk)

            # assume success if we've reached the end of the event stream
            self.close()
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            self.send(text_data=f"ERROR: {str(e)}")
            self.close()
