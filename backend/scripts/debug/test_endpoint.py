from typing import Any, Literal

import django
from django.conf import settings
from rest_framework.test import APIClient

from app.utils.url import build_url

django.setup()


def test_endpoint(
    path: str,
    user_email: str,
    cmd: Literal["POST", "GET", "PUT", "DELETE", "PATCH"] = "POST",
    query_params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    stream: bool = False,
):
    from app.models import User

    settings.ALLOWED_HOSTS = ["*"]
    client = APIClient()
    client.force_authenticate(user=User.objects.get(email="dev@turntable.so"))
    func = getattr(client, cmd.lower())
    response = func(build_url(path, query_params), data)
    if stream:
        out = ""
        for chunk in response.streaming_content:
            c = chunk.decode("utf-8")
            print(c, end="", flush=True)
            out += c
        return out
    else:
        return response.json()


if __name__ == "__main__":
    x = test_endpoint(
        "/query/sql/",
        "dev@turntable.so",
        "POST",
        stream=False,
        data={"query": "select * from dbt_sl_test.customers"},
    )
    breakpoint()
