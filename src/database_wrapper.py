import os
import psycopg2
from dotenv import load_dotenv
from logging_config import logger


CREATE_USERS_TABLE = """CREATE TABLE IF NOT EXISTS users (
    user_id serial PRIMARY KEY,
    username varchar(20),
    password char(60) NOT NULL,
    is_admin boolean NOT NULL
);"""

CREATE_CHANNELS_TABLE = """CREATE TABLE IF NOT EXISTS channels (
    channel_id serial PRIMARY KEY,
    channel_name varchar(100) NOT NULL,
    channel_price varchar(20) NOT NULL
    );"""

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
    global connection
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


load_dotenv()
connect_to_db()
