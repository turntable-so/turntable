from __future__ import annotations

import inspect
import os
import threading
import time
import uuid

import networkx as nx
from hatchet_sdk import Context
from mpire import WorkerPool


class ContextDebugger:
    def __init__(self, data):
        data.setdefault("workflow_run_id", uuid.uuid4())
        self.data = data
        self.stream = []

    def workflow_run_id(self):
        return self.data.get("workflow_run_id")

    def workflow_input(self):
        return self.data.get("input", {})

    def step_output(self, step_name):
        return self.data.get("parents", {}).get(step_name, {})

    def log(self, message):
        print(message)

    def put_stream(self, message):
        self.stream.append(message)


def run_workflow(workflow, input: dict):
    if os.getenv("TEST_ENV"):
        debugger = WorkflowDebugger(workflow, input)
        thread = threading.Thread(target=debugger.run)
        thread.start()
        return debugger.context.workflow_run_id(), debugger, thread

    else:
        from workflows.hatchet import hatchet

        return hatchet.admin.run_workflow(workflow.__name__, input), None, None


def listen_to_stream(
    run_id: str, debugger: WorkflowDebugger | None, thread: threading.Thread
):
    if os.getenv("TEST_ENV"):
        while thread.is_alive():
            time.sleep(0.1)
            stream = debugger.context.stream
            if stream:
                yield stream
    else:
        from workflows.hatchet import hatchet

        yield from hatchet.listener.stream(run_id)


def spawn_workflow(context, workflow, input: dict, key: str | None = None):
    if isinstance(context, Context):
        return context.spawn_workflow(workflow.__name__, input, key).result()
    else:
        return WorkflowDebugger(workflow, input).run().result()


def spawn_workflows(
    context,
    workflow,
    inputs: list[dict],
    keys: list[str | None] = None,
    parallel: bool = True,
):
    if keys is None:
        keys = [None] * len(inputs)
    if len(inputs) != len(keys):
        raise ValueError("inputs and keys must be the same length")

    def helper(input, key):
        return spawn_workflow(context, workflow, input, key)

    if not parallel or len(inputs) == 1 or not isinstance(context, ContextDebugger):
        return [helper(input, key) for input, key in zip(inputs, keys)]

    with WorkerPool(use_dill=True) as pool:
        results = pool.map(helper, zip(inputs, keys))

    return results


class WorkflowDebugger:
    def __init__(self, workflow, input):
        self.workflow = workflow
        self.input = {"input": input}
        self.context = ContextDebugger(self.input)
        self.build_workflow_graph()

    def build_workflow_graph(self):
        self.workflow_graph = nx.DiGraph()
        workflow_functions = inspect.getmembers(self.workflow, inspect.isfunction)
        step_dict = {
            f[1]._step_name: f[1]
            for f in workflow_functions
            if hasattr(f[1], "_step_name")
        }
        for step in step_dict.values():
            self.workflow_graph.add_node(step)
            for parent in step._step_parents:
                self.workflow_graph.add_edge(step_dict[parent], step)

    def run_step(self, step):
        return step(self.workflow(), context=self.context)

    def update_context(self, step, output):
        self.context.data.setdefault("parents", {})[step._step_name] = output

    def run(self):
        try:
            for i, generation in enumerate(
                nx.topological_generations(self.workflow_graph)
            ):
                if len(generation) == 1:
                    out = self.run_step(generation[0])
                    self.update_context(generation[0], out)
                else:
                    with WorkerPool(use_dill=True) as pool:
                        results = pool.map(self.run_step, generation)
                    for step, result in zip(generation, results):
                        self.update_context(step, result)
        except Exception as e:
            if hasattr(self.workflow, "on_failure"):
                self.run_step(self.workflow.on_failure)
            raise e
        return self

    def result(self):
        return self.context.data["parents"] or {}
