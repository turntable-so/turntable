import os
from contextlib import contextmanager


@contextmanager
def set_env(**kwargs):
    original_env = os.environ.copy()
    for k, v in kwargs.items():
        os.environ[k] = v
    yield
    os.environ = original_env
