# Microservices Stack Conventions

Non-negotiable defaults for microservices architecture on this team. Covers
service decomposition, API design, data ownership, and deployment patterns.
Deviations require an ADR with justification. "I prefer it differently" is not
justification.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Decomposition        | Domain-Driven Design bounded contexts   | ADR               |
| API Protocol (sync)  | REST over HTTP/2 with JSON              | ADR               |
| API Protocol (async) | Event-driven with message broker        | ADR               |
| Message Broker       | Apache Kafka                            | ADR               |
| Service Size         | One bounded context per service         | ADR               |
| Data Ownership       | Database-per-service                    | Never             |
| API Versioning       | URL path versioning (`/v1/`, `/v2/`)    | ADR               |
| Service Registry     | DNS-based (Kubernetes Service discovery)| ADR               |
| API Gateway          | Dedicated gateway for external traffic  | Never             |
| Contract Testing     | Consumer-driven contracts (Pact)        | ADR               |
| Deployment           | One service per container, one container per pod | Never    |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| REST + JSON          | gRPC + Protobuf      | High-throughput internal service-to-service calls |
| REST + JSON          | GraphQL              | BFF (Backend-for-Frontend) aggregation layer |
| Apache Kafka         | RabbitMQ             | Simple task queues, low-volume routing    |
| Apache Kafka         | Amazon SQS/SNS       | AWS-native, no self-managed broker needed |
| URL path versioning  | Header versioning    | Internal APIs with sophisticated clients  |
| Pact                 | Schema Registry      | Event-driven contracts (Avro/Protobuf)    |
| DNS discovery        | Consul / Eureka      | Non-Kubernetes environments               |

---

## Service Boundaries

### Decomposition Strategy

```
ecommerce-platform/
  order-service/           # Order lifecycle, checkout, payment orchestration
  inventory-service/       # Stock levels, reservations, warehouse integration
  user-service/            # Authentication, profiles, preferences
  notification-service/    # Email, SMS, push notifications (event-driven)
  catalog-service/         # Product catalog, search, categories
  payment-service/         # Payment processing, refunds, ledger
```

**Rules:**
- Decompose by business capability (bounded context), not by technical layer.
- Each service owns its domain data exclusively. No shared databases.
- A service should be deployable, scalable, and replaceable independently.
- Start with larger services and split only when complexity or scaling demands it.
- If two services always deploy together, they are one service.

### Boundary Heuristics

| Signal                                  | Action                              |
|-----------------------------------------|-------------------------------------|
| Team needs independent release cycles   | Split into separate services        |
| Different scaling requirements          | Split into separate services        |
| Circular dependencies between services  | Merge or redesign boundaries        |
| Shared database tables between services | Merge or extract data service       |
| Feature requires changes in 3+ services | Boundaries are wrong — reconsider   |
| Service has < 1 deployment/month        | Consider merging into a neighbor    |

---

## API Design

### REST Conventions

```
# Resource naming — plural nouns, no verbs.
GET    /v1/orders              # List orders (paginated)
GET    /v1/orders/{id}         # Get single order
POST   /v1/orders              # Create order
PUT    /v1/orders/{id}         # Replace order (full update)
PATCH  /v1/orders/{id}         # Partial update
DELETE /v1/orders/{id}         # Delete order

# Sub-resources for containment relationships.
GET    /v1/orders/{id}/items   # List items in an order
POST   /v1/orders/{id}/items   # Add item to an order

# Actions that don't map to CRUD — use verb sub-resource.
POST   /v1/orders/{id}/cancel  # Cancel an order
POST   /v1/orders/{id}/refund  # Refund an order
```

**Standard Response Envelope:**

```json
{
  "data": { "id": "ord-123", "status": "confirmed" },
  "meta": { "request_id": "req-abc-456", "timestamp": "2026-01-15T10:30:00Z" }
}
```

**Error Response:**

```json
{
  "error": {
    "code": "ORDER_NOT_FOUND",
    "message": "Order ord-999 does not exist.",
    "details": [],
    "request_id": "req-abc-456"
  }
}
```

**Rules:**
- Use plural nouns for resources. `/orders` not `/order`.
- Use HTTP status codes correctly: 200 OK, 201 Created, 204 No Content,
  400 Bad Request, 404 Not Found, 409 Conflict, 422 Unprocessable Entity, 503 Service Unavailable.
- Every response includes a `request_id` for tracing.
- Paginate all list endpoints. Use cursor-based pagination for large datasets.
- Version APIs in the URL path: `/v1/orders`. Increment only on breaking changes.
- Use `PATCH` for partial updates, `PUT` for full replacement.

---

