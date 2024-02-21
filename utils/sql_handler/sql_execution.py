from core_utils.boto3_utils.rds import RdsClient
from core_utils.sql_handler.sql_manager import SqlContext


def create_sql_context(rds_client):
    return SqlContext(rds_client)


rds_client_instance = RdsClient()
sql_context = create_sql_context(rds_client_instance)
