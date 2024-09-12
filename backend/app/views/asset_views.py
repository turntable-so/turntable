from api.serializers import AssetIndexSerializer, AssetSerializer, ResourceSerializer
from app.models import Asset, Resource
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.cache import caches
from rest_framework.permissions import AllowAny
from math import ceil
from django.db.models import Count


cache = caches["default"]


class AssetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "total_pages": ceil(self.page.paginator.count / self.page_size),
                "results": data,
            }
        )


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    pagination_class = AssetPagination

    permission_classes = [AllowAny]

    def list(self, request):
        query = request.query_params.get("q", None)
        resources_filter = request.query_params.get("resources", None)
        tags_filter = request.query_params.get("tags", None)
        types_filter = request.query_params.get("types", None)
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_403_FORBIDDEN
            )

        # Base queryset
        base_queryset = Asset.objects.filter(workspace=workspace)

        # Apply search filter if query exists
        if query and len(query) > 0:
            # TODO: add ranking to this for name, description, tags, etc.
            filtered_assets = base_queryset.filter(name__icontains=query)
        else:
            filtered_assets = base_queryset

        if types_filter and len(types_filter) > 0:
            filtered_assets = filtered_assets.filter(type__in=types_filter.split(","))

        if resources_filter and len(resources_filter) > 0:
            filtered_assets = filtered_assets.filter(
                resource__in=resources_filter.split(",")
            )

        # Calculate filters using the base queryset
        types = (
            base_queryset.values("type").annotate(count=Count("type")).order_by("type")
        )
        sources = (
            base_queryset.values("resource__id")
            .annotate(count=Count("resource__id"))
            .order_by("resource__name")
        )
        tags = (
            base_queryset.values("tags").annotate(count=Count("tags")).order_by("tags")
        )

        # Get all resources for the workspace
        resources = Resource.objects.filter(workspace=workspace)
        resources_serializer = ResourceSerializer(resources, many=True)

        # Paginate the filtered assets
        page = self.paginate_queryset(filtered_assets)
        if page is not None:
            serializer = AssetIndexSerializer(
                page, many=True, context={"request": request}
            )
            response = self.get_paginated_response(serializer.data)
            response.data["filters"] = {
                "types": list(types) if len(types) > 0 else [],
                "sources": list(sources) if len(sources) > 0 else [],
                "tags": list(tags) if len(tags) > 0 else [],
            }
            response.data["resources"] = resources_serializer.data
            return response

        serializer = AssetIndexSerializer(
            filtered_assets, many=True, context={"request": request}
        )

        return Response(
            {
                "results": serializer.data,
                "filters": {
                    "types": list(types),
                    "sources": list(sources),
                    "tags": list(tags),
                },
                "resources": resources_serializer.data,
            }
        )

    def retrieve(self, request, pk=None):
        try:
            asset = Asset.objects.get(id=pk)
            serializer = AssetSerializer(asset, context={"request": request})
            return Response(serializer.data)
        except Asset.DoesNotExist:
            return Response(
                {"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND
            )
