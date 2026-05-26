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

GET_ALL_CHANNELS = "SELECT * FROM channels;"

GET_CHANNEL_DATA = "SELECT channel_name, channel_price FROM channels WHERE channel_id = %s;"

GET_USER_PASSWORD = "SELECT password FROM users WHERE user_id = %s;"

GET_USER_DATA = "SELECT username, is_admin FROM users WHERE user_id = %s;"
