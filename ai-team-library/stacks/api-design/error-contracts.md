# API Design — Error Contracts

Standardized error handling for all APIs. Follows RFC 9457 (Problem Details for
HTTP APIs) as the canonical error format. Every error response must be
machine-parseable and human-readable.

---

## Error Response Format (RFC 9457)

```json
// Standard problem details response
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 422,
  "detail": "The request body contains 2 validation errors.",
  "instance": "/v1/orders",
  "request_id": "req_019abc12-3456-7890",
  "errors": [
    {
      "field": "items[0].quantity",
      "code": "out_of_range",
      "message": "Quantity must be between 1 and 999.",
      "meta": { "min": 1, "max": 999, "actual": 0 }
    },
    {
      "field": "customer_id",
      "code": "not_found",
      "message": "Customer does not exist."
    }
  ]
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | `string` (URI) | Machine-readable error type identifier. Dereferenceable URL to documentation. |
| `title` | `string` | Human-readable summary. Same for all instances of this type. |
| `status` | `integer` | HTTP status code (mirrors the response status). |
| `detail` | `string` | Human-readable explanation specific to this occurrence. |
| `instance` | `string` | URI of the request that caused the error. |

### Extension Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | `string` | Correlation ID for tracing. Echoes `X-Request-ID`. |
| `errors` | `array` | Structured list of individual errors (validation, etc.). |
| `retry_after` | `integer` | Seconds until the client should retry (429, 503). |

---

## Error Catalog

Define error types as a stable catalog. Each type has a permanent URI, a
default title, and a recommended HTTP status code.

```yaml
# errors/catalog.yaml
errors:
  validation_failed:
    type: "https://api.example.com/errors/validation-failed"
    title: "Validation Failed"
    status: 422

  not_found:
    type: "https://api.example.com/errors/not-found"
    title: "Not Found"
    status: 404

  unauthorized:
    type: "https://api.example.com/errors/unauthorized"
    title: "Unauthorized"
    status: 401

  forbidden:
    type: "https://api.example.com/errors/forbidden"
    title: "Forbidden"
    status: 403

  conflict:
    type: "https://api.example.com/errors/conflict"
    title: "Conflict"
    status: 409

  rate_limited:
    type: "https://api.example.com/errors/rate-limited"
    title: "Rate Limit Exceeded"
    status: 429

  internal_error:
    type: "https://api.example.com/errors/internal-error"
    title: "Internal Server Error"
    status: 500

  service_unavailable:
    type: "https://api.example.com/errors/service-unavailable"
    title: "Service Unavailable"
    status: 503
```

**Rules:**
- Error `type` URIs are **permanent**. Once published, never change them.
- The `type` URI should resolve to a documentation page explaining the error.
- Use `about:blank` as the `type` when no additional semantics beyond the HTTP
  status are needed.
- Keep the catalog in a shared module consumed by all services.

---

## Validation Errors

```json
// Field-level validation errors
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 422,
  "detail": "The request body contains 3 validation errors.",
  "instance": "/v1/orders",
  "request_id": "req_019abc12-3456-7890",
  "errors": [
    {
      "field": "email",
      "code": "invalid_format",
      "message": "Must be a valid email address."
    },
    {
      "field": "items",
      "code": "required",
      "message": "At least one item is required."
    },
    {
      "field": "items[0].quantity",
      "code": "out_of_range",
      "message": "Must be between 1 and 999.",
      "meta": { "min": 1, "max": 999 }
    }
  ]
}
```

### Error Codes

Use a fixed vocabulary of error codes across all services:

| Code | Meaning |
|------|---------|
| `required` | Field is missing or null |
| `invalid_format` | Value does not match expected format |
| `out_of_range` | Value is outside allowed min/max |
| `too_short` | String is shorter than minimum length |
| `too_long` | String exceeds maximum length |
| `not_found` | Referenced resource does not exist |
| `already_exists` | Unique constraint violation |
| `immutable` | Field cannot be changed after creation |
| `unauthorized` | Authentication required |
| `forbidden` | Insufficient permissions |
| `conflict` | Concurrent modification conflict |

**Rules:**
- Error codes are **lowercase snake_case** strings.
- Return **all** validation errors in one response, not one at a time.
- The `field` uses dot notation for nested fields and bracket notation for
  arrays: `address.city`, `items[0].quantity`.
- Include `meta` with constraint details so clients can build localized
  messages.

---

## Authentication & Authorization Errors

```json
// 401 Unauthorized — missing or invalid token
{
  "type": "https://api.example.com/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Bearer token is expired. Obtain a new token from /oauth/token."
}

