from django.core.management.base import BaseCommand

from app.models import Resource, Workspace

import uuid

from app.models.resources import DataFileDetails, ResourceType


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    def handle(self, *args, **kwargs):
        ws = Workspace.objects.get(name="Turntable")
        Resource.objects.create(
            name="duckdb",
            type="DUCKDB",
            config={
                "file_path": "/data/yelp_db.duckdb",
            },
        )
        ws = Workspace.objects.get(name="Workspace")
        random_uuid = uuid.uuid4()
        resource = Resource.objects.create(
            type=ResourceType.DB,
            name="duckdb",
            workspace=ws,
        )
        DataFileDetails(
            resource=resource,
            path="/data/yelp_db.duckdb",
        ).save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database"))
