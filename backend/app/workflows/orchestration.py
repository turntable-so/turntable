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
    workspace_id: str,
    resource_id: str,
    dbt_resource_id: str,
    command: str,
    branch_id: str | None = None,
):
    dbt_resource = DBTResource.objects.get(id=dbt_resource_id)
    if not dbt_resource.jobs_allowed:
        raise Exception("Cannot orchestrate dbt commands on development resources")

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
    workspace_id: str,
    resource_id: str,
    dbt_resource_id: str,
    commands: list[str],
    branch_id: str | None = None,
    refresh_artifacts=True,
):
    outs = []
    for i, command in enumerate(commands):
        out = run_dbt_command(
            workspace_id=workspace_id,
            resource_id=resource_id,
            dbt_resource_id=dbt_resource_id,
            command=command,
            branch_id=branch_id,
        )
        outs.append(out)
    if refresh_artifacts:
        dbtresource = DBTResource.objects.get(id=dbt_resource_id)
        dbtresource.upload_artifacts(branch_id=branch_id)
    return returns_helper(outs)


# can't make this a workflow because celery doesn't support streaming this way, but leaving in while for now.
def stream_dbt_command(
    self,
    workspace_id: str,
    resource_id: str,
    branch_id: str,
    dbt_resource_id: str,
    command: str,
    defer: bool = True,
    should_terminate: bool = None,
):
    dbt_resource = DBTResource.objects.get(id=dbt_resource_id)
    if not dbt_resource.development_allowed:
        raise Exception("Cannot stream dbt commands on production resources")
    prod_environment = dbt_resource.get_prod_environment()
    if prod_environment is None or not defer:
        with dbt_resource.dbt_repo_context(branch_id=branch_id) as (
            dbtproj,
            project_dir,
            _,
        ):
            yield from dbtproj.stream_dbt_command(command)
    else:
        with dbt_resource.dbt_transition_context(branch_id=branch_id) as (
            transition,
            project_dir,
            _,
        ):
            transition.before.mount_manifest()
            transition.before.mount_catalog()
            yield from transition.after.stream_dbt_command(
                command, should_terminate=should_terminate
            )
