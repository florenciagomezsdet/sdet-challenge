# Bugs Report — User Management API

## Overview

During the development of the test suite, the following discrepancies were found
between the API's actual behavior and the OpenAPI specification.
Tests were run against both `dev` and `prod` environments locally via Docker.

---

## Executive Summary

7 bugs were identified across both environments. 2 are **Critical** severity
(data not persisted on PUT, authentication bypassed or broken on DELETE).
The `dev` and `prod` environments exhibit **different behaviors** for the same
endpoints, suggesting inconsistent middleware configuration rather than a single
shared defect.

---

## BUG-001 — Duplicate email returns 500 instead of 409

**Endpoint:** `POST /{env}/users`
**Severity:** High
**Environments:** dev, prod

**Request:**
POST /dev/users
{"name": "Duplicate", "email": "exists@example.com", "age": 20}

**Expected:** `409 Conflict` `{"error": "..."}`
**Actual:** `500 Internal Server Error`

**Test:** `TestCreateUser::test_create_duplicate_email_returns_409`

---

## BUG-002 — Invalid email format is accepted

**Endpoint:** `POST /{env}/users`
**Severity:** High
**Environments:** dev, prod

**Request:**
POST /dev/users
{"name": "Bad", "email": "not-an-email", "age": 25}

**Expected:** `400 Bad Request`
**Actual:** `201 Created` — the API accepts invalid email formats without validation

**Test:** `TestCreateUser::test_create_invalid_email_returns_400`

---

## BUG-003 — GET nonexistent user returns 500 instead of 404

**Endpoint:** `GET /{env}/users/{email}`
**Severity:** High
**Environments:** dev, prod

**Request:**
GET /dev/users/ghost@example.com

**Expected:** `404 Not Found` `{"error": "..."}`
**Actual:** `500 Internal Server Error`

**Test:** `TestGetUser::test_get_nonexistent_user_returns_404`

---

## BUG-004 — PUT does not update user data

**Endpoint:** `PUT /{env}/users/{email}`
**Severity:** Critical
**Environments:** dev, prod

**Request:**
PUT /dev/users/jane@example.com
{"name": "Updated Name", "email": "jane@example.com", "age": 35}

**Expected:** User data updated, GET returns new values
**Actual:** `200 OK` is returned but data remains unchanged — GET still returns original values

**Test:** `TestUpdateUser::test_update_reflects_new_data`

---

## BUG-005 — Authentication not enforced in dev environment

**Endpoint:** `DELETE /{env}/users/{email}`
**Severity:** Critical
**Environments:** dev only

**Request:**
DELETE /dev/users/jane@example.com
(no Authorization header)

**Expected:** `401 Unauthorized`
**Actual:** `204 No Content` — user is deleted regardless of missing or invalid token

**Tests:**
- `TestDeleteUser::test_delete_without_token_returns_401`
- `TestDeleteUser::test_delete_with_invalid_token_returns_401`

---

## BUG-006 — Valid token rejected in prod environment

**Endpoint:** `DELETE /{env}/users/{email}`
**Severity:** Critical
**Environments:** prod only

**Request:**
DELETE /prod/users/jane@example.com
Authorization: mysecrettoken

**Expected:** `204 No Content`
**Actual:** `401 Unauthorized` — the API rejects the correct token in prod

**Tests:**
- `TestDeleteUser::test_delete_with_valid_token_returns_204`
- `TestDeleteUser::test_delete_nonexistent_user_returns_404`

---

## BUG-007 — GET after DELETE returns 200 instead of 404 in prod

**Endpoint:** `GET /{env}/users/{email}`
**Severity:** High
**Environments:** prod only

**Request:**
DELETE /prod/users/jane@example.com  → (fails due to BUG-006)
GET    /prod/users/jane@example.com

**Expected:** `404 Not Found`
**Actual:** `200 OK` — user still exists because DELETE failed silently

**Note:** This bug is a downstream effect of BUG-006.

**Test:** `TestDeleteUser::test_deleted_user_returns_404`

---

## Summary

| ID | Endpoint | Severity | Environments | Status |
|---|---|---|---|---|
| BUG-001 | POST /users | High | dev, prod | Open |
| BUG-002 | POST /users | High | dev, prod | Open |
| BUG-003 | GET /users/{email} | High | dev, prod | Open |
| BUG-004 | PUT /users/{email} | Critical | dev, prod | Open |
| BUG-005 | DELETE /users/{email} | Critical | dev only | Open |
| BUG-006 | DELETE /users/{email} | Critical | prod only | Open |
| BUG-007 | GET /users/{email} | High | prod only | Open |