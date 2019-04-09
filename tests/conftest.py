import os
import tempfile

import pytest

from pvtool import create_app

@pytest.fixture
def app():
    """skeleton for testing that is coming
    db_fd: file handle for temporary database"""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """ Use client to make requests to application"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """ Create runner that registers click commands"""
    return app.test_cli_runner()
