import pytest
from app import app
from schemas.exceptions import DatabaseConnectionException, InvalidArgumentException, NameAlreadyExistsException


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


def test_index_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200


def test_channel_browser_returns_200(client, mocker):
    mocker.patch("database_wrapper.get_all_channels", return_value=[])
    response = client.get('/channels')
    assert response.status_code == 200


def test_channel_browser_returns_503_when_db_unavailable(client, mocker):
    mocker.patch("database_wrapper.get_all_channels", side_effect=DatabaseConnectionException("fail"))
    response = client.get('/channels')
    assert response.status_code == 503


def test_create_channel_get_returns_200(logged_in_client):
    response = logged_in_client.get('/channels/create')
    assert response.status_code == 200


def test_create_channel_redirects_when_not_logged_in(client):
    response = client.get('/channels/create')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_create_channel_post_success(logged_in_client, mocker):
    mocker.patch("database_wrapper.add_new_channel")
    response = logged_in_client.post('/channels/create', data={
        'channel_name': 'DAZN',
        'channel_price': '24.99'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert '/channels' in response.headers['Location']


def test_create_channel_post_invalid_data(logged_in_client, mocker):
    mocker.patch("database_wrapper.add_new_channel",
                 side_effect=InvalidArgumentException("Channel Name is invalid"))
    response = logged_in_client.post('/channels/create', data={
        'channel_name': '',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert b"Channel Name is invalid" in response.data


def test_create_channel_post_duplicate_name(logged_in_client, mocker):
    mocker.patch("database_wrapper.add_new_channel",
                 side_effect=NameAlreadyExistsException("Channel name already exists in the database"))
    response = logged_in_client.post('/channels/create', data={
        'channel_name': 'DAZN',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert b"Channel name already exists in the database" in response.data


def test_update_channel_get_returns_200(logged_in_client, mocker):
    mocker.patch("database_wrapper.get_channel_data", return_value=("DAZN", "24.99"))
    response = logged_in_client.get('/channels/1/edit')
    assert response.status_code == 200


def test_update_channel_redirects_when_not_logged_in(client):
    response = client.get('/channels/1/edit')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_update_channel_get_redirects_when_channel_not_found(logged_in_client, mocker):
    mocker.patch("database_wrapper.get_channel_data", return_value=None)
    response = logged_in_client.get('/channels/999/edit', follow_redirects=False)
    assert response.status_code == 302
    assert '/channels' in response.headers['Location']


def test_update_channel_post_success(logged_in_client, mocker):
    mocker.patch("database_wrapper.update_channel_details")
    response = logged_in_client.post('/channels/1/edit', data={
        'channel_name': 'DAZN',
        'channel_price': '29.99'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert '/channels' in response.headers['Location']


def test_update_channel_post_invalid_data(logged_in_client, mocker):
    mocker.patch("database_wrapper.update_channel_details",
                 side_effect=InvalidArgumentException("Channel Name is invalid"))
    response = logged_in_client.post('/channels/1/edit', data={
        'channel_name': '',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert b"Channel Name is invalid" in response.data


def test_update_channel_post_duplicate_name(logged_in_client, mocker):
    mocker.patch("database_wrapper.update_channel_details",
                 side_effect=NameAlreadyExistsException("Channel name already exists in the database"))
    response = logged_in_client.post('/channels/1/edit', data={
        'channel_name': 'DAZN',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert b"Channel name already exists in the database" in response.data


def test_update_channel_returns_503_when_db_unavailable(logged_in_client, mocker):
    mocker.patch("database_wrapper.get_channel_data", side_effect=DatabaseConnectionException("fail"))
    response = logged_in_client.get('/channels/1/edit')
    assert response.status_code == 503


def test_delete_channel_success(logged_in_client, mocker):
    mocker.patch("database_wrapper.delete_channel")
    response = logged_in_client.post('/channels/1/delete', follow_redirects=False)
    assert response.status_code == 302
    assert '/channels' in response.headers['Location']


def test_delete_channel_redirects_when_not_logged_in(client):
    response = client.post('/channels/1/delete')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_delete_channel_returns_503_when_db_unavailable(logged_in_client, mocker):
    mocker.patch("database_wrapper.delete_channel", side_effect=DatabaseConnectionException("fail"))
    response = logged_in_client.post('/channels/1/delete')
    assert response.status_code == 503


def test_delete_channel_flashes_error_on_failure(logged_in_client, mocker):
    mocker.patch("database_wrapper.delete_channel", side_effect=Exception("Failed to delete channel 1"))
    response = logged_in_client.post('/channels/1/delete', follow_redirects=True)
    assert b"Failed to delete channel 1" in response.data


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
                 side_effect=NameAlreadyExistsException("Username already exists"))
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'averylongpassword'
    })
    assert response.status_code == 200
    assert b"Username already exists" in response.data


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
    assert b"Invalid username or password" in response.data


def test_login_post_wrong_password(client, mocker):
    hashed = "$2b$12$LJ3m4sMKfRJG0Z2FHISqOOxlRQ0G1ZW5PzXMGG.Ioqkl3GhzPbXMa"
    mocker.patch("database_wrapper.get_user_by_username", return_value=(1, hashed, False))
    mocker.patch("app.checkpw", return_value=False)
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpasswordhere'
    })
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_login_redirects_when_already_logged_in(logged_in_client):
    response = logged_in_client.get('/login')
    assert response.status_code == 302
    assert '/' == response.headers['Location']


def test_logout_redirects_to_index(logged_in_client):
    response = logged_in_client.post('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert '/' == response.headers['Location']
