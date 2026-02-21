# Node.js API Design

Guidelines for designing RESTful APIs in Node.js with Fastify (or Express),
covering routing, validation, versioning, pagination, and error responses.

---

## Defaults

| Concern            | Default Choice                        | Override Requires |
|--------------------|---------------------------------------|-------------------|
| Framework          | Fastify                               | ADR               |
| Validation         | Typebox / JSON Schema (route-level)   | ADR               |
| Serialization      | Fastify `reply.send()` + schema       | Never             |
| Versioning         | URI prefix (`/v1/`)                   | ADR               |
| Pagination         | Cursor-based (`?cursor=&limit=`)      | ADR               |
| Error Format       | RFC 7807 Problem Details              | ADR               |
| Auth Transport     | `Authorization: Bearer <jwt>`         | ADR               |
| Content Type       | `application/json`                    | ADR               |

---

## Route Registration

Register each resource as a Fastify plugin for encapsulation.

```typescript
// src/routes/orders.ts
import { FastifyPluginAsync } from "fastify";
import { Type, Static } from "@sinclair/typebox";

const OrderParams = Type.Object({
  id: Type.String({ format: "uuid" }),
});
type OrderParams = Static<typeof OrderParams>;

const ordersRoute: FastifyPluginAsync = async (app) => {
  app.get<{ Params: OrderParams }>(
    "/orders/:id",
    {
      schema: {
        params: OrderParams,
        response: {
          200: OrderResponseSchema,
          404: ProblemDetailSchema,
        },
      },
    },
    async (request, reply) => {
      const order = await app.orderService.findById(request.params.id);
      if (!order) throw new NotFoundError("Order", request.params.id);
      return order;
    },
  );
};

export default ordersRoute;
```

---

## Error Response Format (RFC 7807)

Every error response uses a consistent Problem Details envelope.

```typescript
// src/errors/problem-detail.ts
export interface ProblemDetail {
  type: string;       // URI identifying the error class
  title: string;      // Short human-readable summary
  status: number;     // HTTP status code
  detail?: string;    // Longer explanation
  instance?: string;  // URI of the failing request
}

// Centralized Fastify error handler
app.setErrorHandler((error, request, reply) => {
  const status = error instanceof AppError ? error.statusCode : 500;
  const body: ProblemDetail = {
    type: `https://api.example.com/errors/${error.code ?? "INTERNAL"}`,
    title: error.message,
    status,
    instance: request.url,
  };
  request.log.error({ err: error, requestId: request.id }, "request_failed");
  reply.status(status).send(body);
});
```

---

## Do / Don't

### Do
- Validate every request input at the schema level (params, query, body).
- Return pagination metadata (`cursor`, `hasMore`) alongside result arrays.
- Use HTTP `Location` header on `201 Created` responses.
- Version the API in the URI (`/v1/orders`); bump only on breaking changes.
- Scope routes as Fastify plugins so decorators and hooks are encapsulated.
- Use `reply.code(204).send()` for successful deletes (no body).
- Document endpoints with an OpenAPI spec generated from Typebox schemas.

### Don't
- Validate manually in handlers -- rely on framework schema validation.
- Use HTTP `200` for every response; use the correct status code.
- Return raw database errors or stack traces to clients.
- Nest resources deeper than two levels (`/orders/:id/items/:itemId` is the limit).
- Accept unbounded query results -- always enforce a `limit` with a sane max.
- Mix plural and singular resource names (`/orders`, not `/order`).

---

## Common Pitfalls

1. **Missing schema on response** -- Without a response schema, Fastify
   serializes the full object, potentially leaking internal fields. Always
   declare a response schema.
2. **Query parameter coercion** -- Query params arrive as strings. Without
   schema coercion (`Type.Integer()` in Typebox), `?limit=10` is the string
   `"10"`, breaking comparisons.
3. **Swallowed async errors** -- Forgetting to `await` an async handler causes
   Fastify to send `200` before the work finishes. Always return or await the
   promise.
4. **CORS misconfiguration** -- Wildcard `*` origin in production leaks APIs
   to any domain. Use an explicit allowlist via `@fastify/cors`.
5. **Over-fetching in list endpoints** -- Returning full nested objects in
   collection endpoints. Return summaries; let clients fetch details per-item.
6. **Inconsistent error shapes** -- Some routes returning `{ error: "..." }`
   and others `{ message: "..." }`. Centralize via the error handler.

---

## Alternatives

| Concern        | Primary        | Alternative         | Notes                          |
|----------------|----------------|---------------------|--------------------------------|
| Framework      | Fastify        | Express + Zod       | Express for legacy codebases   |
| Validation     | Typebox        | Zod + zod-to-json   | Zod if already used elsewhere  |
| API Docs       | Fastify Swagger| Redoc / Stoplight   | Choose based on audience       |
| Serialization  | fast-json-stringify | JSON.stringify | Built-in with Fastify schemas  |

---

## Checklist

- [ ] Every route has a request schema (params, query, body as applicable).
- [ ] Every route has a response schema for success **and** error cases.
- [ ] Error handler returns RFC 7807 Problem Details consistently.
- [ ] Pagination enforced on all list endpoints (max limit, cursor/offset).
- [ ] No internal fields leak in responses (verified via response schema).
- [ ] API versioned in URI prefix; breaking changes require a version bump.
- [ ] OpenAPI spec generated and accessible at `/docs` in non-production.
- [ ] CORS configured with an explicit origin allowlist (no wildcard in prod).
- [ ] `Content-Type` and `Accept` headers validated.
- [ ] Integration tests cover success, validation failure, not-found, and auth scenarios.
