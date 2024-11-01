from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.conf import settings
from jwt import decode as jwt_decode
from rest_framework_simplejwt.exceptions import InvalidToken


@database_sync_to_async
def get_user(user_id):
    from app.models.user import User

    try:
        user = User.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        raise InvalidToken("User not found")


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if not token:
            raise InvalidToken("Token not provided in query parameters")

        try:
            # This will raise an exception if the token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            await send({
                "type": "websocket.close",
                "code": 4401,
                "reason": "Token is invalid or expired",
            })
            return

        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS512"])
        user = await get_user(user_id=decoded_data["user_id"])
        scope["user"] = user

        return await self.app(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
