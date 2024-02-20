from utils.sql_handler.sql_execution import sql_context


def get_account_id(user_id):
    sql = f"SELECT account_id FROM users_master WHERE cognito_user_id = '{user_id}' "

    user_data = sql_context.exec(sql, {})
    if len(user_data):
        return user_data[0]["account_id"]
    else:
        return None
