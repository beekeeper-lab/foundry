# Event-Driven Operations

Production operations for event-driven systems: monitoring, scaling, partition
management, consumer group operations, disaster recovery, and performance tuning.

---

## Monitoring

### Key Metrics

| Metric                          | Source         | Alert Threshold              |
|---------------------------------|----------------|------------------------------|
| Consumer lag (messages behind)  | Kafka/Burrow   | > 10,000 for 5 min           |
| Consumer lag (time behind)      | Kafka          | > 60s for 5 min              |
| DLQ depth                       | Broker metrics | > 0 (investigate immediately) |
| Message throughput (msg/sec)    | Broker metrics | < 50% of baseline for 5 min  |
| Producer error rate             | App metrics    | > 1% for 5 min               |
| Consumer error rate             | App metrics    | > 5% for 5 min               |
| End-to-end latency (p99)       | OpenTelemetry  | > 5s for 5 min               |
| Broker disk usage               | Broker metrics | > 80%                        |
| Under-replicated partitions     | Kafka JMX      | > 0 for 10 min               |
| Consumer rebalance rate         | Kafka metrics  | > 2/hour                     |
| RabbitMQ queue memory           | Management API | > 80% of high watermark      |
| RabbitMQ unacknowledged msgs    | Management API | > prefetch * 10              |

### Distributed Tracing

```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract

tracer = trace.get_tracer("messaging")


def publish_with_trace(producer, topic: str, message: dict) -> None:
    """Inject trace context into message headers for end-to-end tracing."""
    with tracer.start_as_current_span(f"publish {topic}") as span:
        span.set_attribute("messaging.system", "kafka")
        span.set_attribute("messaging.destination", topic)
        span.set_attribute("messaging.message_id", message["id"])

        headers = {}
        inject(headers)  # Inject W3C traceparent into headers
        message["_trace_headers"] = headers
        producer.send(topic, message)


def consume_with_trace(message: dict) -> None:
    """Extract trace context from message headers to continue the trace."""
    headers = message.get("_trace_headers", {})
    context = extract(headers)

    with tracer.start_as_current_span(
        f"consume {message.get('type', 'unknown')}",
        context=context,
    ) as span:
        span.set_attribute("messaging.system", "kafka")
        span.set_attribute("messaging.message_id", message["id"])
        process_message(message)
```

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Event-Driven System Health                       │
├─────────────────────┬───────────────────────┬───────────────────────┤
│  Consumer Lag       │  Throughput (msg/s)    │  Error Rate           │
│  ████░░░ 2,341      │  ▓▓▓▓▓▓▓▓ 12,450     │  ░░░░░░░░ 0.02%      │
│  per group          │  produce / consume     │  per consumer group   │
├─────────────────────┼───────────────────────┼───────────────────────┤
│  DLQ Depth          │  E2E Latency (p99)    │  Rebalances/hr        │
│  ░░░░░░░░ 0         │  ██░░░░░░ 340ms       │  ░░░░░░░░ 0           │
│  across all topics  │  per consumer group    │  across all groups    │
├─────────────────────┴───────────────────────┴───────────────────────┤
│  Under-replicated: 0  │  Broker Disk: 42%  │  Active Consumers: 24  │
└─────────────────────────────────────────────────────────────────────┘
```

**Rules:**
- Instrument every producer and consumer with OpenTelemetry traces and Prometheus metrics.
- Propagate W3C `traceparent` headers through messages for end-to-end tracing.
- Alert on consumer lag (both count and time), DLQ depth, and error rate.
- Create per-consumer-group dashboards showing lag, throughput, and error rate.
- Track end-to-end latency from produce to consume completion.
- Monitor broker health: disk usage, ISR count, under-replicated partitions.

---

## Kafka Operations

### Partition Management

```bash
# Check partition count and replication
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --topic orders.order.placed.v1

# Increase partitions (cannot decrease)
kafka-topics.sh --bootstrap-server kafka:9092 \
  --alter --topic orders.order.placed.v1 --partitions 12

