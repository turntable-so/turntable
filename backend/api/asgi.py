import os

from django.core.asgi import get_asgi_application
from django.urls import re_path
from app.consumers import DBTCommandConsumer, WorkflowRunConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": 
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(
                            r"^ws/subscribe/(?P<workspace_id>\w+)/$",
                            WorkflowRunConsumer.as_asgi(),
                        ),
                        re_path(
                            r"^ws/dbt_command/(?P<workspace_id>\w+)/$",
                            DBTCommandConsumer.as_asgi(),
                        ),
                    ]
                )
            )
    }
)
