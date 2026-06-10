import pytest
from app import app
from schemas.constants import ADMIN_ACCESS_ERROR, CHANNEL_CREATION_SUCCESS, CHANNEL_UPDATE_SUCCESS, \
    CHANNEL_DELETE_SUCCESS, CHANNEL_NOT_FOUND_ERROR, INVALID_USER_DETAILS_ERROR, CHANNEL_NAME_EXISTS_ERROR, \
    USERNAME_EXISTS_ERROR
from schemas.exceptions import DatabaseConnectionException, InvalidArgumentException, NameAlreadyExistsException


# --- Client Fixtures ---
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def logged_in_client(client, mocker):
    with client.session_transaction() as session:
        session['_user_id'] = '1'
    mocker.patch("database_wrapper.get_user_by_user_id", return_value=("testuser", False))
    yield client


@pytest.fixture
def admin_client(client, mocker):
    with client.session_transaction() as session:
        session['_user_id'] = '1'
    mocker.patch("database_wrapper.get_user_by_user_id", return_value=("testuser", True))
    yield client


# --- Index ---
def test_index_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200


# --- Channel Browser ---
def test_channel_browser_returns_200(client, mocker):
    mocker.patch("database_wrapper.get_all_channels", return_value=[])
    response = client.get('/channels')
    assert response.status_code == 200


def test_channel_browser_returns_503_when_db_unavailable(client, mocker):
    mocker.patch("database_wrapper.get_all_channels", side_effect=DatabaseConnectionException("fail"))
    response = client.get('/channels')
    assert response.status_code == 503


# --- Create Channel ---
def test_create_channel_get_returns_200(admin_client):
    response = admin_client.get('/channels/create')
    assert response.status_code == 200


def test_create_channel_redirects_when_not_admin(logged_in_client):
    response = logged_in_client.get('/channels/create')
    assert response.status_code == 302
    assert '/channels' in response.headers['Location']


