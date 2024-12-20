from celery import current_app
from django.core.management.base import BaseCommand

from app.management.commands.suspend_worker import (
    get_active_queues,
    get_relevant_workers,
)


def add_consumer(
    hostname: str | None = None,
    excluded_queues: list[str] = [],
    inexact_hostname: bool = False,
) -> list[str]:
    active_queues, active_workers, worker_queue_map = get_active_queues(
        exclude_workers_without_queues=False, excluded_queues=excluded_queues
    )
    # ensure the default queue is included
    default_queue = current_app.conf.task_default_queue
    if default_queue:
        active_queues.add(default_queue)

    relevant_workers = get_relevant_workers(
        active_workers, hostname, inexact_hostname=inexact_hostname
    )
    for worker in relevant_workers:
        # add consumer if the worker is not already consuming from the queue
        for queue in active_queues:
            if queue not in worker_queue_map.get(worker, []):
                print(f"Adding consumer for {queue} to {worker}")
                current_app.control.add_consumer(queue=queue, destination=[worker])

    return relevant_workers


class Command(BaseCommand):
    help = "Resume all workers on a given machine."

    def add_arguments(self, parser):
        parser.add_argument("--hostname", type=str, required=False)
        parser.add_argument(
            "--excluded-queues",
            type=str,
            nargs="+",
            required=False,
            default=[],
        )
        parser.add_argument(
            "--inexact-hostname",
            action="store_true",
            required=False,
            default=False,
        )

    def handle(self, *args, **options):
        hostname = options["hostname"]
        excluded_queues = options["excluded_queues"]
        inexact_hostname = options["inexact_hostname"]

        # prevent the worker from being scheduled
        add_consumer(hostname, excluded_queues, inexact_hostname=inexact_hostname)
