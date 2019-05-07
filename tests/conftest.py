import os
import tempfile

import pytest

from pvtool import create_app, TestingConfig
from pvtool.db import db
from pvtool.users import User

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

    user = User(user_name='TESTUSER',_password='testpassword')
    db.session.add(user)

    db.session.commit()

    yield db

    db.drop_all()

@pytest.fixture
def runner(app):
    """Fixture for Command Line Interface testing"""
    return app.test_cli_runner()
