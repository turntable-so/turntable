if __name__ == "__main__":
    import django
    from django.conf import settings
    from rest_framework.test import APIClient

    django.setup()

    from app.models import User

    settings.ALLOWED_HOSTS = ["*"]
    client = APIClient()
    client.force_authenticate(user=User.objects.get(email="dev@turntable.so"))
    response = client.post("/project/stream_dbt_command/", {"command": "run"})
    # print([c for c in response.streaming_content])
    for chunk in response.streaming_content:
        print(chunk.decode("utf-8"), end="", flush=True)
