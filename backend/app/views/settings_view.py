from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def truncate_api_key(
    api_key: str | None, visible_chars: int = 12, mask: str = "********"
) -> str | None:
    if not api_key:
        return None
    return api_key[:visible_chars] + mask


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

        api_keys = {
            "openai_api_key": truncate_api_key(workspace.openai_api_key),
            "anthropic_api_key": truncate_api_key(workspace.anthropic_api_key),
        }

        # Prepare the response data
        response_data = {"exclusion_filters": exclusion_results, "api_keys": api_keys}
        return Response(response_data)

    def post(self, request):
        workspace = request.user.current_workspace()
        api_keys = request.data.get("api_keys", {})
        if "openai_api_key" in api_keys:
            workspace.openai_api_key = api_keys["openai_api_key"]
        if "anthropic_api_key" in api_keys:
            workspace.anthropic_api_key = api_keys["anthropic_api_key"]
        workspace.save()
        return Response(status=status.HTTP_200_OK)
