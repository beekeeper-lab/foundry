# Event Sourcing & CQRS

Patterns for persisting state as a sequence of events and separating read/write
models. Event sourcing captures every state change as an immutable event; CQRS
splits the command (write) and query (read) responsibilities into separate models
optimized for their respective workloads.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Event Store          | PostgreSQL with append-only events table | ADR              |
| Dedicated Event Store| EventStoreDB                            | ADR               |
| Snapshot Strategy    | Every N events (default: 100)           | ADR               |
| Read Model Store     | PostgreSQL (separate schema/database)   | ADR               |
| Projection Engine    | Application-side (custom projectors)    | ADR               |
| CQRS Separation      | Logical (same DB, separate schemas)     | ADR               |
| Event Versioning     | Upcasting at deserialization            | ADR               |
| Concurrency Control  | Optimistic (expected version)           | ADR               |

### Alternatives

| Primary              | Alternative            | When                                    |
|----------------------|------------------------|-----------------------------------------|
| PostgreSQL events    | EventStoreDB           | Native event store features, subscriptions |
| PostgreSQL events    | DynamoDB               | AWS-native, pay-per-request scaling     |
| Logical CQRS         | Physical CQRS          | Independent scaling of read/write, different storage engines |
| Custom projectors    | Kafka Streams / ksqlDB | Real-time stream processing for projections |
| Upcasting            | Event versioning table | Many schema versions, complex migrations |
| Snapshot every N     | Snapshot on time interval | Consistent recovery time regardless of event count |

---

## Event Sourcing Fundamentals

### Event Store Schema (PostgreSQL)

```sql
CREATE TABLE events (
    global_sequence  BIGSERIAL     PRIMARY KEY,
    stream_id        TEXT          NOT NULL,   -- aggregate ID
    stream_version   INTEGER       NOT NULL,   -- position in stream
    event_type       TEXT          NOT NULL,   -- e.g., 'OrderPlaced'
    event_data       JSONB         NOT NULL,   -- event payload
    metadata         JSONB         NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    UNIQUE (stream_id, stream_version)
);

CREATE INDEX idx_events_stream ON events (stream_id, stream_version);
CREATE INDEX idx_events_type ON events (event_type);

-- Snapshots table
CREATE TABLE snapshots (
    stream_id        TEXT          PRIMARY KEY,
    stream_version   INTEGER       NOT NULL,
    snapshot_data    JSONB         NOT NULL,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

### Aggregate with Event Sourcing

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: str = ""
    customer_id: str = ""
    items: list = field(default_factory=list)


@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    order_id: str = ""
    tracking_number: str = ""


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: str = ""
    reason: str = ""


class Order:
    """Event-sourced aggregate. State is derived from events, never set directly."""

    def __init__(self) -> None:
        self.id: str = ""
        self.status: str = "new"
        self.items: list = []
        self.version: int = 0
        self._pending_events: List[DomainEvent] = []

    # --- Command handlers (validate + emit events) ---

    def place(self, order_id: str, customer_id: str, items: list) -> None:
        if self.status != "new":
            raise ValueError(f"Cannot place order in status: {self.status}")
        if not items:
            raise ValueError("Order must contain at least one item")
        self._apply(OrderPlaced(order_id=order_id, customer_id=customer_id, items=items))

    def ship(self, tracking_number: str) -> None:
        if self.status != "placed":
            raise ValueError(f"Cannot ship order in status: {self.status}")
        self._apply(OrderShipped(order_id=self.id, tracking_number=tracking_number))

    def cancel(self, reason: str) -> None:
        if self.status in ("shipped", "cancelled"):
            raise ValueError(f"Cannot cancel order in status: {self.status}")
        self._apply(OrderCancelled(order_id=self.id, reason=reason))

    # --- Event application (state transitions) ---

    def _apply(self, event: DomainEvent) -> None:
        self._mutate(event)
        self._pending_events.append(event)

    def _mutate(self, event: DomainEvent) -> None:
        if isinstance(event, OrderPlaced):
            self.id = event.order_id
            self.status = "placed"
            self.items = event.items
        elif isinstance(event, OrderShipped):
            self.status = "shipped"
        elif isinstance(event, OrderCancelled):
            self.status = "cancelled"
        self.version += 1

    # --- Rehydration ---

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> "Order":
        order = cls()
        for event in events:
            order._mutate(event)
        return order

    def get_pending_events(self) -> List[DomainEvent]:
        return list(self._pending_events)

    def clear_pending_events(self) -> None:
        self._pending_events.clear()
```

### Event Store Repository

