from piedpiper.storeman.client import BaseStorageClient

from minio import Minio
from minio.error import BucketAlreadyOwnedByYou, BucketAlreadyExists
from urllib.parse import urlparse


class MinioClient(BaseStorageClient):
    def __init__(self, *args, **kwargs):
        hostname = kwargs.get("hostname")
        access_key = kwargs.get("access_key")
        secret_key = kwargs.get("secret_key")
        self.storage_client = Minio(
            hostname, access_key=access_key, secret_key=secret_key, secure=False
        )

    def stat_file(self, bucket_name, prefix=None, recursive=False):
        return self.storage_client.list_objects(
            bucket_name, prefix=prefix, recursive=recursive
        )

    def download_file(self, uri, file_path):
        scheme = urlparse(uri).scheme
        if scheme != "minio":
            raise ValueError(f"Unknown URI scheme: {scheme}")
        bucket_name = urlparse(uri).path.split("/")[1]
        object_name = "".join(urlparse(uri).path.split("/")[2:])

        return self.storage_client.fget_object(bucket_name, object_name, file_path)

    def upload_file(self, bucket_name, object_name, file_path):
        try:
            self.storage_client.make_bucket(bucket_name)
        except (BucketAlreadyExists, BucketAlreadyOwnedByYou):
            pass
        self.storage_client.fput_object(bucket_name, object_name, file_path)
        return self.storage_client.stat_object(bucket_name, object_name)
