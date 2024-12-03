import django

django.setup()


if __name__ == "__main__":
    from app.models import Resource, Workspace
    from app.workflows.metadata import (  # noqa
        ingest_metadata,
        prepare_dbt_repos,
        process_metadata,
    )

    workspace = Workspace.objects.get(name="VIO")
    resource = Resource.objects.get(workspace=workspace)
    # prepare_dbt_repos(workspace.id, resource.id)
    # ingest_metadata(workspace.id, resource.id)
    process_metadata(workspace.id, resource.id)
