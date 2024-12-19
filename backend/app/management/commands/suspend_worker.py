import json
import subprocess
import time

from celery import current_app
from django.core.management.base import BaseCommand

POLLING_INTERVAL = 5
MAX_POLLING_ATTEMPTS = 10


# inspect out of process to avoid issues with the inspector
def _inspect_helper(tag: str):
    out = subprocess.run(
        ["celery", "-A", "api", "inspect", tag, "--json"],
        capture_output=True,
        check=True,
        text=True,
    )
    return json.loads(out.stdout)


def _get_active_queues_helper():
    return _inspect_helper("active_queues")


def _get_active_tasks_helper():
    for task_type in ["active", "scheduled", "reserved"]:
        yield _inspect_helper(task_type)


def get_active_queues(
    excluded_queues: list[str] = [],
    exclude_workers_without_queues: bool = True,
) -> tuple[set[str], set[str], dict[str, set[str]]]:
    active_queues = set()
    active_workers = set()
    worker_queue_map = {}
    inspect_helper = _get_active_queues_helper()
    for k, v in inspect_helper.items():
        if exclude_workers_without_queues and not v:
            continue
        worker_queue_map.setdefault(k, set())
        for queue in v:
            if queue["name"] in excluded_queues:
                continue
            name = queue["name"]
            active_queues.add(name)
            active_workers.add(k)
            worker_queue_map[k].add(name)
    return active_queues, active_workers, worker_queue_map


def poller(interval: int = POLLING_INTERVAL, max_attempts: int = MAX_POLLING_ATTEMPTS):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                print(f"Polling {func.__name__}, attempt {attempts+1}")
                if func(*args, **kwargs):
                    return attempts + 1
                time.sleep(interval)
                attempts += 1
            raise TimeoutError(
                f"Failed to complete operation in {max_attempts * interval} seconds"
            )

        return wrapper

    return decorator


def ensure_active_workers(
    hostname: str | None = None,
    excluded_queues: list[str] = [],
    mandate_on_worker: bool = True,
) -> bool:
    active_queues, active_workers, _ = get_active_queues(
        excluded_queues=excluded_queues
    )

    # hostname is in active_workers
    hostnames = [worker.split("@")[1] for worker in active_workers]
    if hostname is not None and hostname not in hostnames:
        return False

    # there are at least two active workers
    if mandate_on_worker and len(hostnames) < 2:
        return False

    return True


def get_relevant_workers(
    active_workers: set[str], hostname: str | None = None
) -> list[str]:
    if hostname is None:
        return list(active_workers)
    return [worker for worker in active_workers if worker.split("@")[1] == hostname]


def cancel_consumer(
    hostname: str | None = None, excluded_queues: list[str] = []
) -> list[str]:
    active_queues, active_workers, worker_queue_map = get_active_queues(
        excluded_queues=excluded_queues
    )
    relevant_workers = get_relevant_workers(
        active_workers=active_workers, hostname=hostname
    )
    for worker in relevant_workers:
        for queue in worker_queue_map[worker]:
            current_app.control.cancel_consumer(queue=queue, destination=[worker])

    return relevant_workers


def ensure_no_active_tasks(worker_names: list[str]) -> bool:
    for tasks_dict in _get_active_tasks_helper():
        for worker in worker_names:
            if tasks_dict.get(worker):
                return False
    return True


class Command(BaseCommand):
    help = "Suspend all workers on a given machine."

    def add_arguments(self, parser):
        parser.add_argument("--hostname", type=str, required=False)
        parser.add_argument("--max-wait", type=int, required=False, default=3600)
        parser.add_argument(
            "--excluded-queues",
            type=str,
            nargs="+",
            required=False,
            default=[],
        )
        parser.add_argument(
            "--test-mode",
            action="store_true",
            required=False,
            default=False,
        )

    def handle(self, *args, **options):
        hostname = options["hostname"]
        max_wait = options["max_wait"]
        excluded_queues = options["excluded_queues"]
        test_mode = options["test_mode"]

        # ensure the worker we want to suspend is running and there's at least one other worker running
        poller()(ensure_active_workers)(
            hostname, excluded_queues, mandate_on_worker=not test_mode
        )

        # prevent the worker from being scheduled
        relevant_workers = cancel_consumer(hostname, excluded_queues)

        # ensure there are no active tasks on suspended worker
        active_tasks_poller = poller(interval=5, max_attempts=max_wait // 5)
        polled = active_tasks_poller(ensure_no_active_tasks)(relevant_workers)
        if test_mode:
            return str(polled)
        return None
