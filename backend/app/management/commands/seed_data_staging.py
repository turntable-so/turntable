from django.core.management.base import BaseCommand

from fixtures.staging_env import create_user, group_1, group_2, group_3


class Command(BaseCommand):
    help = "Seed data with staging user and workspace"

    def handle(self, *args, **kwargs):
        user = create_user()
        group_1(user)
        group_2(user)
        group_3(user)
