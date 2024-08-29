from backend.hatchet_initialization.create_db import create_hatchet_db
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run hatchet custom permissions on start"

    def handle(self, *args, **kwargs):
        out = create_hatchet_db()
        if out["success"]:
            self.stdout.write(self.style.SUCCESS(out["msg"]))
        else:
            self.stdout.write(self.style.WARNING(out["msg"]))
