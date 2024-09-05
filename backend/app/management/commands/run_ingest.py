from django.core.management.base import BaseCommand

from workflows.hatchet import hatchet
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import WorkflowDebugger


class Command(BaseCommand):
    help = "Run hatchet custom permissions on start"

    def add_arguments(self, parser):
        parser.add_argument(
            "-r", "--resource_id", type=str, help="Resource ID", required=True
        )

        # Add a boolean flag --dry-run
        parser.add_argument(
            "--hatchet",
            action="store_true",  # Set dry_run to True if this flag is present
            dest="use_hatchet",  # Store the value in 'dry_run'
            help="Use hatchet for the workflow run",
        )

        # Add a boolean flag --no-dry-run
        parser.add_argument(
            "--no-hatchet",
            action="store_false",  # Set dry_run to False if this flag is present
            dest="dry_run",  # Store the value in 'dry_run'
            help="Use the tester for the workflow run",
        )

    def handle(self, *args, **options):
        use_hatchet = options["use_hatchet"]
        resource_id = options["resource_id"]

        if use_hatchet:
            workflow_run = hatchet.client.admin.run_workflow(
                "MetadataSyncWorkflow",
                {
                    "resource_id": resource_id,
                },
            )
        else:
            WorkflowDebugger(MetadataSyncWorkflow, {"resource_id": resource_id}).run()
