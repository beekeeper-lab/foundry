# Event-Driven / Messaging Stack Conventions

Non-negotiable defaults for event-driven architectures and asynchronous messaging.
Covers broker selection, message design, serialization, consumer patterns, and
topic/queue governance. Deviations require an ADR with justification.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Message Broker       | Apache Kafka 3.x                        | ADR               |
| Task Queue           | RabbitMQ 3.13+                          | ADR               |
| Serialization        | Apache Avro + Schema Registry           | ADR               |
| Schema Registry      | Confluent Schema Registry               | ADR               |
| Schema Evolution     | BACKWARD compatible                     | ADR               |
| Message Envelope     | CloudEvents v1.0 specification          | ADR               |
| Consumer Model       | Consumer group (competing consumers)    | ADR               |
| Delivery Guarantee   | At-least-once                           | ADR               |
| Idempotency          | Consumer-side deduplication             | Never             |
| Dead Letter Queue    | Enabled on every queue/topic            | Never             |
| Retry Policy         | Exponential backoff with jitter         | ADR               |
| Observability        | OpenTelemetry traces + Prometheus metrics | ADR             |

### Alternatives

| Primary              | Alternative            | When                                    |
|----------------------|------------------------|-----------------------------------------|
| Kafka                | RabbitMQ               | Simple task queues, low-throughput routing |
| Kafka                | Amazon SQS/SNS         | AWS-native, no Kafka ops budget         |
| Kafka                | NATS JetStream         | Ultra-low latency, edge deployments     |
| RabbitMQ             | Amazon SQS             | Managed service, no RabbitMQ ops budget |
| Avro                 | Protobuf               | gRPC ecosystem, language-neutral IDL    |
| Avro                 | JSON Schema            | Simple payloads, human-readable debugging |
| CloudEvents          | Custom envelope        | Legacy system interop (wrap with adapter) |
| Confluent SR         | Apicurio Registry      | Open-source, no Confluent license       |

---

## Message Design

### Envelope Structure (CloudEvents)

```json
{
  "specversion": "1.0",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source": "/orders/order-service",
  "type": "com.example.orders.OrderPlaced",
  "datacontenttype": "application/avro",
  "time": "2026-02-20T12:00:00Z",
  "subject": "order-12345",
  "data": { ... }
}
```

**Rules:**
- Every message has a globally unique `id` (UUID v7 preferred for time-ordering).
- `type` follows reverse-domain notation: `com.{org}.{domain}.{EventName}`.
- `source` identifies the producing service and bounded context.
- `time` is always UTC ISO-8601 with timezone offset.
- `subject` carries the aggregate/entity ID for routing and partitioning.

### Event Naming

```
# Pattern: {Domain}.{Aggregate}{PastTenseVerb}
com.example.orders.OrderPlaced
com.example.orders.OrderShipped
com.example.payments.PaymentCaptured
com.example.inventory.StockReserved

# Commands (imperative, not events)
com.example.orders.PlaceOrder
com.example.payments.CapturePayment
```

**Rules:**
- Events are past-tense facts: something **has happened**.
- Commands are imperative: something **should happen**.
- Never mix events and commands on the same topic/queue.
- Use domain-qualified names to avoid collisions across bounded contexts.

---

## Topic / Queue Governance

### Kafka Topics

```
# Pattern: {domain}.{aggregate}.{event-type}.{version}
orders.order.placed.v1
orders.order.shipped.v1
payments.payment.captured.v1

# Dead letter topics
orders.order.placed.v1.dlq

# Retry topics (for delayed retry)
orders.order.placed.v1.retry-1
orders.order.placed.v1.retry-2
orders.order.placed.v1.retry-3
```

### RabbitMQ Exchanges and Queues

```
# Exchange naming: {domain}.{type}
orders.topic          # Topic exchange for order events
payments.fanout       # Fanout for payment notifications

# Queue naming: {consumer-service}.{event-type}
shipping-service.order-placed
notification-service.order-placed

# Dead letter exchange
dlx.orders
```

**Rules:**
- One schema per topic. Never mix event types on a single Kafka topic.
- Kafka: use partitioning by aggregate ID for ordering guarantees within an entity.
- RabbitMQ: use topic exchanges for flexible routing, direct exchanges for point-to-point.
- Version topics when making breaking schema changes (`v1` → `v2`).
- Register all topics/queues in a central catalog (wiki, schema registry, or IaC).

---

## Serialization

### Avro Schema Example

