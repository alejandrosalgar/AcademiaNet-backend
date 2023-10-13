import uuid


def is_uuid_valid(value) -> bool:
    try:
        uuid.UUID(str(value))
    except Exception:
        return False
    return True
