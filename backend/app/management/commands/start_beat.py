import subprocess

from django.core.management.base import BaseCommand

from app.management.commands.start_worker import WATCHMEDO_COMMAND

BASE_CELERY_COMMAND = "celery -A api beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"


class Command(BaseCommand):
    help = "Start the Django development worker."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode", choices=["demo", "dev", "dev-internal", "staging"]
        )

    def handle(self, *args, **options):
        celery_command = BASE_CELERY_COMMAND
        if options["mode"] in ["dev", "dev-internal"]:
            celery_command = WATCHMEDO_COMMAND + celery_command

        subprocess.run(celery_command, shell=True)
