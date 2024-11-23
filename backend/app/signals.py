from asgiref.sync import async_to_sync
from celery import signals, states
from channels.layers import get_channel_layer
from django.core.cache import cache

from app.models.workflows import (
    get_periodic_task_key,
)


def task_start_handler(task_id, task, **kwargs):
    periodic_task_name = task.request.properties.get("periodic_task_name")
    if periodic_task_name:
        cache.set(
            key=get_periodic_task_key(periodic_task_name),
            value=task_id,
            timeout=500,
        )


def get_signal_name(kwargs):
    if signal := kwargs.get("signal", ""):
        return signal.name
    return ""


def send_status_update(task_id, state, task_kwargs):
    ids_to_fetch = {"workspace_id": True, "resource_id": False}
    ids = {}
    for id, mandatory in ids_to_fetch.items():
        if id in task_kwargs:
            ids[id] = task_kwargs[id]
        elif mandatory:
            raise ValueError(f"{id} is required as a kwarg on all tasks")

    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            f"workspace_{ids['workspace_id']}",
            {
                "type": "workflow_status_update",
                "status": state,
                "task_id": str(task_id),
                **ids,
            },
        )
    except Exception as e:
        print(e)
        print("Error sending status update")


SIGNAL_STATE_MAP = {
    "task_prerun": states.STARTED,
    "task_success": states.SUCCESS,
    "task_failure": states.FAILURE,
    "task_revoked": states.REVOKED,
}


@signals.task_prerun.connect
@signals.task_success.connect
@signals.task_failure.connect
@signals.task_revoked.connect
def handle_task_state(
    sender=None,
    headers=None,
    body=None,
    task_id=None,
    task=None,
    state=None,
    result=None,
    **kwargs,
):
    """Handle all task state changes"""
    signal_name = get_signal_name(kwargs)
    if signal_name == "task_prerun":
        task_start_handler(task_id, task, **kwargs)

    state = SIGNAL_STATE_MAP.get(signal_name, "")

    # Get task kwargs from the appropriate source based on signal
    if headers and body:  # before_task_publish
        task_kwargs = body[1]
    elif task:  # other signals
        task_kwargs = task.request.kwargs
    elif sender:  # For success signal
        task_kwargs = sender.request.kwargs  # sender is the task instance
    else:
        return

    send_status_update(task_id, state, task_kwargs)
