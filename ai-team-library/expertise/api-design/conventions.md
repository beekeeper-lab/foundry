# API Design Stack Conventions

Non-negotiable defaults for API design on this team. Covers REST and GraphQL
conventions, versioning strategies, and general design principles. Deviations
require an ADR with justification. "I prefer it differently" is not
justification.

---

## Defaults

| Concern                | Default Choice                          | Override Requires |
|------------------------|-----------------------------------------|-------------------|
| API Style              | REST (JSON over HTTPS)                  | ADR               |
| API Spec Format        | OpenAPI 3.1                             | ADR               |
| Serialization          | JSON (`application/json`)               | ADR               |
| Versioning             | URL path prefix (`/v1/`, `/v2/`)        | ADR               |
| Naming Convention      | `snake_case` for JSON fields            | ADR               |
| Date/Time Format       | ISO 8601 (`2026-02-20T14:30:00Z`)       | Never             |
| ID Format              | UUID v7 (time-sortable)                 | ADR               |
| Pagination             | Cursor-based                            | ADR               |
| Error Format           | RFC 9457 (Problem Details)              | ADR               |
| Auth                   | OAuth 2.0 + Bearer tokens               | ADR               |
| Rate Limiting          | Token bucket per client                 | ADR               |
| HTTP Client            | Language-native HTTP client              | ADR               |
| Content Negotiation    | `Accept` / `Content-Type` headers       | Never             |
| TLS                    | TLS 1.3 minimum                         | Never             |

### Alternatives

| Primary                | Alternative            | When                                      |
|------------------------|------------------------|-------------------------------------------|
| REST                   | GraphQL                | Complex client-driven queries, mobile BFF |
| REST                   | gRPC                   | Internal service-to-service, high throughput |
| URL path versioning    | Header versioning      | Single-version APIs with content negotiation |
| URL path versioning    | Query param versioning | Quick prototyping only                    |
| Cursor pagination      | Offset pagination      | Small static datasets, admin UIs          |
| Cursor pagination      | Keyset pagination      | Direct DB integration, no opaque cursors  |
| UUID v7                | ULID                   | Environments without UUID v7 support      |
| UUID v7                | Auto-increment         | Never in public APIs, internal DBs only   |
| OAuth 2.0              | API keys               | Server-to-server, low-sensitivity data    |
| Token bucket           | Fixed window           | Simpler implementation, less precision    |

---

## REST Conventions

### URL Structure

```
# Resources are nouns, plural, lowercase
GET    /v1/orders                    # List orders
POST   /v1/orders                    # Create an order
GET    /v1/orders/{order_id}         # Get one order
PUT    /v1/orders/{order_id}         # Full replace
PATCH  /v1/orders/{order_id}         # Partial update
DELETE /v1/orders/{order_id}         # Delete

# Sub-resources for parent-child relationships
GET    /v1/orders/{order_id}/items              # List items in order
POST   /v1/orders/{order_id}/items              # Add item to order
GET    /v1/orders/{order_id}/items/{item_id}    # Get one item

# Actions as sub-resource verbs (only when CRUD doesn't fit)
POST   /v1/orders/{order_id}/cancel             # Cancel an order
POST   /v1/orders/{order_id}/items/{item_id}/return  # Return an item

# Filtering, sorting, field selection via query params
GET    /v1/orders?status=pending&sort=-created_at&fields=id,status,total
```

**Rules:**
- Resources are **plural nouns**: `/orders`, `/users`, `/invoices`.
- Use **kebab-case** for multi-word URLs: `/line-items`, `/payment-methods`.
- Use **snake_case** for query parameters and JSON fields.
- IDs in paths use the resource name prefix: `{order_id}`, `{user_id}`.
- Nest sub-resources at most **2 levels** deep. Beyond that, promote to a
  top-level resource with a filter.
- Use HTTP methods semantically: `GET` reads, `POST` creates, `PUT` replaces,
  `PATCH` updates partially, `DELETE` removes.
- `GET` and `DELETE` have **no request body**.
- `POST` returns `201 Created` with a `Location` header.
- `DELETE` returns `204 No Content`.
- `PUT` / `PATCH` return `200 OK` with the updated resource.

### Request/Response Envelope

```json
// Successful single resource (no envelope needed)
GET /v1/orders/019abc12-3456-7890-abcd-ef1234567890
{
  "id": "019abc12-3456-7890-abcd-ef1234567890",
  "status": "pending",
  "total_cents": 4999,
  "currency": "USD",
  "created_at": "2026-02-20T14:30:00Z",
  "updated_at": "2026-02-20T14:30:00Z"
}

// Successful collection (with pagination metadata)
GET /v1/orders?status=pending&limit=20
{
  "data": [
    { "id": "...", "status": "pending", "total_cents": 4999 }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6IjAxOWFiYzEyIn0=",
    "has_more": true
  }
}
```

