import os

import boto3

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
REGION_NAME = os.getenv("REGION_NAME", None)
PROFILE = os.getenv("PROFILE", None)
ENV_PATH = "aws_data.env"
DATABASE_NAME = os.getenv("DATABASE_NAME", None)
DB_CLUSTER_ARN = os.getenv("DB_CLUSTER_ARN", None)
CORALOGIX_SECRETS = os.getenv("CORALOGIX_SECRET", None)
SERVICE_NAME = os.getenv("SERVICE_NAME", "")
RESOURCE_METHOD = os.getenv("RESOURCE_METHOD", None)
APPKEY_SECRET_ARN = os.getenv("APPKEY_SECRET_ARN", None)
DB_CREDENTIALS_SECRETS_STORE_ARN = os.getenv("DB_CREDENTIALS_SECRETS_STORE_ARN", None)
EVENTS_ARN = os.getenv("SNS_ARN", None)


if os.path.exists(ENV_PATH):
    __import__("dotenv").load_dotenv(ENV_PATH, override=True)
    if AWS_ACCESS_KEY_ID is not None:
        boto3.setup_default_session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=REGION_NAME,
        )
    else:
        boto3.setup_default_session(profile_name=PROFILE, region_name=REGION_NAME)


COGNITO_CLIENT = boto3.client("cognito-idp", region_name=REGION_NAME)
RDS_CLIENT = boto3.client("rds-data", region_name=REGION_NAME)
LAMBDA_CLIENT = boto3.client("lambda", region_name=REGION_NAME)
SECRETS_MANAGER_CLIENT = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)
DYNAMO_RESOURCE = boto3.resource("dynamodb", region_name=REGION_NAME)
DYNAMO_CLIENT = boto3.client("dynamodb", region_name=REGION_NAME)
SNS_CLIENT = boto3.client("sns", region_name=REGION_NAME)
S3_RESOURCE = boto3.resource("s3", region_name=REGION_NAME)
S3_CLIENT = boto3.client("s3", region_name=REGION_NAME)
SQS_CLIENT = boto3.client("sqs", REGION_NAME)
STS_CLIENT = boto3.client("sts")


def set_database_globals(
    database=os.getenv("DATABASE_NAME", None),
    resource_arn=os.getenv("DB_CLUSTER_ARN", None),
    secret_arn=os.getenv("DB_CREDENTIALS_SECRETS_STORE_ARN", None),
):
    global DATABASE_NAME, DB_CLUSTER_ARN, DB_CREDENTIALS_SECRETS_STORE_ARN
    DATABASE_NAME = database
    DB_CLUSTER_ARN = resource_arn
    DB_CREDENTIALS_SECRETS_STORE_ARN = secret_arn