## Data Ownership

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Order Service   │     │ Inventory Service │     │   User Service    │
│                  │     │                   │     │                   │
│  ┌────────────┐  │     │  ┌─────────────┐  │     │  ┌─────────────┐  │
│  │ orders DB  │  │     │  │ inventory DB │  │     │  │  users DB   │  │
│  └────────────┘  │     │  └─────────────┘  │     │  └─────────────┘  │
└─────────────────┘     └──────────────────┘     └──────────────────┘
       │                        │                        │
       └────────── Events ──────┴────────────────────────┘
```

**Rules:**
- Each service owns its database. No other service reads from or writes to it directly.
- Services share data through APIs (synchronous) or events (asynchronous).
- Denormalize data across services. Each service stores the data it needs locally.
- Use eventual consistency between services. Strong consistency only within a service.
- For cross-service transactions, use the Saga pattern (choreography or orchestration).
- Never join across service databases — this is a boundary violation.

---

## Configuration

```yaml
# config.yaml — per-service, per-environment configuration.
service:
  name: order-service
  port: 8080
  environment: production

database:
  host: ${DB_HOST}
  port: 5432
  name: orders
  pool_size: 20
  ssl: true

messaging:
  broker: ${KAFKA_BROKERS}
  consumer_group: order-service
  topics:
    - inventory.stock.reserved
    - payment.completed

health:
  liveness_path: /healthz
  readiness_path: /readyz

logging:
  level: info
  format: json
```

**Rules:**
- Externalize all configuration. No hardcoded URLs, credentials, or feature flags.
- Use environment variables for secrets and environment-specific values.
- Each service defines its own configuration schema with validation on startup.
- Fail fast on invalid configuration — do not start with missing required config.

---

## Do / Don't

### Do
- Decompose by business capability using bounded contexts from DDD.
- Enforce database-per-service. Each service owns its data exclusively.
- Use asynchronous events for cross-service data propagation and eventual consistency.
- Include `request_id` / correlation ID in every API response and log entry.
- Design APIs contract-first. Write the OpenAPI spec before implementation.
- Use consumer-driven contract tests to catch breaking changes early.
- Implement health checks (`/healthz`, `/readyz`) in every service.
- Start with a coarser decomposition and split services only when justified.

### Don't
- Share databases between services. This creates hidden coupling and deployment dependencies.
- Build distributed monoliths — if all services must deploy together, merge them.
- Use synchronous calls for workflows that can tolerate seconds of delay. Use events.
- Skip API versioning. Breaking changes without versioning cause cascading failures.
- Create "utility" or "common" services that every other service depends on.
- Use distributed transactions (2PC) across services. Use Sagas instead.
- Decompose prematurely. A well-structured monolith is better than poorly-bounded microservices.
- Ignore data consistency. Understand where eventual consistency is acceptable and where it is not.

---

## Common Pitfalls

1. **Distributed monolith** — Services are deployed independently but can't function
   independently. Every feature requires coordinated changes across 3+ services.
   Fix: redraw boundaries around business capabilities, not technical layers.

2. **Shared database anti-pattern** — Two services read/write the same tables,
   creating invisible coupling. Schema changes break both services simultaneously.
   Fix: split the schema, expose data through APIs or events.

3. **Synchronous chain of doom** — Service A calls B, which calls C, which calls D.
   Latency compounds, availability drops multiplicatively (99.9%^4 = 99.6%).
   Fix: use async events, cache responses, or merge tightly-coupled services.

4. **Premature decomposition** — Splitting a monolith into microservices before
   understanding domain boundaries. Results in chatty services and constant refactoring.
   Fix: build a well-structured modular monolith first, split when boundaries are stable.

5. **No API contracts** — Services evolve their APIs without formal contracts or
   versioning. Consumer breakage discovered only in production.
   Fix: use OpenAPI specs and consumer-driven contract tests (Pact).

6. **God service** — One service accumulates logic from multiple domains because
   it was easier than creating a new service. It becomes a bottleneck and single point
   of failure. Fix: identify the bounded contexts inside it and extract them.

7. **Event soup** — Hundreds of event types with no schema governance. Consumers
   can't keep up with changes, events carry too much or too little data.
   Fix: use a schema registry (Avro/Protobuf), define clear event ownership.

---

## Checklist

- [ ] Services decomposed by business capability / bounded context.
- [ ] Each service owns its database — no shared tables across services.
- [ ] APIs are contract-first with OpenAPI or Protobuf definitions.
- [ ] API versioning strategy defined and enforced (`/v1/`, `/v2/`).
- [ ] Cross-service data flows use events (async) where possible.
- [ ] Saga pattern used for cross-service transactions (no distributed 2PC).
- [ ] Health endpoints (`/healthz`, `/readyz`) implemented in every service.
- [ ] Correlation ID / request ID propagated across all service calls.
- [ ] Consumer-driven contract tests in CI for inter-service APIs.
- [ ] Configuration externalized — no hardcoded URLs or credentials.
- [ ] Each service independently deployable and scalable.
- [ ] Service boundary heuristics reviewed — no circular dependencies.
