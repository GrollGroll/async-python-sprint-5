from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_ping_database():
    response = client.get(app.url_path_for('ping_database'))
    assert response.status_code == 200


# def test_create_user():
#     test_json = {"name": "example", "password": "example_password"}
#     response = client.post(app.url_path_for('create_user'), json=test_json)
#     assert response.status_code == 200


# def test_auth_user():
#     request_data = {"username": "example", "password": "example_password"}
#     response = client.post(app.url_path_for('auth_user'), data=request_data)
#     assert response.status_code == 200


# def test_auth_user_with_invalid_password():
#     request_data = {"username": "example", "password": "noncorrect_password"}
#     response = client.post(app.url_path_for('auth_user'), data=request_data)
#     assert response.status_code == 400


# def test_auth_user_with_invalid_username():
#     request_data = {"username": "noncorrect_username", "password": "example_password"}
#     response = client.post(app.url_path_for('auth_user'), data=request_data)
#     assert response.status_code == 400


# def test_read_users_me():
#     token = 'LQo9G4klEu27cQ'
#     test_headers = {"Authorization": f"Bearer {token}"}
#     response = client.get(app.url_path_for('read_users_me'), headers=test_headers)
#     assert response.status_code == 200


# def test_get_files():
#     token = 'LQo9G4klEu27cQ'
#     test_headers = {"Authorization": f"Bearer {token}"}
#     response = client.get(app.url_path_for('read_users_me'), headers=test_headers)
#     assert response.status_code == 200