// 403 Forbidden — valid token, insufficient permissions
{
  "type": "https://api.example.com/errors/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "Role 'viewer' cannot perform 'orders:delete'.",
  "request_id": "req_019abc12-3456-7890"
}
```

**Rules:**
- `401` means "who are you?" — missing, expired, or malformed credentials.
- `403` means "I know who you are, but you can't do this."
- Never reveal **why** authentication failed in detail (e.g., "password
  incorrect" vs "user not found"). Return a generic message.
- Include the `WWW-Authenticate` header on 401 responses.

---

## Conflict & Concurrency Errors

```json
// 409 Conflict — optimistic concurrency failure
{
  "type": "https://api.example.com/errors/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "Resource was modified by another request. Fetch the latest version and retry.",
  "request_id": "req_019abc12-3456-7890",
  "meta": {
    "expected_version": "etag-abc123",
    "current_version": "etag-def456"
  }
}
```

**Rules:**
- Use `ETag` / `If-Match` for optimistic concurrency control.
- Return `409` when the client's `If-Match` header does not match the current
  resource version.
- Include both the expected and current versions in the error response.
- Clients must re-fetch the resource and reapply their changes.

---

## Server Errors

```json
// 500 Internal Server Error
{
  "type": "https://api.example.com/errors/internal-error",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred. Reference ID: req_019abc12-3456-7890.",
  "request_id": "req_019abc12-3456-7890"
}

// 503 Service Unavailable
{
  "type": "https://api.example.com/errors/service-unavailable",
  "title": "Service Unavailable",
  "status": 503,
  "detail": "The service is temporarily unavailable. Please retry after 30 seconds.",
  "retry_after": 30,
  "request_id": "req_019abc12-3456-7890"
}
```

**Rules:**
- Never expose stack traces, internal paths, or implementation details in
  error responses.
- Log the full error server-side with the `request_id` for correlation.
- Include `Retry-After` header on 503 responses.
- 5xx errors should be generic to the client but detailed in server logs.

---

## GraphQL Error Format

```json
{
  "data": null,
  "errors": [
    {
      "message": "Order not found.",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["order"],
      "extensions": {
        "code": "NOT_FOUND",
        "request_id": "req_019abc12-3456-7890"
      }
    }
  ]
}
```

**Rules:**
- Follow the GraphQL spec error format with `extensions` for custom fields.
- Use `extensions.code` for machine-readable error classification.
- Mutation validation errors go in the payload's `userErrors` field, not in
  top-level `errors`.
- Top-level `errors` are for system-level issues (auth, rate limiting, query
  errors).
- Always include `request_id` in `extensions` for tracing.

---

## Implementation Pattern

```python
# Python / FastAPI example
from fastapi import Request
from fastapi.responses import JSONResponse

class ApiError(Exception):
    def __init__(self, type_uri: str, title: str, status: int, detail: str,
                 errors: list | None = None):
        self.type_uri = type_uri
        self.title = title
        self.status = status
        self.detail = detail
        self.errors = errors

async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    body = {
        "type": exc.type_uri,
        "title": exc.title,
        "status": exc.status,
        "detail": exc.detail,
        "instance": str(request.url.path),
        "request_id": request.headers.get("x-request-id", ""),
    }
    if exc.errors:
        body["errors"] = exc.errors
    return JSONResponse(status_code=exc.status, content=body,
                        media_type="application/problem+json")

# Usage
raise ApiError(
    type_uri="https://api.example.com/errors/validation-failed",
    title="Validation Failed",
    status=422,
    detail="The request body contains 1 validation error.",
    errors=[{"field": "email", "code": "invalid_format",
             "message": "Must be a valid email address."}],
)
```

```typescript
// TypeScript / Express example
interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  request_id?: string;
  errors?: FieldError[];
}

class ApiError extends Error {
  constructor(public problem: ProblemDetail) {
    super(problem.detail);
  }
}

app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof ApiError) {
    const { problem } = err;
    problem.instance = req.originalUrl;
    problem.request_id = req.headers["x-request-id"] as string;
    res.status(problem.status)
       .type("application/problem+json")
       .json(problem);
  } else {
    res.status(500).type("application/problem+json").json({
      type: "https://api.example.com/errors/internal-error",
      title: "Internal Server Error",
      status: 500,
      detail: "An unexpected error occurred.",
      request_id: req.headers["x-request-id"],
    });
  }
});
```

---

## Do / Don't

### Do
- Return `application/problem+json` content type for all error responses.
- Return all validation errors in a single response.
- Use a fixed error code vocabulary across all services.
- Log full error context server-side with the `request_id`.
- Include `Retry-After` header on 429 and 503 responses.
- Make error `type` URIs dereferenceable documentation links.
- Include `meta` with constraint details for client-side message building.

### Don't
- Expose stack traces or internal paths in error responses.
- Return one validation error at a time (return all at once).
- Use different error formats across different endpoints or services.
- Include implementation details (SQL errors, file paths, class names).
- Return 200 with an error payload. Use proper HTTP status codes.
- Return HTML error pages from API endpoints.
- Reveal why authentication failed in detail (prevents enumeration).
