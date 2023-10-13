from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

from core_utils.boto3.constants import (
    CORALOGIX_KEY,
    DYNAMO_CLIENT,
    RESOURCE_METHOD,
    SERVICE_NAME,
)
from core_utils.constants import UUID
from core_utils.logging import send_to_coralogix


class DynamoDBException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def from_dynamodb_to_json(item):
    d = TypeDeserializer()
    return {k: d.deserialize(value=v) for k, v in item.items()}


def dynamo_query_operation(
    table_name: str,
    key_condition_expr: str,
    expr_attributes_values: dict,
    filter_expr: str,
    projection_expr: str = "",
    expression_attribute_names: dict = {},
    consistent_read: bool = True,
) -> list:
    """Query a DynamoDB table

    Args:
        table_name (str): DYNAMODB table name
        key_condition_expr (str): Key condition expression
        expr_attributes_values (dict): Key attribute values
        filter_expr (str): Filter
        projection_expr (str, optional): projection. Defaults to "".
        expression_attribute_names (dict, optional): Expression attributes. Defaults to {}.
        consistent_read (bool, optional): Consistent read. Defaults to True.

    Returns:
        list: Query result as a list
    """
    try:
        items = []
        kwargs = {
            "TableName": table_name,
            "KeyConditionExpression": key_condition_expr,
            "ExpressionAttributeValues": expr_attributes_values,
            "FilterExpression": filter_expr,
            "ConsistentRead": consistent_read,
        }
        if projection_expr:
            kwargs["ProjectionExpression"] = projection_expr
        if expression_attribute_names:
            kwargs["ExpressionAttributeNames"] = expression_attribute_names

        response = DYNAMO_CLIENT.query(**kwargs)
        items.extend(response["Items"])

        while response.get("LastEvaluatedKey", None):
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            response = DYNAMO_CLIENT.query(**kwargs)
            items.extend(response["Items"])

        items = list(map(lambda item: from_dynamodb_to_json(item), items))

        return items
    except ClientError as e:
        # TODO: logging
        raise DynamoDBException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise DynamoDBException(
            "DynamoQueryException", f"Error during dynamo query function: {str(e)}"
        )


def dynamo_execute_statement(query):
    try:
        send_to_coralogix(
            CORALOGIX_KEY, {"UUID": UUID, "Query string": query}, SERVICE_NAME, RESOURCE_METHOD, 3
        )
        response = DYNAMO_CLIENT.execute_statement(Statement=query)
        data = response["Items"]

        while "NextToken" in response:
            response = DYNAMO_CLIENT.execute_statement(
                Statement=query, NextToken=response["NextToken"]
            )
            data.extend(response["Items"])

        result = []
        for item in data:
            result.append(from_dynamodb_to_json(item))

        return result
    except ClientError as e:
        # TODO: logging
        raise DynamoDBException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise DynamoDBException(
            "DynamoExecuteStatementException",
            f"Error during dynamo execute statement function: {str(e)}",
        )
