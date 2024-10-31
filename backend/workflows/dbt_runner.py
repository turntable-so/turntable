import os
import shutil

from hatchet_sdk import Context

from app.models import Resource
from app.models.resources import DBTCoreDetails
from vinyl.lib.utils.files import load_orjson
from workflows.hatchet import hatchet
from workflows.utils.debug import spawn_workflow
from workflows.utils.log import inject_workflow_run_logging


def return_helper(success, stdouts, stderrs, run_results):
    return {
        "success": success,
        "stdouts": stdouts,
        "stderrs": stderrs,
        "run_results": run_results,
    }


@hatchet.workflow(on_events=["run_dbt_command"], timeout="30m")
@inject_workflow_run_logging(hatchet)
class DBTRunnerWorkflow:
    """
    input structure:
        {
            resource_id: str,
            branch_id: str | None,
            commands: list[str]
            dbt_resource_id: str | None,
        }
    """

    @hatchet.step(timeout="30m")
    def run_dbt_commands(self, context: Context):
        resource_id = context.workflow_input()["resource_id"]
        branch_id = context.workflow_input().get("branch_id")
        dbt_resource_id = context.workflow_input().get("dbt_resource_id")
        resource = Resource.objects.get(id=resource_id)
        dbt_resource = resource.get_dbt_resource(dbt_resource_id)

        # Run the dbt commands
        with dbt_resource.dbt_repo_context(branch_id=branch_id) as (
            dbtproj,
            project_dir,
            _,
        ):
            ## delete target folder
            if os.path.exists(dbtproj.target_path):
                shutil.rmtree(dbtproj.target_path)

            ## run dbt commands
            run_results = []
            stdouts = []
            stderrs = []
            for command in context.workflow_input()["commands"]:
                stdout, stderr, success = dbtproj.run_dbt_command(
                    command.split(" "), write_json=True
                )
                stdouts.append(stdout)
                stderrs.append(stderr)
                if os.path.exists(dbtproj.run_results_path):
                    run_results.append(load_orjson(dbtproj.run_results_path))
                else:
                    run_results.append(None)
                if not success:
                    return return_helper(False, stdouts, stderrs, run_results)
            return return_helper(True, stdouts, stderrs, run_results)


@hatchet.workflow(on_events=["stream_dbt_command"], timeout="10m")
@inject_workflow_run_logging(hatchet)
class DBTStreamerWorkflow:
    """
    input structure:
        {
            command: str,
            branch_id: str | None,
            resource_id: str,
            dbt_resource_id: str,
        }
    """

    @hatchet.step(timeout="10m")
    def stream_dbt_command(self, context: Context):
        branch_id = context.workflow_input().get("branch_id")
        dbt_resource_id = context.workflow_input().get("dbt_resource_id")
        dbt_resource = DBTCoreDetails.objects.get(id=dbt_resource_id)
        command = context.workflow_input()["command"]

        def should_terminate():
            return context.done()

        with dbt_resource.dbt_transition_context(branch_id=branch_id) as (
            transition,
            project_dir,
            _,
        ):
            for line in transition.after.stream_dbt_command(
                command, should_terminate=should_terminate
            ):
                context.put_stream(line)


@hatchet.workflow(on_events=["test"], timeout="30m")
@inject_workflow_run_logging(hatchet)
class ParentWorkflow:
    @hatchet.step()
    def parent_step(self, context: Context):
        resource_id = context.workflow_input()["resource_id"]
        results = ["parent"]
        for i in range(10):
            results.append(
                spawn_workflow(
                    context,
                    ChildWorkflow,
                    {"a": str(i), "resource_id": resource_id},
                    key=f"child{i}",
                )
            )
        return results


@hatchet.workflow(on_events=["test2"], timeout="30m")
@inject_workflow_run_logging(hatchet)
class ChildWorkflow:
    @hatchet.step()
    def child_step(self, context: Context):
        return "child" + context.workflow_input()["a"]
