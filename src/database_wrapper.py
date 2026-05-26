import os
import psycopg2
from dotenv import load_dotenv

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

load_dotenv()
connection = psycopg2.connect(os.environ["DATABASE_URL"])


def create_tables():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(CREATE_CHANNELS_TABLE)
