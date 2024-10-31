# make sure django is setup


# rest of imports
import os
import subprocess


def main():
    from django.conf import settings

    superuser_email = os.environ.get("SUPERUSER_EMAIL")
    superuser_password = os.environ.get("SUPERUSER_PASSWORD")

    command = [
        "celery",
        f"--broker={settings.CELERY_BROKER_URL}",
        "flower",
        f"--basic-auth={superuser_email}:{superuser_password}",
        "--loglevel=none",
    ]

    subprocess.run(command)


if __name__ == "__main__":
    import django

    django.setup()
    main()
