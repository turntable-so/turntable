import functools
import keyword
import re
import threading
from collections import OrderedDict
from typing import Any


def _is_iterable(obj: Any) -> bool:
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def get_var_name(variable, local_vars):
    return [var_name for var_name, value in local_vars.items() if value is variable]


def is_valid_class_name(name: str) -> bool:
    # Check if the name is a Python keyword
    if keyword.iskeyword(name):
        return False

    # remove t names to avoid clash with type definitions
    if name == "t":
        return False

    # Check if the name follows the identifier rules
    if not name[0].isalpha() and name[0] != "_":
        return False
    if not all(char.isalnum() or char == "_" for char in name[1:]):
        return False

    return True


def to_valid_class_name(name: str, previous_replacements: list[str] = []) -> str:
    # Step 1: Ensure it starts with a letter or underscore. If not, prepend an underscore.
    if (
        not name[0].isalpha() or name[0] == "t"
    ):  # remove t names to avoid clash with type definitions
        name = "_" + name

    # Step 2: Replace invalid characters with underscores.
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)

    # Step 3: Avoid Python keywords by appending an underscore if needed.
    if keyword.iskeyword(name):
        name += "_"

    # Step 4: Ensure the result is not empty. If it is, default to a placeholder name.
    if not name:
        name = "Class_"

    # Step 5: Avoid duplicate names by appending a number if needed.
    if name in previous_replacements:
        i = 1
        while f"{name}{i}" in previous_replacements:
            i += 1
        name = f"{name}{i}"

    return name


def table_to_python_class(table_name) -> str:
    if not is_valid_class_name(table_name):
        table_name = to_valid_class_name(table_name)
    return "".join([word.capitalize() for word in table_name.split("_")])


def find_all_class_descendants(cls):
    descendants = []
    # Start with direct subclasses
    subclasses = cls.__subclasses__()
    descendants.extend(subclasses)
    # Recursively find subclasses of subclasses
    for subclass in subclasses:
        descendants.extend(find_all_class_descendants(subclass))
    return descendants


def threadsafe_lru_cache(maxsize=128, typed=False):
    def decorator(func):
        cache = OrderedDict()
        cache_lock = threading.Lock()

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            key = functools._make_key(args, kwargs, typed)

            with cache_lock:
                if key in cache:
                    # Move the accessed item to the end to maintain LRU order
                    cache.move_to_end(key)
                    return cache[key]

            result = func(*args, **kwargs)

            with cache_lock:
                if key not in cache:
                    if len(cache) >= maxsize:
                        # Remove the first item in the order (the least recently used)
                        cache.popitem(last=False)
                    cache[key] = result

            return result

        return wrapped

    return decorator
