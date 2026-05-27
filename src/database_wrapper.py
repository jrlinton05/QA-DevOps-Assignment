import os
import psycopg2
from dotenv import load_dotenv
from logging_config import logger
from schemas.constants import CREATE_USERS_TABLE, CREATE_CHANNELS_TABLE, GET_CHANNEL_DATA, GET_ALL_CHANNELS
from schemas.exceptions import DatabaseConnectionException

connection = None


def connect_to_db():
    global connection
    if connection is None:
        try:
            connection = psycopg2.connect(os.environ["DATABASE_URL"])
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseConnectionException(f"Failed to connect to database: {e}")


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


load_dotenv()
connect_to_db()
