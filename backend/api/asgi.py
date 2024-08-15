"""
ASGI config for api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import json
import os

from django.core.asgi import get_asgi_application
from django.urls import re_path
from app.consumers import WorkflowRunConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.generic.websocket import AsyncWebsocketConsumer


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

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(
            [
                re_path(
                    r"^ws/subscribe/(?P<workspace_id>[^/]+)/$",
                    WorkflowRunConsumer.as_asgi(),
                ),
            ]
        ),
    }
)
