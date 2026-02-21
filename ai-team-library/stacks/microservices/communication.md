# Microservices Communication

Standards for inter-service communication: synchronous APIs, asynchronous
messaging, event-driven patterns, and data serialization. Complements
`conventions.md` which defines service boundaries and API design.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Sync Protocol        | REST over HTTP/2 with JSON              | ADR               |
| Async Protocol       | Apache Kafka (event streaming)          | ADR               |
| Serialization (sync) | JSON with schema validation             | ADR               |
| Serialization (async)| Avro with Schema Registry               | ADR               |
| API Documentation    | OpenAPI 3.1                             | ADR               |
| RPC Framework        | gRPC with Protobuf (internal only)      | ADR               |
| Request Timeout      | 5 seconds (default, tune per endpoint)  | Per-service config|
| Retry Policy         | 3 retries with exponential backoff      | Per-service config|

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| REST + JSON          | gRPC + Protobuf      | Low-latency, high-throughput internal calls |
| REST + JSON          | GraphQL              | BFF aggregation, mobile clients with variable data needs |
| Kafka                | RabbitMQ             | Simple work queues, request-reply patterns |
| Kafka                | Amazon SNS/SQS       | AWS-native, no broker management          |
| Kafka                | NATS                 | Ultra-low-latency, lightweight messaging  |
| Avro                 | Protobuf             | Already using gRPC, want unified schema   |
| Avro                 | JSON Schema          | Simple events, schema evolution not critical |

---

## Synchronous Communication

### REST Service-to-Service Calls

```python
# Use an HTTP client with timeouts, retries, and circuit breaking.
import httpx

client = httpx.AsyncClient(
    base_url="http://inventory-service.inventory-prod.svc.cluster.local",
    timeout=httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=10.0),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
)

async def check_stock(product_id: str) -> StockLevel:
    response = await client.get(
        f"/v1/products/{product_id}/stock",
        headers={"X-Request-ID": request_id, "X-Caller-Service": "order-service"},
    )
    response.raise_for_status()
    return StockLevel(**response.json()["data"])
```

**Rules:**
- Always set explicit timeouts on every HTTP client. Never use unbounded timeouts.
- Propagate `X-Request-ID` (correlation ID) on every outbound call.
- Include `X-Caller-Service` header so downstream services know who is calling.
- Use connection pooling. Creating a new TCP connection per request is wasteful.
- Prefer service DNS names over hardcoded IPs or load balancer URLs.

### gRPC for Internal Communication

```protobuf
// inventory.proto — contract-first gRPC service definition.
syntax = "proto3";
package inventory.v1;

service InventoryService {
  rpc CheckStock(CheckStockRequest) returns (CheckStockResponse);
  rpc ReserveStock(ReserveStockRequest) returns (ReserveStockResponse);
}

message CheckStockRequest {
  string product_id = 1;
}

message CheckStockResponse {
  string product_id = 1;
  int32 available_quantity = 2;
  string warehouse_id = 3;
}
```

**Rules:**
- Use gRPC only for internal service-to-service calls. Expose REST for external clients.
- Define `.proto` files in a shared contract repository.
- Use Proto3 syntax. Never use required fields (Proto2 legacy).
- Version proto packages: `package inventory.v1;`.
- Enable gRPC health checking protocol for load balancer integration.
- Use streaming RPCs only when the use case genuinely requires streaming data.

---

## Asynchronous Communication

### Event-Driven Architecture

```
┌──────────────┐    order.created    ┌──────────────┐
│ Order Service │ ──────────────────▶ │    Kafka      │
└──────────────┘                     │   Cluster     │
                                     └──────┬───────┘
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                    ┌──────────────┐ ┌────────────┐ ┌────────────────┐
                    │  Inventory   │ │  Payment   │ │ Notification   │
                    │  Service     │ │  Service   │ │ Service        │
                    └──────────────┘ └────────────┘ └────────────────┘
```

### Event Design

```json
{
  "event_id": "evt-abc-123",
  "event_type": "order.created",
  "event_version": "1.0",
  "timestamp": "2026-01-15T10:30:00Z",
  "source": "order-service",
  "correlation_id": "req-xyz-789",
  "data": {
    "order_id": "ord-456",
    "customer_id": "cust-789",
    "items": [
      { "product_id": "prod-001", "quantity": 2, "unit_price": 29.99 }
    ],
    "total": 59.98,
    "currency": "USD"
  }
}
```

**Rules:**
- Every event has a unique `event_id`, `event_type`, `event_version`, `timestamp`,
  `source`, and `correlation_id`.
- Events carry facts about what happened, not commands about what to do.
- Use past tense for event names: `order.created`, `payment.completed`,
  `stock.reserved`. Not `create_order` or `process_payment`.
- Events are immutable. Never update or delete published events.
- Include enough data for consumers to act without calling back to the producer.
  But do not include the entire entity — include only what changed and identifiers.
- Version events with semantic versioning in the `event_version` field.

### Topic Naming

```
# Pattern: <domain>.<entity>.<event>
order.order.created
order.order.cancelled
inventory.stock.reserved
inventory.stock.released
payment.transaction.completed
payment.transaction.failed
notification.email.sent
```

**Rules:**
- Use dot-separated hierarchical names: `<domain>.<entity>.<event>`.
- One topic per event type. Do not multiplex unrelated events on one topic.
- Partition by entity ID (e.g., `order_id`) for ordering guarantees within an entity.
- Set retention based on consumer needs: 7 days default, longer for audit events.
- Use compacted topics for state snapshots (e.g., current inventory levels).