# Reassign partitions across brokers
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file reassignment.json --execute
```

**Partition sizing guidelines:**

| Throughput (msg/sec) | Partitions | Consumer Instances |
|----------------------|------------|--------------------|
| < 1,000              | 3-6        | 1-3                |
| 1,000 - 10,000       | 6-12       | 3-6                |
| 10,000 - 100,000     | 12-30      | 6-15               |
| > 100,000            | 30-60+     | 15-30+             |

**Rules:**
- Partition count >= max consumer instances in a consumer group.
- Partitions can only be increased, never decreased. Plan ahead.
- More partitions = more parallelism but also more memory, file handles, and
  rebalance time. Don't over-partition.
- Use key-based partitioning for ordering guarantees within an aggregate.
- When changing partition count, messages with the same key may land on different
  partitions. Plan for this in consumers.

### Consumer Group Management

```bash
# List consumer groups
kafka-consumer-groups.sh --bootstrap-server kafka:9092 --list

# Describe consumer group (lag, assignments)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group shipping-service --describe

# Reset offsets (use with caution)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group shipping-service --topic orders.order.placed.v1 \
  --reset-offsets --to-earliest --execute
```

### Retention and Compaction

```properties
# Time-based retention (default)
log.retention.hours=168          # 7 days

# Size-based retention (per partition)
log.retention.bytes=1073741824   # 1 GB per partition

# Compacted topics (keep latest per key)
log.cleanup.policy=compact
min.compaction.lag.ms=86400000   # Don't compact messages younger than 24h
```

**Rules:**
- Set retention based on your replay and recovery requirements.
- Use compacted topics for state/snapshot topics where only the latest value per
  key matters (e.g., user profiles, configuration).
- Never set retention lower than your longest consumer lag window.
- Monitor disk usage relative to retention settings.

---

## RabbitMQ Operations

### Queue Management

```bash
# List queues with message counts
rabbitmqctl list_queues name messages consumers

# Purge a queue (destructive — use with caution)
rabbitmqctl purge_queue shipping-service.order-placed

# Set queue limits
rabbitmqctl set_policy queue-limits ".*" \
  '{"max-length": 1000000, "overflow": "reject-publish"}' \
  --apply-to queues
```

### Cluster Configuration

```bash
# Check cluster status
rabbitmqctl cluster_status

# Enable high availability (mirrored queues → quorum queues preferred)
# Quorum queues (RabbitMQ 3.8+) are the preferred HA mechanism
rabbitmqctl set_policy ha-orders "^orders\." \
  '{"queue-mode": "lazy", "ha-mode": "exactly", "ha-params": 2}' \
  --apply-to queues
```

**Rules:**
- Use quorum queues (not classic mirrored queues) for high availability.
- Set `max-length` and `overflow: reject-publish` to prevent unbounded queue growth.
- Enable lazy queues for queues that routinely have large backlogs.
- Monitor memory and disk alarms — RabbitMQ blocks publishers when thresholds are hit.
- Use the Management Plugin for operational visibility.

---

## Scaling

### Kafka Consumer Scaling

```
# Scale consumers up to the partition count
Topic: orders.order.placed.v1 (12 partitions)

Group: shipping-service
  Consumer-1: partitions [0, 1, 2, 3]    # 4 partitions
  Consumer-2: partitions [4, 5, 6, 7]    # 4 partitions
  Consumer-3: partitions [8, 9, 10, 11]  # 4 partitions

# Adding Consumer-4 triggers rebalance
  Consumer-1: partitions [0, 1, 2]       # 3 partitions
  Consumer-2: partitions [3, 4, 5]       # 3 partitions
  Consumer-3: partitions [6, 7, 8]       # 3 partitions
  Consumer-4: partitions [9, 10, 11]     # 3 partitions

# Adding Consumer-13 is wasteful — it gets no partitions
```

### Auto-Scaling Policy

```yaml
# Kubernetes HPA based on consumer lag
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-consumer
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-consumer
  minReplicas: 2
  maxReplicas: 12   # <= partition count
  metrics:
    - type: External
      external:
        metric:
          name: kafka_consumer_lag
          selector:
            matchLabels:
              consumer_group: shipping-service
              topic: orders.order.placed.v1
        target:
          type: AverageValue
          averageValue: "5000"
