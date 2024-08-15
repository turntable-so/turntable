import os

import dill
import diskcache as dc
import msgpack
import orjson


class DillDisk(dc.Disk):
    def __init__(self, directory, **kwargs):
        super().__init__(directory, **kwargs)

    def put(self, key):
        data = dill.dumps(key)
        return super().put(data)

    def get(self, key, raw):
        data = super().get(key, raw)
        return dill.loads(data)

    def store(self, value, read, key):
        if not read:
            value = dill.dumps(value)
        return super().store(value, read, key=key)

    def fetch(self, mode, filename, value, read):
        data = super().fetch(mode, filename, value, read)
        if not read:
            data = dill.loads(data)
        return data


class ORJSONDisk(dc.Disk):
    def __init__(self, directory, **kwargs):
        super().__init__(directory, **kwargs)

    def put(self, key):
        data = orjson.dumps(key)
        return super().put(data)

    def get(self, key, raw):
        data = super().get(key, raw)
        return orjson.loads(data)

    def store(self, value, read, key=dc.UNKNOWN):
        if not read:
            value = orjson.dumps(value)
        return super().store(value, read, key=key)

    def fetch(self, mode, filename, value, read):
        data = super().fetch(mode, filename, value, read)
        if not read:
            data = orjson.loads(data)
        return data


class MarshalDisk(dc.Disk):
    def __init__(self, directory, **kwargs):
        super().__init__(directory, **kwargs)

    def put(self, key):
        data = msgpack.dumps(key)
        return super().put(data)

    def get(self, key, raw):
        data = super().get(key, raw)
        return msgpack.loads(data)

    def store(self, value, read, key=dc.UNKNOWN):
        if not read:
            try:
                value = msgpack.dumps(value)
            except:
                print(value)
                raise
        return super().store(value, read, key=key)

    def fetch(self, mode, filename, value, read):
        data = super().fetch(mode, filename, value, read)
        if not read:
            data = msgpack.loads(data)
        return data


DillCache = dc.Cache(directory=".cache", disk=DillDisk)


def memoize(tag=None, ignore=()):
    """Decorator that applies caching only if a specific environment variable is set to 'true', with an optional ignore parameter."""

    def decorator(func):
        env_var = bool(os.getenv("ENABLE_CACHE", "0"))
        if env_var:
            # Apply caching if the environment variable is 'true', passing the ignore parameter
            return DillCache.memoize(ignore=ignore)(func)
        else:
            # Just return the original function if caching is not enabled
            return func

    return decorator
