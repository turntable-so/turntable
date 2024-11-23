import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from app.models.resources import Resource
from app.models.settings import StorageSettings
from app.models.user import User
from app.models.workspace import Workspace
from app.services.storage_backends import CustomFileField


class Notebook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    tags = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    ###### tenant_id is DEPRECATED PLEASE DELETE
    tenant_id = models.TextField(null=True)
    #######
    contents = models.JSONField(null=True, blank=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, null=True, related_name="notebooks"
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="notebooks"
    )

    class Meta:
        indexes = [
            models.Index(fields=["tenant_id"]),
        ]


class Block(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    config = models.JSONField(null=True)
    results = CustomFileField(
        upload_to="results/",
        null=True,
        storage_category=StorageSettings.StorageCategories.DATA,
    )
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE, null=True, related_name="blocks"
    )
    resource = models.ForeignKey(
        Resource, on_delete=models.SET_NULL, null=True, related_name="blocks"
    )
