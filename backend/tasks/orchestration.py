import os
import shlex
import shutil

from celery import shared_task

from app.models import DBTResource
from vinyl.lib.utils.files import load_orjson


def return_helper(success, stdout, stderr, run_results):
    return {
        "success": success,
        "stdout": stdout,
        "stderr": stderr,
        "run_results": run_results,
    }


def returns_helper(outs):
    return {
        "success": all(out["success"] for out in outs),
        "stdouts": [out["stdout"] for out in outs],
        "stderrs": [out["stderr"] for out in outs],
        "run_results": [out["run_results"] for out in outs],
    }


@shared_task
def run_dbt_command(
    resource_id: str, dbt_resource_id: str, branch_id: str | None, command: str
):
    dbt_resource = DBTResource.objects.get(id=dbt_resource_id)
    with dbt_resource.dbt_repo_context(branch_id=branch_id, isolate=True) as (
        dbtproj,
        project_dir,
        _,
    ):
        ## delete target folder
        if os.path.exists(dbtproj.target_path):
            shutil.rmtree(dbtproj.target_path)

        # run command
        stdout, stderr, success = dbtproj.run_dbt_command(
            shlex.split(command), write_json=True
        )

        # load run results
        if os.path.exists(dbtproj.run_results_path):
            run_results = load_orjson(dbtproj.run_results_path)
        else:
            run_results = {}
        return return_helper(success, stdout, stderr, run_results)


@shared_task
def run_dbt_commands(
    resource_id: str, dbt_resource_id: str, branch_id: str | None, commands: list[str]
):
    outs = []
    for i, command in enumerate(commands):
        out = (
            run_dbt_command.s(
                resource_id=resource_id,
                dbt_resource_id=dbt_resource_id,
                branch_id=branch_id,
                command=command,
            )
            .apply()
            .get()
        )
        outs.append(out)
    return returns_helper(outs)
