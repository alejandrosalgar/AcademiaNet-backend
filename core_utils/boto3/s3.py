from botocore.exceptions import ClientError

from core_utils.boto3.constants import S3_CLIENT, S3_RESOURCE


class S3Exception(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def read_bucket_file(path: str, bucket: str) -> str:
    try:
        file = S3_RESOURCE.Object(bucket, path).get()["Body"].read().decode("utf-8")
        return file
    except ClientError as e:
        # TODO: logging
        raise S3Exception(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise S3Exception(
            "ReadBucketFileException",
            f"Error during read bucket file function excecution: {str(e)}",
        )


def get_s3_presigned_url(resource_path: str, bucket, expires_in_secs: int = 604800) -> str:
    try:
        return S3_CLIENT.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": resource_path}, ExpiresIn=expires_in_secs
        )
    except ClientError as e:
        # TODO: logging
        raise S3Exception(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise S3Exception(
            "GetPresignedURLException", f"Error during get presigned url function: {str(e)}"
        )


def get_s3_object(path: str, bucket: str):
    """Returns tje S3 document given path resource.
    Args:
        path (str): S3 bucket resource URL
    Raises:
        ValueError if the document was not found
    """
    try:
        object_file = S3_RESOURCE.Object(bucket, path).get()
        return object_file
    except ClientError as e:
        # TODO: logging
        raise S3Exception(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise S3Exception(
            "GetS3ObjectException",
            f"Error during get s3 object function excecution: {str(e)}",
        )
