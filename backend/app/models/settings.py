import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from polymorphic.models import PolymorphicModel

from app.models.workspace import Workspace
from app.utils.fields import encrypt


class WorkspaceSettings(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)


class StorageSettings(WorkspaceSettings):
    class StorageCategories(models.TextChoices):
        DATA = "data"
        METADATA = "metadata"
        EXPORT = "export"

    def get_default_categories():
        return list(StorageSettings.StorageCategories.values)

    applies_to = ArrayField(
        models.CharField(max_length=255, choices=StorageCategories.choices),
        null=True,
        default=get_default_categories,
    )
    s3_access_key = encrypt(models.CharField(max_length=255))
    s3_secret_key = encrypt(models.CharField(max_length=255))
    s3_endpoint_url = models.URLField(max_length=2000)
    s3_public_url = models.URLField(max_length=2000, null=True, blank=True)
    s3_bucket_name = models.CharField(max_length=255)
    s3_region_name = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.s3_public_url:
            self.s3_public_url = self.s3_endpoint_url

        existing = type(self).objects.filter(workspace=self.workspace)
        if existing.exists() and not existing.filter(id=self.id).exists():
            raise ValueError("Only one StorageSettings per workspace is allowed")

        super().save(*args, **kwargs)

    def list_bucket_contents(self, prefix=None):
        import boto3
        from botocore.client import Config

        # Initialize S3 client
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.s3_access_key,
            aws_secret_access_key=self.s3_secret_key,
            endpoint_url=self.s3_endpoint_url,
            region_name=self.s3_region_name,
            config=Config(signature_version="s3v4"),
        )

        try:
            # List objects with optional prefix
            params = {"Bucket": self.s3_bucket_name}
            if prefix:
                params["Prefix"] = prefix

            response = s3_client.list_objects_v2(**params)

            # Extract and return the contents
            contents = []
            if "Contents" in response:
                contents = [
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                    }
                    for obj in response["Contents"]
                ]

            return contents

        except Exception as e:
            raise Exception(f"Failed to list bucket contents: {str(e)}")
