from django.core.management.base import BaseCommand

from app.models import (
    Asset,
)
from fixtures.local_env import (
    create_local_metabase,
    create_local_postgres,
    create_local_user,
    create_local_workspace,
)
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import WorkflowDebugger


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    def handle(self, *args, **kwargs):
        user = create_local_user()
        workspace = create_local_workspace(user)
        postgres = create_local_postgres(workspace)
        metabase = create_local_metabase(workspace)
        if (
            Asset.objects.filter(resource=postgres).count() > 0
            and Asset.objects.filter(resource=metabase).count() > 0
        ):
            self.stdout.write(self.style.SUCCESS("Database already seeded"))
            return
        WorkflowDebugger(MetadataSyncWorkflow, {"resource_id": postgres.id}).run()
        WorkflowDebugger(MetadataSyncWorkflow, {"resource_id": metabase.id}).run()
        self.stdout.write(self.style.SUCCESS("Successfully seeded the database"))
