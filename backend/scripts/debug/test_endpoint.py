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
    # x = test_endpoint(
    #     "/query/sql/",
    #     "dev@turntable.so",
    #     "POST",
    #     stream=False,
    #     data={"query": "select * from dbt_sl_test.customers"},
    # )
    from django_celery_results.models import TaskResult

    from api.serializers import TaskSerializer
    from scripts.debug.profiling import pyprofile

    tasks = TaskResult.objects.all()
    task_2 = TaskResult.objects.filter(
        task_id__in=[
            "809a52ec-cb40-4765-ba57-c5ae45ba3b6d",
            "a0129b8a-22b0-4de1-916f-5770801ce9bb",
        ]
    )
    task_1 = TaskResult.objects.get(task_id="809a52ec-cb40-4765-ba57-c5ae45ba3b6d")

    @pyprofile()
    def serializer_tests():
        def serializer_many():
            return TaskSerializer(tasks, many=True).data

        def serializer_two():
            return TaskSerializer(task_2, many=True).data

        def serializer_one():
            return TaskSerializer(task_1).data

        return {
            "serializer_many": serializer_many(),
            "serializer_two": serializer_two(),
            "serializer_one": serializer_one(),
        }

    x = serializer_tests()
    print(x["serializer_two"])
