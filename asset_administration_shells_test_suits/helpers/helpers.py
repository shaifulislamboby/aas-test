import base64
from functools import wraps
from urllib import parse
import re


def convert_to_base64_form(submodel_identifier: str) -> base64:
    _bytes = submodel_identifier.encode("ascii")
    base64_bytes = base64.b64encode(_bytes)
    return base64_bytes.decode("ascii")


def create_url_encoded_from_id(id_short_path: str) -> str:
    return parse.quote(id_short_path)


def convert_camel_case_to_snake_case(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def aas_logger(original_function):
    """
    Logging decorator function for logging, how the function has been used.
    """
    import logging

    logging.basicConfig(
        filename=f"{original_function.__name__}.log", level=logging.INFO
    )

    @wraps(original_function)
    def wrapper(*args, **kwargs):
        logging.info(f"Ran with args: {args}, and kwargs: {kwargs}")
        return original_function(*args, **kwargs)

    return wrapper
