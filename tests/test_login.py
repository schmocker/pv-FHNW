from flask import session



def test_login_logout(client, auth, init_db):
    """
    GIVEN a Flask app
    WHEN navigated to /login
    THEN check if login redirects to desired state
    """
    assert client.get('/data').status_code == 302
    assert client.get('/signin').status_code == 200
    response = auth.login()

    with client:
        client.get('/')
        print(session)

    assert client.get('/data').status_code == 200
    response = client.get('/signout', follow_redirects=True)

    assert response.status_code == 200
    assert 'Erfolgreich abgemeldet'

    assert client.get('/data').status_code == 302


def test_login_require(client, init_db):
    response = client.post('/data', follow_redirects=True)

    assert b'Bitte melden Sie sich an um diese Seite zu sehen.' in response.data