```json
{
  "type": "record",
  "name": "OrderPlaced",
  "namespace": "com.example.orders",
  "fields": [
    { "name": "orderId", "type": "string" },
    { "name": "customerId", "type": "string" },
    { "name": "items", "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "OrderItem",
          "fields": [
            { "name": "productId", "type": "string" },
            { "name": "quantity", "type": "int" },
            { "name": "unitPrice", "type": { "type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2 } }
          ]
        }
      }
    },
    { "name": "placedAt", "type": { "type": "long", "logicalType": "timestamp-millis" } },
    { "name": "metadata", "type": ["null", { "type": "map", "values": "string" }], "default": null }
  ]
}
```

**Rules:**
- Register every schema in the Schema Registry before producing messages.
- Use BACKWARD compatibility mode: new schemas can read old data.
- Add new fields with defaults (`"default": null` or a sensible value).
- Never remove or rename fields — add new ones and deprecate old ones.
- Use logical types for timestamps (`timestamp-millis`), decimals, and UUIDs.
- Pin schema versions in consumer configurations; never auto-upgrade in production.

---

## Producer Patterns

```java
// Kafka producer with idempotency enabled
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);
props.put("schema.registry.url", "http://schema-registry:8081");

KafkaProducer<String, OrderPlaced> producer = new KafkaProducer<>(props);

// Partition by aggregate ID for ordering guarantees
ProducerRecord<String, OrderPlaced> record = new ProducerRecord<>(
    "orders.order.placed.v1",
    event.getOrderId(),   // key = aggregate ID
    event                 // value = Avro-serialized event
);

producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        log.error("produce_failed topic={} key={}", record.topic(), record.key(), exception);
    } else {
        log.info("produce_succeeded topic={} partition={} offset={}",
            metadata.topic(), metadata.partition(), metadata.offset());
    }
});
```

**Rules:**
- Always set `acks=all` for durability. Never use `acks=0` or `acks=1` in production.
- Enable idempotent producer (`enable.idempotence=true`) to prevent duplicates on retry.
- Use the aggregate/entity ID as the message key for partition-level ordering.
- Handle send failures with callbacks or futures — never fire-and-forget.
- Use transactional producer when publishing to multiple topics atomically.

---

## Consumer Patterns

```java
// Kafka consumer with manual offset commit
Properties props = new Properties();
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "shipping-service");
props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 100);
props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class);

KafkaConsumer<String, OrderPlaced> consumer = new KafkaConsumer<>(props);
consumer.subscribe(List.of("orders.order.placed.v1"));

while (running) {
    ConsumerRecords<String, OrderPlaced> records = consumer.poll(Duration.ofMillis(500));
    for (ConsumerRecord<String, OrderPlaced> record : records) {
        try {
            processEvent(record.value());
            // Commit after successful processing
            consumer.commitSync(Map.of(
                new TopicPartition(record.topic(), record.partition()),
                new OffsetAndMetadata(record.offset() + 1)
            ));
        } catch (RetryableException e) {
            publishToRetryTopic(record, e);
        } catch (Exception e) {
            publishToDeadLetterTopic(record, e);
        }
    }
}
```

**Rules:**
- Disable auto-commit (`enable.auto.commit=false`). Commit offsets only after
  successful processing.
- Use `earliest` auto-offset-reset so new consumer groups process from the beginning.
- Set `max.poll.records` to control batch size and avoid rebalance timeouts.
- Handle poison pills: catch deserialization errors and route to DLQ.
- Consumers must be idempotent — the same message may be delivered more than once.

---

## RabbitMQ Patterns

```python
import pika
import json

# Publisher with confirms
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.confirm_delivery()

channel.exchange_declare(exchange='orders.topic', exchange_type='topic', durable=True)

# Publish with mandatory flag and persistence
channel.basic_publish(
    exchange='orders.topic',
    routing_key='order.placed',
    body=json.dumps(event),
    properties=pika.BasicProperties(
        delivery_mode=2,           # persistent
        content_type='application/json',
        message_id=str(uuid.uuid4()),
        timestamp=int(time.time()),
        headers={'version': '1'},
    ),
    mandatory=True,
)

# Consumer with manual ack and prefetch
channel.queue_declare(queue='shipping-service.order-placed', durable=True, arguments={
    'x-dead-letter-exchange': 'dlx.orders',
    'x-dead-letter-routing-key': 'order.placed.dlq',
    'x-message-ttl': 86400000,    # 24h TTL
})
channel.queue_bind(queue='shipping-service.order-placed',
                   exchange='orders.topic',
                   routing_key='order.placed')

channel.basic_qos(prefetch_count=10)

def callback(ch, method, properties, body):
    try:
        process_event(json.loads(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except RetryableError:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # → DLQ

channel.basic_consume(queue='shipping-service.order-placed', on_message_callback=callback)
channel.start_consuming()
```

