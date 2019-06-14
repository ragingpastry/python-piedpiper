import pytest
from urllib.parse import urlparse


@pytest.fixture
def minio_server(s3_server):
    s3_server.kill()
    server_url = s3_server.boto_endpoint_url
    return urlparse(server_url).netloc


@pytest.fixture
def minio_bucket_with_files(s3_bucket):
    bucket = s3_bucket.name
    object = s3_bucket.client.Object(bucket, "test")
    object.put(Body="test")
    return bucket
