# make sure django is setup
import django

django.setup()

# rest of imports

from workflows.dbt_runner import DBTRunnerWorkflow, DBTStreamerWorkflow
from workflows.execute_dbt_query import DBTQueryPreviewWorkflow
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
    worker.register_workflow(DBTQueryPreviewWorkflow())
    worker.register_workflow(DBTRunnerWorkflow())
    worker.register_workflow(DBTStreamerWorkflow())
    worker.start()


if __name__ == "__main__":
    start()
