import uuid
import requests

AUTH_TOKEN = "mysecrettoken"

def _unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def _delete(base_url, email):
    requests.delete(f"{base_url}/{email}", headers={"Authorization": AUTH_TOKEN})


class TestListUsers:

    def test_returns_200(self, base_url):
        resp = requests.get(base_url)
        assert resp.status_code == 200

    def test_response_is_json_array(self, base_url):
        resp = requests.get(base_url)
        assert isinstance(resp.json(), list)

    def test_content_type_is_json(self, base_url):
        resp = requests.get(base_url)
        assert "application/json" in resp.headers.get("Content-Type", "")

    def test_created_user_appears_in_list(self, base_url, created_user):
        _, email = created_user
        resp = requests.get(base_url)
        emails = [u["email"] for u in resp.json()]
        assert email in emails

    def test_environments_are_isolated(self, base_host, env):
        other_env = "prod" if env == "dev" else "dev"
        email = _unique_email()
        payload = {"name": "Isolation Test", "email": email, "age": 22}
        requests.post(f"{base_host}/{env}/users", json=payload)
        try:
            other_list = requests.get(f"{base_host}/{other_env}/users").json()
            other_emails = [u["email"] for u in other_list]
            assert email not in other_emails
        finally:
            _delete(f"{base_host}/{env}/users", email)


class TestCreateUser:

    def test_create_valid_user_returns_201(self, base_url):
        email = _unique_email()
        resp = requests.post(base_url, json={"name": "John Smith", "email": email, "age": 25})
        try:
            assert resp.status_code == 201
        finally:
            _delete(base_url, email)

    def test_create_returns_user_object(self, base_url):
        email = _unique_email()
        payload = {"name": "John Smith", "email": email, "age": 25}
        resp = requests.post(base_url, json=payload)
        try:
            assert resp.status_code == 201
            data = resp.json()
            assert data["name"] == payload["name"]
            assert data["email"] == payload["email"]
            assert data["age"] == payload["age"]
        finally:
            _delete(base_url, email)

    def test_create_duplicate_email_returns_409(self, base_url, created_user):
        _, email = created_user
        resp = requests.post(base_url, json={"name": "Duplicate", "email": email, "age": 20})
        assert resp.status_code == 409
        assert "error" in resp.json()

    def test_create_missing_name_returns_400(self, base_url):
        resp = requests.post(base_url, json={"email": _unique_email(), "age": 25})
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_create_missing_email_returns_400(self, base_url):
        resp = requests.post(base_url, json={"name": "No Email", "age": 25})
        assert resp.status_code == 400

    def test_create_missing_age_returns_400(self, base_url):
        resp = requests.post(base_url, json={"name": "No Age", "email": _unique_email()})
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_create_invalid_email_returns_400(self, base_url):
        resp = requests.post(base_url, json={"name": "Bad", "email": "not-an-email", "age": 25})
        assert resp.status_code == 400

    def test_create_age_zero_returns_400(self, base_url):
        resp = requests.post(base_url, json={"name": "Zero", "email": _unique_email(), "age": 0})
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_create_age_above_max_returns_400(self, base_url):
        resp = requests.post(base_url, json={"name": "Old", "email": _unique_email(), "age": 151})
        assert resp.status_code == 400
        assert "error" in resp.json()
        
    def test_create_age_1_is_valid(self, base_url):
        email = _unique_email()
        resp = requests.post(base_url, json={"name": "Young", "email": email, "age": 1})
        try:
            assert resp.status_code == 201
        finally:
            _delete(base_url, email)

    def test_create_age_150_is_valid(self, base_url):
        email = _unique_email()
        resp = requests.post(base_url, json={"name": "Elder", "email": email, "age": 150})
        try:
            assert resp.status_code == 201
        finally:
            _delete(base_url, email)

    def test_create_empty_body_returns_400(self, base_url):
        resp = requests.post(base_url, json={})
        assert resp.status_code == 400
        assert "error" in resp.json()   