def test_create_channel_redirects_when_not_logged_in(client):
    response = client.get('/channels/create')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_create_channel_post_success(admin_client, mocker):
    mocker.patch("database_wrapper.add_new_channel")
    mocker.patch("database_wrapper.get_all_channels", return_value=[])
    response = admin_client.post('/channels/create', data={
        'channel_name': 'DAZN',
        'channel_price': '24.99'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert CHANNEL_CREATION_SUCCESS.encode() in response.data


def test_create_channel_post_invalid_data(admin_client, mocker):
    mocker.patch("database_wrapper.add_new_channel",
                 side_effect=InvalidArgumentException("Channel Name is invalid"))
    response = admin_client.post('/channels/create', data={
        'channel_name': '',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert b"Channel Name is invalid" in response.data


def test_create_channel_post_duplicate_name(admin_client, mocker):
    mocker.patch("database_wrapper.add_new_channel",
                 side_effect=NameAlreadyExistsException(CHANNEL_NAME_EXISTS_ERROR))
    response = admin_client.post('/channels/create', data={
        'channel_name': 'DAZN',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert CHANNEL_NAME_EXISTS_ERROR.encode() in response.data


# --- Update Channel ---
def test_update_channel_get_returns_200(admin_client, mocker):
    mocker.patch("database_wrapper.get_channel_data", return_value=("DAZN", "24.99"))
    response = admin_client.get('/channels/1/edit')
    assert response.status_code == 200


def test_update_channel_redirects_when_not_admin(logged_in_client):
    response = logged_in_client.get('/channels/1/edit')
    assert response.status_code == 302
    assert '/channels' in response.headers['Location']


def test_update_channel_redirects_when_not_logged_in(client):
    response = client.get('/channels/1/edit')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_update_channel_get_redirects_when_channel_not_found(admin_client, mocker):
    mocker.patch("database_wrapper.get_channel_data", return_value=None)
    mocker.patch("database_wrapper.get_all_channels", return_value=[])
    response = admin_client.get('/channels/999/edit', follow_redirects=True)
    assert response.status_code == 200
    assert CHANNEL_NOT_FOUND_ERROR.encode() in response.data


def test_update_channel_post_success(admin_client, mocker):
    mocker.patch("database_wrapper.update_channel_details")
    mocker.patch("database_wrapper.get_all_channels", return_value=[])
    response = admin_client.post('/channels/1/edit', data={
        'channel_name': 'DAZN',
        'channel_price': '29.99'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert CHANNEL_UPDATE_SUCCESS.encode() in response.data


def test_update_channel_post_invalid_data(admin_client, mocker):
    mocker.patch("database_wrapper.update_channel_details",
                 side_effect=InvalidArgumentException("Channel Name is invalid"))
    response = admin_client.post('/channels/1/edit', data={
        'channel_name': '',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert b"Channel Name is invalid" in response.data


def test_update_channel_post_duplicate_name(admin_client, mocker):
    mocker.patch("database_wrapper.update_channel_details",
                 side_effect=NameAlreadyExistsException(CHANNEL_NAME_EXISTS_ERROR))
    response = admin_client.post('/channels/1/edit', data={
        'channel_name': 'DAZN',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert CHANNEL_NAME_EXISTS_ERROR.encode() in response.data


def test_update_channel_returns_503_when_db_unavailable(admin_client, mocker):
    mocker.patch("database_wrapper.get_channel_data", side_effect=DatabaseConnectionException("fail"))
    response = admin_client.get('/channels/1/edit')
    assert response.status_code == 503


# --- Delete Channel ---
def test_delete_channel_success(admin_client, mocker):
    mocker.patch("database_wrapper.delete_channel")
    mocker.patch("database_wrapper.get_all_channels", return_value=[])
    response = admin_client.post('/channels/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert CHANNEL_DELETE_SUCCESS.encode() in response.data


def test_delete_channel_redirects_when_not_admin(logged_in_client, mocker):
    mocker.patch("database_wrapper.get_all_channels", return_value=[])
    response = logged_in_client.post('/channels/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert ADMIN_ACCESS_ERROR.encode() in response.data


def test_delete_channel_redirects_when_not_logged_in(client):
    response = client.post('/channels/1/delete')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_delete_channel_returns_503_when_db_unavailable(admin_client, mocker):
    mocker.patch("database_wrapper.delete_channel", side_effect=DatabaseConnectionException("fail"))
    response = admin_client.post('/channels/1/delete')
    assert response.status_code == 503


def test_delete_channel_flashes_error_on_failure(admin_client, mocker):
    mocker.patch("database_wrapper.delete_channel", side_effect=Exception("Failed to delete channel 1"))
    mocker.patch("database_wrapper.get_all_channels", return_value=[])
    response = admin_client.post('/channels/1/delete', follow_redirects=True)
    assert b"Failed to delete channel 1" in response.data


# --- Register User ---
def test_register_get_returns_200(client):
    response = client.get('/register')
    assert response.status_code == 200


def test_register_post_success(client, mocker):
    mocker.patch("database_wrapper.add_new_user")
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'averylongpassword'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_register_post_duplicate_username(client, mocker):
    mocker.patch("database_wrapper.add_new_user",
                 side_effect=NameAlreadyExistsException(USERNAME_EXISTS_ERROR))
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'averylongpassword'
    })
    assert response.status_code == 200
    assert USERNAME_EXISTS_ERROR.encode() in response.data


def test_register_post_invalid_data(client, mocker):
    mocker.patch("database_wrapper.add_new_user",
                 side_effect=InvalidArgumentException("Password must be at least 15 characters"))
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'short'
    })
    assert response.status_code == 200
    assert b"Password must be at least 15 characters" in response.data


def test_register_redirects_when_already_logged_in(logged_in_client):
    response = logged_in_client.get('/register')
    assert response.status_code == 302
    assert '/' == response.headers['Location']


# --- Log In User ---
def test_login_get_returns_200(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_login_post_success(client, mocker):
    hashed = "$2b$12$LJ3m4sMKfRJG0Z2FHISqOOxlRQ0G1ZW5PzXMGG.Ioqkl3GhzPbXMa"
    mocker.patch("database_wrapper.get_user_by_username", return_value=(1, hashed, False))
    mocker.patch("app.checkpw", return_value=True)
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'averylongpassword'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert '/' == response.headers['Location']


def test_login_post_invalid_credentials(client, mocker):
    mocker.patch("database_wrapper.get_user_by_username", return_value=None)
    response = client.post('/login', data={
        'username': 'baduser',
        'password': 'averylongpassword'
    })
    assert response.status_code == 200
    assert INVALID_USER_DETAILS_ERROR.encode() in response.data


def test_login_post_wrong_password(client, mocker):
    hashed = "$2b$12$LJ3m4sMKfRJG0Z2FHISqOOxlRQ0G1ZW5PzXMGG.Ioqkl3GhzPbXMa"
    mocker.patch("database_wrapper.get_user_by_username", return_value=(1, hashed, False))
    mocker.patch("app.checkpw", return_value=False)
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpasswordhere'
    })
    assert response.status_code == 200
    assert INVALID_USER_DETAILS_ERROR.encode() in response.data


def test_login_redirects_when_already_logged_in(logged_in_client):
    response = logged_in_client.get('/login')
    assert response.status_code == 302
    assert '/' == response.headers['Location']


# --- Log Out User ---
def test_logout_redirects_to_index(logged_in_client):
    response = logged_in_client.post('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert '/' == response.headers['Location']
