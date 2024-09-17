import os
import shutil
import time

from django.core.management import call_command
from django.core.management.base import BaseCommand

from app.models import Resource


class Command(BaseCommand):
    help = "Export db data and datahub dbs as a zip in exports folder"

    def handle(self, *args, **kwargs):
        base_dir = "fixtures/datahub_dbs"
        # get db dump
        output_file = os.path.join(base_dir, "dumpdata.json")
        with open(output_file, "w") as f:
            call_command("dumpdata", "--format=json", stdout=f)

        # get datahub db
        for resource in Resource.objects.all():
            if not resource.datahub_db:
                continue
            with resource.datahub_db.open("rb") as f:
                db_save_path = os.path.join(
                    base_dir, f"{resource.id}_{resource.details.subtype}.duckdb"
                )
                with open(db_save_path, "wb") as f2:
                    f2.write(f.read())

        # package everything as a zip
        export_dir = "exports/"
        os.makedirs(export_dir, exist_ok=True)
        zip_path = f"{round(time.time())}_db_export"
        shutil.make_archive(zip_path, "zip", base_dir)
        shutil.move(f"{zip_path}.zip", export_dir)

        # delete dumpdata.json
        os.remove(output_file)
