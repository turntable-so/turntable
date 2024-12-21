import os
import shlex
import shutil
import tempfile
import time
from typing import Any, Callable

import orjson
from celery import states
from git import Repo as GitRepo

from app.models.resources import DBTResource
from app.workflows.utils import task
from vinyl.lib.dbt import STREAM_ERROR_STRING, STREAM_SUCCESS_STRING
from vinyl.lib.utils.files import load_orjson

STREAM_BUFFER_INTERVAL = 1.0


def return_helper(success, stdout, stderr, run_results: dict | None = None):
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


def get_run_results(dbtproj):
    if os.path.exists(dbtproj.run_results_path):
        return load_orjson(dbtproj.run_results_path)
    return {}


def export_run_results_from_outputs(
    outs: list[dict], dbt_resource: Any, repo: str | None = None
) -> None:
    run_results_jsons = [
        orjson.dumps(out["run_results"]).decode("utf-8") for out in outs
    ]
    run_results_jsons = [j for j in run_results_jsons if j is not None]
    return dbt_resource.export_run_results(
        repo_override=repo, run_results_jsons=run_results_jsons
    )


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
    stream: bool = False,
    buffer_interval: float = STREAM_BUFFER_INTERVAL,
):
    repo_override = (
        GitRepo(repo_override_dir) if os.path.exists(repo_override_dir) else None
    )
    dbt_resource = DBTResource.objects.get(id=dbtresource_id)
    if not dbt_resource.jobs_allowed:
        raise Exception("Cannot orchestrate dbt commands on development resources")

    with dbt_resource.dbt_repo_context(
        project_id=project_id,
        isolate=True,
        repo_override=repo_override,
        force_terminal=True,
    ) as (dbtproj, project_dir, _):
        success = None
        stdout = ""
        stderr = ""
        split_command = shlex.split(command)
        if split_command[0] == "dbt":
            split_command.pop(0)

        if stream:
            last_update = time.time()

            for line in dbtproj.stream_dbt_command(split_command, write_json=True):
                if line == STREAM_SUCCESS_STRING:
                    success = True
                    break
                elif line == STREAM_ERROR_STRING:
                    success = False
                    break

                stdout += line
                current_time = time.time()

                if current_time - last_update >= buffer_interval:
                    result = return_helper(
                        success=success,
                        stdout=stdout,
                        stderr=stderr,
                    )
                    self.update_state(
                        state=states.STARTED,
                        meta=result,
                    )
                    last_update = current_time

            if success is None:
                raise RuntimeError("Stream ended without success or error signal")
        else:
            stdout, stderr, success = dbtproj.run_dbt_command(
                split_command, write_json=True
            )

        run_results = get_run_results(dbtproj)
        if save_artifacts and run_results:
            dbt_resource.export_run_results(run_results=run_results)
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

    repo_override = (
        GitRepo(repo_override_dir) if os.path.exists(repo_override_dir) else None
    )

    dbt_resource = DBTResource.objects.get(id=dbtresource_id)
    stdout, stderr, success = dbt_resource.upload_artifacts(
        artifact_source=ArtifactSource.ORCHESTRATION,
        repo_override=repo_override,
        export=True,
    )
    if not success:
        return return_helper(
            False,
            f"Error generating artifacts. Stderr: {stderr}. Stdout: {stdout}",
            "",
            {},
        )
    with dbt_resource.dbt_repo_context(
        project_id=project_id,
        isolate=True,
        repo_override=repo_override,
        force_terminal=True,
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

    with dbt_resource.dbt_repo_context(
        project_id=project_id, isolate=True, force_terminal=True
    ) as (dbtproj, project_dir, repo):
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
            run_dbt_command.si(**task_kwargs, command=command, stream=True)
            for command in commands
        ]

        if save_artifacts:
            tasks.append(
                save_artifacts_task.si(**task_kwargs, parent_task_id=self.request.id)
            )

        outs = self.run_subtasks(*tasks)

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
        with dbt_resource.dbt_repo_context(
            project_id=project_id, force_terminal=True
        ) as (dbtproj, project_dir, _):
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
