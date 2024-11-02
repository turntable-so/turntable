import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Mount juicefs volume"

    def handle(self, *args, **kwargs):
        command = f"juicefs mount {settings.JUICEFS_REDIS_URL} {settings.JUICEFS_MOUNT_POINT} -d --force"
        try:
            subprocess.run(command, shell=True, check=True)
            self.stdout.write(self.style.SUCCESS("JuiceFS mounted"))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"JuiceFS mount failed: {e}"))
