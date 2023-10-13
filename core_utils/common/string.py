import random
import re
import string


def generate_temp_password() -> str:
    NUMBER_OF_CHARACTERS = 2
    characters = (
        random.choices(string.ascii_uppercase, k=NUMBER_OF_CHARACTERS)
        + random.choices(string.ascii_lowercase, k=NUMBER_OF_CHARACTERS)
        + random.choices(string.digits, k=NUMBER_OF_CHARACTERS)
        + random.choices(
            string.ascii_uppercase + string.digits + string.ascii_lowercase,
            k=NUMBER_OF_CHARACTERS,
        )
    )
    random.shuffle(characters)
    password = "".join(characters)
    return password


def parse_phone_number(raw_phone: str) -> str:
    if raw_phone.startswith("+") and len(raw_phone) == 12:
        return raw_phone
    elif len(raw_phone) == 10:
        return _get_country_code() + raw_phone
    return ""


def _get_country_code(country_code: str = "US") -> str:
    codes = {"US": "+1", "CA": "+1"}
    return codes.get(country_code, "+1")


def build_html(tenant_data: dict, template: str) -> str:
    TEMPLATE_REGEX = r"{{(.+?)}}"

    def replace_condition(m):
        return tenant_data[m[1]]

    return re.sub(TEMPLATE_REGEX, replace_condition, template)
