import os
import shutil

from hatchet_sdk import Context

from app.models import Resource
from vinyl.lib.utils.files import load_orjson
from workflows.hatchet import hatchet
from workflows.utils.log import inject_workflow_run_logging


def return_helper(success, stdouts, stderrs, run_results):
    return {
        "success": success,
        "stdouts": stdouts,
        "stderrs": stderrs,
        "run_results": run_results,
    }


@inject_workflow_run_logging(hatchet)
@hatchet.workflow(on_events=["metadata_sync"], timeout="15m")
class DBTRunnerWorkflow:
    """
    input structure:
        {
            resource_id: str,
            commands: list[str]
            dbt_resource_id: str | None,
        }
    """

    @hatchet.step(timeout="30m")
    def run_dbt_commands(self, context: Context):
        resource_id = context.workflow_input()["resource_id"]
        dbt_resource_id = context.workflow_input().get("dbt_resource_id")
        resource = Resource.objects.get(id=resource_id)
        dbt_resource = resource.get_dbt_resource(dbt_resource_id)

        # Run the dbt commands
        with dbt_resource.dbt_repo_context() as (dbtproj, project_dir):
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