class TestGetUser:

    def test_get_existing_user_returns_200(self, base_url, created_user):
        _, email = created_user
        resp = requests.get(f"{base_url}/{email}")
        assert resp.status_code == 200

    def test_get_user_returns_correct_data(self, base_url, created_user, valid_user_payload):
        _, email = created_user
        data = requests.get(f"{base_url}/{email}").json()
        assert data["email"] == valid_user_payload["email"]
        assert data["name"] == valid_user_payload["name"]
        assert data["age"] == valid_user_payload["age"]

    def test_get_nonexistent_user_returns_404(self, base_url):
        resp = requests.get(f"{base_url}/ghost@example.com")
        assert resp.status_code == 404
        assert "error" in resp.json()


class TestUpdateUser:

    def test_update_user_returns_200(self, base_url, created_user):
        _, email = created_user
        resp = requests.put(f"{base_url}/{email}", json={"name": "Updated", "email": email, "age": 35})
        assert resp.status_code == 200

    def test_update_reflects_new_data(self, base_url, created_user):
        _, email = created_user
        requests.put(f"{base_url}/{email}", json={"name": "Updated", "email": email, "age": 35})
        data = requests.get(f"{base_url}/{email}").json()
        assert data["name"] == "Updated"
        assert data["age"] == 35

    def test_update_nonexistent_user_returns_404(self, base_url):
        email = "ghost@example.com"
        resp = requests.put(f"{base_url}/{email}", json={"name": "Ghost", "email": email, "age": 30})
        assert resp.status_code == 404

    def test_update_missing_name_returns_400(self, base_url, created_user):
        _, email = created_user
        resp = requests.put(f"{base_url}/{email}", json={"email": email, "age": 35})
        assert resp.status_code == 400

    def test_update_age_zero_returns_400(self, base_url, created_user):
        _, email = created_user
        resp = requests.put(f"{base_url}/{email}", json={"name": "Name", "email": email, "age": 0})
        assert resp.status_code == 400

    def test_update_invalid_email_returns_400(self, base_url, created_user):
        _, email = created_user
        resp = requests.put(f"{base_url}/{email}", json={"name": "Name", "email": "not-valid", "age": 30})
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_update_missing_age_returns_400(self, base_url, created_user):
        _, email = created_user
        resp = requests.put(f"{base_url}/{email}", json={"name": "Name", "email": email})
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_update_age_above_max_returns_400(self, base_url, created_user):
        _, email = created_user
        resp = requests.put(f"{base_url}/{email}", json={"name": "Name", "email": email, "age": 151})
        assert resp.status_code == 400
        assert "error" in resp.json()


class TestDeleteUser:

    def test_delete_with_valid_token_returns_204(self, base_url):
        email = _unique_email()
        requests.post(base_url, json={"name": "To Delete", "email": email, "age": 25})
        resp = requests.delete(f"{base_url}/{email}", headers={"Authorization": AUTH_TOKEN})
        assert resp.status_code == 204

    def test_deleted_user_returns_404(self, base_url):
        email = _unique_email()
        requests.post(base_url, json={"name": "To Delete", "email": email, "age": 25})
        requests.delete(f"{base_url}/{email}", headers={"Authorization": AUTH_TOKEN})
        assert requests.get(f"{base_url}/{email}").status_code == 404

    def test_delete_without_token_returns_401(self, base_url, created_user):
        _, email = created_user
        resp = requests.delete(f"{base_url}/{email}")
        assert resp.status_code == 401
        assert "error" in resp.json()

    def test_delete_with_invalid_token_returns_401(self, base_url, created_user):
        _, email = created_user
        resp = requests.delete(f"{base_url}/{email}", headers={"Authorization": "wrong-token"})
        assert resp.status_code == 401

    def test_delete_nonexistent_user_returns_404(self, base_url):
        resp = requests.delete(f"{base_url}/ghost@example.com", headers={"Authorization": AUTH_TOKEN})
        assert resp.status_code == 404