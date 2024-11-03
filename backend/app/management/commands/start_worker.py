import subprocess

from django.core.management.base import BaseCommand

CELERY_COMMAND = (
    "celery -A api worker -E --beat --scheduler django --loglevel=info --concurrency=1"
)
EXCLUDE_PATHS = ["/code/media/ws/"]


class Command(BaseCommand):
    help = "Start the Django development server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode", choices=["demo", "dev", "dev-internal", "staging"]
        )

    def handle(self, *args, **options):
        if options["mode"] in ["dev", "dev-internal"]:
            watchmedo_command = f"watchmedo auto-restart -d /code -i {';'.join(EXCLUDE_PATHS)} --recursive -- {CELERY_COMMAND}"
            # subprocess.run(watchmedo_command, shell=True)
            subprocess.run(CELERY_COMMAND, shell=True)
        else:
            subprocess.run(CELERY_COMMAND, shell=True)
