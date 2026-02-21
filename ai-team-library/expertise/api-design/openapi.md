# API Design — OpenAPI Specification

Define the API contract before writing implementation code. The OpenAPI spec
is the single source of truth for all API endpoints, request/response schemas,
authentication, and error formats.

---

## OpenAPI 3.1 Structure

```yaml
openapi: "3.1.0"
info:
  title: Orders API
  version: "1.0.0"
  description: |
    API for managing customer orders. Supports creating, updating,
    and tracking orders through their lifecycle.
  contact:
    name: API Support
    email: api-support@example.com
  license:
    name: MIT

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging
  - url: http://localhost:8080/v1
    description: Local development

security:
  - bearerAuth: []

tags:
  - name: Orders
    description: Order management operations
  - name: Items
    description: Order item operations

paths:
  /orders:
    get:
      operationId: listOrders
      tags: [Orders]
      summary: List orders
      description: Returns a paginated list of orders for the authenticated user.
      parameters:
        - $ref: "#/components/parameters/CursorParam"
        - $ref: "#/components/parameters/LimitParam"
        - name: status
          in: query
          schema:
            $ref: "#/components/schemas/OrderStatus"
      responses:
        "200":
          description: Paginated list of orders
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/OrderListResponse"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "429":
          $ref: "#/components/responses/RateLimited"

    post:
      operationId: createOrder
      tags: [Orders]
      summary: Create an order
      parameters:
        - $ref: "#/components/parameters/IdempotencyKey"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateOrderRequest"
      responses:
        "201":
          description: Order created
          headers:
            Location:
              schema:
                type: string
              description: URI of the created order
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Order"
        "422":
          $ref: "#/components/responses/ValidationError"

  /orders/{order_id}:
    get:
      operationId: getOrder
      tags: [Orders]
      summary: Get an order
      parameters:
        - $ref: "#/components/parameters/OrderId"
      responses:
        "200":
          description: Order details
          headers:
            ETag:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Order"
        "404":
          $ref: "#/components/responses/NotFound"

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  parameters:
    OrderId:
      name: order_id
      in: path
      required: true
      schema:
        type: string
        format: uuid

    CursorParam:
      name: cursor
      in: query
      description: Opaque pagination cursor from a previous response
      schema:
        type: string

    LimitParam:
      name: limit
      in: query
      description: Maximum number of items to return (1-100)
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

    IdempotencyKey:
      name: Idempotency-Key
      in: header
      description: Unique key to ensure idempotent request processing
      schema:
        type: string
        format: uuid

  schemas:
    Order:
      type: object
      required: [id, status, total_cents, currency, created_at, updated_at]
      properties:
        id:
          type: string
          format: uuid
          description: Unique order identifier
          examples: ["019abc12-3456-7890-abcd-ef1234567890"]
        status:
          $ref: "#/components/schemas/OrderStatus"
        total_cents:
          type: integer
          description: Total amount in cents
          examples: [4999]
        currency:
          type: string
          pattern: "^[A-Z]{3}$"
          description: ISO 4217 currency code
          examples: ["USD"]
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    OrderStatus:
      type: string
      enum: [pending, confirmed, shipped, delivered, cancelled]

    CreateOrderRequest:
      type: object
      required: [items, currency]
      properties:
        items:
          type: array
          minItems: 1
          items:
            $ref: "#/components/schemas/OrderItemInput"
        currency:
          type: string
          pattern: "^[A-Z]{3}$"

    OrderItemInput:
      type: object
      required: [product_id, quantity]
      properties:
        product_id:
          type: string
          format: uuid
        quantity:
          type: integer
          minimum: 1
          maximum: 999

    OrderListResponse:
      type: object
      required: [data, pagination]
      properties:
        data:
          type: array
          items:
            $ref: "#/components/schemas/Order"
        pagination:
          $ref: "#/components/schemas/CursorPagination"

    CursorPagination:
      type: object
      required: [has_more]
      properties:
        next_cursor:
          type: string
          nullable: true
        has_more:
          type: boolean

    ProblemDetail:
      type: object
      required: [type, title, status, detail]
      properties:
        type:
          type: string
          format: uri
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string
        request_id:
          type: string
        errors:
          type: array
          items:
            $ref: "#/components/schemas/FieldError"

    FieldError:
      type: object
      required: [field, code, message]
      properties:
        field:
          type: string
        code:
          type: string
        message:
          type: string
        meta:
          type: object

  responses:
    ValidationError:
      description: Validation failed
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetail"

    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetail"

    Unauthorized:
      description: Authentication required
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetail"

    RateLimited:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
        RateLimit-Limit:
          schema:
            type: integer
        RateLimit-Remaining:
          schema:
            type: integer
        RateLimit-Reset:
          schema:
            type: integer
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetail"
```

---

## Spec Organization

```
api/
  openapi.yaml           # Root spec file
  paths/
    orders.yaml          # /orders endpoints
    items.yaml           # /orders/{id}/items endpoints
  schemas/
    order.yaml           # Order schema
    pagination.yaml      # Pagination schemas
    errors.yaml          # Error schemas
  parameters/
    common.yaml          # Shared parameters
  responses/
    errors.yaml          # Shared error responses
```

**Rules:**
- Split large specs into multiple files using `$ref` references.
- Group by resource: one file per resource under `paths/`.
- Share common schemas, parameters, and responses via `components/`.
- The root `openapi.yaml` assembles everything with `$ref`.
- Use a bundler (e.g., `redocly bundle`) to produce a single-file spec for
  tools that don't support multi-file.

