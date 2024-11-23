from typing import Any


def _find_min_length_list_index(list_of_lists: list[list[Any] | None]) -> int | None:
    # Check if the list is empty
    if not list_of_lists:
        return None  # Return None if the list is empty

    # Iterate through the list of lists
    not_started = True
    min_index = None

    for index, lst in enumerate(list_of_lists):
        if lst is None:
            continue
        elif not_started:
            min_length = len(lst)
            min_index = index
            not_started = False
        # Update minimum length and index if a shorter list is found
        elif len(lst) < min_length:
            min_length = len(lst)
            min_index = index

    return min_index


def _get_list_depth(lst):
    if isinstance(lst, list):
        return 1 + max((_get_list_depth(item) for item in lst), default=0)
    return 0


def _get_list_key_depth(tasks, key: str):
    if isinstance(tasks, list) and tasks:  # Check if it's a non-empty list
        return 1 + max(_get_list_key_depth(task.get(key, []), key) for task in tasks)
    return 0
