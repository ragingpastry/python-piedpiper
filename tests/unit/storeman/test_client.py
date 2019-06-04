from minio.error import BucketAlreadyOwnedByYou, BucketAlreadyExists
import pytest
from piedpiper.storeman import client
from piedpiper.storeman.client import MinioClient


@pytest.fixture
def minio_storage_client():
    minio_client = client.init_storage_client(
        client_type="minio",
        url="test",
        access_key="1234",
        secret_key="1234",
        secure=False,
    )

    return minio_client


def test_storeman_client(minio_storage_client):
    assert isinstance(minio_storage_client, MinioClient)


def test_download_artifact(mocker, minio_storage_client):
    mock_fget = mocker.patch("piedpiper.storeman.client.Minio.fget_object")
    minio_storage_client.download_artifact("test", "test_obj", "/path")
    mock_fget.assert_called_with("test", "test_obj", "/path")


def test_minio_upload_artifact(mocker, minio_storage_client):
    mock_make_bucket = mocker.patch("piedpiper.storeman.client.Minio.make_bucket")
    mock_fput_object = mocker.patch("piedpiper.storeman.client.Minio.fput_object")
    mock_stat_object = mocker.patch("piedpiper.storeman.client.Minio.stat_object")

    minio_storage_client.upload_artifact("bucket", "object", "/path")

    mock_make_bucket.assert_called_once_with("bucket")
    mock_fput_object.assert_called_once_with("bucket", "object", "/path")
    mock_stat_object.assert_called_once_with("bucket", "object")


@pytest.mark.parametrize(
    "exceptions", [(BucketAlreadyOwnedByYou("test")), (BucketAlreadyExists("test"))]
)
def test_minio_upload_artifact_bucket_already_owned(
    mocker, minio_storage_client, exceptions
):
    mock_make_bucket = mocker.patch(
        "piedpiper.storeman.client.Minio.make_bucket", side_effect=exceptions
    )
    mock_fput_object = mocker.patch("piedpiper.storeman.client.Minio.fput_object")
    mock_stat_object = mocker.patch("piedpiper.storeman.client.Minio.stat_object")
    minio_storage_client.upload_artifact("bucket", "object", "/path")
    mock_make_bucket.assert_called_once_with("bucket")
    mock_fput_object.assert_called_once_with("bucket", "object", "/path")
    mock_stat_object.assert_called_once_with("bucket", "object")


class StubException(Exception):
    pass


def test_minio_upload_fails(mocker, minio_storage_client):
    mock_response_error = mocker.patch(
        "piedpiper.storeman.client.ResponseError", new_callable=lambda: StubException
    )
    mocker.patch("piedpiper.storeman.client.Minio.make_bucket")
    mocker.patch(
        "piedpiper.storeman.client.Minio.fput_object", side_effect=mock_response_error
    )
    mocker.patch("piedpiper.storeman.client.Minio.stat_object")
    with pytest.raises(mock_response_error):
        minio_storage_client.upload_artifact("bucket", "object", "/path")
