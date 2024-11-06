from typing import Any, Callable


def execute_subtask_dict(subtask_dict: dict[Callable, Any]):
    for task, args in subtask_dict.items():
        task(**args)
