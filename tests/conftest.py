import os
import tempfile

import pytest

from pvtool import create_app, TestingConfig
from pvtool.db import db
from pvtool.routes._users import User

@pytest.fixture
def app():
    """skeleton for testing that is coming
    db_fd: file handle for temporary database"""
    # db_fd, db_path = tempfile.mkstemp()

    app = create_app(TestingConfig)

    ctx = app.app_context()
    ctx.push()
    yield app

    ctx.pop()

    # os.close(db_fd)
    # os.unlink(db_path)


@pytest.fixture
def client(app):
    """ Fixture to emulate client"""
    return app.test_client()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='TESTUSER', password='testpassword'):
        return self._client.post(
            '/signin',
            data={'user_name': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/signout')


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def init_db(app):
    db.create_all()

    new_user = User(2000, 'Hans',
                    'Jakob', 'Heiri')

    new_user.user_name = 'TESTUSER'
    new_user._password = 'testpassword'

    db.session.add(new_user)
    db.session.commit()

    yield db

    db.drop_all()


@pytest.fixture
def runner(app):
    """Fixture for Command Line Interface testing"""
    return app.test_cli_runner()


# add support for incremental tests
def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)
