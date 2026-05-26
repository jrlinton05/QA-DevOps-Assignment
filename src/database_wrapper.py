import os
import psycopg2
from dotenv import load_dotenv
from logging_config import logger
from constants import CREATE_USERS_TABLE, CREATE_CHANNELS_TABLE, GET_CHANNEL_DATA

connection = None


def connect_to_db():
    global connection
    if connection is None:
        try:
            connection = psycopg2.connect(os.environ["DATABASE_URL"])
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")


def create_tables():
    connect_to_db()
    if connection is None:
        logger.error("Attempted to create tables but database connection could not be formed")
        return
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
    if connection is None:
        logger.error("Attempted to fetch channel data but database connection could not be formed")
        return
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_CHANNEL_DATA, (channel_id,))
                data = cursor.fetchone()
                if data is None:
                    logger.warning(f"No data found in table for channel_id: {channel_id}")
                    return None
                logger.info(
                    f"Returned data for channel_id {channel_id}: channel_name - {data[1]}, channel_price: {data[2]}")
                return data[1], data[2]
    except Exception as e:
        logger.error(f"Failed to fetch channel data for channel_id {channel_id}: {e}")


load_dotenv()
connect_to_db()
