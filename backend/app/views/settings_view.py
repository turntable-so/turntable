from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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
        response_data = {"exclusion_filters": exclusion_results}
        return Response(response_data)