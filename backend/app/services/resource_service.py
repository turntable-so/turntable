from asgiref.sync import sync_to_async
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializers import (
    BigQueryDetailsSerializer,
    PostgresDetailsSerializer,
    ResourceSerializer,
)
from app.models import Resource, Workspace
from app.models.resources import BigqueryDetails, PostgresDetails, ResourceSubtype


class CreateResourceSerializer(serializers.Serializer):
    resource = ResourceSerializer()
    subtype = serializers.ChoiceField(choices=ResourceSubtype.choices)
    config = serializers.DictField()


class ResourceDetailsSerializer(serializers.Serializer):
    resource = ResourceSerializer()
    details = serializers.DictField()


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
        resource = payload.data.get("resource")
        config = payload.data.get("config")

        resource_data = ResourceSerializer(data=resource)
        resource_data.is_valid(raise_exception=True)

        if subtype == ResourceSubtype.BIGQUERY:
            detail_serializer = BigQueryDetailsSerializer(
                data={
                    "subtype": subtype,
                    **config,
                }
            )
            detail_serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                resource = Resource.objects.create(
                    **resource_data.validated_data, workspace=self.workspace
                )
                resource.save()
                detail = BigqueryDetails(
                    lookback_days=1,
                    resource=resource,
                    **detail_serializer.validated_data,
                )
                detail.save()
            return resource
        elif subtype == ResourceSubtype.POSTGRES:
            detail_serializer = PostgresDetailsSerializer(
                data={
                    "subtype": subtype,
                    **config,
                }
            )
            detail_serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                resource = Resource.objects.create(
                    **resource_data.validated_data, workspace=self.workspace
                )
                resource.save()
                detail = PostgresDetails(
                    lookback_days=1,
                    resource=resource,
                    **detail_serializer.validated_data,
                )
                detail.save()
            return resource

        else:
            raise ValueError(f"subtype {subtype} not supported by resource service")

    def get(self, resource_id: int) -> ResourceDetailsSerializer:
        resource = Resource.objects.get(id=resource_id, workspace=self.workspace)
        if resource is None:
            raise ValidationError("Resource not found.")

        if resource.details:
            if resource.details.subtype == ResourceSubtype.BIGQUERY:
                return ResourceDetailsSerializer(
                    {
                        "resource": ResourceSerializer(resource).data,
                        "details": BigQueryDetailsSerializer(resource.details).data,
                    }
                ).data
            elif resource.details.subtype == ResourceSubtype.POSTGRES:
                return ResourceDetailsSerializer(
                    {
                        "resource": ResourceSerializer(resource).data,
                        "details": PostgresDetailsSerializer(resource.details).data,
                    }
                ).data
        else:
            return ResourceSerializer(resource).data

        return ValidationError(f"Resource {resource.details.subtype} not suppported")

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

            if data.get("subtype") is not None:
                raise ValidationError(
                    "Can't change the subtype of a resource. It must be removed."
                )

            if data.get("config") is not None:
                if resource.details.subtype == ResourceSubtype.BIGQUERY:
                    config_data = data.get("config")
                    detail_serializer = BigQueryDetailsSerializer(
                        resource.details, data=config_data, partial=True
                    )
                    detail_serializer.is_valid(raise_exception=True)
                    detail_serializer.save()
                elif resource.details.subtype == ResourceSubtype.POSTGRES:
                    config_data = data.get("config")
                    detail_serializer = PostgresDetailsSerializer(
                        resource.details, data=config_data, partial=True
                    )
                    detail_serializer.is_valid(raise_exception=True)
                    detail_serializer.save()
                else:
                    raise ValidationError(
                        f"Config update not supported for subtype {resource.details.subtype}"
                    )

        return resource

    def delete_resource(self, resource_id: int):
        resource = Resource.objects.get(id=resource_id, workspace=self.workspace)
        if resource is None:
            raise ValidationError("Resource not found.")

        resource.delete()
        return

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
