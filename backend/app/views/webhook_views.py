import hmac
import hashlib
from app.models.workflows import DBTOrchestrator
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from adrf.views import APIView
from rest_framework.decorators import action

from django.conf import settings


class WebhookViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    def verify_signature(self, request, secret_key):
        """Verify the HMAC signature from the webhook"""
        received_signature = request.headers.get("X-Signature")
        if not received_signature:
            return False

        body = request.body

        expected_signature = hmac.new(
            secret_key, msg=body, digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, received_signature)

    @action(detail=True, methods=["POST"])
    def run_job(self, request, pk=None):
        print("run_job", request.data)
        print("run_job", request.headers)
        # if not self.verify_signature(request):
        #     return Response(
        #         {"error": "Invalid signature"}, status=status.HTTP_401_UNAUTHORIZED
        # )

        job = DBTOrchestrator.objects.get(id=pk)
        job.schedule_now()

        return Response(status=status.HTTP_201_CREATED)
