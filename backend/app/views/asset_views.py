from api.serializers import AssetIndexSerializer, AssetSerializer
from app.models import Asset, Resource
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.cache import caches

cache = caches["default"]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    def list(self, request):
        workspace = request.user.current_workspace()
        resource_id = request.query_params.get("resource_id")
        cached_assets = cache.get(f"{workspace.id}:{resource_id}:assets")
        if cached_assets:
            return Response(cached_assets)

        if resource_id is None:
            return Response(
                {"error": "resource_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resource = Resource.objects.get(id=resource_id)
        except Resource.DoesNotExist:
            return Response(
                {"error": "Resource not found."}, status=status.HTTP_404_NOT_FOUND
            )

        assets = Asset.objects.filter(resource=resource, workspace=workspace)
        response_data = [
            {
                "id": asset.id,
                "name": asset.name,
                "type": asset.type,
                "unique_name": asset.unique_name,
                "tags": asset.tags,
                "description": asset.description,
                "num_columns": asset.num_columns,
            }
            for asset in assets
        ]
        cache.set(f"{workspace.id}:{resource_id}:assets", response_data)
        response = Response(response_data)
        return response

    def retrieve(self, request, pk=None):
        workspace = request.user.current_workspace()
        asset = Asset.objects.get(id=pk)
        serializer = AssetSerializer(asset, context={"request": request})
        return Response(serializer.data)
