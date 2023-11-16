import os
import re
import traceback
import urllib.parse as parse

from core_utils.boto3_utils.s3 import S3_CLIENT, S3_RESOURCE
from core_utils.boto3_utils.constants import TENANTS_BUCKET
from core_utils.sql_handler.sql_builder import SQLBuilder

TEMPLATE_REGEX = r"{{(.+?)}}"
URL = os.environ["CLOUD_FRONT_URL"]
COMPANY = os.environ["COMPANY"]
URL_COMPANY = os.environ["URL_COMPANY"]
LOGO = os.environ["LOGO"]
STAGE = os.environ["STAGE"]
PROJECT = os.environ["PROJECT"]
LOCATION_PATH = os.path.dirname(__file__)
TENANT_NAME = ""
CONTACT_EMAIL = ""
USER_FULL_NAME = ""


def table_exists(table_name: str) -> bool:
    sql = f"""SELECT EXISTS(
                SELECT *
                 FROM information_schema.tables
                 WHERE
                 table_schema = 'public' AND
                 table_name = '{table_name}'
            );"""
    result = SQLBuilder(sql).execute()[0]["exists"]
    return result


def get_tenant_details(tenant_id: str) -> tuple:
    support_email, logo_path = "", "neostella/logos/logo_light.png"

    # Get support email
    if table_exists("tenant_configuration"):
        sql = f"SELECT * FROM tenant_configuration WHERE tenant_id = '{tenant_id}'"
        tenant_configuration = SQLBuilder(sql).execute("tenant_configuration", False)
        if len(tenant_configuration):
            support_email = tenant_configuration[0]["support_email"]

    # Get logo
    if table_exists("tenant_logos") and table_exists("logos"):
        sql = f"""SELECT tl.*, l.logo_path FROM tenant_logos tl LEFT JOIN logos l
         ON tl.logo_id = l.logo_id WHERE tl.tenant_id = '{tenant_id}' AND tl.logo_type = 'light'"""
        result = SQLBuilder(sql).execute("tenant_logos", False)
        if len(result):
            logo_path = result[0]["logo_path"]

    return support_email, logo_path


def build_html(replace_values, template):
    def replace_condition(m):
        return replace_values[m[1]]

    return re.sub(TEMPLATE_REGEX, replace_condition, template)


def bucket_file_read(path):
    try:
        template_file = (
            S3_RESOURCE.Object(TENANTS_BUCKET, path).get()["Body"].read().decode("utf-8")
        )
        return template_file
    except Exception as e:
        # Something else has gone wrong.
        raise Exception(f"Error while bucket read {str(e)}")


def generate_html_email(
    email, code_parameter, template_file, auth_url: str = "", cognito_user_id: str = ""
):
    custom_template_path = "assets_common/email_templates/" + template_file
    template_file = bucket_file_read(custom_template_path)
    unsubscribe_url = _parse_unsubscribe_url(cognito_user_id, TENANT_NAME)
    replace_values = {
        "username": email,
        "password": code_parameter,
        "url": URL,
        "auth_url": auth_url,
        "stage": STAGE,
        "project": PROJECT,
        "company": COMPANY,
        "url_company": URL_COMPANY,
        "logo": LOGO,
        "tenant_name": TENANT_NAME,
        "contact_email": CONTACT_EMAIL,
        "full_name": USER_FULL_NAME,
        "url_unsubscribe": unsubscribe_url,
        "tenant_address": "",
        "tenant_phone_number": "",
    }

    return build_html(replace_values, template_file)


def _parse_auth_url(base_url: str, email: str, password: str) -> str:
    url = base_url
    parsed_email = parse.quote(email)
    if base_url.endswith("/"):
        url = base_url[:-1]
    return f"{url}/auth/user-activation?user={parsed_email}&token={password}"


def add_subdomain_to_url(tenant_data: dict):
    globals()["URL"] = os.environ["CLOUD_FRONT_URL"]
    subdomain = ""
    if "subdomain" not in tenant_data:
        subdomain = ""
    elif tenant_data["subdomain"] is None:
        subdomain = ""
    else:
        subdomain = tenant_data["subdomain"] + "."

    url_split = URL.split("/")
    url_split[2] = f"{subdomain}{url_split[2]}"
    globals()["URL"] = "/".join(url_split)


def set_tenant_fields(user_pool_id: str):
    sql = f"SELECT * FROM tenants_master WHERE user_pool_id = '{user_pool_id}'"
    tenant_data = SQLBuilder(sql).execute("tenants_master")[0]
    add_subdomain_to_url(tenant_data)
    if tenant_data.get("tenant_name"):
        globals()["TENANT_NAME"] = tenant_data.get("tenant_name")
    if tenant_data.get("admin_email"):
        globals()["CONTACT_EMAIL"] = tenant_data.get("admin_email")
    tenant_id = tenant_data.get("tenant_id")

    try:
        support_email, logo_path = get_tenant_details(tenant_id)
        logo_path = "public/" + logo_path
        globals()["CONTACT_EMAIL"] = support_email
        globals()["LOGO"] = S3_CLIENT.generate_presigned_url(
            "get_object", Params={"Bucket": TENANTS_BUCKET, "Key": logo_path}, ExpiresIn=3600
        )
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


def set_user_fields(event: dict) -> None:
    globals()["USER_FULL_NAME"] = event["request"]["userAttributes"].get("name")


def _parse_unsubscribe_url(user_id: str, tenant_name: str) -> str:
    parsed_tenant_name = parse.quote(tenant_name.replace("'", ""))
    url = URL
    if url.endswith("/"):
        url = url[:-1]
    return f"{url}/email-unsubscription?t={parsed_tenant_name}&c={user_id}"


def lambda_handler(event, context):
    user_pool_id = event["userPoolId"]
    cognito_user_id = event["userName"]
    set_tenant_fields(cognito_user_id, user_pool_id)
    set_user_fields(event)
    action = event["triggerSource"]
    email = event["request"]["userAttributes"]["email"]
    code_parameter = event["request"]["codeParameter"]
    if action == "CustomMessage_AdminCreateUser":
        normal_email = email
        email = event["request"]["usernameParameter"]
        auth_url = _parse_auth_url(URL, normal_email, code_parameter)
        rendered_html = generate_html_email(
            email, code_parameter, "user_creation.html", auth_url, cognito_user_id
        )
        message_response = rendered_html
        subject = f"You've been invited to join {TENANT_NAME}'s client portal"
    if action == "CustomMessage_ForgotPassword":
        rendered_html = generate_html_email(
            email, code_parameter, "forgot_password.html", cognito_user_id=cognito_user_id
        )
        message_response = rendered_html
        subject = "Instructions for Resetting Your Client Portal Password"

    event["response"]["emailMessage"] = message_response
    event["response"]["emailSubject"] = subject

    return event
