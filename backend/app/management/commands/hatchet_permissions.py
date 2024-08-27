import os

import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Command(BaseCommand):
    help = "Run hatchet custom permissions on start"

    def handle(self, *args, **kwargs):
        if os.getenv("STAGING") == "true":
            self.stdout.write(
                self.style.WARNING("Skipping hatchet database creation on staging.")
            )
            return
        if os.getenv("LOCAL_DB") == "true":
            dbname = settings.DATABASES["default"]["NAME"]
            user = settings.DATABASES["default"]["USER"]
            password = settings.DATABASES["default"]["PASSWORD"]
            host = settings.DATABASES["default"]["HOST"]
            port = settings.DATABASES["default"]["PORT"]

            connection = psycopg2.connect(
                dbname=dbname, user=user, password=password, host=host, port=port
            )
        else:
            database_url = settings.DATABASES["default"]
            connection = psycopg2.connect(dsn=database_url)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        # Check if the database exists
        hatchet_db = os.environ.get("DATABASE_POSTGRES_DB_NAME")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{hatchet_db}'")
        exists = cursor.fetchone()

        if not exists:
            # Create the database
            cursor.execute(f"CREATE DATABASE {hatchet_db}")
            self.stdout.write(
                self.style.SUCCESS(f"Database '{hatchet_db}' created successfully.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Database '{hatchet_db}' already exists.")
            )
        cursor.execute(f"ALTER DATABASE {hatchet_db} OWNER to {user}")

        cursor.close()
        connection.close()
