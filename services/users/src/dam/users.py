from core_utils.sql_handler.sql_operator import SQLOperator
from core_utils.sql_handler.sql_builder import SQLBuilder   
from core_utils.core_models.users import Users
from pydantic import BaseModel
from typing import Any
import uuid


def get_list(params: BaseModel, tenant_id: str = None) -> list[Users]:
    dict_params = params.model_dump(exclude_none=True)
    dict_params["tenant_id"] = tenant_id=uuid.UUID(tenant_id)
    dict_params["offset"] = dict_params.get("page") * dict_params.get("per_page")
    users: list[Users] = (
        SQLBuilder().
        select(Users.table).
        where(
            [
                f"{column}=:{column}" for column in params.model_dump(
                    include={"cognito_user_id", "account_id", "is_active"}, exclude_none=True
                    )
            ] + 
            [
                f"LOWER({column}) LIKE :{column}" for column in params.model_dump(
                    include={"full_name", "email"}, exclude_none=True
                    )
            ] +
            ["tenant_id = :tenant_id"]
        ).
        order_by("full_name").
        limit(":per_page").
        offset(":offset").
        execute(
            Users.table, 
            mandatory_result=False, 
            parameters=dict_params
        )

    )

    return users

def get_details(cognito_user_id:str = None) -> Users | None:
    user: Users = SQLOperator().select_model(Users, cognito_user_id=uuid.UUID(cognito_user_id))
    return user[0] if user else None

def insert(user_id:str = None, tenant_id:str = None, payload: dict[str, Any]=None) -> str:
    cognito_user_id = SQLOperator().insert(
        Users(created_by=uuid.UUID(user_id), tenant_id=uuid.UUID(tenant_id), **payload)
    )
    return cognito_user_id

def update(
    user:Users
):
    SQLOperator().update(user)