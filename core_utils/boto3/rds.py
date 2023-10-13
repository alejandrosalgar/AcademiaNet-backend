import json
from typing import Dict, List

from botocore.exceptions import ClientError

from core_utils.boto3.constants import (
    DATABASE_NAME,
    DB_CLUSTER_ARN,
    DB_CREDENTIALS_SECRETS_STORE_ARN,
    RDS_CLIENT,
)

TRANSACTION_ID = None


def set_transaction_id(transaction_id: None):
    global TRANSACTION_ID
    TRANSACTION_ID = transaction_id


class RDSException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def begin_transaction(
    database: str = None,
    resource_arn: str = None,
    secret_arn: str = None,
) -> list:
    # TODO: logging
    try:
        if None in [database, resource_arn, secret_arn]:
            database, resource_arn, secret_arn = (
                DATABASE_NAME,
                DB_CLUSTER_ARN,
                DB_CREDENTIALS_SECRETS_STORE_ARN,
            )
        response = RDS_CLIENT.begin_transaction(
            database=database,
            resourceArn=resource_arn,
            secretArn=secret_arn,
        )
    except ClientError as e:
        # TODO: logging
        raise RDSException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise RDSException(
            "BeginTransactionException",
            f"Error during begin transaction function: {str(e)}",
        )
    set_transaction_id(response["transactionId"])


def commit_transaction(
    resource_arn: str = None,
    secret_arn: str = None,
    transaction_id: str = None,
):
    try:
        if None in [resource_arn, secret_arn]:
            resource_arn, secret_arn = (
                DB_CLUSTER_ARN,
                DB_CREDENTIALS_SECRETS_STORE_ARN,
            )
        if transaction_id is None:
            transaction_id = TRANSACTION_ID
        RDS_CLIENT.commit_transaction(
            resourceArn=resource_arn,
            secretArn=secret_arn,
            transactionId=transaction_id,
        )
    except ClientError as e:
        # TODO: logging
        raise RDSException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise RDSException(
            "CommitTransactionException",
            f"Error during commit transaction function {str(e)}",
        )
    set_transaction_id(None)


def rollback_transaction(
    resource_arn: str = None,
    secret_arn: str = None,
    transaction_id: str = None,
):
    try:
        if None in [resource_arn, secret_arn]:
            resource_arn, secret_arn = (
                DB_CLUSTER_ARN,
                DB_CREDENTIALS_SECRETS_STORE_ARN,
            )
        if transaction_id is None:
            transaction_id = TRANSACTION_ID

        RDS_CLIENT.rollback_transaction(
            resourceArn=resource_arn,
            secretArn=secret_arn,
            transactionId=transaction_id,
        )
    except ClientError as e:
        # TODO: logging
        raise RDSException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise RDSException(
            "RollbackTransactionException",
            f"Error during execution of the excecute statement function: {str(e)}",
        )
    set_transaction_id(None)


def rds_execute_statement(
    params: List[Dict],
    sql: str,
    database: str = None,
    resource_arn: str = None,
    secret_arn: str = None,
    transaction_id: str = None,
) -> list:
    # TODO: logging
    try:
        if None in [database, resource_arn, secret_arn]:
            database, resource_arn, secret_arn = (
                DATABASE_NAME,
                DB_CLUSTER_ARN,
                DB_CREDENTIALS_SECRETS_STORE_ARN,
            )

        execute_statement_params = {
            "secretArn": secret_arn,
            "database": database,
            "resourceArn": resource_arn,
            "parameters": params,
            "sql": sql,
            "includeResultMetadata": True,
        }
        if TRANSACTION_ID is not None and transaction_id is None:
            params["transactionId"] = TRANSACTION_ID
        elif transaction_id is not None:
            params["transactionId"] = transaction_id

        response = deserialize_rds_response(
            RDS_CLIENT.execute_statement(**execute_statement_params)
        )
    except ClientError as e:
        # TODO: logging
        raise RDSException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise RDSException(
            "ExcecuteStatementException",
            f"Error during execution of the excecute statement function {str(e)}",
        )
    return response


def deserialize_rds_response(data: dict) -> list:
    """
    function to return a dictionary of attribute-value of RDS response in boto3
    """
    records = data.get("records", [])
    columns = data.get("columnMetadata", [])
    result = []
    for record in records:
        record_dict = {}
        col_count = 0
        for current_column in columns:
            attribute = current_column["name"]
            key = list(record[col_count].keys())[0]
            value = list(record[col_count].values())[0]
            if key in ["booleanValue", "doubleValue", "longValue"]:
                record_dict[attribute] = value
            elif key == "stringValue":
                # Check if it is a json as a string or only a string
                try:
                    json_value = json.loads(value)
                    record_dict[attribute] = (
                        str(json_value)
                        if (isinstance(json_value, int) or isinstance(json_value, float))
                        else json_value
                    )
                except json.JSONDecodeError:
                    record_dict[attribute] = str(value)
            elif key == "arrayValue":
                record_dict[attribute] = list(value.values())[0]
            elif key == "isNull":
                record_dict[attribute] = None
            elif key == "blobValue":
                record_dict[attribute] = value
            col_count += 1

        result.append(record_dict)

    return result
