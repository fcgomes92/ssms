import logging

from sqlalchemy.schema import MetaData

from falcon import testing

import pytest

from base64 import b64encode

import ssms.app
from ssms.models import Admin, Client


@pytest.fixture(scope='module')
def conf_logger():
    _default_logging_format = '[%(asctime)s][%(name)s]: %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        filename='./logging.log',
                        filemode='w',
                        format=_default_logging_format)


@pytest.fixture(scope='module')
def db_session():
    metadata = MetaData(ssms.app.engine)
    metadata.reflect()
    session = ssms.app.Session()
    yield session
    metadata.drop_all()


@pytest.fixture
def client():
    api = ssms.app.create_app()
    return testing.TestClient(api)


@pytest.fixture(scope='module')
def db_session():
    metadata = MetaData(ssms.app.engine)
    metadata.reflect()
    session = ssms.app.Session()
    yield session
    metadata.drop_all()


@pytest.fixture(scope='module')
def admin():
    admin = Admin(**dict(
        email='admin@test.com',
        first_name='Admin',
        last_name='Admin'
    ))
    admin.set_password('admin')
    admin.save()

    setattr(admin, 'basic_password', b64encode("{}:{}".format(admin.email, 'admin').encode()).decode("ascii"))

    yield admin


@pytest.fixture(scope='module')
def user_client():
    client = Client(**dict(
        email='client@test.com',
        first_name='Client',
        last_name='Client'
    ))
    client.set_password('admin')
    client.save()

    setattr(client, 'basic_password', b64encode("{}:{}".format(client.email, 'admin').encode()).decode("ascii"))

    yield client
