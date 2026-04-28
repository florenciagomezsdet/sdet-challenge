# Bugs Report — User Management API

## Overview

During the development of the test suite, the following discrepancies were found
between the API's actual behavior and the OpenAPI specification (`sdet_challenge_api.yml`).

---

## BUG-001 — POST /users returns 200 instead of 201

**Endpoint:** `POST /{env}/users`
**Severity:** High
**Environments:** dev, prod

**Expected (per spec):** `201 Created`
**Actual:** `200 OK`

**Test that exposes it:** `TestCreateUser::test_create_valid_user_returns_201`

---

## BUG-002 — Age validation not enforced on POST and PUT

**Endpoint:** `POST /{env}/users` · `PUT /{env}/users/{email}`
**Severity:** High
**Environments:** dev, prod

**Expected (per spec):** `age` must be between 1 and 150. Values `0` or `151`
should return `400 Bad Request`.
**Actual:** The API accepts age values outside the valid range without returning an error.

**Tests that expose it:**
- `TestCreateUser::test_create_age_zero_returns_400`
- `TestCreateUser::test_create_age_above_max_returns_400`
- `TestUpdateUser::test_update_age_zero_returns_400`

---

## BUG-003 — DELETE without auth token returns 204 instead of 401

**Endpoint:** `DELETE /{env}/users/{email}`
**Severity:** Critical
**Environments:** dev, prod

**Expected (per spec):** Requests without the `Authentication` header should
return `401 Unauthorized`.
**Actual:** The API deletes the user and returns `204 No Content` even without
a valid token.

**Test that exposes it:** `TestDeleteUser::test_delete_without_token_returns_401`

---

## BUG-004 — Environments are not isolated (shared database)

**Endpoint:** All endpoints
**Severity:** High
**Environments:** dev + prod

**Expected (per spec):** "Each environment maintains its own separate database."
Users created in `dev` must not appear in `prod` and vice versa.
**Actual:** Both environments share the same database. A user created in `dev`
is visible in `prod`.

**Test that exposes it:** `TestListUsers::test_environments_are_isolated`

---

## Summary

| ID | Endpoint | Severity | Status |
|---|---|---|---|
| BUG-001 | POST /users | High | Open |
| BUG-002 | POST and PUT /users | High | Open |
| BUG-003 | DELETE /users/{email} | Critical | Open |
| BUG-004 | All endpoints | High | Open |