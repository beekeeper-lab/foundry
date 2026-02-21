# Messaging Patterns

Production patterns for reliable message processing: saga orchestration,
dead letter queues, idempotency, retry strategies, outbox pattern, and
claim-check for large payloads.

---

## Saga Pattern

Sagas coordinate multi-service transactions through a sequence of local
transactions, each publishing events that trigger the next step. If any step
fails, compensating actions undo the preceding steps.

### Orchestration-Based Saga

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


class SagaStatus(Enum):
    STARTED = "started"
    COMPLETING = "completing"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


@dataclass
class SagaStep:
    name: str
    action_topic: str
    compensation_topic: str
    status: str = "pending"
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class OrderSaga:
    """Orchestrator for a multi-step order fulfillment saga."""

    saga_id: UUID = field(default_factory=uuid4)
    order_id: str = ""
    status: SagaStatus = SagaStatus.STARTED
    current_step: int = 0
    steps: List[SagaStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.steps:
            self.steps = [
                SagaStep(
                    name="reserve_inventory",
                    action_topic="inventory.commands.reserve",
                    compensation_topic="inventory.commands.release",
                ),
                SagaStep(
                    name="process_payment",
                    action_topic="payments.commands.capture",
                    compensation_topic="payments.commands.refund",
                ),
                SagaStep(
                    name="schedule_shipping",
                    action_topic="shipping.commands.schedule",
                    compensation_topic="shipping.commands.cancel",
                ),
            ]


class SagaOrchestrator:
    """Drives the saga forward or compensates on failure."""

    def __init__(self, saga_store, message_bus) -> None:
        self._store = saga_store
        self._bus = message_bus

    def start(self, saga: OrderSaga) -> None:
        self._store.save(saga)
        self._execute_next_step(saga)

    def handle_step_success(self, saga_id: UUID, step_name: str) -> None:
        saga = self._store.load(saga_id)
        step = self._find_step(saga, step_name)
        step.status = "completed"
        step.completed_at = datetime.utcnow()
        saga.current_step += 1

        if saga.current_step >= len(saga.steps):
            saga.status = SagaStatus.COMPLETED
            self._store.save(saga)
        else:
            self._store.save(saga)
            self._execute_next_step(saga)

    def handle_step_failure(self, saga_id: UUID, step_name: str, error: str) -> None:
        saga = self._store.load(saga_id)
        step = self._find_step(saga, step_name)
        step.status = "failed"
        step.error = error
        saga.status = SagaStatus.COMPENSATING
        self._store.save(saga)
        self._compensate(saga)

    def _execute_next_step(self, saga: OrderSaga) -> None:
        step = saga.steps[saga.current_step]
        step.status = "in_progress"
        self._store.save(saga)
        self._bus.publish(step.action_topic, {
            "saga_id": str(saga.saga_id),
            "order_id": saga.order_id,
            "step": step.name,
        })

    def _compensate(self, saga: OrderSaga) -> None:
        """Execute compensation in reverse order for completed steps."""
        for step in reversed(saga.steps):
            if step.status == "completed":
                step.status = "compensating"
                self._bus.publish(step.compensation_topic, {
                    "saga_id": str(saga.saga_id),
                    "order_id": saga.order_id,
                    "step": step.name,
                })

    def _find_step(self, saga: OrderSaga, name: str) -> SagaStep:
        return next(s for s in saga.steps if s.name == name)
```

### Choreography-Based Saga

```
OrderPlaced → [Inventory Service] → StockReserved
StockReserved → [Payment Service] → PaymentCaptured
PaymentCaptured → [Shipping Service] → ShipmentScheduled

# On failure — compensating events
PaymentFailed → [Inventory Service] → StockReleased
ShipmentFailed → [Payment Service] → PaymentRefunded
                 [Inventory Service] → StockReleased
```

**When to use which:**

| Factor               | Orchestration           | Choreography              |
|----------------------|-------------------------|---------------------------|
| Complexity           | 3+ steps or conditional | 2-3 simple linear steps   |
| Visibility           | Central saga state      | Distributed, harder to trace |
| Coupling             | Orchestrator knows steps | Services know each other's events |
| Testing              | Test orchestrator logic | Test each service independently |
| Preferred default    | **Yes**                 | Only for simple flows     |

**Rules:**
- Persist saga state to survive service restarts. Use a dedicated saga store.
- Each step must have a corresponding compensation action defined upfront.
- Compensations execute in reverse order of completed steps.
- Compensations must be idempotent — they may be triggered more than once.
- Use timeouts per step. If a step doesn't respond, treat it as a failure.
- Log every state transition for audit and debugging.

---

## Dead Letter Queues (DLQ)

Dead letter queues capture messages that cannot be processed after exhausting
all retry attempts. They prevent poison pills from blocking the consumer and
provide a holding area for manual investigation.

### DLQ Architecture

```
┌────────────┐     process     ┌───────────┐
│ Main Queue │───────────────→│  Consumer  │
└────────────┘                └─────┬─────┘
                                    │
                              failure │ (after max retries)
                                    │
                                    ▼
                              ┌───────────┐
                              │    DLQ    │
                              └─────┬─────┘
                                    │
                              review │ (manual or automated)
                                    │
                                    ▼
                              ┌───────────┐
                              │  DLQ Tool │ (inspect, replay, discard)
                              └───────────┘
```

### DLQ Message Enrichment

```python
def send_to_dlq(original_message: dict, error: Exception, retry_count: int) -> dict:
    """Enrich the original message with failure context before sending to DLQ."""
    return {
        "original_message": original_message,
        "dlq_metadata": {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "retry_count": retry_count,
            "failed_at": datetime.utcnow().isoformat(),
            "source_topic": original_message.get("_source_topic"),
            "consumer_group": original_message.get("_consumer_group"),
            "original_timestamp": original_message.get("time"),
        },
    }
```

**Rules:**
- Every queue/topic must have a DLQ configured. No exceptions.
- Enrich DLQ messages with failure metadata: error type, message, stack trace,
  retry count, timestamp, source topic, and consumer group.
- Monitor DLQ depth with alerts. A non-empty DLQ requires investigation.
- Provide tooling to inspect, replay, and discard DLQ messages.
- Set a TTL on DLQ messages (e.g., 14 days) to prevent unbounded growth.
- Never auto-replay from DLQ without fixing the root cause first.

---

## Idempotency

At-least-once delivery means consumers may receive the same message multiple
times. Idempotency ensures that processing a message more than once produces
the same result as processing it once.

### Idempotency Key Store

```python
class IdempotencyStore:
    """Tracks processed message IDs to prevent duplicate processing."""

    def __init__(self, connection) -> None:
        self._conn = connection

    def setup(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS processed_messages (
                    message_id    TEXT        PRIMARY KEY,
                    processed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    result        JSONB
                )
            """)
            # Auto-cleanup: TTL index removes entries older than 7 days
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed_ttl
                ON processed_messages (processed_at)
            """)
            self._conn.commit()

    def is_duplicate(self, message_id: str) -> bool:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM processed_messages WHERE message_id = %s",
                (message_id,)
            )
            return cur.fetchone() is not None

    def mark_processed(self, message_id: str, result: dict = None) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO processed_messages (message_id, result)
                   VALUES (%s, %s) ON CONFLICT (message_id) DO NOTHING""",
                (message_id, json.dumps(result) if result else None)
            )
            self._conn.commit()


class IdempotentConsumer:
    """Wraps message processing with deduplication."""

    def __init__(self, store: IdempotencyStore, handler) -> None:
        self._store = store
        self._handler = handler

    def process(self, message: dict) -> None:
        message_id = message["id"]

        if self._store.is_duplicate(message_id):
            log.info("duplicate_skipped message_id=%s", message_id)
            return

        # Process within transaction — mark processed and execute atomically
        result = self._handler.handle(message)
        self._store.mark_processed(message_id, result)
```

### Natural Idempotency

```python
# Idempotent by nature — setting a value is the same regardless of repetition
def handle_address_changed(event: AddressChanged) -> None:
    db.execute(
        "UPDATE customers SET address = %s WHERE id = %s",
        (event.new_address, event.customer_id)
    )

# NOT idempotent — incrementing produces different results on replay
def handle_points_earned(event: PointsEarned) -> None:
    # BAD: db.execute("UPDATE accounts SET points = points + %s WHERE id = %s", ...)
    # GOOD: use the message ID to prevent double-counting
    db.execute(
        """INSERT INTO point_transactions (event_id, account_id, points)
           VALUES (%s, %s, %s) ON CONFLICT (event_id) DO NOTHING""",
        (event.event_id, event.account_id, event.points)
    )
```

**Rules:**
- Every consumer must be idempotent. This is non-negotiable for at-least-once delivery.
- Use the message `id` as the idempotency key. Store it alongside the business transaction.
- Prefer `INSERT ... ON CONFLICT DO NOTHING` (upsert) over check-then-act patterns.
- For operations that are not naturally idempotent (increments, sends), record the
  event ID in the same transaction as the side effect.
- Clean up the idempotency store periodically (TTL of 7 days covers most replay windows).
- For exactly-once semantics, combine idempotent consumers with transactional outbox.

---

## Retry Strategies

### Exponential Backoff with Jitter

```python
import random
import time


def calculate_backoff(attempt: int, base_delay: float = 1.0,
                      max_delay: float = 60.0, jitter: bool = True) -> float:
    """Calculate delay with exponential backoff and optional jitter."""
    delay = min(base_delay * (2 ** attempt), max_delay)
    if jitter:
        delay = random.uniform(0, delay)  # Full jitter
    return delay


class RetryHandler:
    """Retry with backoff, then route to DLQ."""

    MAX_RETRIES = 5

    def __init__(self, handler, dlq_publisher) -> None:
        self._handler = handler
        self._dlq = dlq_publisher

    def process(self, message: dict) -> None:
        retry_count = message.get("_retry_count", 0)

        try:
            self._handler.handle(message)
        except RetryableError as e:
            if retry_count >= self.MAX_RETRIES:
                self._dlq.send(message, error=e, retry_count=retry_count)
                return
            delay = calculate_backoff(retry_count)
            message["_retry_count"] = retry_count + 1
            # Re-publish to retry topic with delay
            self._publish_delayed(message, delay)
        except NonRetryableError as e:
            # Immediate DLQ — no point retrying
            self._dlq.send(message, error=e, retry_count=retry_count)
```

### Kafka Retry Topics

```
# Main topic
orders.order.placed.v1

# Retry topics with increasing delays
orders.order.placed.v1.retry-1   (delay: 10s)
orders.order.placed.v1.retry-2   (delay: 60s)
orders.order.placed.v1.retry-3   (delay: 300s)

# Dead letter topic (after all retries exhausted)
orders.order.placed.v1.dlq
```

**Rules:**
- Always use exponential backoff with jitter. Fixed delays cause thundering herds.
- Classify errors: retryable (transient network, timeout, 503) vs. non-retryable
  (validation, 4xx, deserialization). Only retry retryable errors.
- Set a max retry count (default: 5). After exhaustion, route to DLQ.
- For Kafka, use separate retry topics with increasing consumer poll delays.
- For RabbitMQ, use per-message TTL with dead-letter exchange chaining.
- Log every retry with attempt count, delay, and error details.

---

## Transactional Outbox Pattern

The outbox pattern ensures that database writes and message publishing happen
atomically, preventing data inconsistency when the broker is unavailable.

```
┌─────────────────────────────────────────┐
│            Single Transaction           │
│                                         │
│  1. Write business data to DB           │
│  2. Write event to outbox table         │
│                                         │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Outbox Relay (CDC/Poller)       │
│                                         │
│  3. Read unpublished from outbox        │
│  4. Publish to message broker           │
│  5. Mark as published                   │
│                                         │
└─────────────────────────────────────────┘
```

### Outbox Table

```sql
CREATE TABLE outbox (
    id              BIGSERIAL     PRIMARY KEY,
    aggregate_type  TEXT          NOT NULL,
    aggregate_id    TEXT          NOT NULL,
    event_type      TEXT          NOT NULL,
    payload         JSONB         NOT NULL,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    published_at    TIMESTAMPTZ,
    topic           TEXT          NOT NULL
);

CREATE INDEX idx_outbox_unpublished ON outbox (created_at)
    WHERE published_at IS NULL;
```

### Outbox Usage

```python
def place_order(command: PlaceOrderCommand, db, outbox) -> None:
    """Business write + outbox insert in one transaction."""
    with db.transaction():
        # 1. Business data
        order = Order(id=command.order_id, customer_id=command.customer_id,
                      items=command.items, status="placed")
        db.insert("orders", order)

        # 2. Outbox event (same transaction)
        outbox.insert({
            "aggregate_type": "Order",
            "aggregate_id": command.order_id,
            "event_type": "OrderPlaced",
            "payload": serialize(order),
            "topic": "orders.order.placed.v1",
        })
    # Transaction commits both or neither


class OutboxRelay:
    """Polls outbox and publishes to the message broker."""

    def __init__(self, db, publisher, batch_size: int = 100) -> None:
        self._db = db
        self._publisher = publisher
        self._batch_size = batch_size

    def poll_and_publish(self) -> int:
        with self._db.transaction():
            rows = self._db.query(
                """SELECT id, topic, payload FROM outbox
                   WHERE published_at IS NULL
                   ORDER BY id LIMIT %s FOR UPDATE SKIP LOCKED""",
                (self._batch_size,)
            )
            for row in rows:
                self._publisher.publish(row["topic"], row["payload"])
                self._db.execute(
                    "UPDATE outbox SET published_at = NOW() WHERE id = %s",
                    (row["id"],)
                )
            return len(rows)
```

**Rules:**
- Write business data and outbox event in the same database transaction.
- Use a poller or CDC (Debezium) to relay outbox events to the broker.
- The relay must handle duplicates — broker publishing is at-least-once.
- Use `FOR UPDATE SKIP LOCKED` in the poller to allow concurrent relay instances.
- Clean up published outbox rows periodically (after retention period).
- Prefer CDC (Debezium) over polling for lower latency and reduced DB load.

---

## Claim-Check Pattern

For messages larger than the broker's size limit (typically 1 MB for Kafka),
store the payload externally and pass a reference in the message.

```python
def publish_large_event(event: dict, s3_client, producer) -> None:
    """Store payload in S3, publish reference to Kafka."""
    payload_key = f"events/{event['type']}/{event['id']}.json"
    s3_client.put_object(
        Bucket="event-payloads",
        Key=payload_key,
        Body=json.dumps(event["data"]),
        ContentType="application/json",
    )
    # Message contains only the reference
    producer.send("orders.order.placed.v1", {
        "id": event["id"],
        "type": event["type"],
        "time": event["time"],
        "data_ref": f"s3://event-payloads/{payload_key}",
    })


def consume_large_event(message: dict, s3_client) -> dict:
    """Fetch full payload from S3 using the claim check."""
    if "data_ref" in message:
        bucket, key = parse_s3_uri(message["data_ref"])
        response = s3_client.get_object(Bucket=bucket, Key=key)
        message["data"] = json.loads(response["Body"].read())
    return message
```

**Rules:**
- Use claim-check when payload exceeds 1 MB or contains binary data.
- Store payloads in durable object storage (S3, GCS, Azure Blob).
- The message reference must include enough info to retrieve the payload.
- Set retention policies on the object store matching the message retention.
- Consumers must handle both inline and referenced payloads gracefully.

---

## Do / Don't

### Do
- Use orchestration sagas for flows with 3+ steps or conditional branching.
- Persist saga state to survive restarts and enable recovery.
- Enrich DLQ messages with full failure context (error, stack trace, retry count).
- Use exponential backoff with jitter for all retry strategies.
- Classify errors as retryable vs. non-retryable before deciding on retry.
- Use the transactional outbox pattern when you need atomic DB + publish.
- Store processed message IDs for idempotency within the business transaction.

### Don't
- Implement distributed transactions (2PC) across services — use sagas instead.
- Auto-replay DLQ messages without investigating and fixing the root cause.
- Retry non-retryable errors (validation failures, deserialization errors).
- Use fixed retry delays — they cause thundering herds under load.
- Skip compensation actions in sagas — partial completion corrupts system state.
- Put large payloads (>1 MB) directly in messages — use claim-check.
- Rely on message ordering for saga orchestration — use saga state instead.

---

## Common Pitfalls

1. **Saga compensation not idempotent** — A compensation action runs twice
   (e.g., double refund) because the saga orchestrator retried after a timeout.
   Fix: make every compensation idempotent using the saga ID as an idempotency key.

2. **Missing outbox cleanup** — The outbox table grows unbounded because
   published rows are never deleted. Fix: schedule periodic cleanup of rows
   older than the retention period (e.g., 7 days).

3. **DLQ ignored in production** — DLQ messages accumulate silently because
   no one monitors them. Fix: alert on DLQ depth > 0, assign a rotation to
   investigate and resolve DLQ messages.

4. **Check-then-act race condition** — Two instances check if a message was
   processed (both find "no"), then both process it. Fix: use `INSERT ... ON
   CONFLICT DO NOTHING` or database-level uniqueness constraints.

5. **Retry storm on permanent failure** — A validation error triggers infinite
   retries because it's classified as retryable. Fix: distinguish transient
   errors (network, timeout) from permanent errors (bad data) and route
   permanent failures directly to DLQ.

6. **Saga timeout not configured** — A saga step hangs forever because the
   downstream service is down. Fix: set a timeout per step (e.g., 30s) and
   trigger compensation when the timeout expires.

---

## Checklist

- [ ] Saga pattern selected (orchestration for complex flows, choreography for simple).
- [ ] Saga state persisted in a durable store with status tracking.
- [ ] Every saga step has a defined compensation action.
- [ ] Compensations are idempotent and tested.
- [ ] DLQ configured on every queue/topic with failure metadata enrichment.
- [ ] DLQ depth monitored and alerted on.
- [ ] DLQ tooling available (inspect, replay, discard).
- [ ] Consumers are idempotent using message ID deduplication or natural idempotency.
- [ ] Idempotency store cleaned up periodically (TTL).
- [ ] Retry strategy uses exponential backoff with jitter and max retries.
- [ ] Errors classified as retryable vs. non-retryable.
- [ ] Transactional outbox used where atomic DB + publish is required.
- [ ] Outbox relay running (poller or CDC) with published row cleanup.
- [ ] Claim-check pattern used for payloads exceeding 1 MB.
