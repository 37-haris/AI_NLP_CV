# Chat API

Base prefix: `/chats`

!!! warning "Authentication required"
    All endpoints require a valid `access_token` cookie. Requests without it return `401 Unauthorized`.

---

## GET /chats/

Get all chats for the logged-in user.

**Response**

```json
[
  {"id": 3, "title": "Cat on a roof",     "created_at": "2025-01-15 10:30:00"},
  {"id": 2, "title": "Sunset photo",      "created_at": "2025-01-14 18:20:00"},
  {"id": 1, "title": "Image description", "created_at": "2025-01-13 09:10:00"}
]
```

---

## POST /chats/

Create a new chat.

**Request body**

```json
{ "title": "Cat on a roof" }
```

**Response** `201 Created`

```json
{ "chat_id": 4, "title": "Cat on a roof" }
```

---

## GET /chats/{chat_id}/messages

Get all messages in a chat ordered oldest to newest.

**Response**

```json
[
  {
    "id": 1,
    "role": "user",
    "content": "My cat photo",
    "image_path": "/static/uploads/1/abc123.jpg",
    "created_at": "2025-01-15 10:30:00"
  },
  {
    "id": 2,
    "role": "ai",
    "content": "{\"en\": \"A cat sitting...\", \"fr\": \"Un chat assis...\"}",
    "image_path": null,
    "created_at": "2025-01-15 10:30:05"
  }
]
```

---

## POST /chats/{chat_id}/messages

Save a message to a chat.

**Request body**

```json
{
  "chat_id":    1,
  "role":       "user",
  "content":    "My cat photo",
  "image_path": "/static/uploads/1/abc123.jpg"
}
```

| Field | Required | Description |
|---|---|---|
| `chat_id` | Yes | Parent chat ID |
| `role` | Yes | `"user"` or `"ai"` |
| `content` | Yes | Text or JSON string `{"en":"...","fr":"..."}` |
| `image_path` | No | Path to saved image (user messages only) |

---

## PATCH /chats/{chat_id}/title

Update the title of a chat.

**Request body**

```json
{ "title": "New title" }
```

---

## DELETE /chats/{chat_id}

Delete a chat and all its messages.

**Response** `200 OK`

```json
{ "message": "Chat deleted." }
```