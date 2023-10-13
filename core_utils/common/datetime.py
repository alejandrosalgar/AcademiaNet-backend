from datetime import datetime


def parse_plain_datetime(time) -> datetime:
    if isinstance(time, datetime):
        return datetime.now().replace(second=0, microsecond=0)
    return datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
