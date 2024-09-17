from functools import reduce
from api.serializers import AssetIndexSerializer, AssetSerializer, ResourceSerializer
from app.models import Asset, Resource
from app.models.metadata import ColumnLink, AssetLink
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.cache import caches
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.views.decorators.cache import cache_page
from math import ceil
from django.utils.decorators import method_decorator

from django.db.models import (
    Count,
    Q,
    Exists,
    OuterRef,
    Case,
    When,
    IntegerField,
    BooleanField,
)

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

    @method_decorator(cache_page(60))  # Cache the response for 60 seconds
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
        base_queryset = Asset.objects.filter(workspace=workspace).order_by("name")
        # Exclude assets based on workspace.assets_exclude_name_contains
        exclude_filters = workspace.assets_exclude_name_contains
        if exclude_filters:
            exclude_q = Q()
            for filter_string in exclude_filters:
                exclude_q |= Q(name__icontains=filter_string)
            base_queryset = base_queryset.exclude(exclude_q)

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

        if tags_filter and len(tags_filter) > 0:
            tag_list = tags_filter.split(",")
            filtered_assets = filtered_assets.filter(
                reduce(
                    lambda x, y: x | y, [Q(tags__contains=[tag]) for tag in tag_list]
                )
            )

        # Calculate filters using the base queryset
        types = (
            filtered_assets.exclude(type__exact="")
            .values("type")
            .annotate(count=Count("type"))
            .order_by("type")
        )
        sources = (
            filtered_assets.values("resource__id")
            .annotate(count=Count("resource__id"))
            .order_by("resource__name")
        )
        tags = (
            filtered_assets.filter(tags__isnull=False)
            .exclude(tags__exact=[])
            .values_list("tags", flat=True)
            .order_by()
            .distinct()
        )
        tags = [
            {"type": tag, "count": filtered_assets.filter(tags__contains=[tag]).count()}
            for sublist in tags
            for tag in sublist
            if tag
        ]

        # Get all resources for the workspace
        resources = Resource.objects.filter(workspace=workspace)
        resources_serializer = ResourceSerializer(resources, many=True)

        filtered_assets = filtered_assets.prefetch_related("columns")
        filtered_assets = filtered_assets.annotate(column_count=Count("columns"))
        # Add a count for columns with no column links
        filtered_assets = filtered_assets.annotate(
            unused_columns_count=Count(
                "columns",
                filter=~Exists(ColumnLink.objects.filter(source=OuterRef("columns"))),
            )
        )

        # Apply sorting
        sort_by = request.query_params.get("sort_by")
        sort_order = request.query_params.get("sort_order", "asc")

        print(sort_by, sort_order, flush=True)

        if sort_by in ["column_count", "unused_columns_count"]:
            order_by = f"{'-' if sort_order == 'desc' else ''}{sort_by}"
            filtered_assets = filtered_assets.order_by(order_by)
        else:
            # Default sorting
            filtered_assets = filtered_assets.order_by("name")

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

    @method_decorator(cache_page(60))  # Cache the response for 60 seconds
    @action(detail=False, methods=["GET"])
    def index(self, request):
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_403_FORBIDDEN
            )
        resources = Resource.objects.filter(workspace=workspace)
        assets = Asset.objects.filter(resource__in=resources).values(
            "resource_id",
            "id",
            "name",
            "type",
        )
        exclude_filters = workspace.assets_exclude_name_contains
        if exclude_filters:
            exclude_q = Q()
            for filter_string in exclude_filters:
                exclude_q |= Q(name__icontains=filter_string)
            assets = assets.exclude(exclude_q)

        grouped_assets = {}
        for asset in assets:
            resource_id = str(asset["resource_id"])
            if resource_id not in grouped_assets:
                grouped_assets[resource_id] = []
            grouped_assets[resource_id].append(
                {"id": asset["id"], "name": asset["name"], "type": asset["type"]}
            )

        resource_serializer = ResourceSerializer(resources, many=True)
        resource_data = resource_serializer.data
        for resource in resource_data:
            resource["assets"] = (
                grouped_assets[str(resource["id"])]
                if str(resource["id"]) in grouped_assets
                else []
            )
        return Response(resource_data)
