from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.models import Workspace


class SettingsView(APIView):
    def get(self, request):
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Get the list of exclusion filters
        exclusion_filters = workspace.assets_exclude_name_contains

        # Initialize a list to store the results
        exclusion_results = []

        # For each filter, count the number of assets that match
        for filter_string in exclusion_filters:
            matching_assets_count = workspace.asset_set.filter(
                name__icontains=filter_string
            ).count()
            exclusion_results.append(
                {"filter_name_contains": filter_string, "count": matching_assets_count}
            )

        # Prepare the response data
        response_data = {
            "exclusion_filters": exclusion_results,
            "api_keys": {
                "metabase": workspace.api_key_metabase,
            },
        }

        return Response(response_data)
    
    def post(self, request):
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND
            )

        api_keys = request.data.get("api_keys", {})
        metabase_api_key = api_keys.get("metabase")
        if metabase_api_key is not None:
            workspace.api_key_metabase = metabase_api_key
            workspace.save()

        return Response({"detail": "Workspace updated successfully."}, status=status.HTTP_200_OK)
