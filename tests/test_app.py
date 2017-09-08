import falcon
from falcon import testing

import pytest

import ssms.app
from ssms.models import Admin

import json


@pytest.fixture
def client():
    api = ssms.app.create_app()
    return testing.TestClient(api)


@pytest.fixture(scope='module')
def db_connection():
    yield ssms.app.db
    ssms.app.db.eval("db.dropDatabase()")


@pytest.fixture(scope='module')
def admin():
    admin = Admin(email='admin@test.com', first_name='Admin', last_name='Admin')
    admin.set_password('admin')
    admin.save()
    yield admin


def test_users_list_resource__on_post(db_connection, client, admin):
    mock_data = {
        'email': 'fcgomes.92@gmail.com',
        'first_name': 'Fernando',
        'last_name': 'Coelho Gomes',
        'password': 'qwe123',
        'type': 'client'
    }

    response = client.simulate_post(
        '/v1/users/',
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    data.pop('id')

    mock_data.pop('password')

    assert response.status == falcon.HTTP_OK
    assert data == mock_data


def test_users_list_resource__on_get(db_connection, client, admin):
    response = client.simulate_get('/v1/users/')

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)


def test_admins_list_resource__on_get(db_connection, client, admin):
    response = client.simulate_get(
        '/v1/admins/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    # assert isinstance(data, list)
    # assert len(data) == 1
