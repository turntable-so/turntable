import json


def convert_sets_to_lists(data):
    if isinstance(data, dict):  # Check if the input is a dictionary
        for key, value in data.items():
            data[key] = convert_sets_to_lists(value)  # Recursively process each item
    elif isinstance(data, set):  # Check if it's a set
        return json.dumps(list(data))  # Convert sets to lists
    return data  # Return the input as-is if it's neither a dict nor a set


def list_union(l1: list, l2: list) -> list:
    return list(set(l1) | set(l2))
