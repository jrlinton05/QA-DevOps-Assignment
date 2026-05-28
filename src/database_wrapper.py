import os
import psycopg2
from dotenv import load_dotenv
from logging_config import logger
from schemas.constants import CREATE_USERS_TABLE, CREATE_CHANNELS_TABLE, GET_CHANNEL_DATA, GET_ALL_CHANNELS, \
    GET_ALL_CHANNEL_NAMES, ADD_CHANNEL
from schemas.exceptions import DatabaseConnectionException, InvalidArgumentException, NameAlreadyExistsException

connection = None


# --- Database Connection ---
def connect_to_db():
    global connection
    if connection is None:
        try:
            connection = psycopg2.connect(os.environ["DATABASE_URL"])
            logger.info("Connected to database successfully")
        except Exception as e:
            error_message = f"Failed to connect to database: {e}"
            logger.error(error_message)
            raise DatabaseConnectionException(error_message)


# --- Table Creation ---
def create_tables():
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
                cursor.execute(CREATE_CHANNELS_TABLE)
                logger.info("Create tables operation executed successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")


# --- Channel Table Read Methods ---
def get_channel_data(channel_id):
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_CHANNEL_DATA, (channel_id,))
                data = cursor.fetchone()
                if data is None:
                    logger.warning(f"No data found in table for channel_id: {channel_id}")
                    return None
                logger.info(
                    f"Returned data for channel_id {channel_id}: channel_name - {data[0]}, channel_price: {data[1]}")
                return data
    except Exception as e:
        logger.error(f"Failed to fetch channel data for channel_id {channel_id}: {e}")


def get_all_channels():
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_CHANNELS)
                data = cursor.fetchall()
                if not data:
                    logger.warning("No channels were found in the database")
                else:
                    logger.info(f"Found channels in the database: {data}")
                return data
    except Exception as e:
        logger.error(f"Failed to fetch channel data: {e}")


def get_all_channel_names():
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_CHANNEL_NAMES)
                data = [row[0] for row in cursor.fetchall()]
                if not data:
                    logger.warning("No channel names were found in the database")
                else:
                    logger.info(f"Found the following channel names in the database: {data}")
                return data
    except Exception as e:
        logger.error(f"Failed to fetch channel names: {e}")


# --- Channel Table Create Methods ---
def add_new_channel(channel_name, channel_price):
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

        formatted_price = f"{price_as_float:.2f}"
    except ValueError:
        error_message = f"Channel Price {channel_price} is not a valid number"
        logger.warning(error_message)
        raise InvalidArgumentException(error_message)

    # Check channel name not in use
    existing_channel_names = get_all_channel_names()
    if channel_name in existing_channel_names:
        raise NameAlreadyExistsException

    # Add channel to database
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(ADD_CHANNEL, (channel_name, formatted_price))
                logger.info(f"Added new channel with name: {channel_name} and price: {formatted_price}")
    except Exception as e:
        logger.error(f"Failed to add new channel name: {e}")


# --- Initialisation ---
load_dotenv()
