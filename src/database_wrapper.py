import os
import psycopg2
from bcrypt import hashpw, gensalt
from retrying import retry

import data_validation
from logging_config import logger
from schemas.constants import (CREATE_USERS_TABLE, CREATE_CHANNELS_TABLE, GET_CHANNEL_DATA, GET_ALL_CHANNELS,
                               GET_ALL_CHANNEL_NAMES, ADD_CHANNEL, UPDATE_CHANNEL, DELETE_CHANNEL, GET_USER_BY_USERNAME,
                               GET_USER_BY_ID,
                               ADD_USER, GET_ALL_USERNAMES, DATABASE_CONNECTION_ERROR, DATABASE_CONNECTION_SUCCESS,
                               TABLE_CREATION_SUCCESS, CHANNEL_NAME_EXISTS_ERROR, USERNAME_EXISTS_ERROR,
                               TABLE_CREATION_ERROR, NO_CHANNELS_FOUND_ERROR, CHANNEL_DATA_FETCHING_ERROR,
                               NO_CHANNEL_NAMES_FOUND_ERROR, CHANNEL_NAME_FETCHING_ERROR, CHANNEL_CREATION_ERROR,
                               CHANNEL_UPDATE_ERROR, USER_DETAIL_FETCHING_ERROR, NO_USERNAMES_FOUND_ERROR,
                               USERNAME_FETCHING_ERROR, USER_CREATION_ERROR, CHANNEL_DELETE_ERROR)
from schemas.exceptions import DatabaseConnectionException, NameAlreadyExistsException

connection = None


# --- Validation ---
def check_if_channel_name_exists(channel_name: str):
    existing_channel_names = get_all_channel_names()
    lowercase_channel_names = [name.lower() for name in existing_channel_names]

    if channel_name.lower() in lowercase_channel_names:
        raise NameAlreadyExistsException(CHANNEL_NAME_EXISTS_ERROR)


def check_if_username_exists(username: str):
    existing_usernames = get_all_usernames()
    lowercase_usernames = [name.lower() for name in existing_usernames]
    if username.lower() in lowercase_usernames:
        raise NameAlreadyExistsException(USERNAME_EXISTS_ERROR)


# --- Database Connection ---
@retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
def connect_to_db():
    """Attempts to connect to the PostgreSQL database with automated retries.

    Stale connections are tested for to ensure connection remains fresh.

    Raises DatabaseConnectionException if a connection could not be formed.
    """
    global connection

    # Test connection to database
    if connection is not None:
        try:
            connection.cursor().execute("SELECT 1")
        except Exception:
            connection = None

    # Form a connection to the database if one is not already established
    if connection is None:
        try:
            logger.info("Attempting to connect to database")
            connection = psycopg2.connect(os.environ["DATABASE_URL"])
            logger.info(DATABASE_CONNECTION_SUCCESS)
        except Exception as e:
            error_message = f"{DATABASE_CONNECTION_ERROR}: {e}"
            logger.error(error_message)
            raise DatabaseConnectionException(error_message)


# --- Table Creation ---
def create_tables():
    """Creates all necessary tables in the database if they do not already exist."""
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
                cursor.execute(CREATE_CHANNELS_TABLE)
                logger.info(TABLE_CREATION_SUCCESS)
    except Exception as e:
        logger.error(f"{TABLE_CREATION_ERROR}: {e}")


# --- Channel Table Read Methods ---
def get_channel_data(channel_id: int) -> tuple[str, str]:
    """Returns a tuple containing the channel name followed by channel price for the given channel id."""
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
        logger.error(f"{CHANNEL_DATA_FETCHING_ERROR} for channel_id {channel_id}: {e}")


def get_all_channels() -> list[tuple[int, str, str]]:
    """Returns a list of tuples each containing a channel id, channel name, and channel price."""
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_CHANNELS)
                data = cursor.fetchall()
                if not data:
                    logger.warning(NO_CHANNELS_FOUND_ERROR)
                else:
                    logger.info(f"Found channels in the database: {data}")
                return data
    except Exception as e:
        logger.error(f"{CHANNEL_DATA_FETCHING_ERROR}: {e}")


