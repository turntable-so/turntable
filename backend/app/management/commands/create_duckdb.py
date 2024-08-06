from django.core.management.base import BaseCommand

from app.models import Resource, Workspace


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
            workspace=ws,
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database"))
