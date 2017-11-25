import logging

from sqlalchemy.schema import MetaData

from falcon import testing

import pytest

import ssms.app
from ssms.models import Admin


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
    admin = Admin(
        **dict(
            email='admin@test.com',
            first_name='Admin',
            last_name='Admin'
        )
    )
    admin.set_password('admin')
    admin.save()
    yield admin
