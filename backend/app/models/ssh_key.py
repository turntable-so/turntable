from __future__ import annotations

import logging
import uuid
from contextlib import contextmanager

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.db import models

from app.models.workspace import Workspace
from app.utils.fields import encrypt

logger = logging.getLogger(__name__)


def generate_rsa_key_pair():
    # Generate a new RSA key pair
    key = rsa.generate_private_key(
        backend=default_backend(), public_exponent=65537, key_size=2048
    )

    # Serialize the public key
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )

    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return public_key.decode("utf-8"), private_key.decode("utf-8")


class SSHKey(models.Model):
    # pk
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # fields
    public_key = models.TextField()
    # TODO: add encryption to this key
    private_key = encrypt(models.TextField())

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]

    @classmethod
    def generate_deploy_key(cls, workspace: Workspace):
        ssh_key = cls.objects.filter(workspace=workspace).last()
        if ssh_key is not None:
            return ssh_key

        public_key, private_key = generate_rsa_key_pair()
        ssh_key = SSHKey.objects.create(
            workspace=workspace,
            public_key=public_key,
            private_key=private_key,
        )
        logger.debug(f"SSH keys generated successfully for {workspace}")

        return ssh_key
