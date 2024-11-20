import os

from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import (
    Asset,
)
from app.workflows.metadata import sync_metadata
from fixtures.local_env import (
    create_local_metabase,
    create_local_postgres,
    create_local_user,
    create_local_workspace,
    create_repository_n,
    create_ssh_key_n,
)
from vinyl.lib.utils.env import set_env


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        user = create_local_user()
        workspace = create_local_workspace(user)
        git_repo = None
        if os.getenv("SSHKEY_0_PUBLIC") and os.getenv("SSHKEY_0_PRIVATE"):
            ssh_key = create_ssh_key_n(workspace, 0)
            git_repo = create_repository_n(workspace, 0, ssh_key)
        postgres = create_local_postgres(workspace, git_repo)
        metabase = create_local_metabase(workspace)
        if (
            Asset.objects.filter(resource=postgres).count() > 0
            and Asset.objects.filter(resource=metabase).count() > 0
        ):
            self.stdout.write(self.style.SUCCESS("Database already seeded"))
            return
        with set_env(CUSTOM_CELERY_EAGER="true"):
            print(os.getenv("CUSTOM_CELERY_EAGER"))
            sync_metadata(resource_id=postgres.id, workspace_id=workspace.id)
            sync_metadata(resource_id=metabase.id, workspace_id=workspace.id)
        self.stdout.write(self.style.SUCCESS("Successfully seeded the database"))
