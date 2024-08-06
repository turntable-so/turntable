from django.core.management.base import BaseCommand
import ibis

from app.models import GithubInstallation, Profile, Resource, User, Workspace

import uuid

from app.services.asset_service import AssetService


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    def handle(self, *args, **kwargs):
        ws = Workspace.objects.get(name="Turntable")
        resource = Resource.objects.get(name="duckdb")
        assets = AssetService(ws.id).get_assets_for_resource(resource.id)
        breakpoint()

    # def handle(self, *args, **kwargs):
    #     sql = "select business_id from business limit 10;"
    #     resource = Resource.objects.get(name="duckdb")
    #     connect = ibis.duckdb.connect(resource.config["file_path"])
    #     table = connect.sql(sql)
    #     df = table.execute()
    #     result = df.to_json(orient="records")
    #     breakpoint()
