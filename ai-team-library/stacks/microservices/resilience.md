# Microservices Resilience

Standards for circuit breakers, retries, timeouts, bulkheads, rate limiting, and
graceful degradation. These patterns prevent cascading failures in distributed
systems.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Circuit Breaker      | Per-dependency circuit breaker           | Never             |
| Retry Policy         | 3 retries, exponential backoff + jitter  | Per-service config|
| Request Timeout      | 5 seconds (tune per dependency)          | Per-service config|
| Bulkhead             | Thread pool / semaphore per dependency   | ADR               |
| Rate Limiting        | Token bucket at API gateway              | ADR               |
| Fallback Strategy    | Cached/default response on failure       | Per-service config|
| Health Checks        | Liveness + readiness probes              | Never             |
| Load Shedding        | Return 503 when capacity exceeded        | ADR               |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| Custom circuit breaker| Resilience4j (JVM)  | JVM-based services with complex policies  |
| Custom circuit breaker| Polly (.NET)        | .NET services                             |
| Custom circuit breaker| Istio (mesh-level)  | Uniform resilience across all services    |
| Token bucket limiter | Sliding window       | Smoother rate enforcement needed          |
| Local rate limiting  | Distributed (Redis)  | Multi-instance services sharing quotas    |

---

## Circuit Breaker

```
    ┌──────────┐   success   ┌──────────┐
    │  CLOSED  │◀────────────│HALF-OPEN │
    │(normal)  │             │(testing) │
    └────┬─────┘             └────┬─────┘
         │ failures               │ failure
         │ exceed                 │
         │ threshold              │
         ▼                        │
    ┌──────────┐                  │
    │   OPEN   │──── timeout ─────┘
    │(failing) │
    └──────────┘
```

### Configuration

```python
# Circuit breaker with sensible defaults.
class CircuitBreakerConfig:
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 3          # Successes in half-open before closing
    timeout_seconds: float = 30.0       # Time in open state before testing
    slow_call_threshold_ms: float = 2000  # Calls slower than this count as failures
    slow_call_rate_threshold: float = 0.8  # % of slow calls that triggers opening
    window_size: int = 10               # Rolling window of calls to evaluate
```

### Implementation Pattern

```python
import time
from enum import Enum
from collections import deque

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failures = deque(maxlen=config.window_size)
        self.last_failure_time = 0.0
        self.half_open_successes = 0

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.last_failure_time > self.config.timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.half_open_successes = 0
            else:
                raise CircuitOpenError(f"Circuit {self.name} is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as err:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_successes += 1
            if self.half_open_successes >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failures.clear()

    def _on_failure(self):
        self.failures.append(time.monotonic())
        self.last_failure_time = time.monotonic()
        failure_count = len(self.failures)
        if failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
```

**Rules:**
- Create one circuit breaker per external dependency (database, service, third-party API).
- Never share a circuit breaker across unrelated dependencies.
- Monitor circuit breaker state transitions as metrics.
- Alert when a circuit opens — it indicates a downstream failure.
- Configure thresholds based on the dependency's SLA, not arbitrary numbers.
- Include slow-call detection. A call that takes 10 seconds is worse than a fast failure.

---

## Retry Policy

```python
import asyncio
import random

async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    retryable_exceptions: tuple = (TimeoutError, ConnectionError),
):
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as err:
            if attempt == max_retries:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = delay * random.uniform(0.5, 1.0)
            await asyncio.sleep(jitter)
```

**Rules:**
- Retry only on transient errors (timeouts, 503, connection reset). Never retry on
  400, 401, 404, or 422 — these are deterministic failures.
- Use exponential backoff with jitter to prevent thundering herd on recovery.
- Set a maximum number of retries (3 is the default). More retries increase load on
  a struggling dependency.
- Retries must be idempotent. If the operation is not idempotent, do not retry.
- Log every retry attempt with the attempt number and delay for debugging.
- Combine retries with circuit breakers: retries handle transient blips, circuit
  breakers handle sustained failures.

### Retry Budget

```
# Per-service retry budget — limit total retry traffic.
# If more than 20% of requests are retries, stop retrying to avoid amplification.
retry_budget:
  max_retry_ratio: 0.2      # Max 20% of total traffic can be retries
  min_retries_per_second: 10 # Always allow at least 10 retries/sec
  ttl_seconds: 10            # Window for calculating retry ratio
```

---

## Timeout Strategy

```yaml
# Timeout configuration per dependency.
timeouts:
  inventory-service:
    connect: 1s
    read: 3s
    write: 3s
  payment-service:
    connect: 2s
    read: 10s    # Payment processing is slower
    write: 5s
  cache:
    connect: 0.5s
    read: 0.5s
  database:
    connect: 2s
    query: 5s
    transaction: 30s
```

**Rules:**
- Set separate connect, read, and write timeouts. A single "timeout" is too coarse.
- Tune timeouts per dependency based on measured p99 latency plus headroom.
- The overall request timeout must be less than the caller's timeout. Propagate
  deadline context to prevent wasted work.
- Use deadline propagation: if the caller has 5s left, do not start a 10s operation.
- A timeout is a failure. Record it in metrics and count it against the circuit breaker.
- Never use infinite timeouts. Every I/O call must have a finite timeout.

---

## Bulkhead Pattern

