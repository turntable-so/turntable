from api.serializers import AssetIndexSerializer, AssetSerializer
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
    serializer_class = AssetSerializer
    pagination_class = AssetPagination

    permission_classes = [AllowAny]

    def list(self, request):
        query = request.query_params.get("q", None)
        if query:
            # TODO: add ranking to this for name, description, tags, etc.
            assets = Asset.objects.filter(name__icontains=query)
        else:
            assets = Asset.objects.all()

        types = assets.values("type").annotate(count=Count("type")).order_by("type")
        sources = (
            assets.values("resource__id")
            .annotate(count=Count("resource__id"))
            .order_by("resource__name")
        )
        tags = assets.values("tags").annotate(count=Count("tags")).order_by("tags")

        page = self.paginate_queryset(assets)
        if page is not None:
            serializer = AssetIndexSerializer(
                page, many=True, context={"request": request}
            )
            response = self.get_paginated_response(serializer.data)
            response.data["filters"] = {
                "types": list(types),
                "sources": list(sources),
                "tags": list(tags),
            }
            return response

        serializer = AssetIndexSerializer(
            assets, many=True, context={"request": request}
        )

        return Response(
            {
                "results": serializer.data,
                "filters": {
                    "types": list(types),
                    "sources": list(sources),
                    "tags": list(tags),
                },
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
