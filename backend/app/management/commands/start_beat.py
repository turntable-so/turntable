import subprocess

from django.core.management.base import BaseCommand

BASE_CELERY_COMMAND = "celery -A api beat --l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

class Command(BaseCommand):
    help = "Start the Django development worker."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode", choices=["demo", "dev", "dev-internal", "staging"]
        )


    def handle(self, *args, **options):
        celery_command = BASE_CELERY_COMMAND
        subprocess.run(celery_command, shell=True)