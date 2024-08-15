from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import AssetSerializer, LineageSerializer
from app.models import Asset
from app.services.lineage_service import LineageService


class LineageViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, pk=None):
        workspace = request.user.current_workspace()
        lineage_service = LineageService(workspace_id=workspace.id)
        asset_id = pk
        predecessor_depth = int(request.query_params.get("predecessor_depth"))
        successor_depth = int(request.query_params.get("successor_depth"))
        lineage_type = request.query_params.get("lineage_type")
        if lineage_type not in ["all", "direct_only"]:
            return Response(
                {
                    "error": "lineage_type query parameter must be either 'all' or 'direct_only'."
                },
                status=400,
            )
        asset = Asset.objects.get(id=asset_id, workspace=workspace.id)

        lineage = lineage_service.get_lineage(
            asset_id=asset_id,
            predecessor_depth=predecessor_depth,
            successor_depth=successor_depth,
            lineage_type=lineage_type,
        )

        asset_serializer = AssetSerializer(asset, context={"request": request})
        lineage_serializer = LineageSerializer(lineage, context={"request": request})
        return Response(
            {
                "root_asset": asset_serializer.data,
                "lineage": lineage_serializer.data,
            }
        )
