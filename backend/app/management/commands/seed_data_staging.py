from django.core.management.base import BaseCommand
from django.db import transaction

from fixtures.staging_env import (
    create_user,
    group_1,
    group_2,
    group_3,
    group_5,
    group_6,
)


class Command(BaseCommand):
    help = "Seed data with staging user and workspace"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        pass

        user = create_user()
        group_1(user)
        group_2(user)
        group_3(user)
        group_5(user)
        group_6(user)
        self.stdout.write(
            self.style.SUCCESS("Successfully seeded the database with staging data")
        )
