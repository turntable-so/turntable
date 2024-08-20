import pytest
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.management import call_command
from django.db import connection

from app.models import Resource
from app.utils.environment import set_env_variable


@pytest.mark.django_db
def test_secret_rotation(local_postgres, local_metabase):
    def get_postgres_field_value():
        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM app_postgresdetails")
            return bytes(cursor.fetchone()[0])

    def get_metabase_field_value():
        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM app_metabasedetails")
            return bytes(cursor.fetchone()[0])

    # get current encrypted values
    postgres_encrypted_before = get_postgres_field_value()
    metabase_encrypted_before = get_metabase_field_value()

    new_key = str(Fernet.generate_key().decode())

    call_command("rotate_encryption_key", key=new_key)

    # Check that the encrypted values have changed
    assert postgres_encrypted_before != get_postgres_field_value()
    assert metabase_encrypted_before != get_metabase_field_value()

    # Check that the details are still the same when pulled down
    try:
        cur_key = settings.ENCRYPTION_KEY
        settings.ENCRYPTION_KEY = new_key
        with set_env_variable("NEW_READ_ENCRYPTION_KEY", "true"):
            assert (
                local_postgres.details
                == Resource.objects.get(id=local_postgres.id).details
            )
            assert (
                local_metabase.details
                == Resource.objects.get(id=local_metabase.id).details
            )
    finally:
        settings.ENCRYPTION_KEY = cur_key
