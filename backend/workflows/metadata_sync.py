import tempfile

from hatchet_sdk import Context

from app.core.e2e import DataHubDBParser
from app.models import (
    DBTResourceSubtype,
    Resource,
)

# from redis_client import redis_client
from workflows.hatchet import hatchet

# def get_resources(context: Context):
#     workspace_id = context.workflow_input()["workspace_id"]
#     resource_ids = context.workflow_input().get("resource_ids")
#     if not resource_ids:
#         # no e2e resources to ingest
#         return None

#     context.log("Getting resources...")
#     resources = Resource.objects.filter(id__in=resource_ids, workspace_id=workspace_id)
#     context.log(f"Got resources: {[r.id for r in resources]}")
#     return resources


# @hatchet.workflow()
# class UploadDBTArtifacts:
#     @hatchet.step()
#     def upload_dbt_artifacts(self, context: Context):
#         id = context.workflow_input()["id"]
#         DBTCoreDetails.objects.get(id=id).upload_artifacts()


# @hatchet.workflow()
# class IngestMetadata:
#     @hatchet.step()
#     def ingest_metadata(self, context: Context):
#         id = context.workflow_input()["id"]
#         ResourceDetails.objects.get(id=id).run_datahub_ingest()


# @hatchet.workflow()
# class ProcessMetadata:
#     @hatchet.step()
#     def process_metadata(self, context: Context):
#         id = context.workflow_input()["id"]
#         resource = Resource.objects.get(id=id)
#         with resource.datahub_db.open("rb") as f:
#             with tempfile.NamedTemporaryFile(
#                 "wb", delete=False, suffix=".duckdb"
#             ) as f2:
#                 f2.write(f.read())
#                 parser = DataHubDBParser(resource, f2.name)
#                 parser.parse()
#         return pickle.dumps(parser)


@hatchet.workflow(on_events=["metadata_sync"], timeout="15m")
class MetadataSyncWorkflow:
    """
    input structure:
        {
            resource_id: str,
            use_ai: bool
        }
    """

    @hatchet.step(timeout="30m")
    def prepare_dbt_repos(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        for dbt_repo in resource.dbtresource_set.all():
            if dbt_repo.subtype == DBTResourceSubtype.CORE:
                dbt_repo.upload_artifacts()

    @hatchet.step(timeout="30m", parents=["prepare_dbt_repos"])
    def ingest_metadata(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        resource.resourcedetails.run_datahub_ingest()
        with resource.datahub_db.open("rb") as f:
            with open("fixtures/capchase_looker.duckdb", "wb") as f2:
                f2.write(f.read())

    @hatchet.step(timeout="30m", parents=["ingest_metadata"])
    def process_metadata(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        with resource.datahub_db.open("rb") as f:
            with tempfile.NamedTemporaryFile(
                "wb", delete=False, suffix=".duckdb"
            ) as f2:
                f2.write(f.read())
                parser = DataHubDBParser(resource, f2.name)
                parser.parse()

        DataHubDBParser.combine_and_upload([parser], resource)

    # @hatchet.step(parents=["start"], timeout="1h")
    # def get_github_repo(self, context: Context):
    #     dbt_resource_id = context.workflow_input()["dbt_resource_id"]
    #      = context.workflow_input()[""]
    #     resource = ResourceService().get_resource_by_id(dbt_resource_id)
    #     github_service = GithubService()
    #     repo = github_service.get_repository_by_id(resource.github_repo_id)

    #     return {
    #         "repo_id": repo.id,
    #         "repo_owner": repo.owner.login,
    #         "repo_name": repo.name,
    #         "default_branch": repo.default_branch,
    #         "github_installation": github_service.installation_id,
    #     }

    # @hatchet.step(parents=["get_github_repo"], timeout="1h")
    # @log_stdout
    # def save_repo(self, context: Context):
    #      = context.workflow_input()[""]
    #     dbt_resource_id = context.workflow_input()["dbt_resource_id"]
    #     repo_id = str(context.step_output("get_github_repo")["repo_id"])

    #     github_service = GithubService()

    #     context.log("downloading zipball...")
    #     with github_service.repo_context(repo_id) as (
    #         zip_contents,
    #         temp_dir,
    #     ):
    #         contents = zip_contents
    #         context.log("downloaded")
    #         context.log("saving to repository table...")
    #         get_repo_step_output = context.step_output("get_github_repo")
    #         resource = ResourceService().get_resource_by_id(dbt_resource_id)
    #         installation = GithubInstallation.objects.get(
    #             id=get_repo_step_output["github_installation"]
    #         )
    #         repository = Repository.objects.create(
    #             resource=resource,
    #             github_repo_id=get_repo_step_output["repo_id"],
    #             repo_owner=get_repo_step_output["repo_owner"],
    #             repo_name=get_repo_step_output["repo_name"],
    #             default_branch=get_repo_step_output["default_branch"],
    #             github_installation=installation,
    #             =,
    #         )
    #         context.log(f"Repository with {repository.id} written")

    #         repo_path = get_repo_path(repository.id, )
    #         resource = ResourceService().get_resource_by_repository(
    #             repository.id
    #         )
    #         with dbt_repo_context(
    #             =,
    #             zip_contents=contents,
    #             resource=resource,
    #         ) as (dbtproj, extractdir):
    #             dbtproj.mount_manifest()
    #             dbtproj.dbt_compile(models_only=True)
    #             dbtproj.mount_catalog()

    #             with tempfile.TemporaryDirectory() as tmp_dir:
    #                 # create a zipball of the dbt project
    #                 archive_name = shutil.make_archive(
    #                     tmp_dir,
    #                     "zip",
    #                     root_dir=extractdir,
    #                     base_dir=os.listdir(extractdir)[0],
    #                 )

    #                 with open(archive_name, "rb") as f:
    #                     repository.repo_file.save(repo_path, File(f), save=True)

    #         context.log(f"uploaded zipball to {repo_path}")
    #         # repository.repo_path_zip = repo_path
    #         # repository.save()

    #         return {"repository_id": str(repository.id)}
