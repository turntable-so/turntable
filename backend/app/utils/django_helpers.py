import os

import django
from django.apps import apps


def safe_django_setup():
    if not apps.ready:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
        django.setup()
