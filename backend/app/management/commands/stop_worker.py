from celery import current_app
from django.core.management.base import BaseCommand

BASE_CELERY_COMMAND = "celery -A api worker -E --loglevel=info"


class Command(BaseCommand):
    help = "Stop all workers on a given machine."

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, required=False)

    def handle(self, *args, **options):
        worker_responses = current_app.control.ping(timeout=1.0)
        active_workers = [list(worker.keys())[0] for worker in worker_responses]
        relevant_workers = [
            worker
            for worker in active_workers
            if worker.split("@")[0] == options["name"]
        ]
        if not relevant_workers:
            raise ValueError(f"Worker {options['name']} not found")

        current_app.control.shutdown(destination=relevant_workers)
