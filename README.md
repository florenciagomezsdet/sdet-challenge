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


## Test Design Decisions

**Environment parametrization:** Instead of duplicating test files per environment,
a single suite is parametrized via `pytest_generate_tests`. This keeps tests DRY
and guarantees identical coverage across `dev` and `prod`.

**Unique emails per test:** Each test generates a UUID-based email to avoid state
pollution between tests, making the suite safe to run in parallel.

**Teardown strategy:** The `created_user` fixture uses `yield` with a best-effort
delete in teardown, ensuring cleanup even when assertions fail.

**Authorization header finding:** During testing, it was discovered that `dev` and
`prod` behave differently regarding authentication — `dev` ignores the token entirely
(BUG-005) while `prod` rejects even valid tokens (BUG-006). This suggests different
middleware configurations per environment.

**fail-fast: false in CI:** The matrix strategy intentionally never cancels the
sibling job on failure. This ensures both environments always produce a report,
even when one has critical bugs.