```python
import asyncio

class Bulkhead:
    """Limits concurrent calls to a dependency to prevent resource exhaustion."""

    def __init__(self, name: str, max_concurrent: int = 25, max_wait: float = 5.0):
        self.name = name
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_wait = max_wait

    async def call(self, func, *args, **kwargs):
        try:
            await asyncio.wait_for(self.semaphore.acquire(), timeout=self.max_wait)
        except asyncio.TimeoutError:
            raise BulkheadFullError(f"Bulkhead {self.name} is full")
        try:
            return await func(*args, **kwargs)
        finally:
            self.semaphore.release()

# Usage: one bulkhead per dependency.
inventory_bulkhead = Bulkhead("inventory-service", max_concurrent=25)
payment_bulkhead = Bulkhead("payment-service", max_concurrent=10)
```

**Rules:**
- Isolate each external dependency behind its own bulkhead (semaphore or thread pool).
- Size the bulkhead based on the dependency's capacity, not the caller's capacity.
- Fail fast when the bulkhead is full — do not queue indefinitely.
- Monitor bulkhead saturation as a metric. High saturation indicates a bottleneck.
- Combine bulkheads with circuit breakers: bulkheads limit concurrency, circuit breakers
  stop calls after failures.

---

## Rate Limiting

```python
import time

class TokenBucket:
    """Rate limiter using token bucket algorithm."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate          # Tokens per second
        self.capacity = capacity  # Max burst size
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

**Rules:**
- Apply rate limiting at the API gateway for external traffic.
- Use per-client rate limits based on API key or tenant ID.
- Return `429 Too Many Requests` with `Retry-After` header when rate limited.
- Use token bucket for bursty traffic, sliding window for smooth enforcement.
- For multi-instance services, use distributed rate limiting (Redis-based).
- Rate limit internal service-to-service calls only when protecting critical resources.

---

## Graceful Degradation

```python
# Fallback to cached data when a dependency is unavailable.
async def get_product_recommendations(user_id: str) -> list[Product]:
    try:
        return await recommendation_service.get_recommendations(user_id)
    except (CircuitOpenError, TimeoutError):
        # Degrade gracefully: return cached popular products.
        cached = await cache.get(f"popular_products")
        if cached:
            return cached
        # Final fallback: return empty list, UI shows generic content.
        return []
```

**Rules:**
- Define a fallback for every external dependency. What does the service do when
  the dependency is unavailable?
- Fallback strategies: cached data, default values, reduced functionality, queue for later.
- Communicate degradation to the caller via response metadata (e.g., `"degraded": true`).
- Never silently degrade. Log and emit metrics when fallbacks activate.
- Test fallback paths regularly. They are the least-exercised code paths and the most
  critical during outages.

---

## Do / Don't

### Do
- Use one circuit breaker per external dependency.
- Set explicit connect, read, and write timeouts on every I/O call.
- Retry only on transient errors with exponential backoff and jitter.
- Isolate dependencies with bulkheads to prevent resource exhaustion.
- Define and test fallback behavior for every external dependency.
- Monitor circuit breaker state, retry counts, timeout rates, and bulkhead saturation.
- Use deadline propagation to cancel work that the caller has already abandoned.

### Don't
- Share a circuit breaker across multiple unrelated dependencies.
- Retry non-idempotent operations. Duplicate writes cause data corruption.
- Use infinite timeouts. Every I/O call must have a finite, tuned timeout.
- Retry on client errors (4xx). These are deterministic and retrying wastes resources.
- Ignore retry amplification. If a service retries 3x and its caller retries 3x, that
  is 9x the load on the downstream service.
- Queue requests indefinitely in a full bulkhead. Fail fast with a clear error.
- Skip testing fallback paths. Untested fallbacks fail when you need them most.

---

## Common Pitfalls

1. **Retry storm** — Every service in the chain retries 3x. A single failure becomes
   27x (3^3) the load on the failing service, delaying recovery. Fix: use retry
   budgets and only retry at the edge (closest to the user).

2. **Circuit breaker too sensitive** — Circuit opens on a single transient failure
   and blocks all traffic for 30 seconds. Fix: use a rolling window (e.g., 5 failures
   in 10 calls) instead of consecutive failure counts.

3. **Timeout longer than caller's deadline** — Service A gives Service B a 5s timeout,
   but B calls C with a 10s timeout. B does 10s of work that A has already abandoned.
   Fix: propagate deadlines and check remaining time before starting work.

4. **Missing bulkheads** — A slow dependency consumes all threads/connections, starving
   fast dependencies. The entire service becomes unresponsive even though only one
   dependency is slow. Fix: isolate each dependency with its own connection pool.

5. **Fallback that calls the same failing dependency** — The fallback path makes a
   slightly different call to the same service that is down. Fix: fallbacks must use
   independent data sources (cache, defaults, a different service).

6. **No jitter on retries** — All instances retry at the same intervals, creating
   periodic load spikes on recovery. Fix: add random jitter (±50%) to every backoff.

---

## Checklist

- [ ] Circuit breaker configured per external dependency with appropriate thresholds.
- [ ] Retry policy uses exponential backoff with jitter; retries only transient errors.
- [ ] Retry budget limits total retry traffic to prevent amplification.
- [ ] Separate connect, read, write timeouts set for every dependency.
- [ ] Deadline propagation implemented across service call chains.
- [ ] Bulkheads isolate each dependency's connection pool / concurrency.
- [ ] Rate limiting enforced at the API gateway with `429` + `Retry-After`.
- [ ] Fallback behavior defined and tested for every external dependency.
- [ ] Circuit breaker state transitions emitted as metrics and alerts.
- [ ] Graceful degradation communicated to callers via response metadata.
- [ ] Load shedding returns `503 Service Unavailable` when at capacity.
- [ ] All resilience patterns covered in integration and chaos tests.