---

## Schema Best Practices

```yaml
# Use required arrays — don't rely on nullable for optionality
Order:
  type: object
  required: [id, status, total_cents]  # Explicit required list
  properties:
    id:
      type: string
      format: uuid
    status:
      type: string
      enum: [pending, confirmed, shipped]
    total_cents:
      type: integer
      minimum: 0
    notes:
      type: string         # Not in required = optional
      maxLength: 1000

# Use examples for documentation and mocking
Product:
  type: object
  properties:
    name:
      type: string
      examples: ["Widget Pro"]
      minLength: 1
      maxLength: 200
    price_cents:
      type: integer
      minimum: 0
      examples: [1999]

# Use oneOf/anyOf for polymorphic types
PaymentMethod:
  oneOf:
    - $ref: "#/components/schemas/CreditCard"
    - $ref: "#/components/schemas/BankTransfer"
  discriminator:
    propertyName: type
    mapping:
      credit_card: "#/components/schemas/CreditCard"
      bank_transfer: "#/components/schemas/BankTransfer"
```

**Rules:**
- Always specify `required` fields explicitly.
- Use `format` hints: `uuid`, `date-time`, `email`, `uri`.
- Add `minimum`, `maximum`, `minLength`, `maxLength` constraints.
- Use `pattern` for string formats (e.g., `"^[A-Z]{3}$"` for currency).
- Use `examples` (plural, OpenAPI 3.1) for documentation and mocking.
- Use `enum` for fixed value sets.
- Prefer `oneOf` with `discriminator` for polymorphic types.
- Never use `additionalProperties: true` in response schemas (it prevents
  code generation from producing typed models).

---

## Code Generation

```bash
# Generate server stubs
openapi-generator-cli generate \
  -i api/openapi.yaml \
  -g python-fastapi \
  -o generated/server

# Generate TypeScript client
openapi-generator-cli generate \
  -i api/openapi.yaml \
  -g typescript-fetch \
  -o generated/client \
  --additional-properties=supportsES6=true,npmName=@myorg/api-client

# Validate spec
redocly lint api/openapi.yaml

# Bundle multi-file spec
redocly bundle api/openapi.yaml -o dist/openapi.yaml

# Generate documentation
redocly build-docs api/openapi.yaml -o docs/api.html
```

**Rules:**
- Validate the spec in CI with `redocly lint` or `spectral lint`.
- Generate server stubs as a starting point, then implement business logic.
- Generate client SDKs from the spec instead of hand-writing HTTP calls.
- Regenerate clients on every spec change. Commit generated code or publish
  as packages.
- Use `operationId` on every endpoint — it becomes the function name in
  generated code.

---

## Workflow

1. **Design** — Write the OpenAPI spec for new endpoints before coding.
2. **Review** — Review the spec in a PR (use Redocly preview or Swagger UI).
3. **Validate** — CI runs `redocly lint` on every commit.
4. **Generate** — Generate server stubs and client SDKs.
5. **Implement** — Fill in the business logic behind the generated stubs.
6. **Test** — Contract tests verify the implementation matches the spec.
7. **Publish** — Deploy updated docs and client SDKs on release.

---

## Contract Testing

```python
# Validate responses against OpenAPI spec
import schemathesis

schema = schemathesis.from_uri("http://localhost:8080/openapi.yaml")

@schema.parametrize()
def test_api_contract(case):
    response = case.call()
    case.validate_response(response)
```

**Rules:**
- Run contract tests in CI to catch spec/implementation drift.
- Use `schemathesis` (Python), `dredd` (Node), or `prism` (mock server)
  for automated contract validation.
- Contract tests complement, not replace, unit and integration tests.
- The spec is the contract. Implementation that diverges from the spec is a
  bug, not a feature.

---

## Do / Don't

### Do
- Write the OpenAPI spec before implementing endpoints.
- Use `$ref` to share schemas, parameters, and responses.
- Add `operationId` to every endpoint for code generation.
- Validate the spec in CI on every commit.
- Include examples in schemas for documentation and mocking.
- Add constraints (min, max, pattern, enum) to all fields.
- Generate client SDKs from the spec.

### Don't
- Write the spec after the implementation (it will drift).
- Duplicate schemas across endpoints (use `$ref`).
- Use `additionalProperties: true` in response schemas.
- Skip `required` arrays (makes all fields appear optional).
- Use generic types (`type: object` with no properties defined).
- Forget `operationId` (breaks code generators).
- Hand-write HTTP clients when a generated SDK exists.

---

## Common Pitfalls

1. **Spec drift** — The spec says one thing, the implementation does another.
   Run contract tests in CI to catch drift early.

2. **Missing error schemas** — Documenting only happy paths. Define
   `responses` for 400, 401, 403, 404, 422, 429, and 500 on every endpoint.

3. **No `operationId`** — Without `operationId`, code generators produce
   meaningless function names like `get_v1_orders_order_id`. Always set
   meaningful operation IDs.

4. **Unvalidated spec** — A syntactically valid but semantically wrong spec
   (mismatched `$ref`, missing required fields) causes runtime failures.
   Lint in CI.

5. **Monolithic spec file** — A single 5,000-line YAML file is unmaintainable.
   Split into `paths/`, `schemas/`, and `parameters/` directories.

6. **No examples** — Without examples, generated documentation shows empty
   request/response bodies. Add realistic examples to every schema.
