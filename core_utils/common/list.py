def flatten_dictionary(dictionary: dict) -> list:
    """Recursive function that flattens nested dictionaries."""

    keys = []

    for key, value in dictionary.items():
        if type(value) is dict:
            keys.extend(flatten_dictionary(value))
        else:
            keys.append(key)

    return keys