**Rules:**
- Enable publisher confirms. Never assume a publish succeeded without confirmation.
- Set `delivery_mode=2` (persistent) for durable messages.
- Always declare queues as `durable=True` and configure dead-letter exchanges.
- Use `basic_qos(prefetch_count=N)` to limit in-flight messages per consumer.
- Use manual acknowledgment (`basic_ack`/`basic_nack`). Never use auto-ack in production.
- Use `basic_nack(requeue=False)` to route unprocessable messages to the DLQ.

---

## Do / Don't

### Do
- Design messages as immutable facts — events describe what happened, not what to do.
- Include a unique message ID and correlation ID in every message envelope.
- Use schema evolution (Avro/Protobuf + Schema Registry) for contract management.
- Partition by aggregate ID to guarantee ordering within an entity.
- Enable dead-letter queues on every topic/queue from day one.
- Make every consumer idempotent — store processed message IDs or use natural idempotency keys.
- Monitor consumer lag, error rates, and DLQ depth as primary health indicators.
- Test message contracts with consumer-driven contract tests (Pact or schema compatibility checks).
- Use correlation IDs to trace message flows across services.

### Don't
- Put multiple event types on a single Kafka topic — it breaks schema evolution and consumer isolation.
- Use auto-commit (Kafka) or auto-ack (RabbitMQ) — it risks losing messages on crash.
- Include large payloads (>1 MB) in messages — use claim-check pattern with object storage.
- Rely on message ordering across partitions — order is guaranteed only within a partition.
- Expose internal domain objects as message schemas — create dedicated event schemas.
- Use synchronous request-reply over messaging unless latency is acceptable.
- Hard-code broker addresses — use service discovery or environment configuration.
- Ignore schema compatibility checks — breaking changes will crash consumers.

---

## Common Pitfalls

1. **Consumer lag snowball** — A slow consumer falls behind, increasing lag.
   Backpressure triggers rebalancing, which causes further lag. Fix: right-size
   partitions, tune `max.poll.records`, scale consumer instances, and alert on
   lag thresholds before they snowball.

2. **Poison pill messages** — A malformed message crashes the consumer in a loop.
   The consumer restarts, re-reads the same message, crashes again. Fix: wrap
   deserialization in try-catch, route unparseable messages to the DLQ immediately.

3. **Duplicate processing without idempotency** — At-least-once delivery means
   duplicates will happen (network retries, rebalances, crashes). Fix: store
   processed message IDs in the database within the same transaction as the
   business operation, or use natural idempotency keys.

4. **Schema evolution breaks consumers** — A producer adds a required field
   without a default, breaking all existing consumers. Fix: always add new fields
   with defaults, use BACKWARD compatibility mode, and test schema changes against
   the registry before deploying.

5. **Unbounded retry storms** — Retrying a failed message forever creates an
   infinite loop that wastes resources. Fix: use exponential backoff with a max
   retry count, then route to DLQ for manual investigation.

6. **Lost messages from fire-and-forget** — Publishing without `acks=all` (Kafka)
   or without publisher confirms (RabbitMQ) means messages can vanish silently.
   Fix: always use durable publishing with acknowledgments.

7. **Rebalance thrashing** — Consumers that take too long to process a batch
   trigger session timeouts and rebalances. Fix: tune `max.poll.interval.ms`,
   reduce batch size, or use static group membership.

---

## Checklist

- [ ] Message broker selected and justified (Kafka for streaming, RabbitMQ for task queues).
- [ ] All messages use a standard envelope (CloudEvents or equivalent).
- [ ] Schemas registered in Schema Registry with BACKWARD compatibility.
- [ ] Every topic/queue has a corresponding dead-letter topic/queue configured.
- [ ] Producers use `acks=all` (Kafka) or publisher confirms (RabbitMQ).
- [ ] Consumers use manual offset commit / manual ack — no auto-commit/auto-ack.
- [ ] Consumers are idempotent — duplicate messages do not cause side effects.
- [ ] Retry policy configured with exponential backoff, max retries, and DLQ fallback.
- [ ] Consumer lag monitored with alerts on threshold breaches.
- [ ] Correlation IDs propagated through all message flows.
- [ ] Schema evolution tested before deployment (compatibility check in CI).
- [ ] No secrets or PII in message headers or unencrypted payloads.
- [ ] Topic/queue naming follows governance conventions.
- [ ] Message payloads under 1 MB (claim-check for larger data).
