from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists


def init_storage_client(client_type="minio", **kwargs):
    """
    Initializes and returns a storage client based on
    the client_type passed to the function.
    :param client_type: String that defines the client requested
    :param kwargs: Keyword args to pass to the init of client_type
    :return: storage client
    """
    if client_type == "minio":
        url = kwargs.get("url")
        access_key = kwargs.get("access_key")
        secret_key = kwargs.get("secret_key")
        secure = kwargs.get("secure", True)
        return MinioClient(url, access_key, secret_key, secure)


class MinioClient:
    """
    Wraps Minio python client to provide a common interface
    between different storage clients
    """

    def __init__(self, url, access_key, secret_key, secure):
        self.url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.storage_client = Minio(
            self.url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    def download_artifact(self, bucket_name, object_name, file_path):
        """
        Downloads an object from Minio
        :param bucket_name: Name of the bucket the object is in
        :param object_name: Name of the object to download
        :param file_path: Path to store the downloaded object
        :return: Minio Object
        """
        return self.storage_client.fget_object(bucket_name, object_name, file_path)

    def upload_artifact(self, bucket_name, object_name, file_path):
        """
        Uploads an object to Minio
        :param bucket_name: Name of the bucket to store the object
        :param object_name: Name given to the object once uploaded
        :param file_path: Path to the object on the local filesystem
        :return: Minio object representing the uploaded object
        """
        try:
            self.storage_client.make_bucket(bucket_name)
        except BucketAlreadyOwnedByYou:
            pass
        except BucketAlreadyExists:
            pass
        finally:
            try:
                self.storage_client.fput_object(bucket_name, object_name, file_path)
                return self.storage_client.stat_object(bucket_name, object_name)
            except ResponseError as e:
                message = f"Unable to upload artifact to {self.url}. \n\n{e}"
                raise ResponseError(message)
