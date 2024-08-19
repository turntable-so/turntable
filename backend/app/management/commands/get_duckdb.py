from django.core.management.base import BaseCommand

from app.models import Resource, Workspace
from app.services.asset_service import AssetService


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    def handle(self, *args, **kwargs):
        ws = Workspace.objects.get(name="Turntable")
        resource = Resource.objects.get(name="duckdb")
        assets = AssetService(ws.id).get_assets_for_resource(resource.id)
