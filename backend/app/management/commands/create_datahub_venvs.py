import subprocess

from django.core.management.base import BaseCommand

from app.models import ResourceDetails


def get_all_subclasses(cls):
    subclasses = set(cls.__subclasses__())
    for (
        subclass
    ) in subclasses.copy():  # Copy to avoid modifying the set while iterating
        subclasses.update(get_all_subclasses(subclass))
    return subclasses


class Command(BaseCommand):
    help = "Create datahub venvs"

    def handle(self, *args, **kwargs):
        for cls in get_all_subclasses(ResourceDetails):
            instance = cls()
            subprocess.run(["uv", "pip", "install", "setuptools", "wheel", "--system"])
            if hasattr(instance, "venv_path") and instance.venv_path is not None:
                print(type(instance))
                cls().create_venv_and_install_datahub(force=True)
