import os
import subprocess

from django.core.management.base import BaseCommand

BASE_CELERY_COMMAND = "celery -A api worker -E --loglevel=info"
IGNORE_FOLDERS = ["./media/ws"]
IGNORE_PATTERNS = []
MAX_DEPTH = 10
for path in IGNORE_FOLDERS:
    for depth in range(1, MAX_DEPTH):
        IGNORE_PATTERNS.append(path + "/*" * depth)
IGNORE_PATTERNS = ";".join(IGNORE_PATTERNS)
WATCHMEDO_COMMAND = f'watchmedo auto-restart --directory=. --pattern="*.py" --recursive --ignore-patterns="{IGNORE_PATTERNS}" --ignore-directories -- '


class Command(BaseCommand):
    help = "Start the Django development worker."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode", choices=["demo", "dev", "dev-internal", "staging"]
        )
        parser.add_argument("--concurrency", type=int, default=8)
        parser.add_argument(
            "--pool",
            choices=["solo", "threads", "processes", "gevent", "eventlet"],
            default="threads",
        )
        parser.add_argument("--worker_name", type=str, default=None)

    def handle(self, *args, **options):
        if options["concurrency"] < 2:
            raise ValueError("Concurrency must be at least 2")
        celery_command = (
            BASE_CELERY_COMMAND
            + f" --concurrency={options['concurrency']} --pool={options['pool']}"
        )
        worker_name = options["worker_name"] or os.getenv("WORKER_NAME")
        if worker_name:
            celery_command += f" --hostname={worker_name}@h"
        if options["mode"] in ["dev", "dev-internal", "staging"]:
            celery_command = WATCHMEDO_COMMAND + celery_command

        subprocess.run(celery_command, shell=True)
