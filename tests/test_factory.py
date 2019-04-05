import os
import tempfile

import pytest

from app import app

@pytest.fixture
def client():
    """skeleton for testing that is coming"""
    app.app.config['TESTING'] = True
    client = app.app.test_client()

    yield client
