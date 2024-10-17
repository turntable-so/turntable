import shlex
import os
import json

from django.http import StreamingHttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from adrf.views import APIView
from asgiref.sync import sync_to_async

from app.models.git_connections import Branch
from workflows.dbt_runner import DBTStreamerWorkflow


class StreamDBTCommandView(APIView):
    async def post(self, request):
        from workflows.main import hatchet

        try:
            data = json.loads(request.body)
            command = data.get("command")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON in request body")

        if not command:
            return HttpResponseBadRequest("Command is required")

        # Convert command to list if it's a string
        if isinstance(command, str):
            command = shlex.split(command)
        elif not isinstance(command, list):
            return HttpResponseBadRequest("Command must be a string or a list")

        # Use sync_to_async for synchronous functions
        workspace = await sync_to_async(request.user.current_workspace)()
        dbt_details = await sync_to_async(workspace.get_dbt_details)()
        branch_name = request.GET.get("branch_name")
        if branch_name:
            try:
                branch = await sync_to_async(Branch.objects.get)(
                    workspace=workspace,
                    repository=dbt_details.repository,
                    branch_name=branch_name,
                )
                branch_id = branch.id
            except Branch.DoesNotExist:
                return HttpResponseNotFound(f"Branch {branch_name} not found")
        else:
            branch_id = None

        # Fetch resource_id synchronously before entering async function
        resource_id = await sync_to_async(lambda: str(dbt_details.resource.id))()
        dbt_resource_id = str(dbt_details.id)

        if os.getenv("BYPASS_HATCHET") == "true":

            async def stream():
                # Wrap synchronous context manager
                transition_context = await sync_to_async(dbt_details.dbt_transition_context)(
                    branch_id=branch_id
                )
                # Since the context manager is synchronous, use async with sync_to_async
                async with sync_to_async(transition_context.__enter__)() as (transition, _, repo):
                    # Wrap synchronous generator function
                    for output in transition.after.stream_dbt_command(command):
                        yield output
                # Ensure the context manager's __exit__ method is called
                await sync_to_async(transition_context.__exit__)(None, None, None)

        else:

            async def stream():
                input = {
                    "command": command,
                    "branch_id": str(branch_id) if branch_id else None,
                    "resource_id": resource_id,
                    "dbt_resource_id": dbt_resource_id,
                }
                # Ensure run_workflow is async
                id = await hatchet.client.admin.run_workflow(
                    DBTStreamerWorkflow.__name__,
                    input=input,
                )
                # Use the asynchronous listener
                async for event in hatchet.client.listener.stream(id):
                    if event.payload and event.type == "STEP_RUN_EVENT_TYPE_STREAM":
                        yield event.payload

        return StreamingHttpResponse(stream(), content_type="text/event-stream")
