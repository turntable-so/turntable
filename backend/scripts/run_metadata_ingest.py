import django

django.setup()

from app.workflows.metadata import prepare_dbt_repos, ingest_metadata, process_metadata  # noqa
from app.models import Workspace, Resource  # noqa

if __name__ == "__main__":
    workspace = Workspace.objects.get(name="VIO")
    resource = Resource.objects.filter(workspace=workspace).first()
    # breakpoint()
    # prepare_dbt_repos(workspace.id, resource.id)
    # ingest_metadata(workspace.id, resource.id)
    process_metadata(workspace.id, resource.id)
