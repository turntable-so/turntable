import logging
from functools import lru_cache

import requests
from dotenv import load_dotenv
from fastapi import Request
from jose import jwt
from jose.exceptions import JWTError

logger = logging.getLogger(__name__)

load_dotenv()


@lru_cache(maxsize=None)
def get_clerk_jwks(url: str = "https://clerk.turntable.so/.well-known/jwks.json"):
    # Clerk Frontend API URL, see: https://reference.clerk.dev/reference/frontend-api-reference/well-known-requestsl
    # Frontend API can be found under Developer Settings > API Keys  in the Clerk Dashboard.
    response = requests.get(url)
    response.raise_for_status()
    data_json = response.json()

    return data_json


async def get_user_id_from_clerk_jwt(request: Request):
    # Strip the "Bearer " prefix from the header
    token = request.headers.get("Authorization", "")[7:] or request.query_params["jwt"]

    clerk_jwks = get_clerk_jwks()

    try:
        decoded = jwt.decode(token, clerk_jwks["keys"][0], algorithms=["RS256"])
    except JWTError as e:
        # For now, this is expected for most endpoints, since not all routes are guarded by JWTs.
        logger.warning(f"JWTError: {e} for path {request.url.path}")

        try:
            return get_user_id_from_clerk_oauth_access_token(request)
        except Exception as e:
            logger.warning(f"Exception: {e} for path {request.url.path}")

        return None

    # return user_id
    return decoded["sub"]


# NOTE THAT WE DO NOT SUPPORT ORGS IN PRODUCTION YET
# That is why we are using neat-sponge here
async def get_org_id_from_clerk_jwt(request: Request):
    # Strip the "Bearer " prefix from the header
    token = request.headers.get("Authorization", "")[7:] or request.query_params["jwt"]

    clerk_jwks = get_clerk_jwks(
        "https://neat-sponge-48.clerk.accounts.dev/.well-known/jwks.json"
    )
    decoded = jwt.decode(token, clerk_jwks["keys"][0], algorithms=["RS256"])

    return decoded["org_id"]


def get_user_id_from_clerk_oauth_access_token(request: Request):
    # Strip the "Bearer " prefix from the header
    token = (
        request.headers.get("Authorization", "")[7:]
        or request.query_params["access_token"]
    )
    url = "https://clerk.turntable.so/oauth/userinfo"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data_json = response.json()

    user_id = data_json["user_id"]

    if user_id is None:
        raise Exception("user_id is None")

    logger.warning(f"user_id is {user_id}")

    return user_id