```

**Rules:**
- Kafka: max consumer instances per group = partition count. Beyond that,
  instances are idle.
- Scale consumers based on lag, not CPU. Lag is the meaningful metric for
  message processing.
- When scaling up, expect a brief rebalance period where processing pauses.
- Use cooperative sticky assignor to minimize partition movement during rebalance.
- For RabbitMQ: add more consumers to a queue for horizontal scaling (no
  partition limit, but ordering is not guaranteed).

---

## Disaster Recovery

### Kafka

```bash
# Mirror topics to a standby cluster
# Use MirrorMaker 2 (MM2) for cross-cluster replication

# mm2.properties
clusters = primary, standby
primary.bootstrap.servers = kafka-primary:9092
standby.bootstrap.servers = kafka-standby:9092
primary->standby.enabled = true
primary->standby.topics = orders\..*

# Verify replication lag
kafka-consumer-groups.sh --bootstrap-server kafka-standby:9092 \
  --group mm2-consumer --describe
```

### RabbitMQ

```bash
# Federation for cross-datacenter replication
rabbitmqctl set_parameter federation-upstream standby \
  '{"uri": "amqp://standby-rabbit:5672", "ack-mode": "on-confirm"}'

# Shovel for moving messages between clusters
rabbitmqctl set_parameter shovel migrate-orders \
  '{"src-uri": "amqp://primary:5672", "src-queue": "orders",
    "dest-uri": "amqp://standby:5672", "dest-queue": "orders"}'
```

### Recovery Procedures

| Scenario                  | Kafka Recovery                        | RabbitMQ Recovery                  |
|---------------------------|---------------------------------------|------------------------------------|
| Single broker failure     | ISR replicas take over automatically  | Quorum queue leader election       |
| Full cluster failure      | Failover to standby (MM2)            | Promote standby (federation)       |
| Consumer data corruption  | Reset offsets to known-good position  | Purge + replay from source         |
| Schema registry failure   | Restore from backup, schemas in Avro files | N/A                           |

**Rules:**
- Maintain a standby cluster for critical topics using MM2 (Kafka) or federation (RabbitMQ).
- Test failover procedures quarterly. Untested DR is not DR.
- Document runbooks for every failure scenario in the table above.
- Kafka: set `min.insync.replicas=2` with `replication.factor=3` for durability.
- RabbitMQ: use quorum queues which handle node failures automatically.
- Back up the Schema Registry. Lost schemas = consumers cannot deserialize.

---

## Performance Tuning

### Kafka Producer Tuning

```properties
# Batch messages for throughput
batch.size=65536                   # 64 KB
linger.ms=10                       # Wait up to 10ms for batch to fill
compression.type=lz4               # Compress batches (lz4 = fast, good ratio)
buffer.memory=67108864             # 64 MB send buffer
max.in.flight.requests.per.connection=5  # With idempotence enabled
```

### Kafka Consumer Tuning

```properties
# Fetch tuning
fetch.min.bytes=1024               # Min bytes before returning a fetch
fetch.max.wait.ms=500              # Max wait time for fetch.min.bytes
max.partition.fetch.bytes=1048576  # 1 MB per partition per fetch

# Session and poll tuning
session.timeout.ms=30000           # Broker marks consumer dead after 30s
heartbeat.interval.ms=10000        # Heartbeat frequency (1/3 of session timeout)
max.poll.interval.ms=300000        # Max time between polls before rebalance
max.poll.records=500               # Records per poll
```

### RabbitMQ Tuning

```bash
# Connection and channel limits
rabbitmqctl set_vm_memory_high_watermark 0.6

# Publisher confirms batch size
# (application-level — batch confirms every N messages)
CONFIRM_BATCH_SIZE=100

