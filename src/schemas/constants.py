# SQL Queries
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

GET_ALL_CHANNELS = "SELECT * FROM channels ORDER BY channel_id;"

GET_ALL_CHANNEL_NAMES = "SELECT channel_name FROM channels;"

GET_CHANNEL_DATA = "SELECT channel_name, channel_price FROM channels WHERE channel_id = %s;"

ADD_CHANNEL = "INSERT INTO channels (channel_name, channel_price) VALUES (%s, %s);"

UPDATE_CHANNEL = "UPDATE channels SET channel_name = %s, channel_price = %s WHERE channel_id = %s;"

DELETE_CHANNEL = "DELETE FROM channels WHERE channel_id = %s;"

GET_USER_BY_USERNAME = "SELECT user_id, password, is_admin FROM users WHERE username = %s;"

GET_USER_BY_ID = "SELECT username, is_admin FROM users WHERE user_id = %s;"

GET_ALL_USERS = "SELECT username, is_admin FROM users;"

GET_ALL_USERNAMES = "SELECT username FROM users;"

ADD_USER = "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s);"

# Success Messages
DATABASE_CONNECTION_SUCCESS = "Connected to database successfully"

CHANNEL_CREATION_SUCCESS = "Channel created successfully"

CHANNEL_UPDATE_SUCCESS = "Channel updated successfully"

CHANNEL_DELETE_SUCCESS = "Channel deleted successfully"

ACCOUNT_CREATION_SUCCESS = "Account created successfully"

TABLE_CREATION_SUCCESS = "Create tables operation executed successfully"

# Error Messages
DATABASE_CONNECTION_ERROR = "Unable to connect to database"

REQUEST_RATE_EXCEEDED_ERROR = "Too many requests. Please try again in a minute"

PAGE_NOT_FOUND_ERROR = ["The requested URL does not exist",
                        "Please use the navigation bar at the top of the screen to return to Telescope"]

ADMIN_ACCESS_ERROR = "Access to this page requires admin permissions"

INVALID_USER_DETAILS_ERROR = "Invalid username or password"

USERNAME_EXISTS_ERROR = "Username already exists"

NO_USERNAMES_FOUND_ERROR = "No usernames were found in the database"

USER_DETAIL_FETCHING_ERROR = "Error occurred while fetching user details"

USERNAME_FETCHING_ERROR = "Failed to fetch usernames"

USER_CREATION_ERROR = "Failed to create new user"

CHANNEL_DATA_FETCHING_ERROR = "Failed to fetch channel data"

CHANNEL_NOT_FOUND_ERROR = "Channel not found"

NO_CHANNELS_FOUND_ERROR = "No channels were found in the database"

NO_CHANNEL_NAMES_FOUND_ERROR = "No channel names were found in the database"

CHANNEL_NAME_FETCHING_ERROR = "Failed to fetch channel names"

CHANNEL_NAME_EXISTS_ERROR = "Channel name already exists in the database"

CHANNEL_CREATION_ERROR = "Failed to create new channel"

CHANNEL_UPDATE_ERROR = "Failed to update channel"

CHANNEL_DELETE_ERROR = "Failed to delete channel"

TABLE_CREATION_ERROR = "Failed to create tables"

# Config
LOG_MESSAGE_FORMAT = "%(asctime)s | %(levelname)s: %(message)s"
