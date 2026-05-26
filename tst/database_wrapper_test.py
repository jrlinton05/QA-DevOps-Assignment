import database_wrapper
import pytest


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


def test_exception_thrown_when_connect_to_db_fails(mocker):
    mocker.patch("database_wrapper.psycopg2.connect", side_effect=Exception("connection failed"))
    mock_logger = mocker.patch("database_wrapper.logger")

    database_wrapper.connect_to_db()

    assert database_wrapper.connection is None
    mock_logger.error.assert_called_once_with("Failed to connect to database: connection failed")


def test_get_channel_data(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = (1, "DAZN", "£24.99")

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
