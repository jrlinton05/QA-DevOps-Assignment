import database_wrapper
import pytest

from schemas.exceptions import DatabaseConnectionException


@pytest.fixture(autouse=True)
def setup():
    database_wrapper.connection = None


def test_connect_to_db(mocker):
    mock_response = mocker.Mock()
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_response)
    mock_logger = mocker.patch("database_wrapper.logger")

    database_wrapper.connect_to_db()

    assert database_wrapper.connection == mock_response
    mock_logger.info.assert_called_once_with("Connected to database successfully")


def test_exception_raised_when_connect_to_db_fails(mocker):
    mocker.patch("database_wrapper.psycopg2.connect", side_effect=Exception("connection failed"))
    mock_logger = mocker.patch("database_wrapper.logger")

    with pytest.raises(DatabaseConnectionException):
        database_wrapper.connect_to_db()

    assert database_wrapper.connection is None
    mock_logger.error.assert_called_once_with("Failed to connect to database: connection failed")


def test_get_channel_data(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = ("DAZN", "£24.99")

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_channel_data(1)

    assert result == ("DAZN", "£24.99")
    mock_logger.info.assert_called_with("Returned data for channel_id 1: channel_name - DAZN, channel_price: £24.99")


def test_get_channel_data_when_channel_does_not_exist(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_channel_data(1)

    assert result is None
    mock_logger.warning.assert_called_with("No data found in table for channel_id: 1")


def test_database_connection_exception_raised_when_get_channel_data_cannot_find_connection(mocker):
    mocker.patch("database_wrapper.psycopg2.connect", side_effect=Exception("connection failed"))

    with pytest.raises(DatabaseConnectionException):
        database_wrapper.get_channel_data(1)


def test_get_all_channels_returns_single_value(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [(1, "DAZN", "£24.99")]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channels()

    assert result == [(1, "DAZN", "£24.99")]
    mock_logger.info.assert_called_with("Found channels in the database: [(1, 'DAZN', '£24.99')]")


def test_get_all_channels_returns_multiple_values(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [(1, "DAZN", "£24.99"), (2, "HBO Max", "£8.99")]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channels()

    assert result == [(1, "DAZN", "£24.99"), (2, "HBO Max", "£8.99")]
    mock_logger.info.assert_called_with(
        "Found channels in the database: [(1, 'DAZN', '£24.99'), (2, 'HBO Max', '£8.99')]")


def test_get_all_channels_when_database_is_empty(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = []

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channels()

    assert result == []
    mock_logger.warning.assert_called_with("No channels were found in the database")


def test_database_connection_exception_raised_when_get_all_channels_cannot_find_connection(mocker):
    mocker.patch("database_wrapper.psycopg2.connect", side_effect=Exception("connection failed"))

    with pytest.raises(DatabaseConnectionException):
        database_wrapper.get_all_channels()


def test_get_all_channel_names_returns_single_value(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [("DAZN",)]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channel_names()

    assert result == [("DAZN",)]
    mock_logger.info.assert_called_with("Found the following channel names in the database: [('DAZN',)]")


def test_get_all_channel_names_returns_multiple_values(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [("DAZN",), ("HBO Max",)]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channel_names()

    assert result == [("DAZN",), ("HBO Max",)]
    mock_logger.info.assert_called_with("Found the following channel names in the database: [('DAZN',), ('HBO Max',)]")


def test_get_all_channel_names_when_database_is_empty(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = []

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channel_names()

    assert result == []
    mock_logger.warning.assert_called_with("No channel names were found in the database")


def test_database_connection_exception_raised_when_get_all_channel_names_cannot_find_connection(mocker):
    mocker.patch("database_wrapper.psycopg2.connect", side_effect=Exception("connection failed"))

    with pytest.raises(DatabaseConnectionException):
        database_wrapper.get_all_channel_names()
