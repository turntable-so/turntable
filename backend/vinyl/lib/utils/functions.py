import inspect
import os
import signal
from enum import Enum
from functools import wraps
from typing import get_type_hints

from pydantic import validate_call

_validate = validate_call(
    validate_return=False, config={"arbitrary_types_allowed": True}
)


def _with_modified_env(var_name: str, new_value: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Save the original value of the environment variable (if it exists)
            original_value = os.environ.get(var_name, None)

            # Set the new value for the environment variable
            os.environ[var_name] = new_value

            try:
                # Call the actual function
                result = func(*args, **kwargs)
            finally:
                # Restore the original value of the environment variable
                if original_value is not None:
                    os.environ[var_name] = original_value
                else:
                    # The environment variable was not set before, so remove it
                    del os.environ[var_name]

            return result

        return wrapper

    return decorator


class ModifiedEnv:
    def __init__(self, var_name: str, new_value: str):
        self.var_name = var_name
        self.new_value = new_value
        self.original_value = None

    def __enter__(self):
        # Save the original value of the environment variable (if it exists)
        self.original_value = os.environ.get(self.var_name, None)

        # Set the new value for the environment variable
        os.environ[self.var_name] = self.new_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the original value of the environment variable
        if self.original_value is not None:
            os.environ[self.var_name] = self.original_value
        else:
            # The environment variable was not set before, so remove it
            del os.environ[self.var_name]


def find_enum_arguments(func):
    # Get the signature of the function
    # Iterate over the parameters of the function
    out = {}
    type_hints = get_type_hints(func)
    # Iterate over the type hints of the function
    for name, hint in type_hints.items():
        # Check if the type is a subclass of enum.Enum
        if inspect.isclass(hint) and issubclass(hint, Enum):
            out[name] = hint

    return out


# Define the timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Function has timed out")


# Decorator to add a timeout to a function
def timeout(seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Set the signal handler and the alarm
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Disable the alarm after function executes
                signal.alarm(0)
            return result

        return wrapper

    return decorator
