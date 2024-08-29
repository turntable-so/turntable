from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class HealthCheckViewSet(viewsets.ViewSet):
    authentication_classes = []  # Disable authentication for this view
    permission_classes = [AllowAny]  # Allow anyone to access this view

    @action(detail=False, methods=["get"])
    def health(self, request):
        return Response({"status": "ok"})
