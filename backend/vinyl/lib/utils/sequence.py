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