# Prefetch (QoS) — balance throughput vs. fairness
# Low prefetch (1-10): fair distribution, lower throughput
# High prefetch (50-250): better throughput, less fair
channel.basic_qos(prefetch_count=50)
```

### Performance Benchmarks

| Scenario                    | Kafka (3 brokers)     | RabbitMQ (3 nodes)     |
|-----------------------------|----------------------|------------------------|
| Throughput (1 KB msgs)      | 500K-1M msg/sec      | 20K-50K msg/sec        |
| Latency (p99, 1 KB)        | 5-15ms               | 1-5ms                  |
| Persistent + replicated     | 200K-500K msg/sec    | 10K-25K msg/sec        |
| Message size sweet spot     | 1 KB - 100 KB        | 1 KB - 50 KB           |
| Consumer groups supported   | Thousands             | Hundreds               |

**Rules:**
- Tune `batch.size` and `linger.ms` together. Larger batches = higher throughput
  but higher latency.
- Use `lz4` compression for the best throughput/compression ratio.
- Set `max.poll.interval.ms` > worst-case processing time for a batch to avoid
  unnecessary rebalances.
- Set `session.timeout.ms` and `heartbeat.interval.ms` at a 3:1 ratio.
- RabbitMQ: tune `prefetch_count` based on consumer processing speed. Start at
  50 and adjust.
- Benchmark with production-like message sizes and patterns before going live.

---

## Do / Don't

### Do
- Monitor consumer lag as the primary health indicator for event-driven systems.
- Propagate trace context (W3C traceparent) through all messages.
- Set up auto-scaling based on consumer lag, not CPU utilization.
- Use cooperative sticky assignor (Kafka) to minimize rebalance disruption.
- Test disaster recovery procedures quarterly with realistic failover scenarios.
- Tune producer batching and consumer prefetch for your specific workload.
- Document runbooks for every operational scenario.

### Don't
- Add more Kafka consumers than partitions — excess instances sit idle.
- Set retention shorter than your longest consumer lag window.
- Ignore under-replicated partitions — they indicate broker or disk problems.
- Use auto-purge on queues without understanding the consequences.
- Skip performance testing — production traffic patterns differ from defaults.
- Forget to monitor broker-level metrics (disk, memory, ISR) alongside application metrics.

---

## Common Pitfalls

1. **Rebalance storm from slow consumers** — A slow consumer exceeds
   `max.poll.interval.ms`, triggers a rebalance, which causes other consumers to
   pause, increasing lag further. Fix: increase `max.poll.interval.ms`, reduce
   `max.poll.records`, or process messages faster.

2. **Disk full on Kafka broker** — Retention settings allow more data than disk
   capacity. Kafka stops accepting writes. Fix: monitor disk usage relative to
   retention, set alerts at 80%, and ensure retention * throughput < disk capacity.

3. **RabbitMQ memory alarm blocks all publishers** — A consumer goes down, messages
   pile up in memory, RabbitMQ triggers the memory alarm and blocks all publishers
   system-wide. Fix: use lazy queues, set `max-length` policies, and monitor queue depth.

4. **Schema Registry is a single point of failure** — If the registry goes down,
   producers and consumers can't serialize/deserialize new schemas. Fix: run the
   registry in HA mode, back up schemas, and cache schemas locally in consumers.

5. **Partition key change breaks ordering** — Changing the partition count means
   the same key may hash to a different partition. Consumers that depend on
   ordering see events out of order. Fix: plan partition count upfront, and if
   you must change, migrate consumers to handle the transition.

---

## Checklist

- [ ] OpenTelemetry traces instrumented on all producers and consumers.
- [ ] Prometheus metrics exported: lag, throughput, error rate, latency.
- [ ] Grafana dashboard created with consumer lag, DLQ depth, and throughput panels.
- [ ] Alerts configured for consumer lag, DLQ depth > 0, and error rate spikes.
- [ ] Kafka: `min.insync.replicas=2`, `replication.factor=3` on production topics.
- [ ] Kafka: partition count aligned with consumer scaling requirements.
- [ ] RabbitMQ: quorum queues used for durable, HA queues.
- [ ] RabbitMQ: `max-length` and memory policies configured.
- [ ] Auto-scaling configured based on consumer lag metric.
- [ ] Disaster recovery plan documented and tested quarterly.
- [ ] MirrorMaker 2 (Kafka) or federation (RabbitMQ) configured for standby.
- [ ] Performance benchmarked with production-like workloads.
- [ ] Producer batching and consumer prefetch tuned for workload.
- [ ] Operational runbooks documented for all failure scenarios.
