from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import boto3
from urllib.parse import urlparse, urlunparse

class PublicMediaStorage(S3Boto3Storage):
    bucket_name = 'public-assets'
    default_acl = 'public-read'
    file_overwrite = False
    custom_domain = False

class CustomS3Boto3Storage(S3Boto3Storage):

    def url(self, name, parameters=None, expire=None):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL
        )
        params = {'Bucket': self.bucket_name, 'Key': name}
        if expire:
            params['Expires'] = expire
        signed_url = s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
        
        parsed_url = urlparse(signed_url)
        external_netloc = urlparse(settings.AWS_S3_PUBLIC_URL).netloc
        signed_url = urlunparse(parsed_url._replace(netloc=external_netloc))
        
        return signed_url