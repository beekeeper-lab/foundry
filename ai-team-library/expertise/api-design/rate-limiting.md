# API Design — Rate Limiting

Rate limiting protects your API from abuse, ensures fair resource allocation,
and maintains service stability. Ship with rate limits from the first release.
Adding them retroactively breaks clients that assumed unlimited access.

---

## Strategy: Token Bucket (Default)

Token bucket allows bursts while enforcing a sustainable average rate.

```
Configuration:
  bucket_size:  100      # Maximum burst size
  refill_rate:  10/sec   # Tokens added per second
  key:          client_id # Rate limit scope

Behavior:
  - Bucket starts full (100 tokens).
  - Each request consumes 1 token.
  - Tokens refill at 10/sec up to the bucket size.
  - When empty, requests receive 429 Too Many Requests.
```

### Alternative Strategies

| Strategy | How It Works | When |
|----------|-------------|------|
| Token bucket | Tokens refill at a steady rate, burst up to bucket size | Default. Smooth rate with burst tolerance |
| Fixed window | Counter resets every N seconds | Simple to implement, thundering herd at window boundaries |
| Sliding window log | Tracks exact timestamps of requests | Most accurate, higher memory per client |
| Sliding window counter | Weighted average of current and previous window | Good balance of accuracy and memory |
| Leaky bucket | Processes requests at a fixed rate, queues excess | When you need strict output rate (not input) |

---

## Rate Limit Headers

Include rate limit headers on **every** response, not just 429s.

```http
HTTP/1.1 200 OK
RateLimit-Limit: 100
RateLimit-Remaining: 73
RateLimit-Reset: 1740076800
```

| Header | Type | Description |
|--------|------|-------------|
| `RateLimit-Limit` | integer | Maximum requests allowed in the current window |
| `RateLimit-Remaining` | integer | Requests remaining in the current window |
| `RateLimit-Reset` | integer | Unix timestamp when the window resets |
| `Retry-After` | integer | Seconds until the client should retry (429 only) |

### 429 Response

```json
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
RateLimit-Limit: 100
RateLimit-Remaining: 0
RateLimit-Reset: 1740076800
Retry-After: 30

{
  "type": "https://api.example.com/errors/rate-limited",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded the rate limit of 100 requests per minute. Retry after 30 seconds.",
  "retry_after": 30
}
```

---

## Rate Limit Tiers

Define tiers based on client type or subscription level:

| Tier | Requests/min | Burst | Use Case |
|------|-------------|-------|----------|
| Free | 60 | 10 | Trial users, public endpoints |
| Standard | 600 | 100 | Paid users, typical workloads |
| Premium | 6000 | 1000 | High-volume partners |
| Internal | 30000 | 5000 | Service-to-service calls |

**Rules:**
- Document rate limits in the API specification and developer portal.
- Different endpoints may have different limits (e.g., search is more
  expensive than read).
- Write operations (POST, PUT, DELETE) may have lower limits than reads.
- Authentication endpoints (login, token refresh) need aggressive limits
  to prevent brute force.

---

## Rate Limit Keys

| Scope | Key | When |
|-------|-----|------|
| Per client | `client_id` or API key | Default for authenticated APIs |
| Per user | `user_id` | Multi-tenant with per-user fairness |
| Per IP | Source IP | Unauthenticated endpoints, login |
| Per endpoint | `client_id` + endpoint | Expensive operations need separate limits |
| Global | None | Hard ceiling on total system throughput |

**Rules:**
- Authenticated endpoints rate limit by `client_id`, not by IP.
- Unauthenticated endpoints rate limit by IP address.
- Combine scopes for expensive operations: per-client AND per-endpoint.
- Use `X-Forwarded-For` behind load balancers, but validate the header
  chain to prevent spoofing.

---

## Implementation Pattern

