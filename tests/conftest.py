import os
import tempfile

import pytest

from pvtool import create_app, TestingConfig


@pytest.fixture
def app():
    """skeleton for testing that is coming
    db_fd: file handle for temporary database"""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(TestingConfig)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
