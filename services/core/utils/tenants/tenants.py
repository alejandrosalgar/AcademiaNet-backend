from utils.sql_handler.sql_execution import sql_context


def check_tenant_limit(table, tenant_id):
    limit_query = f"""SELECT object_limit FROM objects_master WHERE table_name = '{table}' 
        AND tenant_id = '{tenant_id}'"""
    limit = sql_context.exec(limit_query, {})[0]["object_limit"]
    user_len_query = (
        f"SELECT COUNT(*) from {table} WHERE tenant_id = '{tenant_id}' AND is_active = true"
    )
    user_len = sql_context.exec(user_len_query, {})[0]["count"]
    if limit == 0:
        return True
    if limit <= user_len:
        return False
    else:
        return True


def get_user_timezone(user_id: str) -> str:
    default_time_zone = "UTC"
    sql = f"SELECT time_zone FROM users_master WHERE cognito_user_id = '{user_id}'"
    time_zone_list = sql_context.exec(sql, {})

    if len(time_zone_list):
        return time_zone_list[0]["time_zone"]
    return default_time_zone
