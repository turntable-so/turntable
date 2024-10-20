from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from urllib.parse import parse_qs
from jwt import decode as jwt_decode

from app.models.user import User

@database_sync_to_async
def get_user(validated_token):
    try:
        user = User.objects.get(id=validated_token["user_id"])
        return user
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if not token:
            raise InvalidToken("Token not provided in query parameters")

        try:
            # This will raise an exception if the token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            raise e
        
        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        scope["user"] = await get_user(validated_token=decoded_data)

        return await self.app(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
