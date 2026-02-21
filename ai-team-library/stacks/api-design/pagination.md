# API Design — Pagination

Every endpoint that returns a collection must be paginated. Unbounded lists
are a ticking time bomb — they work fine in dev with 10 records and OOM in
production with 10 million.

---

## Cursor-Based Pagination (Default)

Cursors are opaque tokens that point to a position in the result set. They
are stable under concurrent inserts/deletes and perform well at any offset.

### Request

```
GET /v1/orders?limit=20&cursor=eyJpZCI6IjAxOWFiYzEyIn0=
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Items per page (max: 100) |
| `cursor` | string | (none) | Opaque cursor from previous response |

### Response

```json
{
  "data": [
    { "id": "019abc12-...", "status": "pending", "total_cents": 4999 },
    { "id": "019abc13-...", "status": "shipped", "total_cents": 2499 }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6IjAxOWFiYzEzIn0=",
    "has_more": true
  }
}
```

### Implementation

```python
# Python / SQLAlchemy cursor pagination
import base64
import json
from sqlalchemy import select

def encode_cursor(record_id: str) -> str:
    return base64.urlsafe_b64encode(
        json.dumps({"id": record_id}).encode()
    ).decode()

def decode_cursor(cursor: str) -> str:
    payload = json.loads(base64.urlsafe_b64decode(cursor))
    return payload["id"]

async def list_orders(limit: int = 20, cursor: str | None = None):
    query = select(Order).order_by(Order.id)

    if cursor:
        last_id = decode_cursor(cursor)
        query = query.where(Order.id > last_id)

    query = query.limit(limit + 1)  # Fetch one extra to detect has_more
    results = await session.execute(query)
    rows = results.scalars().all()

    has_more = len(rows) > limit
    items = rows[:limit]

    return {
        "data": [serialize(item) for item in items],
        "pagination": {
            "next_cursor": encode_cursor(items[-1].id) if has_more else None,
            "has_more": has_more,
        },
    }
```

**Rules:**
- Cursors are **opaque** to clients. Never document the internal format.
- Encode cursor data as base64url to keep it URL-safe.
- Fetch `limit + 1` rows and check if the extra row exists to determine
  `has_more` without a separate count query.
- Default `limit` is 20, maximum is 100. Return `400` for values above max.
- The cursor is tied to the sort order. Changing sort invalidates cursors.
- Expired or invalid cursors return `400`, not `404`.

---

## Offset-Based Pagination (Alternative)

Use offset pagination only for small datasets, admin UIs, or when clients
need to jump to arbitrary pages.

### Request

```
GET /v1/admin/audit-logs?page=3&per_page=50
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `per_page` | integer | 20 | Items per page (max: 100) |

### Response

```json
{
  "data": [
    { "id": "...", "action": "order.created", "timestamp": "2026-02-20T14:30:00Z" }
  ],
  "pagination": {
    "page": 3,
    "per_page": 50,
    "total_count": 1247,
    "total_pages": 25
  }
}
```

**Rules:**
- Pages are **1-indexed** (page 1 is the first page, not page 0).
- Include `total_count` and `total_pages` only if the count query is cheap.
- For large tables, omit `total_count` (it requires a full table scan).
- Offset pagination is **unstable**: inserting a row shifts all subsequent
  pages. Clients may see duplicates or miss items.
- Maximum `per_page` is 100.

---

## Keyset Pagination (Alternative)

Keyset pagination is cursor pagination without the opaque encoding. Clients
pass the last seen sort key directly. Useful for internal APIs where
simplicity beats abstraction.

### Request

```
GET /v1/events?sort=created_at&after=2026-02-20T14:30:00Z&limit=50
```

### Response

```json
{
  "data": [
    {
      "id": "...",
      "event_type": "order.created",
      "created_at": "2026-02-20T14:31:00Z"
    }
  ],
  "pagination": {
    "last_created_at": "2026-02-20T15:00:00Z",
    "has_more": true
  }
}
```

**Rules:**
- The keyset column must be **indexed** and have a **stable sort order**.
- For non-unique columns (like `created_at`), add a tiebreaker (`id`).
- Clients pass the sort column value directly, not an opaque cursor.
- Suitable for internal APIs. Use opaque cursors for public APIs to avoid
  coupling clients to the sort implementation.

---

## GraphQL Pagination (Relay Connections)

```graphql
query {
  orders(first: 20, after: "cursor123") {
    edges {
      node {
        id
        status
        totalCents
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

**Rules:**
- Follow the **Relay Connection Specification** for all paginated fields.
- Use `first`/`after` for forward pagination, `last`/`before` for backward.
- `totalCount` is optional and should be omitted for large collections.
- Each edge has its own `cursor` for resuming from any position.
- Limit `first`/`last` to a maximum value (default: 100).
- Return `pageInfo.hasNextPage` / `hasPreviousPage` for navigation.

---

## Pagination Headers (Link Header)

For REST APIs, include RFC 8288 `Link` headers for discoverability:

```http
HTTP/1.1 200 OK
Link: <https://api.example.com/v1/orders?cursor=abc123>; rel="next",
      <https://api.example.com/v1/orders>; rel="first"
```

**Rules:**
- Include `rel="next"` when there are more pages.
- Include `rel="first"` to allow returning to the beginning.
- `rel="prev"` is optional for cursor pagination (cursors are forward-only
  by default).
- Offset pagination should include `rel="first"`, `rel="prev"`, `rel="next"`,
  and `rel="last"`.

---

## Do / Don't

### Do
- Default to cursor-based pagination for all new endpoints.
- Set a maximum page size (100) and reject larger requests.
- Use `limit + 1` fetch to determine `has_more` without count queries.
- Keep cursors opaque in public APIs.
- Include pagination metadata in every collection response.
- Index the columns used for cursor/keyset pagination.

### Don't
- Return unbounded collections. Every list endpoint must be paginated.
- Expose cursor internals (encoding format, field names) in documentation.
- Use offset pagination for large or frequently-mutated datasets.
- Allow `limit=0` or negative values. Validate and return `400`.
- Use `total_count` on tables with millions of rows (expensive full scan).
- Change cursor format without a version bump (breaks existing clients).

---

## Common Pitfalls

1. **Missing pagination on "small" collections** — Collections always grow.
   What has 5 items today will have 50,000 next year. Paginate from day one.

2. **COUNT(*) on large tables** — `total_count` requires scanning the entire
   table. For large datasets, omit it or cache it with a TTL.

3. **Offset instability** — Inserting a record between page fetches causes
   the client to see duplicates or skip items. Use cursor pagination for
   user-facing APIs.

4. **Non-indexed cursor column** — Cursor pagination degrades to a full
   table scan if the sort column lacks an index. Always verify the query
   plan.

5. **Leaking cursor format** — If clients parse cursors and build them
   manually, any change to the encoding breaks clients. Keep cursors opaque.

6. **No maximum page size** — Without a max, a client can request
   `limit=1000000` and exhaust server memory. Cap at 100.
