import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

from app.consumers import AIChatConsumer, DBTCommandConsumer, TaskResultConsumer
from app.websocket_auth import JWTAuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddlewareStack(
            URLRouter(
                [
                    re_path(
                        r"^ws/subscribe/(?P<workspace_id>\w+)/$",
                        TaskResultConsumer.as_asgi(),
                    ),
                    re_path(
                        r"^ws/dbt_command/$",
                        DBTCommandConsumer.as_asgi(),
                    ),
                    re_path(
                        r"^ws/infer/$",
                        AIChatConsumer.as_asgi(),
                    ),
                ]
            )
        ),
    }
)
