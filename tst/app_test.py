import pytest
from app import app
from schemas.exceptions import DatabaseConnectionException, InvalidArgumentException, NameAlreadyExistsException


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
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


def test_create_channel_get_returns_200(client):
    response = client.get('/channels/create')
    assert response.status_code == 200


def test_create_channel_post_success(client, mocker):
    mocker.patch("database_wrapper.add_new_channel")
    response = client.post('/channels/create', data={
        'channel_name': 'DAZN',
        'channel_price': '24.99'
    }, follow_redirects=False)
    assert response.status_code == 302


def test_create_channel_post_invalid_data(client, mocker):
    mocker.patch("database_wrapper.add_new_channel",
                 side_effect=InvalidArgumentException("Channel Name is invalid"))
    response = client.post('/channels/create', data={
        'channel_name': '',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert b"Channel Name is invalid" in response.data


def test_create_channel_post_duplicate_name(client, mocker):
    mocker.patch("database_wrapper.add_new_channel",
                 side_effect=NameAlreadyExistsException("Channel name already exists in the database"))
    response = client.post('/channels/create', data={
        'channel_name': 'DAZN',
        'channel_price': '24.99'
    })
    assert response.status_code == 200
    assert b"Channel name already exists in the database" in response.data
