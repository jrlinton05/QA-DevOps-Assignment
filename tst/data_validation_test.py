import pytest
import data_validation
from schemas.exceptions import InvalidArgumentException


# --- Validate Channel Data ---
def test_validate_channel_data_with_free_channel():
    data_validation.validate_channel_data("DAZN", "0.00")


def test_validate_channel_data_with_price_to_one_decimal_place():
    data_validation.validate_channel_data("DAZN", "9.9")


def test_validate_channel_data_with_price_without_decimal():
    data_validation.validate_channel_data("DAZN", "9")


def test_validate_channel_data_raises_exception_when_name_is_empty():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_channel_data("", "24.99")


def test_validate_channel_data_raises_exception_when_name_exceeds_max_length():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_channel_data("A" * 101, "24.99")


def test_validate_channel_data_raises_exception_when_price_is_empty():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_channel_data("DAZN", "")


def test_validate_channel_data_raises_exception_when_price_exceeds_max_length():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_channel_data("DAZN", "9" * 21)


def test_validate_channel_data_raises_exception_when_price_is_not_a_number():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_channel_data("DAZN", "abc")


def test_validate_channel_data_raises_exception_when_price_is_negative():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_channel_data("DAZN", "-5.99")


def test_validate_channel_data_raises_exception_when_price_has_more_than_two_decimal_places():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_channel_data("DAZN", "9.999")


# --- Validate User Data ---
def test_validate_user_data_with_valid_data():
    data_validation.validate_user_data("testuser", "averylongpassword")


def test_validate_user_data_raises_exception_when_username_is_empty():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_user_data("", "averylongpassword")


def test_validate_user_data_raises_exception_when_username_exceeds_max_length():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_user_data("a" * 21, "averylongpassword")


def test_validate_user_data_with_username_exactly_20_characters():
    data_validation.validate_user_data("a" * 20, "averylongpassword")


def test_validate_user_data_raises_exception_when_password_is_empty():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_user_data("testuser", "")


def test_validate_user_data_raises_exception_when_password_is_too_short():
    with pytest.raises(InvalidArgumentException):
        data_validation.validate_user_data("testuser", "short")


def test_validate_user_data_with_password_exactly_15_characters():
    data_validation.validate_user_data("testuser", "a" * 15)
