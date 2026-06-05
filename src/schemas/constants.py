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
