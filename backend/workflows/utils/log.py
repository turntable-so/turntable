import contextlib
import io
import sys

import networkx as nx
from hatchet_sdk import Context

from app.models import Resource, WorkflowRun
from workflows.utils.debug import ContextDebugger, WorkflowDebugger


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


def inject_workflow_run_logging(hatchet, log_stdout: bool = False):
    """
    Must include resource_id in the input structure otherwise this will fail.
    """

    def decorator(cls):
        # get first and last steps
        debugger = WorkflowDebugger(cls, {})
        debugger.build_workflow_graph()
        generations = list(nx.topological_generations(debugger.workflow_graph))

        # on start
        @hatchet.step(timeout="15s")
        def create_workflow_run(self, context: Context):
            resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
            workflow_run_id = context.workflow_run_id()
            workflow_run = WorkflowRun.objects.create(
                id=workflow_run_id, resource=resource, status="RUNNING"
            )
            return {"workflow_run_id": str(workflow_run.id)}

        setattr(cls, "create_workflow_run", create_workflow_run)
        for step in generations[0]:
            cur_parents = getattr(step, "_step_parents", [])
            setattr(step, "_step_parents", cur_parents + ["create_workflow_run"])
            setattr(cls, step.__name__, step)

        # on_end
        @hatchet.step(
            timeout="15s", parents=[step._step_name for step in generations[-1]]
        )
        def mark_workflow_run_success(self, context: Context):
            workflow_run_id = context.workflow_run_id()
            workflow_run = WorkflowRun.objects.get(id=workflow_run_id)
            workflow_run.status = "SUCCESS"
            workflow_run.save()

        setattr(cls, "mark_workflow_run_success", mark_workflow_run_success)

        # on_failure
        @hatchet.on_failure_step()
        def on_failure(self, context: Context):
            workflow_run_id = context.workflow_run_id()
            workflow_run = WorkflowRun.objects.get(id=workflow_run_id)
            workflow_run.status = "FAILED"
            workflow_run.save()

        setattr(cls, "on_failure", on_failure)

        # log stdout
        if log_stdout:
            for step in debugger.workflow_graph.nodes:
                setattr(cls, step, log_stdout(getattr(cls, step)))

        return cls

    return decorator
