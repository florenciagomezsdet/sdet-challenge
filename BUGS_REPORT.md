# Bugs Report — User Management API

## Overview

During the development of the test suite, the following discrepancies were found
between the API's actual behavior and the OpenAPI specification.

---

## BUG-001 — Duplicate email returns 500 instead of 409

**Endpoint:** `POST /{env}/users`
**Severity:** High

**Expected:** `409 Conflict`
**Actual:** `500 Internal Server Error`

**Test:** `TestCreateUser::test_create_duplicate_email_returns_409`

---

## BUG-002 — Invalid email format is accepted

**Endpoint:** `POST /{env}/users`
**Severity:** High

**Expected:** `400 Bad Request` for emails like `not-an-email`
**Actual:** `201 Created` — the API accepts invalid email formats

**Test:** `TestCreateUser::test_create_invalid_email_returns_400`

---

## BUG-003 — GET nonexistent user returns 500 instead of 404

**Endpoint:** `GET /{env}/users/{email}`
**Severity:** High

**Expected:** `404 Not Found`
**Actual:** `500 Internal Server Error`

**Test:** `TestGetUser::test_get_nonexistent_user_returns_404`

---

## BUG-004 — PUT does not update user data

**Endpoint:** `PUT /{env}/users/{email}`
**Severity:** Critical

**Expected:** User data is updated and new values are returned
**Actual:** API returns `200 OK` but data remains unchanged

**Test:** `TestUpdateUser::test_update_reflects_new_data`

---

## BUG-005 — GET after DELETE returns 500 instead of 404

**Endpoint:** `GET /{env}/users/{email}`
**Severity:** High

**Expected:** `404 Not Found` after deleting a user
**Actual:** `500 Internal Server Error`

**Test:** `TestDeleteUser::test_deleted_user_returns_404`

---

## BUG-006 — DELETE ignores authentication token

**Endpoint:** `DELETE /{env}/users/{email}`
**Severity:** Critical

**Expected:** `401 Unauthorized` when no token or wrong token is provided
**Actual:** `204 No Content` — the API deletes the user regardless of authentication

**Tests:**
- `TestDeleteUser::test_delete_without_token_returns_401`
- `TestDeleteUser::test_delete_with_invalid_token_returns_401`

---

## Summary

| ID | Endpoint | Severity | Status |
|---|---|---|---|
| BUG-001 | POST /users | High | Open |
| BUG-002 | POST /users | High | Open |
| BUG-003 | GET /users/{email} | High | Open |
| BUG-004 | PUT /users/{email} | Critical | Open |
| BUG-005 | GET /users/{email} | High | Open |
| BUG-006 | DELETE /users/{email} | Critical | Open |