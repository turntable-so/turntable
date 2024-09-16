from django.core.management.base import BaseCommand

from app.models import Resource, Workspace


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    def handle(self, *args, **kwargs):
        ws = Workspace.objects.get(name="capchase")
        breakpoint()
