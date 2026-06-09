import logging

from schemas.constants import LOG_MESSAGE_FORMAT

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_MESSAGE_FORMAT
)
logger = logging.getLogger(__name__)
