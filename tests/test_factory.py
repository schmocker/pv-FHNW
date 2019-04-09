from pvtool import create_app


def test_config():
    """ Test if testing configuration is indeed passed to application"""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_home(client):
    response = client.get('/')
    assert response.data == b'Hello, World! '

