import json
from typing import (
    Any,
    Sequence,
    Type,
    TypeVar,
    cast,
    overload,
)

import orjson
from cryptography.fernet import Fernet
from django.conf import settings
from django.core import checks
from django.core.checks import CheckMessage
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from typing_extensions import Protocol


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


F = TypeVar("F", bound=models.Field)
FIELD_CACHE: dict[type, type] = {}


class DBAPI(Protocol):
    def Binary(self, obj: bytes | str) -> Any: ...


class DatabaseWrapper(Protocol):
    Database: DBAPI


class EncryptedMixin(models.Field):
    """
    A field mixin storing encrypted data

    :param bytes key: This is an optional argument.

        Allows for specifying an instance specific encryption key.
    :param int ttl: This is an optional argument.

        The amount of time in seconds that a value can be stored for. If the
        time to live of the data has passed, it will become unreadable.
        The expired value will return an :class:`Expired` object.
    """

    supported_lookups = ("isnull",)

    def __init__(self, *args, **kwargs) -> None:
        self.base_class: Type[models.Field]
        self.wasinstance: bool

        self.key: bytes | str = kwargs.pop("key", None)
        self.ttl: int = kwargs.pop("ttl", None)

        self._fernet = Fernet(settings.ENCRYPTION_KEY)
        super().__init__(*args, **kwargs)

    def _description(self) -> str:
        return _("Encrypted %s") % super().description

    description = property(_description)  # type: ignore[assignment]

    def _dump(self, value: Any) -> bytes:
        return self._fernet.encrypt(orjson.dumps(value))

    def _load(self, value: bytes) -> Any:
        return orjson.loads(self._fernet.decrypt(value, self.ttl))

    def check(self, **kwargs: Any) -> list[CheckMessage]:
        errors = super().check(**kwargs)
        if getattr(self, "remote_field", None):
            errors.append(
                checks.Error(
                    "Base field for encrypted cannot be a related field.",
                    hint=None,
                    obj=self,
                    id="encrypted.E002",
                )
            )
        return errors

    def clone(self):
        name, path, args, kwargs = super().deconstruct()
        # Determine if the class that subclassed us has been subclassed.
        if self.__class__.__mro__.index(EncryptedMixin) <= 1:
            return encrypt(self.base_class(*args, **kwargs), self.key, self.ttl)
        return self.__class__(*args, **kwargs)

    def deconstruct(self) -> tuple[str, str, Sequence[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        if self.wasinstance is False:
            path = f"{self.base_class.__module__}.{self.base_class.__name__}"
        # Determine if the class that subclassed us has been subclassed.
        elif self.__class__.__mro__.index(EncryptedMixin) <= 1:
            path = f"{encrypt.__module__}.{encrypt.__name__}"
            args = [self.base_class(*args, **kwargs)]
            kwargs = {}
            if self.ttl is not None:
                kwargs["ttl"] = self.ttl
        return name, path, args, kwargs

    def get_lookup(self, lookup_name: str) -> Any | None:
        if lookup_name not in self.supported_lookups:
            return None
        return super().get_lookup(lookup_name)

    def get_transform(self, lookup_name: str) -> Any | None:
        if lookup_name not in self.supported_lookups:
            return None
        return super().get_transform(lookup_name)

    def get_internal_type(self) -> str:
        return "BinaryField"

    def get_db_prep_value(
        self, value: Any, connection: BaseDatabaseWrapper, prepared: bool = False
    ) -> Any:
        value = models.Field.get_db_prep_value(self, value, connection, prepared)
        if value is not None:
            return cast(DatabaseWrapper, connection).Database.Binary(self._dump(value))
        return value

    get_db_prep_save = models.Field.get_db_prep_save

    def from_db_value(self, value, *args, **kwargs) -> Any:
        if value is not None:
            return self._load(force_bytes(value))
        return value


def get_encrypted_field(base_class: Type[F], wasinstance: bool) -> Type[F]:
    """
    A get or create method for encrypted fields, we cache the field in
    the module to avoid recreation. This also allows us to always return
    the same class reference for a field.
    """
    assert issubclass(base_class, models.Field)
    return FIELD_CACHE.setdefault(
        base_class,
        type(
            ("Encrypted" if wasinstance else "") + base_class.__name__,
            (EncryptedMixin, base_class),
            {"base_class": base_class, "wasinstance": wasinstance},
        ),
    )


@overload
def encrypt(base_field: F, key=None, ttl=None) -> F: ...


@overload
def encrypt(base_field: Type[F]) -> Type[F]: ...


def encrypt(base_field, key: bytes | str | None = None, ttl: int | None = None):
    """
    A decorator for creating encrypted model fields.

    :param base_field: Base Field to encrypt
    :param bytes key: This is an optional argument.

        Allows for specifying an instance specific encryption key.
    :param int ttl: This is an optional argument.

        The amount of time in seconds that a value can be stored for. If the
        time to live of the data has passed, it will become unreadable.
        The expired value will return an :class:`Expired` object.
    """
    if isinstance(base_field, type):
        assert issubclass(base_field, models.Field)
        assert key is None
        assert ttl is None
        return get_encrypted_field(base_field, False)

    name, path, args, kwargs = base_field.deconstruct()
    kwargs.update({"key": key, "ttl": ttl})
    return get_encrypted_field(type(base_field), True)(*args, **kwargs)
