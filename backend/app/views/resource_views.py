from app.models.resources import Resource
from rest_framework import viewsets
from rest_framework.response import Response
from api.serializers import ResourceSerializer

from rest_framework import status


class ResourceViewSet(viewsets.ModelViewSet):

    serializer_class = ResourceSerializer

    def list(self, request):
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_403_FORBIDDEN
            )
        resources = Resource.objects.filter(workspace=workspace)
        serializer = self.get_serializer(resources, many=True)
        return Response(serializer.data)
