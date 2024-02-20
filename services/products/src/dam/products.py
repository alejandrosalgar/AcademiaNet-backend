from core_utils.sql_handler.sql_operator import SQLOperator
from core_utils.sql_handler.sql_builder import SQLBuilder
from src.models.products import Products
from pydantic import BaseModel
from typing import Any
import uuid


def get_list(params: BaseModel, tenant_id: str = None) -> list[Products]:
    dict_params = params.model_dump(exclude_none=True)
    dict_params["tenant_id"] = tenant_id = uuid.UUID(tenant_id)
    dict_params["offset"] = dict_params.get("page") * dict_params.get("per_page")
    products: list[Products] = (
        SQLBuilder()
        .select(Products.table)
        .where(
            [
                f"{column}=:{column}"
                for column in params.model_dump(
                    include={"product_id", "is_active"}, exclude_none=True
                )
            ]
            + [
                f"LOWER({column}) LIKE :{column}"
                for column in params.model_dump(
                    include={"product_name"}, exclude_none=True
                )
            ]
            + ["tenant_id = :tenant_id"]
        )
        .order_by("product_name")
        .limit(":per_page")
        .offset(":offset")
        .execute(Products.table, mandatory_result=False, parameters=dict_params)
    )

    return products


def get_details(product_id: str = None) -> Products | None:
    product: Products = SQLOperator().select_model(
        Products, product_id=uuid.UUID(product_id)
    )
    return product[0] if product else None


def insert(product_id: str = None, tenant_id: str = None, payload: dict[str, Any] = None) -> str:
    product_id = SQLOperator().insert(
        Products(created_by=uuid.UUID(product_id), tenant_id=uuid.UUID(tenant_id), **payload)
    )
    return product_id


def update(product: Products):
    SQLOperator().update(product)