```python
import json
from typing import List, Optional


class EventStore:
    """Append-only event store backed by PostgreSQL."""

    def __init__(self, connection) -> None:
        self._conn = connection

    def append(self, stream_id: str, events: List[DomainEvent],
               expected_version: int) -> None:
        """Append events with optimistic concurrency control."""
        with self._conn.cursor() as cur:
            for i, event in enumerate(events):
                version = expected_version + i + 1
                try:
                    cur.execute(
                        """INSERT INTO events (stream_id, stream_version, event_type,
                           event_data, metadata)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (stream_id, version, type(event).__name__,
                         json.dumps(serialize_event(event)),
                         json.dumps({"correlation_id": str(event.event_id)}))
                    )
                except UniqueViolation:
                    raise ConcurrencyError(
                        f"Stream {stream_id} version conflict at {version}"
                    )
            self._conn.commit()

    def load_stream(self, stream_id: str,
                    after_version: int = 0) -> List[DomainEvent]:
        """Load events for a stream, optionally after a snapshot version."""
        with self._conn.cursor() as cur:
            cur.execute(
                """SELECT event_type, event_data, stream_version
                   FROM events
                   WHERE stream_id = %s AND stream_version > %s
                   ORDER BY stream_version""",
                (stream_id, after_version)
            )
            return [deserialize_event(row) for row in cur.fetchall()]

    def load_snapshot(self, stream_id: str) -> Optional[dict]:
        """Load the latest snapshot for an aggregate."""
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT snapshot_data, stream_version FROM snapshots WHERE stream_id = %s",
                (stream_id,)
            )
            row = cur.fetchone()
            return {"data": row[0], "version": row[1]} if row else None

    def save_snapshot(self, stream_id: str, version: int, data: dict) -> None:
        """Save or update a snapshot."""
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO snapshots (stream_id, stream_version, snapshot_data)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (stream_id)
                   DO UPDATE SET stream_version = %s, snapshot_data = %s, created_at = NOW()""",
                (stream_id, version, json.dumps(data), version, json.dumps(data))
            )
            self._conn.commit()
```

**Rules:**
- Events are immutable. Never update or delete rows in the events table.
- Use optimistic concurrency control with `stream_version` to prevent conflicting writes.
- Load aggregates by replaying events from the store — the aggregate reconstructs
  its own state from the event stream.
- Separate command handlers (which validate and emit events) from event application
  (which mutates state). Commands can be rejected; events cannot.
- Use `global_sequence` for cross-stream ordering (projections, CDC).
- Snapshot after every N events (default 100) to bound rehydration time.

---

## CQRS (Command Query Responsibility Segregation)

### Architecture

```
┌──────────────┐     Commands      ┌──────────────┐
│   API Layer  │──────────────────→│ Command Side │
│              │                   │ (Aggregates) │
│              │                   │ Event Store  │
└──────────────┘                   └──────┬───────┘
       │                                  │
       │ Queries                   Events │ (publish)
       │                                  │
       ▼                                  ▼
┌──────────────┐                   ┌──────────────┐
│  Read Model  │←──────────────────│  Projector   │
│  (Optimized) │     Projections   │  (Consumer)  │
└──────────────┘                   └──────────────┘
```

### Command Handler

```python
class PlaceOrderCommand:
    def __init__(self, order_id: str, customer_id: str, items: list) -> None:
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items


class PlaceOrderHandler:
    def __init__(self, event_store: EventStore) -> None:
        self._store = event_store

    def handle(self, command: PlaceOrderCommand) -> None:
        # Load aggregate from event stream
        events = self._store.load_stream(command.order_id)
        order = Order.from_events(events)

        # Execute business logic (may raise on invalid state)
        order.place(command.order_id, command.customer_id, command.items)

        # Persist new events with optimistic concurrency
        self._store.append(
            stream_id=command.order_id,
            events=order.get_pending_events(),
            expected_version=order.version - len(order.get_pending_events()),
        )

        # Publish events to message broker for projections
        for event in order.get_pending_events():
            message_bus.publish(event)
```

### Read Model Projector

```python
class OrderSummaryProjector:
    """Builds a denormalized read model from order events."""

    def __init__(self, read_db) -> None:
        self._db = read_db

    def handle(self, event: DomainEvent) -> None:
        if isinstance(event, OrderPlaced):
            self._db.execute(
                """INSERT INTO order_summaries
                   (order_id, customer_id, status, item_count, placed_at)
                   VALUES (%s, %s, %s, %s, %s)""",
                (event.order_id, event.customer_id, "placed",
                 len(event.items), event.occurred_at)
            )
        elif isinstance(event, OrderShipped):
            self._db.execute(
                "UPDATE order_summaries SET status = 'shipped' WHERE order_id = %s",
                (event.order_id,)
            )
        elif isinstance(event, OrderCancelled):
            self._db.execute(
                "UPDATE order_summaries SET status = 'cancelled' WHERE order_id = %s",
                (event.order_id,)
            )
```