**Rules:**
- Single resources are returned directly (no wrapper).
- Collections are wrapped in a `data` array with a `pagination` object.
- Monetary values are integers in the smallest currency unit (cents).
- Always include `created_at` and `updated_at` timestamps.
- Never include internal database fields (`_id`, `__v`, `row_version`).

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST (include `Location` header) |
| `204` | No Content | Successful DELETE |
| `301` | Moved Permanently | Resource URL changed permanently |
| `304` | Not Modified | Conditional GET with `ETag` / `If-None-Match` |
| `400` | Bad Request | Malformed request, validation failure |
| `401` | Unauthorized | Missing or invalid authentication |
| `403` | Forbidden | Authenticated but not authorized |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | Duplicate creation, version conflict |
| `422` | Unprocessable Entity | Valid syntax but semantic error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unhandled server error |
| `502` | Bad Gateway | Upstream service failure |
| `503` | Service Unavailable | Maintenance or overload |

---

## GraphQL Conventions

```graphql
# Schema-first design
type Query {
  order(id: ID!): Order
  orders(filter: OrderFilter, first: Int, after: String): OrderConnection!
}

type Mutation {
  createOrder(input: CreateOrderInput!): CreateOrderPayload!
  cancelOrder(input: CancelOrderInput!): CancelOrderPayload!
}

# Relay-style connection for pagination
type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type OrderEdge {
  node: Order!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Input types for mutations
input CreateOrderInput {
  items: [OrderItemInput!]!
  customerId: ID!
}

# Payload types with userErrors for validation
type CreateOrderPayload {
  order: Order
  userErrors: [UserError!]!
}

type UserError {
  field: [String!]
  message: String!
  code: ErrorCode!
}
```

**Rules:**
- Use **schema-first** design. Define the schema before implementation.
- Queries use **Relay-style connections** for pagination (`first`/`after`,
  `last`/`before`).
- Mutations follow the **input/payload pattern**: `xxxInput` → `xxxPayload`.
- Mutation payloads include `userErrors` for client-facing validation errors.
- Use `ID!` (non-null) for required identifiers.
- Naming: types are `PascalCase`, fields are `camelCase`, enums are
  `UPPER_SNAKE_CASE`.
- Implement **query complexity analysis** to prevent abusive queries.
- Set a **maximum depth limit** (default: 10 levels).
- Use **DataLoader** for N+1 prevention in resolvers.
- Implement **persisted queries** in production to prevent arbitrary query
  execution.

---

## Versioning

```
# URL path versioning (default)
/v1/orders
/v2/orders

# Header versioning (alternative)
Accept: application/vnd.myapi.v2+json
```

**Rules:**
- Increment the major version only for **breaking changes**: removing fields,
  changing field types, removing endpoints, changing behavior.
- Non-breaking changes do **not** require a new version: adding fields, adding
  endpoints, adding optional query parameters, adding new enum values.
- Support at most **2 concurrent versions** (current + previous).
- Deprecate the old version with a sunset timeline (minimum 6 months).
- Return a `Deprecation` header and `Sunset` header on deprecated versions.
- Document migration guides between versions.
- GraphQL: versioning is unnecessary when following additive-only schema
  evolution with `@deprecated` directives.

