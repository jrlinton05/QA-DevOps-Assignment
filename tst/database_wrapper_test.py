from dotenv import load_dotenv

import database_wrapper
import pytest

from schemas.constants import ADD_CHANNEL, UPDATE_CHANNEL, DELETE_CHANNEL
from schemas.exceptions import DatabaseConnectionException, NameAlreadyExistsException, InvalidArgumentException


load_dotenv()


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
    mock_cursor.fetchone.return_value = ("DAZN", "24.99")

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_channel_data(1)

    assert result == ("DAZN", "24.99")
    mock_logger.info.assert_called_with("Returned data for channel_id 1: channel_name - DAZN, channel_price: 24.99")


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
    mock_cursor.fetchall.return_value = [(1, "DAZN", "24.99")]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channels()

    assert result == [(1, "DAZN", "24.99")]
    mock_logger.info.assert_called_with("Found channels in the database: [(1, 'DAZN', '24.99')]")


def test_get_all_channels_returns_multiple_values(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [(1, "DAZN", "24.99"), (2, "HBO Max", "8.99")]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channels()

    assert result == [(1, "DAZN", "24.99"), (2, "HBO Max", "8.99")]
    mock_logger.info.assert_called_with(
        "Found channels in the database: [(1, 'DAZN', '24.99'), (2, 'HBO Max', '8.99')]")


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

    assert result == ["DAZN"]
    mock_logger.info.assert_called_with("Found the following channel names in the database: ['DAZN']")


def test_get_all_channel_names_returns_multiple_values(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [("DAZN",), ("HBO Max",)]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    result = database_wrapper.get_all_channel_names()

    assert result == ["DAZN", "HBO Max"]
    mock_logger.info.assert_called_with("Found the following channel names in the database: ['DAZN', 'HBO Max']")


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


def test_add_new_channel(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [("Existing Channel",)]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.add_new_channel("DAZN", "24.99")

    mock_cursor.execute.assert_called_with(ADD_CHANNEL, ("DAZN", "24.99"))


def test_add_new_channel_with_free_channel(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [("Existing Channel",)]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.add_new_channel("DAZN", "0.00")

    mock_cursor.execute.assert_called_with(ADD_CHANNEL, ("DAZN", "0.00"))


def test_add_new_channel_with_price_to_one_decimal_place(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [("Existing Channel",)]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.add_new_channel("DAZN", "9.9")

    mock_cursor.execute.assert_called_with(ADD_CHANNEL, ("DAZN", "9.90"))


def test_add_new_channel_with_price_without_decimal(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [("Existing Channel",)]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.add_new_channel("DAZN", "9")

    mock_cursor.execute.assert_called_with(ADD_CHANNEL, ("DAZN", "9.00"))


def test_add_new_channel_raises_exception_when_name_is_empty():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.add_new_channel("", "24.99")


def test_add_new_channel_raises_exception_when_name_exceeds_max_length():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.add_new_channel("A" * 101, "24.99")


def test_add_new_channel_raises_exception_when_price_is_empty():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.add_new_channel("DAZN", "")


def test_add_new_channel_raises_exception_when_price_exceeds_max_length():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.add_new_channel("DAZN", "9" * 21)


def test_add_new_channel_raises_exception_when_price_is_not_a_number():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.add_new_channel("DAZN", "abc")


def test_add_new_channel_raises_exception_when_price_is_negative():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.add_new_channel("DAZN", "-5.99")


def test_add_new_channel_raises_exception_when_price_has_more_than_two_decimal_places():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.add_new_channel("DAZN", "9.999")


def test_add_new_channel_raises_exception_when_name_already_exists(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [("DAZN",)]

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    with pytest.raises(NameAlreadyExistsException):
        database_wrapper.add_new_channel("DAZN", "24.99")


def test_database_connection_exception_raised_when_add_new_channel_cannot_find_connection(mocker):
    mocker.patch("database_wrapper.psycopg2.connect", side_effect=Exception("connection failed"))

    with pytest.raises(DatabaseConnectionException):
        database_wrapper.add_new_channel("DAZN", "24.99")


def test_update_channel_details(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 1

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.update_channel_details(1, "DAZN", "24.99")

    mock_cursor.execute.assert_called_with(UPDATE_CHANNEL, ("DAZN", "24.99", 1))


def test_update_channel_details_with_free_channel(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 1

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.update_channel_details(1, "DAZN", "0.00")

    mock_cursor.execute.assert_called_with(UPDATE_CHANNEL, ("DAZN", "0.00", 1))


def test_update_channel_details_with_price_to_one_decimal_place(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 1

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.update_channel_details(1, "DAZN", "9.9")

    mock_cursor.execute.assert_called_with(UPDATE_CHANNEL, ("DAZN", "9.90", 1))


def test_update_channel_details_with_price_without_decimal(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 1

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.update_channel_details(1, "DAZN", "9")

    mock_cursor.execute.assert_called_with(UPDATE_CHANNEL, ("DAZN", "9.00", 1))


def test_update_channel_details_raises_exception_when_name_is_empty():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.update_channel_details(1, "", "24.99")


def test_update_channel_details_raises_exception_when_name_exceeds_max_length():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.update_channel_details(1, "A" * 101, "24.99")


def test_update_channel_details_raises_exception_when_price_is_empty():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.update_channel_details(1, "DAZN", "")


def test_update_channel_details_raises_exception_when_price_exceeds_max_length():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.update_channel_details(1, "DAZN", "9" * 21)


def test_update_channel_details_raises_exception_when_price_is_not_a_number():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.update_channel_details(1, "DAZN", "abc")


def test_update_channel_details_raises_exception_when_price_is_negative():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.update_channel_details(1, "DAZN", "-5.99")


def test_update_channel_details_raises_exception_when_price_has_more_than_two_decimal_places():
    with pytest.raises(InvalidArgumentException):
        database_wrapper.update_channel_details(1, "DAZN", "9.999")


def test_update_channel_details_warns_when_no_channel_is_found(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 0

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.update_channel_details(1, "DAZN", "24.99")

    mock_cursor.execute.assert_called_with(UPDATE_CHANNEL, ("DAZN", "24.99", 1))
    mock_logger.warning.assert_called_with("Attempted to update channel with id 1, but no channel was found")


def test_database_connection_exception_raised_when_update_channel_details_cannot_find_connection(mocker):
    mocker.patch("database_wrapper.psycopg2.connect", side_effect=Exception("connection failed"))

    with pytest.raises(DatabaseConnectionException):
        database_wrapper.update_channel_details(1, "DAZN", "24.99")


def test_delete_channel(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 1

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.delete_channel(1)

    mock_cursor.execute.assert_called_with(DELETE_CHANNEL, (1,))
    mock_logger.info.assert_called_with("Deleted channel with id 1")


def test_delete_channel_warns_when_no_channel_is_found(mocker):
    mock_logger = mocker.patch("database_wrapper.logger")

    mock_cursor = mocker.MagicMock()
    mock_cursor.rowcount = 0

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("database_wrapper.psycopg2.connect", return_value=mock_connection)

    database_wrapper.delete_channel(1)

    mock_cursor.execute.assert_called_with(DELETE_CHANNEL, (1,))
    mock_logger.warning.assert_called_with("Attempted to delete channel with id 1, but no channel was found")


def test_database_connection_exception_raised_when_delete_channel_cannot_find_connection(mocker):
    mocker.patch("database_wrapper.psycopg2.connect", side_effect=Exception("connection failed"))

    with pytest.raises(DatabaseConnectionException):
        database_wrapper.delete_channel(1)
