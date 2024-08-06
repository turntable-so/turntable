import os

from workflows.utils.encoding import decode_base64


def get_github_auth_info():
    github_app_id = os.getenv("GITHUB_APP_ID")
    if github_app_id is None:
        raise ValueError("GITHUB_APP_ID is not set")

    github_private_key = decode_base64(os.getenv("GITHUB_PRIVATE_KEY_BASE64"))
    if github_private_key is None:
        raise ValueError("GITHUB_PRIVATE_KEY_BASE64 is not set")

    return github_app_id, github_private_key
