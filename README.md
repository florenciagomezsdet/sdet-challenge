# SDET Take-Home Challenge — User Management API

## Description

End-to-end test suite for the User Management API, covering all CRUD operations
across `dev` and `prod` environments.

## Tech Stack

- **Language:** Python 3.12
- **Test Framework:** pytest
- **HTTP Client:** requests
- **Reports:** pytest-html

## Project Structure

sdet-challenge/
├── .github/
│   └── workflows/
│       └── e2e.yml        # CI pipeline (parallel dev + prod)
├── tests/
│   ├── conftest.py        # Fixtures and env parametrization
│   └── test_users_api.py  # Full E2E test suite
├── reports/               # HTML test reports (generated)
├── BUGS_REPORT.md         # Bugs found during testing
├── README.md
├── pytest.ini
└── requirements.txt

## Setup

### 1. Start the API

```bash
docker run -p 3000:3000 ghcr.io/danielsilva-loanpro/sdet-interview-challenge:latest
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run tests

```bash
# Both environments
pytest tests/ -v

# Dev only
pytest tests/ --env=dev -v

# Prod only
pytest tests/ --env=prod -v
```

### 4. Generate HTML report

```bash
pytest tests/ --env=dev --html=reports/report-dev.html --self-contained-html
```

## CI Pipeline

The GitHub Actions workflow runs `dev` and `prod` in **parallel** using a matrix
strategy. Each job starts its own Docker container and uploads an HTML report as
an artifact. Both jobs run independently (`fail-fast: false`) so a failure in
one environment never blocks the other.

## Test Coverage

| Suite | Scenarios covered |
|---|---|
| `TestListUsers` | 200 response, JSON array, user in list, env isolation |
| `TestCreateUser` | 201 created, 400 validation, 409 duplicate, age boundaries |
| `TestGetUser` | 200 found, 404 not found, correct data returned |
| `TestUpdateUser` | 200 updated, 400 validation, 404 not found |
| `TestDeleteUser` | 204 deleted, 401 no auth, 401 wrong token, 404 not found |

## Bugs Found

See [BUGS_REPORT.md](./BUGS_REPORT.md) for the full list of discrepancies found
between the API behavior and the OpenAPI specification.