**Rules:**
- The command side owns business rules and writes to the event store.
- The read side builds denormalized views optimized for query patterns.
- Projections are eventually consistent — the read model may lag behind the
  write model. Design UIs to tolerate this (optimistic updates, loading states).
- Projectors must be idempotent — replaying the same event produces the same result.
- Store the last processed `global_sequence` per projector to enable restart
  from the correct position.
- Rebuild read models by replaying all events from the beginning. Design
  projectors so they can be torn down and rebuilt without data loss.

---

## Event Versioning

```python
# Upcaster: transforms old event schemas to the current version
class EventUpcaster:
    """Transforms events from older versions to the current schema."""

    def upcast(self, event_type: str, event_data: dict, version: int) -> dict:
        if event_type == "OrderPlaced" and version == 1:
            # v1 → v2: added 'currency' field (default USD)
            event_data.setdefault("currency", "USD")
            return event_data
        if event_type == "OrderPlaced" and version == 2:
            # v2 → v3: renamed 'items' to 'line_items'
            if "items" in event_data:
                event_data["line_items"] = event_data.pop("items")
            return event_data
        return event_data
```

**Rules:**
- Never modify stored events. Upcasting happens at deserialization time.
- Add a `schema_version` field to event metadata.
- Upcasters transform old event shapes to the current expected shape.
- Chain upcasters: v1 → v2 → v3 (each step handles one version increment).
- Test upcasters against real historical events to verify compatibility.
- For major schema changes, consider a new event type rather than upcasting.

---

## Do / Don't

### Do
- Store events as the source of truth. The event log is the authoritative record.
- Use aggregates to enforce business invariants before emitting events.
- Use optimistic concurrency control (`expected_version`) to prevent write conflicts.
- Snapshot aggregates with many events to keep rehydration time bounded.
- Design projectors to be idempotent and rebuildable from scratch.
- Use correlation IDs to trace a command through events and projections.
- Version events from the start — even v1 needs an explicit version marker.

### Don't
- Update or delete events in the event store. Events are immutable forever.
- Query the event store directly for read-heavy workloads — use projections.
- Assume strong consistency between command and query sides (it's eventually consistent).
- Put business logic in projectors — they only transform and store data.
- Use event sourcing for simple CRUD entities where it adds no value.
- Skip concurrency control — without `expected_version`, conflicting writes corrupt state.
- Build projections that depend on event ordering across different streams.

---

## Common Pitfalls

1. **Event store as CRUD** — Treating the event store like a mutable database
   (updating/deleting events) destroys the audit trail and breaks projections.
   The event store is append-only; corrections are recorded as compensating events.

2. **Unbounded event streams** — An aggregate with millions of events takes
   minutes to rehydrate. Fix: implement snapshotting (every N events) and load
   events only after the last snapshot.

3. **Projection rebuild takes hours** — Replaying all events for a large system
   is slow. Fix: partition projections by stream or time range, parallelize
   replay, and use checkpoint-based restart.

4. **Missing concurrency control** — Two commands executing simultaneously on
   the same aggregate both read version 5, both write version 6. One overwrites
   the other. Fix: use `expected_version` and retry on conflict.

5. **Event schema migration breaks consumers** — Changing the event structure
   breaks existing projectors and downstream consumers. Fix: use upcasters,
   never modify stored events, and add new fields with defaults.

6. **Eventual consistency confusion** — Users see stale data in the read model
   immediately after a write. Fix: return the command result directly (e.g.,
   the new version or ID), use optimistic UI updates, or poll until the
   projection catches up.

---

## Checklist

- [ ] Events table is append-only; no UPDATE or DELETE operations permitted.
- [ ] Optimistic concurrency control implemented with `expected_version`.
- [ ] Aggregates enforce invariants in command handlers before emitting events.
- [ ] Snapshot strategy configured (every N events) for long-lived aggregates.
- [ ] Projectors are idempotent and track their last processed position.
- [ ] Projections can be fully rebuilt by replaying all events.
- [ ] Event versioning strategy defined (upcasters or versioned types).
- [ ] Correlation IDs flow from command → events → projections.
- [ ] Read model staleness is communicated to the UI (timestamps, loading states).
- [ ] No business logic in projectors — only data transformation.
