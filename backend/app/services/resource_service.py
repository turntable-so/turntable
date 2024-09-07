from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializers import (
    BigQueryDetailsSerializer,
    DatabricksDetailsSerializer,
    DBTCoreDetailsSerializer,
    MetabaseDetailsSerializer,
    PostgresDetailsSerializer,
    ResourceSerializer,
    SnowflakeDetailsSerializer,
)
from app.models import DBTCoreDetails, Resource, Workspace
from app.models.resources import (
    BigqueryDetails,
    DatabricksDetails,
    DBTResource,
    MetabaseDetails,
    PostgresDetails,
    ResourceDetails,
    ResourceSubtype,
    SnowflakeDetails,
)


class CreateResourceSerializer(serializers.Serializer):
    resource = ResourceSerializer()
    subtype = serializers.ChoiceField(choices=ResourceSubtype.choices)
    config = serializers.DictField()


class ResourceDetailsSerializer(serializers.Serializer):
    resource = ResourceSerializer()
    details = serializers.DictField()


class ResourceServiceHelper:
    subtype: ResourceSubtype
    serializer: ResourceDetailsSerializer
    details_obj: ResourceDetails | DBTResource

    @classmethod
    def create_resource(cls, payload, workspace: Workspace) -> Resource:
        subtype = cls.subtype
        resource = payload.data.get("resource")
        config = payload.data.get("config")
        resource_data = ResourceSerializer(data=resource)
        resource_data.is_valid(raise_exception=True)

        detail_serializer = cls.serializer(
            data={
                "subtype": subtype,
                **config,
            }
        )
        detail_serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            resource = Resource.objects.create(
                **resource_data.validated_data, workspace=workspace
            )
            resource.save()
            detail_args = {"resource": resource, **detail_serializer.validated_data}
            if (
                hasattr(cls.details_obj, "requires_start_date")
                and cls.details_obj().requires_start_date is True
            ):
                detail_args["lookback_days"] = 1

            detail = cls.details_obj(**detail_args)
            detail.save()
        return resource

    @classmethod
    def get(cls, resource_id: str, workspace: Workspace) -> ResourceDetailsSerializer:
        resource = Resource.objects.get(id=resource_id, workspace=workspace)
        if resource is None:
            raise ValidationError("Resource not found.")
        response = ResourceDetailsSerializer(
            {
                "resource": ResourceSerializer(resource).data,
                "details": cls.serializer(resource.details).data,
            }
        ).data

        if resource.dbtresource_set.exists():
            # we only support one dbt project per resource for now
            response["dbt_details"] = DBTCoreDetailsSerializer(
                resource.dbtresource_set.first()
            ).data

        return response

    @classmethod
    def partial_update_helper(cls, resource: Resource, data: dict) -> Resource:
        if data.get("config") is not None:
            config_data = data.get("config")
            detail_serializer = cls.serializer(
                resource.details, data=config_data, partial=True
            )
            detail_serializer.is_valid(raise_exception=True)
            detail_serializer.save()


class BigQueryResourceService(ResourceServiceHelper):
    subtype = ResourceSubtype.BIGQUERY
    serializer = BigQueryDetailsSerializer
    details_obj = BigqueryDetails


class SnowflakeResourceService(ResourceServiceHelper):
    subtype = ResourceSubtype.SNOWFLAKE
    serializer = SnowflakeDetailsSerializer
    details_obj = SnowflakeDetails


class PostgresResourceService(ResourceServiceHelper):
    subtype = ResourceSubtype.POSTGRES
    serializer = PostgresDetailsSerializer
    details_obj = PostgresDetails


class DatabricksResourceService(ResourceServiceHelper):
    subtype = ResourceSubtype.DATABRICKS
    serializer = DatabricksDetailsSerializer
    details_obj = DatabricksDetails


class MetabaseResourceService(ResourceServiceHelper):
    subtype = ResourceSubtype.METABASE
    serializer = MetabaseDetailsSerializer
    details_obj = MetabaseDetails


