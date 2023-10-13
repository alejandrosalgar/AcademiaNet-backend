import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Self, Tuple, Type, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from core_utils.boto3.rds import rds_execute_statement

T = TypeVar("T")


class InvalidFieldError(Exception):
    """Exception thrown when an invalid attribute is requested in a model"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InsertionError(Exception):
    """Exception thrown when a DB insertion fails"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class MissingConditionError(Exception):
    """Exception thrown when requesting data without a mandatory clause"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class MissingUpdateError(Exception):
    """Exception thrown when updating data without a SET clause"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


class CustomBaseModel(BaseModel):
    """Custom class to be extended from every Pydantic model.
    Adds audit data and functionality for updated attributes"""

    model_config = ConfigDict(validate_assignment=True)
    created_at: datetime | str = Field(default_factory=get_timestamp)
    updated_at: datetime | str | None = Field(default=None)
    created_by: str | None = Field(default=None)
    updated_by: str | None = Field(default=None)
    updated_attrs: List[str] = Field(default_factory=list, exclude=True)

    def __setattr__(self, name: str, value: Any) -> None:
        self.updated_attrs.append(name)
        return super().__setattr__(name, value)


class SQLBuilder:
    """Class to construct all SQL queries"""

    def __init__(self, native_query: str = "") -> None:
        self.query = native_query

    def select(self, table: str, select_query: List[str] | None = None) -> Self:
        columns = select_query if select_query is not None else "*"
        self.query += f"SELECT {', '.join(columns)} FROM {table} "
        return self

    def where(self, where_query: List[str] | None = None) -> Self:
        if where_query is None:
            where_query = []
        self.query += f"WHERE {' AND '.join(where_query)} "
        return self

    def limit(self, number_records: int = 1) -> Self:
        self.query += f"LIMIT {number_records} "
        return self

    def offset(self, number_records: int = 1) -> Self:
        self.query += f"OFFSET {number_records} "
        return self

    def count(self, table: str, count_column: str | None = None) -> Self:
        column = count_column if count_column is not None else "*"
        self.query += f"SELECT COUNT({column}) FROM {table} "
        return self

    def insert(self, table: str, list_keys: List[Tuple[str, type]]) -> Self:
        self.query += (
            f"INSERT INTO {table} ({', '.join([elmt[0] for elmt in list_keys])}) VALUES "
            f"""({', '.join([f":{column[0]}::VARCHAR[]" if column[1] is list
                             else f":{column[0]}" for column in list_keys])})"""
        )
        return self

    def on_conflict(self, on_conflict_column: str) -> Self:
        self.query += f"ON CONFLICT({on_conflict_column}) DO "
        return self

    def return_value(self, return_value: str) -> Self:
        self.query += f"RETURNING {return_value}"
        return self

    def update(self, table: str, update_values: List) -> Self:
        if not update_values:
            raise MissingUpdateError("No attribute changes provided")
        self.query += f"UPDATE {table} SET {', '.join(update_values)} "
        return self

    def order_by(self, order_by_query: str, order_method: Literal["ASC", "DESC"] = "ASC") -> Self:
        self.query += f"ORDER BY {order_by_query} {order_method}, created_at desc "
        return self

    def order_by_custom(self, order_by_list: List) -> Self:
        self.query += f"ORDER BY {', '.join(order_by_list)} "
        return self

    def group_by(self, values: List | None) -> Self:
        if values is None:
            values = []
        self.query += f"GROUP BY {', '.join(values)} "
        return self

    def inner_join(self, inner_join_query: str) -> Self:
        self.query += f"INNER JOIN {inner_join_query} "
        return self

    def left_join(self, left_join_query: str) -> Self:
        self.query += f"LEFT JOIN {left_join_query} "
        return self

    def right_join(self, right_join_query: str) -> Self:
        self.query += f"RIGHT JOIN {right_join_query} "
        return self

    def delete(self, delete_from: str, where_clause: List[str]) -> Self:
        if not where_clause:
            raise MissingConditionError("You must provide a WHERE clause to delete")
        self.query += f"DELETE FROM {delete_from} WHERE {' AND '.join(where_clause)} "
        return self


def get_value(value: Any) -> str:
    """Function maps Python types to RDS types

    Args:
        value (Any): Python attribute

    Returns:
        str: RDS data type
    """
    type_mapping = {
        str: "stringValue",
        int: "longValue",
        float: "doubleValue",
        bool: "booleanValue",
    }
    if isinstance(value, Enum):
        return type_mapping.get(type(value.value))

    return type_mapping.get(type(value), "stringValue")


def validate_uuid(possible_uuid: str) -> bool:
    """Function validates if a string is a valid UUID

    Args:
        possible_uuid (str): string to validate

    Returns:
        bool: Whether it's valid or not
    """
    try:
        _ = uuid.UUID(possible_uuid)
        return True
    except ValueError:
        return False


