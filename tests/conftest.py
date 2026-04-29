import uuid
import os
import pytest
import requests

BASE_HOST = os.getenv("API_HOST", "http://localhost:3000")
AUTH_TOKEN = "mysecrettoken"
ALL_ENVIRONMENTS = ["dev", "prod"]


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=None,
        choices=["dev", "prod"],
        help="Target environment (dev | prod). Omit to run against both.",
    )


def pytest_generate_tests(metafunc):
    if "env" in metafunc.fixturenames:
        chosen = metafunc.config.getoption("--env")
        envs = [chosen] if chosen else ALL_ENVIRONMENTS
        metafunc.parametrize("env", envs)


@pytest.fixture(scope="session")
def base_host():
    return BASE_HOST


@pytest.fixture
def base_url(env, base_host):
    return f"{base_host}/{env}/users"


@pytest.fixture
def auth_token():
    return AUTH_TOKEN


@pytest.fixture
def new_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def valid_user_payload(new_email):
    return {"name": "Jane Doe", "email": new_email, "age": 30}


@pytest.fixture
def created_user(base_url, valid_user_payload):
    resp = requests.post(base_url, json=valid_user_payload)
    email = valid_user_payload["email"]
    yield resp, email
    requests.delete(
        f"{base_url}/{email}",
        headers={"Authorization": AUTH_TOKEN},
    )