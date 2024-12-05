import json
from contextlib import contextmanager

import orjson


def orjson_dumps(*args, **kwargs):
    # Remove arguments that orjson doesn't support
    kwargs.pop("cls", None)
    kwargs.pop("default", None)

    # Use orjson.dumps and decode the result
    return orjson.dumps(args[0] if args else None).decode()


def orjson_loads(*args, **kwargs):
    # Remove arguments that orjson doesn't support
    kwargs.pop("cls", None)
    kwargs.pop("object_hook", None)

    # Use orjson.loads
    return orjson.loads(args[0] if args else None)


def orjson_dump(obj, fp, **kwargs):
    # Write the output of dumps to the file object
    fp.write(orjson_dumps(obj, **kwargs))


def orjson_load(fp, **kwargs):
    # Read from file object and pass to loads
    return orjson_loads(fp.read(), **kwargs)


@contextmanager
def with_orjson():
    """Temporarily patch json module to use orjson implementations."""
    # Store original methods
    original_dumps = json.dumps
    original_loads = json.loads
    original_dump = json.dump
    original_load = json.load

    try:
        # Apply patches
        json.dumps = orjson_dumps
        json.loads = orjson_loads
        json.dump = orjson_dump
        json.load = orjson_load
        yield
    finally:
        # Restore original methods
        json.dumps = original_dumps
        json.loads = original_loads
        json.dump = original_dump
        json.load = original_load


def patch_json_with_orjson(func):
    """Decorator that patches json with orjson for the duration of the function call."""

    def wrapper(*args, **kwargs):
        with with_orjson():
            return func(*args, **kwargs)

    return wrapper


@contextmanager
def with_libyaml():
    """Temporarily patch yaml module to use libyaml implementations."""
    try:
        from yaml import CDumper, CLoader, Dumper, Loader
    except ImportError:
        yield
        return

    original_loader = Loader
    original_dumper = Dumper

    try:
        Loader = CLoader
        Dumper = CDumper
        yield
    finally:
        Loader = original_loader
        Dumper = original_dumper


def patch_yaml_with_libyaml(func):
    """Decorator that patches yaml with libyaml for the duration of the function call."""

    def wrapper(*args, **kwargs):
        with with_libyaml():
            return func(*args, **kwargs)

    return wrapper
