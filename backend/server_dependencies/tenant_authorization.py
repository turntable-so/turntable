import json
import logging
from functools import lru_cache
from typing import List

import jwt
import requests
from dotenv import load_dotenv
from fastapi import HTTPException, Request
from jwt.algorithms import RSAAlgorithm
from pydantic import BaseModel

logger = logging.getLogger(__name__)

load_dotenv()


@lru_cache(maxsize=None)
def get_clerk_jwks():
    url = "https://neat-sponge-48.clerk.accounts.dev/.well-known/jwks.json"
    # Clerk Frontend API URL, see: https://reference.clerk.dev/reference/frontend-api-reference/well-known-requestsl
    # Frontend API can be found under Developer Settings > API Keys  in the Clerk Dashboard.
    response = requests.get(url)
    response.raise_for_status()
    data_json = response.json()

    return data_json


class Tenant(BaseModel):
    id: str
    org_permissions: List[str]
    org_role: str
    user_id: str


async def get_tenant(request: Request) -> Tenant:
    # Strip the "Bearer " prefix from the header
    try:
        token = (
            request.headers.get("Authorization", "")[7:] or request.query_params["jwt"]
        )
    except KeyError:
        logger.error("Missing JWT token")
        raise HTTPException(status_code=401, detail="Missing JWT token")

    clerk_jwks = get_clerk_jwks()
    public_key = RSAAlgorithm.from_jwk(json.dumps(clerk_jwks["keys"][0]))

    decoded = jwt.decode(token, public_key, algorithms=["RS256"])

    return Tenant(
        id=decoded["org_id"],
        org_permissions=decoded["org_permissions"],
        org_role=decoded["org_role"],
        user_id=decoded["sub"],
    )


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
