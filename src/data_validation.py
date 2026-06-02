from schemas.exceptions import InvalidArgumentException
from logging_config import logger


def validate_channel_data(channel_name: str, channel_price: str):
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
