from django.db.models import Prefetch

from app.core.serialization import ResourceObject
from app.models import Repository, Resource
from app.utils.queryset import (
    first_with_queryset,
    get_with_queryset,
)


class ResourceService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def get_resources(
        self,
    ):
        resources = Resource.objects.prefetch_related("repository_set").filter(
            tenant_id=self.tenant_id
        )
        return resources

    def get_resource_by_repository(self, repository_id: str):
        repository = Prefetch(
            "repository_set",
            queryset=Repository.objects.filter(
                id=repository_id, tenant_id=self.tenant_id
            ),
        )
        resource = Resource.objects.prefetch_related("profile", repository).filter(
            repository__id=repository_id, tenant_id=self.tenant_id
        )
        return first_with_queryset(resource)

    def get_resource_by_id(
        self, resource_id: str, repository_info: bool = False
    ) -> Resource:
        if repository_info:
            # Step 1: Create a subquery to find the earliest repository ID for each resource
            repository_id = (
                Repository.objects.filter(
                    tenant_id=self.tenant_id,
                    status="IMPORTED",
                ).latest("created_at")
            ).id
            repository = Prefetch(
                "repository_set",
                queryset=Repository.objects.filter(id=repository_id),
            )
            resource = Resource.objects.prefetch_related("profile", repository)
        else:
            resource = Resource.objects.prefetch_related("profile")

        return get_with_queryset(resource, id=resource_id, tenant_id=self.tenant_id)

    def get_connector(self, resource_id: str):
        self.get_resource_by_id(resource_id, repository_info=False)

        # Create a ResourceObject instance from the resource object
        connector = ResourceObject(resource=resource)._get_connector()
        return connector
