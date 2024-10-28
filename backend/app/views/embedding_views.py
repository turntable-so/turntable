import re
import time
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import jwt
import requests

from app.models.metadata import Asset
from app.models.resources import MetabaseDetails, ResourceDetails

class EmbeddingViewSet(viewsets.ViewSet):
    # this is the type used for the iframe url to embed
    asset_type_to_embed_type = {
        Asset.AssetType.CHART: "question",
        Asset.AssetType.DASHBOARD: "dashboard",
    }
    # this is the type used for the metabase api
    asset_type_to_api_type = {
        Asset.AssetType.CHART: "card",
        Asset.AssetType.DASHBOARD: "dashboard",
    }

    @action(detail=False, methods=["GET"])
    def metabase(self, request):
        asset_id = request.query_params.get("asset_id")
        workspace = request.user.current_workspace()
        
        if not workspace:
            return Response({"detail": "Workspace not found."}, status=404)
        if not asset_id:
            return Response({"detail": "Asset ID is required."}, status=400)
        
        metabase_details_res = self._get_metabase_details_from_asset(asset_id)
        if not metabase_details_res:
            return Response({"detail": "Metabase details not found."}, status=404)
        
        asset = metabase_details_res["asset"]
        metabase_details = metabase_details_res["metabase_details"]

        jwt_shared_secret = metabase_details.jwt_shared_secret
        if not jwt_shared_secret:
            return Response({"detail": "Metabase JWT shared secret not configured."}, status=400)

        metabase_site_url = metabase_details.connect_uri

        embed_type = self.asset_type_to_embed_type[asset.type]
        if not embed_type:
            return Response({"detail": "Asset type not supported for embedding."}, status=400)
    
        metabase_entity_id = self._get_metabase_entity_id(asset_id)

        metabase_resource = { embed_type: int(metabase_entity_id) }
        payload = {
            'resource': metabase_resource,
            'params': {},
            'exp': round(time.time()) + (60 * 10),
        }

        # this is the token we'll use to check if the asset is embeddable, and to generate the iframe url
        token = jwt.encode(payload, jwt_shared_secret, algorithm='HS256')

        api_asset_type = self.asset_type_to_api_type[asset.type]
        if not api_asset_type:
            return Response({"detail": "Asset type not supported for url embedding."}, status=400)

        response = requests.get(f"{metabase_site_url}/api/embed/{api_asset_type}/{token}")
        if response.text == "Embedding is not enabled for this object.":
            return Response({"detail": "NOT_EMBEDDED"}, status=400)
        elif response.status_code != 200:
            return Response({"detail": "Error getting embeddable asset."}, status=500)

        iframe_url = f"{metabase_site_url}/embed/{embed_type}/{token}#bordered=false&titled=false"
        return Response({'iframe_url': iframe_url})

    @action(detail=False, methods=["POST"])
    def metabase_make_embeddable(self, request):
        asset_id = request.query_params.get("asset_id")
        workspace = request.user.current_workspace()
        
        if not workspace:
            return Response({"detail": "Workspace not found."}, status=404)
        if not asset_id:
            return Response({"detail": "Asset ID is required."}, status=400)
        
        metabase_details_res = self._get_metabase_details_from_asset(asset_id)
        if not metabase_details_res:
            return Response({"detail": "Metabase details not found."}, status=404)
        
        asset = metabase_details_res["asset"]
        metabase_details = metabase_details_res["metabase_details"]

        metabase_api_key = metabase_details.api_key
        if not metabase_api_key:
            return Response({"detail": "Metabase API key not configured."}, status=400)
        
        api_asset_type = self.asset_type_to_api_type[asset.type]
        if not api_asset_type:
            return Response({"detail": "Asset type not supported for url embedding."}, status=400)
        
        metabase_entity_id = self._get_metabase_entity_id(asset_id)
        
        metabase_response = requests.put(f"{metabase_details.connect_uri}/api/{api_asset_type}/{metabase_entity_id}", headers={
            'Content-Type': 'application/json',
            "X-API-KEY": metabase_api_key,
        }, json={"enable_embedding": True})

        if metabase_response.status_code != 200:
            return Response({"detail": f"Error marking asset embeddable: {metabase_response.text}"}, status=500)

        return Response({"detail": "ASSET_EMBEDDED"}, status=200)
    
    # TODO theres a better way to do this with joins
    def _get_metabase_details_from_asset(self, asset_id: str):
        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return None
        
        try:
            resource_details = ResourceDetails.objects.get(resource_id=asset.resource_id)
        except ResourceDetails.DoesNotExist:
            return None
        
        try:
            metabase_details = MetabaseDetails.objects.get(resourcedetails_ptr_id=resource_details.id)
        except MetabaseDetails.DoesNotExist:
            return None

        return dict(
            asset=asset,
            resource_details=resource_details,
            metabase_details=metabase_details,
        )
    
    def _get_metabase_entity_id(self, asset_id: str):
        # get the last number in the urn, which corresponds to the metabase asset id
        return re.search(r"\d+(?=\)$)", f"{asset_id}").group()
    