def get_all_channel_names() -> list[str]:
    """Returns a list of all channel names."""
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_CHANNEL_NAMES)
                data = [row[0] for row in cursor.fetchall()]
                if not data:
                    logger.warning(NO_CHANNEL_NAMES_FOUND_ERROR)
                else:
                    logger.info(f"Found the following channel names in the database: {data}")
                return data
    except Exception as e:
        logger.error(f"{CHANNEL_NAME_FETCHING_ERROR}: {e}")
        raise e


# --- Channel Table Create Methods ---
def add_new_channel(channel_name: str, channel_price: str):
    """Validates the given channel data before adding a new entry to the channels table."""
    data_validation.validate_channel_data(channel_name, channel_price)
    check_if_channel_name_exists(channel_name)

    formatted_price = f"{float(channel_price):.2f}"

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(ADD_CHANNEL, (channel_name, formatted_price))
                logger.info(f"Added new channel with name: {channel_name} and price: {formatted_price}")
    except Exception as e:
        logger.error(f"{CHANNEL_CREATION_ERROR}: {e}")
        raise Exception(CHANNEL_CREATION_ERROR)


# --- Channel Table Update Methods ---
def update_channel_details(channel_id: int, new_channel_name: str, new_channel_price: str):
    """Validates the given channel data before updating the relevant row in the channels table."""
    new_channel_name = new_channel_name.strip()
    new_channel_price = new_channel_price.strip()

    data_validation.validate_channel_data(new_channel_name, new_channel_price)

    existing_details = get_channel_data(channel_id)
    if existing_details and existing_details[0] != new_channel_name:
        check_if_channel_name_exists(new_channel_name)

    new_formatted_price = f"{float(new_channel_price):.2f}"

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CHANNEL, (new_channel_name, new_formatted_price, channel_id))
                if cursor.rowcount <= 0:
                    logger.warning(f"Attempted to update channel with id {channel_id}, but no channel was found")
                else:
                    logger.info(f"Updated channel with id {channel_id}. "
                                f"New name: {new_channel_name}. New price: {new_formatted_price}")
    except Exception as e:
        logger.error(f"{CHANNEL_UPDATE_ERROR} with id {channel_id}: {e}")
        raise Exception(f"{CHANNEL_UPDATE_ERROR} {channel_id}")


# --- Channel Table Delete Methods ---
def delete_channel(channel_id: int):
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(DELETE_CHANNEL, (channel_id,))
                if cursor.rowcount <= 0:
                    logger.warning(f"Attempted to delete channel with id {channel_id}, but no channel was found")
                else:
                    logger.info(f"Deleted channel with id {channel_id}")
    except Exception as e:
        logger.error(f"{CHANNEL_DELETE_ERROR} with id {channel_id}: {e}")
        raise Exception(f"{CHANNEL_DELETE_ERROR} {channel_id}")


# --- User Table Read Methods ---
def get_user_by_username(username: str) -> tuple[int, str, bool]:
    """Returns the user id, password, and admin status of the given username."""
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_USER_BY_USERNAME, (username,))
                return cursor.fetchone()
    except Exception as e:
        logger.error(f"{USER_DETAIL_FETCHING_ERROR}: {e}")
        raise e


def get_user_by_user_id(user_id: int) -> tuple[str, bool]:
    """Returns the username and admin status for the given user id."""
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_USER_BY_ID, (user_id,))
                return cursor.fetchone()
    except Exception as e:
        logger.error(f"{USER_DETAIL_FETCHING_ERROR}: {e}")
        raise e


def get_all_usernames() -> list[str]:
    """Returns a list of all existing usernames."""
    connect_to_db()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_USERNAMES)
                data = [row[0] for row in cursor.fetchall()]
                if not data:
                    logger.warning(NO_USERNAMES_FOUND_ERROR)
                else:
                    logger.info(f"Found the following usernames in the database: {data}")
                return data
    except Exception as e:
        logger.error(f"{USERNAME_FETCHING_ERROR}: {e}")
        raise e


# --- User Table Create Methods ---
def add_new_user(username: str, password: str):
    """Validates the given user details before adding a new entry to the users table."""
    data_validation.validate_user_data(username, password)
    check_if_username_exists(username)

    hashed_password = hashpw(password.encode(), gensalt()).decode()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(ADD_USER, (username, hashed_password, False))
                logger.info(f"Added new user: {username}")
    except Exception as e:
        logger.error(f"{USER_CREATION_ERROR}: {e}")
        raise Exception(USER_CREATION_ERROR)
