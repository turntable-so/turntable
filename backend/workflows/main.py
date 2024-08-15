# make sure django is setup
import django

django.setup()

# rest of imports

from workflows.execute_query import ExecuteQueryWorkflow
from workflows.hatchet import hatchet
from workflows.metadata_sync import (
    MetadataSyncWorkflow,
)


# create worker and register workflows
def start():
    worker = hatchet.worker("turntable-worker", max_runs=5)
    worker.register_workflow(MetadataSyncWorkflow())
    worker.register_workflow(ExecuteQueryWorkflow())
    worker.start()


if __name__ == "__main__":
    start()
