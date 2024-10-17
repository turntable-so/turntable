"""
ASGI config for api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import json
import os

from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from app.consumers import (
    StreamingInferenceConsumer,
    TestStreamingInference,
    WorkflowRunConsumer,
)
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.security.websocket import AllowedHostsOriginValidator


class RealtimeNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Process the data and send updates
        await self.send(text_data=json.dumps({"status": "Updated status"}))


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    re_path(
                        r"^ws/subscribe/(?P<workspace_id>[^/]+)/$",
                        WorkflowRunConsumer.as_asgi(),
                    ),
                    re_path(
                        r"^infer/stream/$",
                        StreamingInferenceConsumer.as_asgi(),
                    ),
                    re_path(
                        r"^ws/echo/(?P<workspace_id>\w+)/$",
                        TestStreamingInference.as_asgi(),
                    ),
                ]
            )
        ),
    }
)
