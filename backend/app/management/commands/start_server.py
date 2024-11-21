import uvicorn
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start the Django development server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode", choices=["demo", "dev", "dev-internal", "staging"]
        )

    def handle(self, *args, **options):
        call_command("migrate")
        call_command("custom_create_superuser")
        call_command("collectstatic", interactive=False)

        # if options["mode"] in ["demo", "dev", "dev-internal"]:
        #     call_command("seed_data")
        # if options["mode"] in ["dev-internal", "staging"]:
        #     call_command("seed_data_staging")

        uvicorn_args = {
            "host": "0.0.0.0",
            "port": 8000,
        }

        if options["mode"] in ["dev", "dev-internal", "staging"]:
            uvicorn_args["reload"] = True
            uvicorn_args["reload_excludes"] = ["/code/media/ws/"]

        uvicorn.run("api.asgi:application", **uvicorn_args)
