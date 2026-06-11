from schemas.exceptions import InvalidArgumentException
from logging_config import logger


def validate_channel_data(channel_name: str, channel_price: str):
    """Validates the provided channel data, raising an appropriate exception if invalid.

    Raises InvalidArgumentException with user-friendly error message if any data is invalid.
    """
    error_message = ""

    if not channel_name:
        error_message = "Channel name cannot be blank"
    elif len(channel_name) > 100:
        error_message = "Channel name must be 100 characters or fewer"
    elif channel_name != channel_name.strip():
        error_message = "Channel name may not use a space as the first or last character"

    elif not channel_price:
        error_message = "Channel price cannot be blank"
    elif len(channel_price) > 20:
        error_message = "Channel price must be 20 characters or fewer"
    else:
        try:
            price_as_float = float(channel_price)
            if price_as_float < 0:
                error_message = "Channel price must be a positive value"
            elif round(price_as_float, 2) != price_as_float:
                error_message = "Channel price must contain two decimal places at most"
        except ValueError:
            error_message = "Channel price must be a valid number"

    if error_message != "":
        logger.warning(f"Channel validation failed: {error_message}")
        raise InvalidArgumentException(error_message)


def validate_user_data(username: str, password: str):
    """Validates the provided user data based on NIST guidelines, raising an appropriate exception if invalid.

    Raises InvalidArgumentException with user-friendly error message if any data is invalid.
    """
    error_message = ""

    if not username:
        error_message = "Must enter a username"
    elif len(username) > 20:
        error_message = "Username must be 20 characters or fewer"
    elif not username.replace("_", "").replace("-", "").isalnum():
        error_message = "Username may only contain letters, numbers, hyphens, and underscores"

    elif not password:
        error_message = "Must enter a password"
    elif len(password) < 15:
        error_message = "Password must be 15 characters or longer"
    elif password != password.strip():
        error_message = "Password may not use a space as the first or last character"

    if error_message != "":
        logger.warning(f"User validation failed: {error_message}")
        raise InvalidArgumentException(error_message)
