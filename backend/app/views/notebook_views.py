from rest_framework import status, viewsets
from rest_framework.response import Response

from api.serializers import NotebookDetailSerializer, NotebookSerializer
from app.models import Notebook


class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.objects.all()

    def create(self, request):
        workspace = request.user.current_workspace()
        serializer = NotebookDetailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(workspace=workspace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        workspace = request.user.current_workspace()
        try:
            notebook = Notebook.objects.get(pk=pk, workspace=workspace)
        except Notebook.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = NotebookDetailSerializer(notebook, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        workspace = request.user.current_workspace()
        notebooks = Notebook.objects.filter(workspace=workspace).order_by("-created_at")
        serializer = NotebookSerializer(notebooks, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        workspace = request.user.current_workspace()
        try:
            notebook = Notebook.objects.get(pk=pk, workspace=workspace)
        except Notebook.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = NotebookDetailSerializer(notebook)
        return Response(serializer.data)
