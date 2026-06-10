from schemas.exceptions import InvalidArgumentException
from logging_config import logger


def validate_channel_data(channel_name: str, channel_price: str):
    """Validates the provided channel data, raising an appropriate exception if invalid.

    Raises InvalidArgumentException with user-friendly error message if any data is invalid.
    """
    # Check values are not empty and do not exceed data table limitations
    if not channel_name or len(channel_name) > 100:
        error_message = f"Channel Name {channel_name} is invalid"
        logger.warning(error_message)
        raise InvalidArgumentException(error_message)
    if not channel_price or len(channel_price) > 20:
        error_message = f"Channel Price {channel_price} is invalid"
        logger.warning(error_message)
        raise InvalidArgumentException(error_message)

    # Check price value is valid
    try:
        price_as_float = float(channel_price)
        if price_as_float < 0:
            error_message = f"Channel Price {channel_price} must be positive"
            logger.warning(error_message)
            raise InvalidArgumentException(error_message)

        if round(price_as_float, 2) != price_as_float:
            error_message = f"Channel Price {channel_price} must contain two decimal places at most"
            logger.warning(error_message)
            raise InvalidArgumentException(error_message)
    except ValueError:
        error_message = f"Channel Price {channel_price} is not a valid number"
        logger.warning(error_message)
        raise InvalidArgumentException(error_message)


def validate_user_data(username: str, password: str):
    """Validates the provided user data based on NIST guidelines, raising an appropriate exception if invalid.

    Raises InvalidArgumentException with user-friendly error message if any data is invalid.
    """
    if not username or len(username) > 20:
        error_message = f"Username is invalid"
        logger.warning(error_message)
        raise InvalidArgumentException(error_message)
    if not password or len(password) < 15:
        error_message = "Password must be at least 15 characters"
        logger.warning(error_message)
        raise InvalidArgumentException(error_message)
