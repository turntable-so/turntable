from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from app.utils.environment import set_env_variable
from app.utils.fields import EncryptedMixin


class Command(BaseCommand):
    help = "Rotate ENCRYPTION_KEY and update the database accordingly"

    def add_arguments(self, parser):
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            help="Input new encryption key",
        )

    def bulk_update_with_new_key(self, model, instances, encrypted_fields, new_key):
        try:
            cur_key = settings.ENCRYPTION_KEY
            settings.ENCRYPTION_KEY = new_key

            with set_env_variable("NEW_WRITE_ENCRYPTION_KEY", "true"):
                for instance in instances:
                    instance.save()

        finally:
            settings.ENCRYPTION_KEY = cur_key

    def handle(self, *args, **kwargs):
        app_config = apps.get_app_config("app")
        new_key = kwargs["key"]

        for model in app_config.get_models():
            for field in model._meta.get_fields():
                encrypted_fields = []
                if EncryptedMixin in field.__class__.__mro__:
                    encrypted_fields.append(field.name)
            if encrypted_fields:
                instances = model.objects.all()
                self.bulk_update_with_new_key(
                    model, instances, encrypted_fields, new_key
                )