def validate_timestamp(timestamp_str: str, format_: str = "%Y-%m-%d %H:%M:%S.%f") -> bool:
    """Function validates if a string is a valid timestamp without time zone

    Args:
        timestamp_str (str): string to validate
        format_ (str, optional): timestamp format. Defaults to '%Y-%m-%dT%H:%M:%S.%f'.

    Returns:
        bool: Whether it's valid or not
    """
    try:
        _ = datetime.strptime(timestamp_str, format_)
        return True
    except ValueError:
        return False


def get_sql_parameters(**kwargs) -> List[Dict]:
    """Function returns the RDS parameters for the SQL statement
    Returns:
        List[Dict]: RDS parameters
    """
    parameters = []
    not_uuid = {"cognito_user_id", "follower_id", "followed_id"}
    for column, value in kwargs.items():
        value_type = get_value(value)
        param_value = {"name": column, "value": {value_type: value}}
        if isinstance(value, str) and column not in not_uuid and validate_uuid(value):
            param_value["typeHint"] = "UUID"
        elif isinstance(value, str) and validate_timestamp(value):
            param_value["typeHint"] = "TIMESTAMP"
        elif isinstance(value, list):
            param_value["value"]["stringValue"] = f"{{{', '.join(value)}}}"
        elif isinstance(value, Enum):
            param_value["value"][value_type] = value.value
        elif isinstance(value, uuid.UUID):
            param_value["value"]["stringValue"] = str(value)
            param_value["typeHint"] = "UUID"
        parameters.append(param_value)
    return parameters