### Consumer Patterns

```python
# Idempotent consumer — handle duplicate deliveries safely.
async def handle_order_created(event: OrderCreatedEvent) -> None:
    # Check if already processed (idempotency key).
    if await event_store.is_processed(event.event_id):
        logger.info("event_already_processed", event_id=event.event_id)
        return

    # Process the event.
    await inventory.reserve_stock(event.data.items)

    # Mark as processed.
    await event_store.mark_processed(event.event_id)
```

**Rules:**
- All consumers must be idempotent. Messages may be delivered more than once.
- Use an idempotency store keyed by `event_id` to detect duplicates.
- Process events in order within a partition. Do not assume global ordering.
- Use consumer groups for horizontal scaling. One partition = one consumer at a time.
- Commit offsets after successful processing, not before.
- Handle poison messages with a dead-letter queue (DLQ) after N retries.

---

## Saga Pattern

### Choreography (Event-Based)

```
Order Service          Inventory Service       Payment Service
     │                       │                       │
     │── order.created ─────▶│                       │
     │                       │── stock.reserved ────▶│
     │                       │                       │── payment.completed ──▶
     │◀── order.confirmed ───│◀── payment.confirmed ─│
     │                       │                       │
  (on failure at any step, compensating events undo previous steps)
     │                       │                       │
     │── order.cancelled ───▶│── stock.released ────▶│── payment.refunded ──▶
```

### Orchestration (Central Coordinator)

```python
# Order saga orchestrator — coordinates the multi-step transaction.
class OrderSaga:
    steps = [
        SagaStep(action=reserve_stock, compensation=release_stock),
        SagaStep(action=charge_payment, compensation=refund_payment),
        SagaStep(action=confirm_order, compensation=cancel_order),
    ]

    async def execute(self, order: Order) -> SagaResult:
        completed = []
        for step in self.steps:
            try:
                await step.action(order)
                completed.append(step)
            except SagaStepError as err:
                # Compensate in reverse order.
                for completed_step in reversed(completed):
                    await completed_step.compensation(order)
                return SagaResult(status="rolled_back", failed_step=step, error=err)
        return SagaResult(status="completed")
```

**Rules:**
- Use choreography for simple flows (2-3 steps) where services are loosely coupled.
- Use orchestration for complex flows (4+ steps) or when visibility is critical.
- Every saga step must have a compensating action defined.
- Compensating actions must be idempotent — they may be called multiple times.
- Persist saga state so it can resume after crashes.
- Set timeouts on saga steps. Escalate to a dead-letter/manual review after timeout.

---

## Do / Don't

### Do
- Set explicit timeouts on every synchronous call (connect, read, write).
- Propagate correlation IDs (`X-Request-ID`) across all service calls and events.
- Make all event consumers idempotent with duplicate detection.
- Use contract-first API design: write OpenAPI/Protobuf specs before code.
- Partition Kafka topics by entity ID for ordering guarantees.
- Include a dead-letter queue for every consumer to capture poison messages.
- Version events and APIs independently. Add fields, never remove or rename.

### Don't
- Make synchronous call chains longer than 2 hops. Decompose or use events.
- Use unbounded timeouts. A missing timeout turns a slow dependency into a full outage.
- Publish commands as events. Events describe what happened, not what should happen.
- Share message broker topics across unrelated domains. One topic per event type.
- Assume global ordering across Kafka partitions. Order is guaranteed only within a partition.
- Commit consumer offsets before processing. This causes data loss on crashes.
- Use distributed transactions (2PC) across services. Use the Saga pattern.

---

## Common Pitfalls

1. **Synchronous chain of doom** — Service A calls B calls C calls D. Latency
   is additive, availability is multiplicative (99.9%^4 = 99.6%). Fix: use async
   events or merge tightly-coupled services.

2. **Missing idempotency** — Consumer processes duplicate messages, creating
   duplicate orders/charges. Fix: store `event_id` on first processing, skip
   on re-delivery.

3. **Event schema breakage** — Producer adds/removes fields without versioning.
   Consumers fail to deserialize. Fix: use a schema registry with compatibility
   checks (backward/forward).

4. **Unbounded consumer lag** — Consumer falls behind producer. Events pile up
   and processing becomes hours stale. Fix: monitor consumer lag, scale consumers
   horizontally, raise alerts on lag thresholds.

5. **Saga without compensation** — A saga step fails mid-way and there is no
   rollback logic. Data is left in an inconsistent state across services.
   Fix: define and test compensating actions for every saga step.

6. **Request/response over Kafka** — Using Kafka for synchronous request-reply
   patterns. Adds latency and complexity for no benefit. Fix: use REST/gRPC for
   synchronous calls, Kafka for fire-and-forget events.

---

## Checklist

- [ ] Every synchronous call has explicit connect, read, and write timeouts.
- [ ] Correlation ID propagated on all outbound HTTP headers and event metadata.
- [ ] Event consumers are idempotent with duplicate detection by `event_id`.
- [ ] Events use past-tense naming and include `event_id`, `event_type`, `event_version`.
- [ ] Kafka topics partitioned by entity ID for ordering guarantees.
- [ ] Dead-letter queues configured for every consumer group.
- [ ] Schema registry enforces backward-compatible event evolution.
- [ ] Saga patterns have compensating actions for every step.
- [ ] Consumer offsets committed after successful processing only.
- [ ] No synchronous call chains longer than 2 hops.
- [ ] API contracts defined in OpenAPI or Protobuf before implementation.
- [ ] gRPC health checking enabled for internal RPC services.
