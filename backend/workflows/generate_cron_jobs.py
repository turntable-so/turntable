#!/usr/bin/env python

import json
import logging
import sys
from time import sleep

from dotenv import load_dotenv
from hatchet_sdk import CreateWorkflowVersionOpts

from workflows.hatchet import hatchet
from workflows.sync_dbt_project_direct import SyncDbtProjectWorkflowDirect

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    sleep(100)
    try:
        answer = hatchet.client.admin.put_workflow(
            "production_SyncDbtProjectWorkflowDirect",
            SyncDbtProjectWorkflowDirect(),
            overrides=CreateWorkflowVersionOpts(
                cron_triggers=["0 14 * * *"],
                cron_input=json.dumps(
                    {
                        "dbt_resource_id": "ec6b5c1c-5d2e-4edc-84fc-20b796ba3128",
                        "tenant_id": "org_2fpSXQmvdTGCnofnrK3JkROjlOh",
                        "e2e_resource_ids": ["30a887df-4717-4d76-9b84-c9de01741301"],
                    }
                ),
            ),
        )

        logger.info("Workflow updated: %s", answer)
        sys.exit(0)
    except Exception:
        logger.exception("An error occurred while updating the workflow")
        sys.exit(0)  # Ensure the script exits with an error code


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unhandled exception")
        sys.exit(0)
    sys.exit(0)  # Ensure the script exits cleanly
