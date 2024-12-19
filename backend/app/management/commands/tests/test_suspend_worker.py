import math
import time

import pytest
from django.core.management import call_command

from app.management.commands.suspend_worker import get_active_queues
from app.workflows.utils import long_running_task


# test different task durations to ensure shutdown is happening after the task is done
# don't resume worker for shortest test. For some reason, doesn't pass for github actions.
@pytest.mark.parametrize("duration", [4, 9, 14])
def test_suspend_worker(custom_celery, test_queue_name, test_worker_name, duration):
    res = long_running_task.si(duration=duration).apply_async()
    active_queues, active_workers, _ = get_active_queues()
    assert test_queue_name in active_queues
    excluded_queues = [q for q in active_queues if q != test_queue_name]
    hostname = test_worker_name.split("@")[1]
    called = call_command(
        "suspend_worker",
        excluded_queues=excluded_queues,
        test_mode=True,
        hostname=hostname,
    )
    assert called == str(math.ceil(duration / 5))
    assert res.get()

    # resume worker
    call_command("resume_worker", hostname=hostname, excluded_queues=excluded_queues)
    time.sleep(1)
    active_queues, _, _ = get_active_queues()
    assert test_queue_name in active_queues
