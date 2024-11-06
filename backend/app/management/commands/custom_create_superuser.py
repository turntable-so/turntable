import os

from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import User


class Command(BaseCommand):
    help = "Create a superuser for the django admin panel"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        email = os.getenv("SUPERUSER_EMAIL")
        password = os.getenv("SUPERUSER_PASSWORD")
        if not email or not password: raise EnvironmentError("SUPERUSER_EMAIL and SUPERUSER_PASSWORD must be set")
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING("Superuser already exists"))
        else:
            User.objects.create_superuser(email, password)
            self.stdout.write(self.style.SUCCESS("Successfully created superuser"))
