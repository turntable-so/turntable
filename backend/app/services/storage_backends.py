import os
from urllib.parse import urlparse, urlunparse

import boto3
from django.conf import settings
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    bucket_name = "public-assets"
    default_acl = "public-read"
    file_overwrite = False
    custom_domain = False


class CustomS3Boto3Storage(S3Boto3Storage):
    def __init__(self, workspace_id: str, storage_category, *args, **kwargs):
        from app.models.settings import StorageSettings

        ws = StorageSettings.objects.filter(
            workspace_id=workspace_id, applies_to__contains=[storage_category]
        ).first()

        self.access_key = ws.s3_access_key if ws else settings.AWS_S3_ACCESS_KEY_ID
        self.secret_key = ws.s3_secret_key if ws else settings.AWS_S3_SECRET_ACCESS_KEY
        self.endpoint_url = ws.s3_endpoint_url if ws else settings.AWS_S3_ENDPOINT_URL
        self.public_url = ws.s3_public_url if ws else settings.AWS_S3_PUBLIC_URL
        self.bucket_name = ws.s3_bucket_name if ws else settings.AWS_STORAGE_BUCKET_NAME
        self.signature_version = "s3v4"

        super().__init__(*args, **kwargs)

    def url(self, name, parameters=None, expire=None):
        signed_url = super().url(name, parameters, expire=3600)
        parsed_url = urlparse(signed_url)
        external_netloc = urlparse(self.public_url).netloc
        signed_url = urlunparse(parsed_url._replace(netloc=external_netloc))

        return signed_url


class CustomFileField(models.FileField):
    """
    A custom FileField that supports dynamic S3 storage.
    """

    def __init__(self, *args, storage_category, **kwargs):
        self.storage_category = storage_category
        # Don't set storage in __init__
        kwargs.pop("storage", None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """
        Handle field deconstruction for migrations
        """
        name, path, args, kwargs = super().deconstruct()
        kwargs["storage_category"] = self.storage_category
        return name, path, args, kwargs

    def pre_save(self, instance, add):
        """
        Ensure correct storage is set before save operations
        """
        if not hasattr(instance, "workspace_id"):
            raise ValueError("Workspace ID is required to use CustomFileField")
        self.storage = CustomS3Boto3Storage(
            workspace_id=instance.workspace_id,
            storage_category=self.storage_category,
        )
        return super().pre_save(instance, add)


# TODO: Remove this once we can remove the old migrations
class CustomS3Boto3StorageDeprecated(S3Boto3Storage):
    def url(self, name, parameters=None, expire=None):
        client_config = {
            "aws_access_key_id": settings.AWS_S3_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_S3_SECRET_ACCESS_KEY,
            "endpoint_url": settings.AWS_S3_ENDPOINT_URL,
        }
        if region := os.getenv("AWS_S3_REGION_NAME"):
            client_config["region_name"] = region
        if not os.getenv("LOCAL_S3", "false") == "true":
            client_config["config"] = boto3.session.Config(signature_version="s3v4")
        s3_client = boto3.client("s3", **client_config)
        params = {"Bucket": self.bucket_name, "Key": name}
        if expire:
            params["Expires"] = expire
        signed_url = s3_client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=3600
        )

        parsed_url = urlparse(signed_url)
        external_netloc = urlparse(settings.AWS_S3_PUBLIC_URL).netloc
        signed_url = urlunparse(parsed_url._replace(netloc=external_netloc))

        return signed_url