### Deprecation Headers

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 20 Aug 2027 00:00:00 GMT
Link: <https://api.example.com/docs/migration/v1-to-v2>; rel="deprecation"
```

---

## Request Headers

| Header | Purpose | Required |
|--------|---------|----------|
| `Authorization` | Bearer token | Yes (authenticated endpoints) |
| `Content-Type` | Request body format | Yes (POST/PUT/PATCH) |
| `Accept` | Desired response format | Recommended |
| `Idempotency-Key` | Prevent duplicate mutations | Recommended (POST) |
| `X-Request-ID` | Correlation ID for tracing | Recommended |
| `If-None-Match` | Conditional GET with ETag | Optional |
| `If-Match` | Optimistic concurrency control | Optional (PUT/PATCH) |

## Response Headers

| Header | Purpose | When |
|--------|---------|------|
| `Content-Type` | Response body format | Always |
| `Location` | URI of created resource | 201 responses |
| `ETag` | Resource version tag | GET single resource |
| `X-Request-ID` | Echo correlation ID | Always |
| `RateLimit-Limit` | Max requests per window | Always |
| `RateLimit-Remaining` | Remaining requests | Always |
| `RateLimit-Reset` | Window reset time (Unix) | Always |
| `Retry-After` | Seconds until retry | 429 and 503 responses |
| `Cache-Control` | Caching directives | GET responses |
| `Deprecation` | Version deprecated flag | Deprecated endpoints |
| `Sunset` | Removal date | Deprecated endpoints |

---

## Do / Don't

### Do
- Use plural nouns for resource names (`/orders`, not `/order`).
- Use HTTP methods semantically (GET reads, POST creates, etc.).
- Return appropriate HTTP status codes (not 200 for everything).
- Use `snake_case` for JSON fields consistently.
- Include `created_at` and `updated_at` on every resource.
- Use ISO 8601 for all dates and times with UTC timezone.
- Use integers for monetary values (cents, not dollars).
- Implement idempotency keys for non-idempotent operations.
- Version your API from day one (`/v1/`).
- Return the created/updated resource in the response body.
- Use `ETag` and `If-Match` for optimistic concurrency control.
- Provide `X-Request-ID` for distributed tracing.

### Don't
- Use verbs in resource URLs (`/getOrders` → `/orders`).
- Return 200 for errors. Use proper HTTP status codes.
- Include sensitive data in URLs (tokens, passwords, PII).
- Use camelCase or PascalCase in JSON fields.
- Return nested objects more than 3 levels deep in REST.
- Use auto-increment IDs in public APIs (leaks ordering info).
- Break existing clients silently. Version breaking changes.
- Mix singular and plural resource names in the same API.
- Use `PUT` for partial updates. Use `PATCH` instead.
- Return different response shapes for the same endpoint.
- Use HTTP status codes outside their defined semantics.

---

## Common Pitfalls

1. **Inconsistent naming** — Mixing `camelCase`, `snake_case`, and
   `PascalCase` in the same API confuses clients and breaks code generators.
   Pick one (we use `snake_case`) and enforce it with linting.

2. **Over-nesting URLs** — Deeply nested URLs like
   `/v1/orgs/{id}/teams/{id}/members/{id}/roles` are fragile and hard to
   cache. Flatten to top-level resources with filters beyond 2 levels.

3. **Missing pagination on collections** — Every endpoint that returns a
   list must be paginated. Unbounded collections will eventually time out
   or OOM as data grows.

4. **Chatty APIs without aggregation** — Requiring clients to make 10
   requests to render one screen kills performance. Design aggregate
   endpoints or use GraphQL for complex client needs.

5. **Ignoring idempotency** — Retrying a POST without an idempotency key
   creates duplicate resources. Always support `Idempotency-Key` headers
   for non-idempotent operations.

6. **Versioning too often** — Every version doubles maintenance cost. Only
   version for breaking changes. Additive changes (new fields, new
   endpoints) are backwards-compatible and do not need a version bump.

7. **Exposing internal models** — Returning database entities directly
   couples your API contract to your schema. Use separate DTO/response
   models that evolve independently.

8. **Missing correlation IDs** — Without `X-Request-ID` headers, debugging
   distributed failures requires log timestamp correlation which is slow
   and error-prone.

9. **No rate limiting from day one** — Adding rate limiting retroactively
   breaks clients that assumed unlimited access. Ship with rate limits and
   document them from the first release.

10. **Floating point for money** — Using `float` for monetary values causes
    rounding errors (`0.1 + 0.2 != 0.3`). Use integer cents or a decimal
    type with fixed precision.

---

## Checklist

- [ ] API spec defined in OpenAPI 3.1 before implementation begins.
- [ ] All endpoints use plural noun resource names.
- [ ] URL path versioning in place (`/v1/`).
- [ ] JSON fields use `snake_case` consistently.
- [ ] All dates/times are ISO 8601 with UTC timezone.
- [ ] Every collection endpoint is paginated (cursor-based by default).
- [ ] Error responses follow RFC 9457 Problem Details format.
- [ ] Rate limiting headers present on all responses.
- [ ] `Idempotency-Key` supported on POST/PUT endpoints.
- [ ] `X-Request-ID` echoed in all responses.
- [ ] Authentication via OAuth 2.0 Bearer tokens.
- [ ] No sensitive data in URLs or logs.
- [ ] No auto-increment IDs exposed in public API.
- [ ] Monetary values represented as integer cents.
- [ ] `ETag` / `If-Match` used for optimistic concurrency.
- [ ] GraphQL queries have complexity and depth limits.
- [ ] Deprecation headers set on sunset endpoints.
- [ ] Migration guide documented for each version transition.
- [ ] CORS configured for browser clients.
- [ ] TLS 1.3 enforced; no plaintext HTTP.
