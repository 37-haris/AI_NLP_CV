# Authentication API

Base prefix: `/auth`

---

## POST /auth/register

Register a new user account.

**Request body**

```json
{
  "username":  "john_doe",
  "firstname": "John",
  "lastname":  "Doe",
  "password":  "secret123"
}
```

**Validation rules**

- `username`: 3–50 characters
- `firstname` / `lastname`: 1–50 characters
- `password`: minimum 6 characters

**Responses**

| Status | Description |
|---|---|
| `201 Created` | `{"message": "Compte créé avec succès."}` |
| `409 Conflict` | Username already taken |
| `422 Unprocessable` | Validation failed |

---

## POST /auth/login

Authenticate and receive a JWT cookie.

**Request body**

```json
{
  "username": "john_doe",
  "password": "secret123"
}
```

**Responses**

| Status | Description |
|---|---|
| `200 OK` | Sets `access_token` httponly cookie, returns user info |
| `401 Unauthorized` | Wrong username or password |

**Success response**

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "firstname": "John",
    "lastname": "Doe"
  }
}
```

!!! info "Cookie"
    The `access_token` cookie is `httponly` (not accessible by JS) and expires after **1 hour**.

---

## GET /auth/logout

Destroy the session by deleting the JWT cookie.

**Responses**

| Status | Description |
|---|---|
| `302 Redirect` | Cookie deleted → redirected to `/` |

---

## POST /auth/predict

Upload an image and receive bilingual captions.

**Request** — `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `image` | file | Yes | Image file to caption |
| `user_text` | string | No | Optional note appended to caption |

**Responses**

| Status | Description |
|---|---|
| `200 OK` | Returns EN + FR captions and saved image path |
| `500 Error` | Model or translation failure |

**Success response**

```json
{
  "en": "A cat sitting on a windowsill looking outside.",
  "fr": "Un chat assis sur un rebord de fenêtre regardant dehors.",
  "image_path": "/static/uploads/1/a3f8c2d1.jpg"
}
```