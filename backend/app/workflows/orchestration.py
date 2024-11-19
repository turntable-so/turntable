import os
import shlex
import shutil
import tempfile
from typing import Callable

from git import Repo as GitRepo

from app.models.resources import DBTResource
from app.workflows.utils import chain, task
from vinyl.lib.utils.files import load_orjson


def return_helper(success, stdout, stderr, run_results):
    return {
        "success": success,
        "stdout": stdout,
        "stderr": stderr,
        "run_results": run_results,
    }


def returns_helper(outs):
    # get the run_results from the last non-empty run_results
    run_result = None
    for out in outs[::-1]:
        if not out:
            continue
        if rr := out.get("run_results"):
            run_result = rr
            break

    return {
        "success": all(out["success"] for out in outs),
        "stdouts": [out["stdout"] for out in outs],
        "stderrs": [out["stderr"] for out in outs],
        "run_results": run_result,
    }


@task
def run_dbt_command(
    self,
    workspace_id: str,
    resource_id: str,
    dbtresource_id: str,
    command: str,
    project_id: str | None = None,
    repo_override_dir: str | None = None,
    save_artifacts: bool = True,
):
    dbt_resource = DBTResource.objects.get(id=dbtresource_id)
    if not dbt_resource.jobs_allowed:
        raise Exception("Cannot orchestrate dbt commands on development resources")

    with dbt_resource.dbt_repo_context(
        project_id=project_id, isolate=True, repo_override=GitRepo(repo_override_dir)
    ) as (dbtproj, project_dir, _):
        # run command
        try:
            split_command = shlex.split(command)
            if split_command[0] == "dbt":
                split_command.pop(0)
            stdout, stderr, success = dbtproj.run_dbt_command(
                split_command, write_json=True
            )
        finally:
            if os.path.exists(dbtproj.run_results_path):
                run_results = load_orjson(dbtproj.run_results_path)
            else:
                run_results = {}

        return return_helper(success, stdout, stderr, run_results)


@task
def save_artifacts_task(
    self,
    workspace_id: str,
    resource_id: str,
    dbtresource_id: str,
    parent_task_id: str,
    project_id: str | None = None,
    repo_override_dir: str | None = None,
):
    from app.models.resources import ArtifactSource
    from app.models.workflows import ArtifactType, TaskArtifact

    dbt_resource = DBTResource.objects.get(id=dbtresource_id)
    stdout, stderr, success = dbt_resource.upload_artifacts(
        artifact_source=ArtifactSource.ORCHESTRATION,
        repo_override=GitRepo(repo_override_dir),
    )
    if not success:
        return return_helper(
            False,
            f"Error generating artifacts. Stderr: {stderr}. Stdout: {stdout}",
            "",
            {},
        )
    with dbt_resource.dbt_repo_context(
        project_id=project_id, repo_override=GitRepo(repo_override_dir)
    ) as (dbtproj, _, _):
        # Save a zip of the target directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_zip_path = os.path.join(tmp_dir, f"target_{parent_task_id}.zip")
            shutil.make_archive(tmp_zip_path, "zip", dbtproj.target_path)

            # Create TaskArtifact and save the zip file
            artifact = TaskArtifact.objects.create(
                task_id=parent_task_id,
                workspace_id=workspace_id,
                artifact_type=ArtifactType.TARGET,
            )
            with open(f"{tmp_zip_path}.zip", "rb") as zip_file:
                artifact.artifact.save(f"target_{parent_task_id}.zip", zip_file)

    return return_helper(True, "uploaded artifacts successfully", "", {})


@task
def run_dbt_commands(
    self,
    workspace_id: str,
    resource_id: str,
    dbtresource_id: str,
    commands: list[str],
    project_id: str | None = None,
    save_artifacts=True,
):
    dbt_resource = DBTResource.objects.get(id=dbtresource_id)
    if not dbt_resource.jobs_allowed:
        raise Exception("Cannot orchestrate dbt commands on development resources")

    with dbt_resource.dbt_repo_context(project_id=project_id, isolate=True) as (
        dbtproj,
        project_dir,
        repo,
    ):
        if os.path.exists(dbtproj.target_path):
            shutil.rmtree(dbtproj.target_path)
        outs = []
        task_kwargs = {
            "workspace_id": workspace_id,
            "resource_id": resource_id,
            "dbtresource_id": dbtresource_id,
            "project_id": project_id,
            "repo_override_dir": repo.working_tree_dir,
        }
        # Create a chain of tasks
        tasks = [
            run_dbt_command.si(**task_kwargs, command=command) for command in commands
        ]

        if save_artifacts:
            tasks.append(
                save_artifacts_task.si(**task_kwargs, parent_task_id=self.request.id)
            )

        outs = chain(*tasks).apply_async_and_get_all()

    return returns_helper(outs)


# can't make this a workflow because celery doesn't support streaming this way, but leaving in while for now.
def stream_dbt_command(
    workspace_id: str,
    resource_id: str,
    project_id: str,
    dbt_resource_id: str,
    command: str,
    defer: bool = True,
    should_terminate: Callable[[], bool] | None = None,
):
    dbt_resource = DBTResource.objects.get(id=dbt_resource_id)
    if not dbt_resource.development_allowed:
        raise Exception("Cannot stream dbt commands on production resources")
    job_environment = dbt_resource.get_job_dbtresource(
        workspace_id=workspace_id, resource_id=resource_id
    )
    if job_environment is None or not defer:
        with dbt_resource.dbt_repo_context(project_id=project_id) as (
            dbtproj,
            project_dir,
            _,
        ):
            yield from dbtproj.stream_dbt_command(
                command, should_terminate=should_terminate, write_json=True
            )
    else:
        with dbt_resource.dbt_transition_context(
            project_id=project_id, override_job_resource=job_environment
        ) as (transition, project_dir, _):
            transition.before.mount_manifest()
            transition.before.mount_catalog()
            yield from transition.after.stream_dbt_command(
                command, should_terminate=should_terminate, write_json=True
            )
