from rest_framework.response import Response
from app.models import Block
from api.serializers import (
    BlockSerializer,
)
from rest_framework import viewsets, status


class BlockViewSet(viewsets.ModelViewSet):

    queryset = Block.objects.all()

    def retrieve(self, request, pk=None):
        try:
            block = Block.objects.get(pk=pk)
        except Block.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BlockSerializer(block)
        return Response(serializer.data)
