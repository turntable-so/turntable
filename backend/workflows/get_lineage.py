from hatchet_sdk import Context

from app.core.dbt import LiveDBTParser
from app.models import Resource
from workflows.hatchet import hatchet
from workflows.utils.log import inject_workflow_run_logging


def return_helper(success, stdouts, stderrs, run_results):
    return {
        "success": success,
        "stdouts": stdouts,
        "stderrs": stderrs,
        "run_results": run_results,
    }


@inject_workflow_run_logging(hatchet)
@hatchet.workflow(on_events=["get_lineage"], timeout="15m")
class GetLineageWorkflow:
    """
    input structure:
        {
            resource_id: str,
            dbt_file_path: str,
            branch_id: str | None,
            dbt_resource_id: str | None,
            predecessor_depth: int | None,
            successor_depth: int | None,
            defer: bool,
        }
    """

    @hatchet.step(timeout="30m")
    def get_lineage_step(self, context: Context):
        resource_id = context.workflow_input()["resource_id"]
        branch_id = context.workflow_input().get("branch_id")
        dbt_resource_id = context.workflow_input().get("dbt_resource_id")
        dbt_file_path = context.workflow_input().get("dbt_file_path")
        predecessor_depth = context.workflow_input().get("predecessor_depth")
        successor_depth = context.workflow_input().get("successor_depth")
        defer = context.workflow_input().get("defer")

        resource = Resource.objects.get(id=resource_id)
        dbt_resource = resource.get_dbt_resource(dbt_resource_id)

        # Run the dbt commands
        with dbt_resource.dbt_transition_context(branch_id=branch_id) as (
            transition,
            project_dir,
            _,
        ):
            transition.mount_manifest(defer=defer)
            node_id = None
            for k, v in transition.after.manifest["nodes"].items():
                if dbt_file_path == v["original_file_path"]:
                    node_id = k
                    break
            if not node_id:
                raise ValueError(f"Node {dbt_file_path} not found in manifest")

            dbtparser = LiveDBTParser.parse_project(
                proj=transition.after,
                node_id=node_id,
                resource=resource,
                predecessor_depth=predecessor_depth,
                successor_depth=successor_depth,
                defer=defer,
            )
            return dbtparser.get_lineage().to_dict()
