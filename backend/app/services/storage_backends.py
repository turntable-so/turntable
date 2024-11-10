import os
from urllib.parse import urlparse, urlunparse

import boto3
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    bucket_name = "public-assets"
    default_acl = "public-read"
    file_overwrite = False
    custom_domain = False


class CustomS3Boto3Storage(S3Boto3Storage):
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
