import os
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import Workspace
from fixtures.local_env import (
    create_local_orchestration,
)


class Command(BaseCommand):
    help = "Seed orchestration data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        try:
            workspace_id = os.getenv("BIGQUERY_0_WORKSPACE_ID")
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Workspace {workspace_id} does not exist")
            )
            return

        create_local_orchestration(workspace)
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully seeded the database with orchestration data"
            )
        )
