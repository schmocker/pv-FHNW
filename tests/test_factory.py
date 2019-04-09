from pvtool import create_app


def test_config():
    """ Test if testing configuration is indeed passed to application"""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_links(client):
    """Testing the elements from nav bar"""
    assert client.get('/').status_code == 200
    assert client.get('/upload').status_code == 200
    assert client.get('/pv_modules').status_code == 200
    assert client.get('/data').status_code == 200