class SQLOperator:
    """Utilitary class to perform CRUD operations for every model

    Raises:
        InvalidFieldError: If non-existent fields are passed to the select method
        MissingConditionError: If a WHERE clause is not provided in the select method
    """

    @staticmethod
    def _validate_fields(class_model: Type[T], fields) -> None:
        correct_fields = list(class_model.model_fields.keys())
        if not all(item in correct_fields for item in fields):
            raise InvalidFieldError(f"Field is not part of the model {class_model.__name__}")

    @staticmethod
    def select(
        class_model: Type[T],
        fields: List[str] = None,
        limit: int = 500,
        offset: int = 0,
        order_by: str | None = None,
        order_method: Literal["ASC", "DESC"] = "ASC",
        **kwargs,
    ) -> List[Dict]:
        """Returns data from the DB

        Args:
            class_model (Type['T']): Pydantic Model class
            fields (List[str], optional): columns to retrieve. Defaults to None.

        Raises:
            MissingConditionError: If no filters are provided for the WHERE clause

        Returns:
            List[Dict]: Data from the DB
        """
        if not kwargs:
            raise MissingConditionError("Select clauses should include filters")

        if fields is not None:
            SQLOperator._validate_fields(class_model, fields)

        parameters = get_sql_parameters(**kwargs)

        sql_statement = (
            SQLBuilder()
            .select(class_model.table, fields)
            .where([f"{column}=:{column}" for column in kwargs])
        )
        if order_by is None and offset > 0:
            raise MissingConditionError("You can't provide an offset without an ORDER BY clause")
        if order_by is not None:
            SQLOperator._validate_fields(class_model, [order_by])
            sql_statement = sql_statement.order_by(order_by, order_method)

        sql_statement = sql_statement.limit(limit).offset(offset)

        return rds_execute_statement(sql=sql_statement.query, parameters=parameters)

    @staticmethod
    def count_records(class_model: Type[T], column_name: str | None = None, **kwargs) -> int:
        """Function counts number of records in the DB

        Args:
            class_model (Type['T']): Pydantic Model for which we want to count
            column_name (str | None, optional): Column to count, if any. Defaults to None.

        Returns:
            int: Count value
        """
        if not kwargs:
            kwargs = {"1": "1"}
        sql_statement = (
            SQLBuilder()
            .count(class_model.table, column_name)
            .where([f"{column}='{value}'" for column, value in kwargs.items()])
            .query
        )
        count = rds_execute_statement(sql=sql_statement)
        return count["records"][0][0].get("longValue")

    @staticmethod
    def select_model(
        class_model: Type[T],
        limit: int = 500,
        offset: int = 0,
        order_by: str | None = None,
        order_method: Literal["ASC", "DESC"] = "ASC",
        **kwargs,
    ) -> List[T]:
        """Returns list of Pydantic objects. Similar to 'select' method but returns objects
            instead of JSONs

        Args:
            class_model (Type['T']): Pydantic Model class

        Raises:
            MissingConditionError: If no filters are provided for the WHERE clause

        Returns:
            List['T']: List of Pydantic objects
        """
        if not kwargs:
            raise MissingConditionError("Select clauses should include filters")

        parameters = get_sql_parameters(**kwargs)

        sql_statement = (
            SQLBuilder()
            .select(class_model.table)
            .where([f"{column}=:{column}" for column in kwargs])
        )
        if order_by is None and offset > 0:
            raise MissingConditionError("You can't provide an offset without an ORDER BY clause")
        if order_by is not None:
            SQLOperator._validate_fields(class_model, [order_by])
            sql_statement = sql_statement.order_by(order_by, order_method)

        sql_statement = sql_statement.limit(limit).offset(offset)

        result = rds_execute_statement(sql=sql_statement.query, parameters=parameters)
        return [class_model(**obj) for obj in result]

    @staticmethod
    def insert(pydantic_obj) -> str | None:
        """Inserts a record to the DB

        Args:
            pydantic_obj (_type_): Pydantic object

        Returns:
            str | None: Inserted record's primary key or None for composite keys
        """
        dump = pydantic_obj.model_dump(mode="json", exclude_none=True)

        sql_statement = (
            SQLBuilder()
            .insert(
                pydantic_obj.__class__.table,
                [(key, type(dump[key])) for key in pydantic_obj.model_fields if key in dump],
            )
            .query
        )

        parameters = get_sql_parameters(**dump)

        response = rds_execute_statement(sql=sql_statement, parameters=parameters)
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise InsertionError(f"There was an error inserting {pydantic_obj}")
        if isinstance(pydantic_obj.__class__.primary_key, str):
            return getattr(pydantic_obj, pydantic_obj.__class__.primary_key)
        return None

    @staticmethod
    def update(pydantic_obj) -> None:
        """Receives a Pydantic object with modified attributes and updates the
        corresponding record in the DB
        """
        pydantic_obj.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        if isinstance(pydantic_obj.primary_key, (tuple, list)):
            return SQLOperator.__update_composite(pydantic_obj)

        class_model = pydantic_obj.__class__
        obj_pk_name = getattr(pydantic_obj, "primary_key")
        parameter_dict = {attr: getattr(pydantic_obj, attr) for attr in pydantic_obj.updated_attrs}

        parameters = get_sql_parameters(**parameter_dict)

        sql_statement = (
            SQLBuilder()
            .update(
                class_model.table,
                [f"{updated_attr}=:{updated_attr}" for updated_attr in pydantic_obj.updated_attrs],
            )
            .where(
                [
                    f"{class_model.table}.{class_model.primary_key}="
                    f"""'{getattr(pydantic_obj, obj_pk_name)}'"""
                ]
            )
            .query
        )
        rds_execute_statement(sql=sql_statement, parameters=parameters)
        return None

    @staticmethod
    def __update_composite(pydantic_obj) -> None:
        """
        Receives a Pydantic object from a model with a composite PK
        with modified attributes and updates the
        corresponding record in the DB
        """
        class_model = pydantic_obj.__class__
        obj_composite_pk = getattr(pydantic_obj, "primary_key")
        parameter_dict = {attr: getattr(pydantic_obj, attr) for attr in pydantic_obj.updated_attrs}
        parameters = get_sql_parameters(**parameter_dict)

        sql_statement = (
            SQLBuilder()
            .update(
                class_model.table,
                [f"{updated_attr}=:{updated_attr}" for updated_attr in pydantic_obj.updated_attrs],
            )
            .where(
                [
                    f"{class_model.table}.{fk}='{getattr(pydantic_obj, fk)}'"
                    for fk in obj_composite_pk
                ]
            )
            .query
        )

        rds_execute_statement(sql=sql_statement, parameters=parameters)

    @staticmethod
    def delete(pydantic_obj) -> None:
        """
        Receives a Pydantic object and deletes the record from the DB using the object's PK
        """
        if isinstance(pydantic_obj.primary_key, (tuple, list)):
            return SQLOperator.__delete_composite(pydantic_obj)

        class_model = pydantic_obj.__class__
        obj_pk_name = getattr(pydantic_obj, "primary_key")
        sql_statement = (
            SQLBuilder()
            .delete(
                class_model.table,
                [
                    f"{class_model.table}.{class_model.primary_key}="
                    f"""'{getattr(pydantic_obj, obj_pk_name)}'"""
                ],
            )
            .query
        )
        rds_execute_statement(sql=sql_statement)
        return None

    @staticmethod
    def __delete_composite(pydantic_obj) -> None:
        """
        Receives a Pydantic object and deletes the record from the DB using the object's
        composite PK
        """
        class_model = pydantic_obj.__class__
        obj_composite_pk = getattr(pydantic_obj, "primary_key")
        sql_statement = (
            SQLBuilder()
            .delete(
                class_model.table,
                [
                    f"{class_model.table}.{fk}='{getattr(pydantic_obj, fk)}'"
                    for fk in obj_composite_pk
                ],
            )
            .query
        )
        rds_execute_statement(sql=sql_statement)