```python
# Python / Redis token bucket
import time
import redis

class TokenBucket:
    def __init__(self, redis_client: redis.Redis, bucket_size: int,
                 refill_rate: float):
        self.redis = redis_client
        self.bucket_size = bucket_size
        self.refill_rate = refill_rate

    def allow(self, key: str) -> tuple[bool, dict]:
        now = time.time()
        pipe = self.redis.pipeline()

        bucket_key = f"ratelimit:{key}"
        # Atomic check-and-decrement with Lua script
        lua_script = """
        local bucket_key = KEYS[1]
        local bucket_size = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local data = redis.call('HMGET', bucket_key, 'tokens', 'last_refill')
        local tokens = tonumber(data[1]) or bucket_size
        local last_refill = tonumber(data[2]) or now

        -- Refill tokens
        local elapsed = now - last_refill
        tokens = math.min(bucket_size, tokens + elapsed * refill_rate)

        -- Try to consume
        local allowed = tokens >= 1
        if allowed then
            tokens = tokens - 1
        end

        redis.call('HMSET', bucket_key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', bucket_key, math.ceil(bucket_size / refill_rate) * 2)

        return {allowed and 1 or 0, math.floor(tokens), math.ceil((1 - tokens) / refill_rate)}
        """

        result = self.redis.eval(lua_script, 1, bucket_key,
                                  self.bucket_size, self.refill_rate, now)
        allowed, remaining, reset_in = result

        return bool(allowed), {
            "limit": self.bucket_size,
            "remaining": max(0, remaining),
            "reset": int(now + reset_in),
            "retry_after": 0 if allowed else reset_in,
        }
```

```typescript
// TypeScript / Express middleware
import rateLimit from "express-rate-limit";

// Basic fixed window (for simple cases)
const apiLimiter = rateLimit({
  windowMs: 60 * 1000,     // 1 minute
  max: 100,                 // 100 requests per window
  standardHeaders: true,    // RateLimit-* headers
  legacyHeaders: false,     // Disable X-RateLimit-* headers
  keyGenerator: (req) => req.headers["x-api-key"] || req.ip,
  handler: (req, res) => {
    res.status(429).type("application/problem+json").json({
      type: "https://api.example.com/errors/rate-limited",
      title: "Rate Limit Exceeded",
      status: 429,
      detail: `Rate limit of ${100} requests per minute exceeded.`,
      retry_after: Math.ceil((req.rateLimit.resetTime - Date.now()) / 1000),
    });
  },
});

app.use("/v1/", apiLimiter);
```

---

## Client-Side Handling

```python
# Client retry with exponential backoff
import time
import httpx

def request_with_retry(client: httpx.Client, method: str, url: str,
                       max_retries: int = 3, **kwargs) -> httpx.Response:
    for attempt in range(max_retries + 1):
        response = client.request(method, url, **kwargs)

        if response.status_code != 429:
            return response

        # Respect Retry-After header
        retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
        time.sleep(min(retry_after, 60))  # Cap at 60 seconds

    return response  # Return last response if all retries exhausted
```

**Rules:**
- Clients must respect `Retry-After` headers. Never retry immediately.
- Use exponential backoff with jitter for retries.
- Cap the maximum retry delay (60 seconds is reasonable).
- Circuit-break after repeated 429s rather than retrying indefinitely.

---

## Do / Don't

### Do
- Ship rate limits from the first API release.
- Include `RateLimit-*` headers on every response.
- Use token bucket for most scenarios (burst-tolerant).
- Rate limit by `client_id` for authenticated endpoints.
- Rate limit by IP for unauthenticated endpoints.
- Document rate limits in the API specification.
- Use atomic operations (Redis Lua scripts) for rate limit checks.
- Apply stricter limits to authentication and write endpoints.

### Don't
- Add rate limiting as an afterthought. Clients will depend on unlimited access.
- Rate limit by IP alone for authenticated APIs (shared IPs penalize all users).
- Return 429 without `Retry-After` header.
- Use in-memory rate limiting in a multi-instance deployment (use Redis/shared store).
- Allow clients to self-report their identity for rate limiting (use server-derived keys).
- Set rate limits so high they provide no protection.
- Forget to rate limit internal/service-to-service calls (a runaway service can DDoS you).

---

## Common Pitfalls

1. **In-memory counters in multi-instance deployments** — Each instance
   tracks separately, so actual request rate is N times the limit (where N
   is the number of instances). Use a shared store like Redis.

2. **Fixed window thundering herd** — All clients reset simultaneously at
   the window boundary, causing a traffic spike. Use token bucket or
   sliding window instead.

3. **Missing rate limits on auth endpoints** — Login and password reset
   endpoints without rate limiting enable brute force attacks. Apply
   aggressive per-IP limits.

4. **IP-only rate limiting behind a proxy** — All requests appear to come
   from the proxy IP. Extract the real client IP from `X-Forwarded-For`,
   but validate the header chain.

5. **No graceful degradation** — When rate limited, return useful
   information: how long to wait, what the limit is, how to request a
   higher tier. Don't just say "too many requests."

6. **Cost-unaware rate limiting** — A search query costs 100x more than a
   simple GET. Weight expensive operations higher or give them separate,
   lower limits.
