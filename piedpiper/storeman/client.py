from abc import ABC, abstractmethod


def storage_client(storage_type, **kwargs):
    if storage_type == "minio":
        from piedpiper.storeman.minio_client import MinioClient

        return MinioClient(**kwargs)
    else:
        raise NotImplementedError("Only minio is supported at the moment.")


class BaseStorageClient(ABC):
    @abstractmethod
    def stat_file(self, bucket_name, prefix=None, recursive=False):
        """
        Return information on the specified files
        :param bucket_name:
        :param prefix:
        :param recursive:
        :return:
        """

    @abstractmethod
    def download_file():
        """
        Downloads a file to a given location.
        :param bucket_name:
        :param object_name:
        :param file_path:
        :return:
        """

    @abstractmethod
    def upload_file(self, bucket_name, object_name, file_path):
        """
        Uploads a file to a given bucket with a given object_name
        :param bucket_name:
        :param object_name:
        :param file_path:
        :return:
        """
