def format_audit(data: list):
    for row in data:
        row["audit_data"] = {
            "created": {
                "created_by_user_id": row.pop("created_by"),
                "created_by_user_name": row.pop("created_by_user_name"),
                "created_at": row.pop("created_at"),
            },
            "updated": {
                "updated_by_user_id": row.pop("updated_by"),
                "updated_by_user_name": row.pop("updated_by_user_name"),
                "updated_at": row.pop("updated_at"),
            },
        }


def format_for_rds(value) -> str:
    if value is None or value == "":
        return "NULL"
    elif isinstance(value, str) and value != "NOW()":
        parsed_value = parse_str_characters(value)
        return f"'{parsed_value}'"
    else:
        return f"{value}"


def _check_str_characters(value: str) -> bool:
    if "'" in value:
        return True
    return False


def parse_str_characters(value: str) -> str:
    if _check_str_characters(value):
        return value.replace(r"'", r"''")
    return value


def parse_insert_data_rds(data: dict) -> dict:
    return {key: format_for_rds(value) for key, value in data.items()}


def parse_rds_list_to_str(records: list) -> str:
    return ", ".join(f"'{w}'" for w in records)


def parse_batch_values_data_rds(records: list) -> list:
    return [list(parse_insert_data_rds(data).values()) for data in records]


def parse_update_data_rds(data: dict) -> list:
    return [f"{key} = {format_for_rds(value)}" for key, value in data.items()]


def parse_update_sum_data_rds(data: dict) -> list:
    return [f"{key} = {key} + {format_for_rds(value)}" for key, value in data.items()]