class DBTResourceService(ResourceServiceHelper):
    subtype = ResourceSubtype.DBT
    serializer = DBTCoreDetailsSerializer
    details_obj = DBTCoreDetails

    @classmethod
    def create_resource(cls, payload, workspace: Workspace) -> Resource:
        subtype = cls.subtype
        resource = payload.data.get("resource")
        config = payload.data.get("config")

        resource_data = ResourceSerializer(data=resource)
        resource_data.is_valid(raise_exception=True)
        resource_id = config.get("resource_id")
        if not resource_id:
            raise ValidationError("Resource ID is required for DBT resources.")

        detail_serializer = DBTCoreDetailsSerializer(
            data={
                "subtype": subtype,
                **config,
            }
        )

        detail_serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            resource = Resource.objects.get(id=resource_id, workspace=workspace)
            detail = DBTCoreDetails(
                resource=resource,
                **detail_serializer.data,
            )
            resource.save()
            detail.save()

        return resource

    @classmethod
    def get(cls, resource_id: str, workspace: Workspace) -> ResourceDetailsSerializer:
        resource = Resource.objects.get(id=resource_id, workspace=workspace)
        response = ResourceDetailsSerializer(
            {
                "resource": ResourceSerializer(resource).data,
                "details": {},
            }
        ).data

        return response


class ResourceService:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def list(self):
        resources = Resource.objects.all().filter(workspace=self.workspace)
        serializer = ResourceSerializer(resources, many=True)
        return serializer.data
        # the code should go below here

    def create_resource(self, data: dict) -> Resource:
        payload = CreateResourceSerializer(data=data)
        payload.is_valid(raise_exception=True)
        subtype = payload.data.get("subtype")
        for cls in ResourceServiceHelper.__subclasses__():
            if cls.subtype == subtype:
                return cls.create_resource(payload, self.workspace)
        raise ValueError(f"subtype {subtype} not supported by resource service")

    def get(self, resource_id: str) -> ResourceDetailsSerializer:
        resource = Resource.objects.get(id=resource_id, workspace=self.workspace)
        if resource is None:
            raise ValidationError("Resource not found.")

        for cls in ResourceServiceHelper.__subclasses__():
            if cls.subtype == resource.details.subtype:
                return cls.get(resource_id, self.workspace)

        response = ResourceDetailsSerializer(
            {
                "resource": ResourceSerializer(resource).data,
                "details": {},
            }
        ).data
        return response

    def partial_update(self, resource_id: str, data: dict) -> Resource:
        resource = Resource.objects.get(id=resource_id, workspace=self.workspace)
        if resource is None:
            raise ValidationError("Resource not found.")

        with transaction.atomic():
            if data.get("resource") is not None:
                payload = ResourceSerializer(
                    resource, data=data.get("resource"), partial=True
                )
                payload.is_valid(raise_exception=True)
                resource = payload.save()  # This calls the update method
            # the only subtype allowed to be attached or modified is dbt
            if data.get("subtype") == "dbt":
                if resource.dbtresource_set.exists():
                    dbt_resource = resource.dbtresource_set.first()
                    dbt_payload = DBTCoreDetailsSerializer(
                        dbt_resource, data=data.get("config"), partial=True
                    )
                    dbt_payload.is_valid()
                    print(dbt_payload.errors, flush=True)
                    dbt_payload.is_valid(raise_exception=True)
                    dbt_payload.save()
                    return
                else:
                    print("creating dbt resource", flush=True)
                    raise ValidationError("Resource does not have a dbt resource")
            if data.get("subtype") is not None:
                raise ValidationError(
                    "Can't change the subtype of a resource. It must be removed."
                )

            if data.get("config") is not None:
                for cls in ResourceServiceHelper.__subclasses__():
                    if cls.subtype == resource.details.subtype:
                        cls.partial_update_helper(resource, data)
                        return resource
                raise ValidationError(
                    f"Config update not supported for subtype {resource.details.subtype}"
                )
        return resource

    def delete_resource(self, resource_id: int):
        resource = Resource.objects.get(id=resource_id, workspace=self.workspace)
        if resource is None:
            raise ValidationError("Resource not found.")

        resource.delete()

    def test_resource(self, resource_id: int):
        resource = Resource.objects.get(id=resource_id, workspace=self.workspace)

        test_db = resource.details.test_db_connection()
        test_datahub = resource.details.test_datahub_connection()

        return {
            "test_db": test_db,
            "test_datahub": test_datahub,
        }
        

    async def sync_resource(self, resource_id: int):
        from workflows.hatchet import hatchet

        resource = await Resource.objects.aget(id=resource_id, workspace=self.workspace)
        if resource is None:
            raise ValidationError("Resource not found.")

        workflow_run = hatchet.client.admin.run_workflow(
            "MetadataSyncWorkflow",
            {
                "workspace_id": self.workspace.id,
                "resource_id": resource_id,
            },
        )

        return {
            "workflow_run_id": workflow_run.workflow_run_id,
        }
