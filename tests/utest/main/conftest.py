import pytest

@pytest.fixture(scope="function")
def log_in(client, user):
    resp = client.post('/auth/login', data = {
            "email": user.email,
            "password": "password"
        }, follow_redirects = True)
    assert resp.status_code == 200
    assert resp.request.path == "/"
    assert "Hello, " in resp.get_data(as_text=True)
    yield resp
    client.get('/auth/logout', follow_redirects = True)
    assert resp.request.path == "/"
    assert "Logged out successfully" in resp.get_data(as_text=True)
