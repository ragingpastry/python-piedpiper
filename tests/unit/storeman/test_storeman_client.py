from piperci.storeman.client import storage_client

from minio import Minio
import os
import pytest


def test_storage_client():
    storecli = storage_client(
        storage_type="minio", hostname="localhost", access_key="1234", secret_key="1234"
    )

    assert isinstance(storecli.storage_client, Minio)


def test_storage_client_not_supported():
    with pytest.raises(NotImplementedError):
        storage_client(storage_type="not_implemented")


def test_stat_file(minio_server, minio_bucket_with_files):
    storecli = storage_client(
        storage_type="minio",
        hostname=minio_server,
        access_key="MINIO_TEST_ACCESS",
        secret_key="MINIO_TEST_SECRET",
    )
    bucket = minio_bucket_with_files
    assert len(list(storecli.stat_file(bucket)))


def test_download_file(minio_server, minio_bucket_with_files, tmp_path):
    storecli = storage_client(
        storage_type="minio",
        hostname=minio_server,
        access_key="MINIO_TEST_ACCESS",
        secret_key="MINIO_TEST_SECRET",
    )
    bucket = minio_bucket_with_files
    uri = f"minio://172.17.0.1:8089/{bucket}/test"
    storecli.download_file(uri, os.path.join(tmp_path, "test.txt"))
    assert os.path.isfile(os.path.join(tmp_path, "test.txt"))


def test_download_file_invalid_scheme():
    storecli = storage_client(
        storage_type="minio",
        hostname='test',
        access_key="MINIO_TEST_ACCESS",
        secret_key="MINIO_TEST_SECRET",
    )
    uri = f"http://172.17.0.1:8089/test/test"
    with pytest.raises(ValueError):
        storecli.download_file(uri, 'test')


def test_upload_file(minio_server, tmp_path):
    with open(os.path.join(tmp_path, "test.txt"), "w") as f:
        f.write("test")
    storecli = storage_client(
        storage_type="minio",
        hostname=minio_server,
        access_key="MINIO_TEST_ACCESS",
        secret_key="MINIO_TEST_SECRET",
    )
    storecli.upload_file(
        "testbucket", "test_object", os.path.join(tmp_path, "test.txt")
    )

    assert len(list(storecli.stat_file("testbucket", prefix="test_object")))


def test_upload_file_bucket_exists(minio_server, minio_bucket_with_files, tmp_path):
    with open(os.path.join(tmp_path, "test.txt"), "w") as f:
        f.write("test")
    storecli = storage_client(
        storage_type="minio",
        hostname=minio_server,
        access_key="MINIO_TEST_ACCESS",
        secret_key="MINIO_TEST_SECRET",
    )
    bucket = minio_bucket_with_files
    storecli.upload_file(bucket, "testfile", os.path.join(tmp_path, "test.txt"))

    assert len(list(storecli.stat_file("testbucket", prefix="test_object")))
