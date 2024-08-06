import json

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


class EncryptedJSONField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher.encrypt(json.dumps(value).encode("utf-8")).decode("utf-8")

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return json.loads(self.cipher.decrypt(value.encode("utf-8")).decode("utf-8"))

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, dict):
            return value
        return json.loads(self.cipher.decrypt(value.encode("utf-8")).decode("utf-8"))
