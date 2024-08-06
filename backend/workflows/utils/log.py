import contextlib
import io
import sys

from hatchet_sdk import Context

from workflows.utils.debug import ContextDebugger


class StreamLogger(io.StringIO):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context
        self.original_stdout = sys.stdout

    def write(self, s):
        # Write to the StringIO buffer
        super().write(s)
        # Log the output to the context
        self.context.log(s)
        # Also write to the original stdout
        self.original_stdout.write(s)
        return len(s)

    def flush(self):
        # Flush both the StringIO buffer and the original stdout
        super().flush()
        self.original_stdout.flush()


def log_stdout(func):
    def wrapper(self, *args, **kwargs):
        # Extract the context from the arguments
        context = kwargs.get("context", args[0] if args else None)
        if context is None:
            raise ValueError("Context argument with a log method is required")

        if isinstance(context, ContextDebugger):
            # If the context is a ContextDebugger object, then we don't need to log the output
            return func(self, *args, **kwargs)

        # Create a StreamLogger object to capture and log the output in real-time
        stream_logger = StreamLogger(context)

        # Redirect stdout to the StreamLogger
        with contextlib.redirect_stdout(stream_logger):
            result = func(self, *args, **kwargs)

        return result

    return wrapper
