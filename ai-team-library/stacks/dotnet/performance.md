# .NET Performance

Performance guidelines for .NET 8+ applications. Measure first, optimize second.
Premature optimization wastes time; ignoring performance until production wastes
money. These rules establish the baseline expectations.

---

## Defaults

| Concern                | Default                                        |
|------------------------|------------------------------------------------|
| Profiling              | `dotnet-trace`, `dotnet-counters`, BenchmarkDotNet |
| Memory analysis        | `dotnet-dump`, `dotnet-gcdump`                 |
| HTTP client            | `IHttpClientFactory` with connection pooling   |
| EF Core queries        | `AsNoTracking()` for reads, compiled queries for hot paths |
| Caching                | `IMemoryCache` for local, `IDistributedCache` for shared |
| JSON serialization     | `System.Text.Json` with source generators      |
| String handling        | `StringBuilder`, `string.Create`, `Span<char>` |
| Async model            | `async`/`await` all the way -- no `.Result` or `.Wait()` |
| Object pooling         | `ObjectPool<T>` for expensive allocations in hot paths |
| Response compression   | Brotli/gzip via `UseResponseCompression()`     |

---

## Do / Don't

### Do

- Measure before optimizing. Use BenchmarkDotNet for micro-benchmarks and
  `dotnet-counters` for runtime metrics.
- Use `AsNoTracking()` on all read-only EF Core queries.
- Use `IHttpClientFactory` -- never instantiate `HttpClient` directly.
- Use `System.Text.Json` source generators for high-throughput serialization.
- Use `CancellationToken` to stop unnecessary work on cancelled requests.
- Use `ValueTask<T>` for methods that complete synchronously on the hot path.
- Pool large byte arrays with `ArrayPool<T>.Shared`.
- Use compiled queries for EF Core queries executed thousands of times.

### Don't

- Don't call `.Result` or `.Wait()` on async methods -- it blocks threads and
  causes deadlocks.
- Don't use `ToList()` when you only need `FirstOrDefault()` or `AnyAsync()`.
- Don't load entire tables into memory. Always filter and paginate at the database.
- Don't allocate in hot loops. Prefer `Span<T>`, `stackalloc`, or pooled buffers.
- Don't use `string.Format` or `$""` interpolation in tight loops -- use
  `StringBuilder` or `string.Create`.
- Don't use `Count()` on `IEnumerable<T>` when `Any()` suffices.
- Don't ignore the EF Core query log. Review generated SQL during development.

---

## EF Core Performance

```csharp
// Read-only query -- no change tracking overhead
var orders = await context.Orders
    .AsNoTracking()
    .Where(o => o.Status == OrderStatus.Active)
    .Select(o => new OrderSummary(o.Id, o.CustomerName, o.Total))
    .ToListAsync(ct);

// Compiled query -- reuse the expression tree for hot paths
private static readonly Func<AppDbContext, Guid, CancellationToken, Task<Order?>>
    GetOrderById = EF.CompileAsyncQuery(
        (AppDbContext ctx, Guid id, CancellationToken ct) =>
            ctx.Orders.AsNoTracking().FirstOrDefault(o => o.Id == id));

// Usage
var order = await GetOrderById(context, orderId, ct);
```

**Key rules:**
- Project only the columns you need with `.Select()`. Avoid `SELECT *`.
- Add explicit indexes for columns in `WHERE` and `JOIN` clauses.
- Use `AsSplitQuery()` for queries with multiple `Include()` to avoid
  cartesian explosion.
- Batch updates/deletes with `ExecuteUpdateAsync`/`ExecuteDeleteAsync` (.NET 7+)
  instead of loading entities first.

---

## JSON Serialization with Source Generators

```csharp
// Define a source-generated context for hot-path DTOs
[JsonSerializable(typeof(OrderResponse))]
[JsonSerializable(typeof(PagedResponse<OrderSummary>))]
[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase)]
public partial class AppJsonContext : JsonSerializerContext;

// Register in Program.cs
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.TypeInfoResolverChain.Insert(0, AppJsonContext.Default);
});

// Or serialize directly
var json = JsonSerializer.Serialize(response, AppJsonContext.Default.OrderResponse);
```

Source generators eliminate reflection at runtime, reducing startup time and
allocation on every serialization call.

---

## Caching Strategy

```csharp
// IMemoryCache for single-instance, frequently accessed data
public sealed class ProductService(IMemoryCache cache, IProductRepository repo)
{
    public async Task<Product?> GetBySkuAsync(string sku, CancellationToken ct)
    {
        return await cache.GetOrCreateAsync($"product:{sku}", async entry =>
        {
            entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5);
            entry.SlidingExpiration = TimeSpan.FromMinutes(1);
            return await repo.GetBySkuAsync(sku, ct);
        });
    }
}

// IDistributedCache (Redis) for shared cache across instances
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = config.GetConnectionString("Redis");
    options.InstanceName = "myapp:";
});
```

---

## HTTP Client Best Practices

```csharp
// Use IHttpClientFactory -- handles DNS rotation and socket exhaustion
builder.Services.AddHttpClient<IPaymentGateway, PaymentGateway>(client =>
{
    client.BaseAddress = new Uri("https://payments.example.com");
    client.Timeout = TimeSpan.FromSeconds(10);
})
.AddStandardResilienceHandler(); // Polly retry, circuit breaker, timeout

// Never do this:
// private static readonly HttpClient _client = new HttpClient(); // socket exhaustion
```

---

## Common Pitfalls

1. **Blocking async code** -- `.Result` and `.Wait()` exhaust the thread pool
   under load and cause deadlocks. Use `await` all the way to the controller.
2. **N+1 queries** -- Accessing navigation properties without `.Include()`
   fires one query per row. Enable EF Core query logging to spot them.
3. **SELECT * everywhere** -- Loading 20 columns when you need 3. Use
   `.Select()` projections to reduce data transfer and memory.
4. **Missing indexes** -- Full table scans on columns in WHERE clauses. Review
   the query plan with `EXPLAIN ANALYZE` and add indexes.
5. **Creating HttpClient in a loop** -- Causes socket exhaustion. Use
   `IHttpClientFactory` always.
6. **Over-caching** -- Caching mutable data without invalidation leads to stale
   reads. Cache only data that changes infrequently and set appropriate TTLs.
7. **Large object heap pressure** -- Allocating large arrays (> 85KB) on every
   request. Use `ArrayPool<T>` or `RecyclableMemoryStream`.
8. **Ignoring GC metrics** -- High Gen 2 collections indicate a memory
   problem. Monitor with `dotnet-counters` and investigate with `dotnet-gcdump`.

---

## Alternatives

| Tool                  | When to consider                                |
|-----------------------|-------------------------------------------------|
| BenchmarkDotNet       | Micro-benchmarks for algorithm/serialization comparison |
| k6 / NBomber          | Load testing HTTP endpoints under realistic traffic |
| MiniProfiler          | In-page profiling during development            |
| Seq / Grafana         | Visualizing performance metrics over time       |
| Redis                 | Distributed cache when IMemoryCache is insufficient |
| Polly                 | Resilience (retries, circuit breaker) for HTTP calls |

---

## Checklist

- [ ] All read-only EF Core queries use `AsNoTracking()`
- [ ] Hot-path queries use `.Select()` projection, not full entity loading
- [ ] Compiled queries used for high-frequency database calls
- [ ] `IHttpClientFactory` used for all HTTP clients -- no manual `new HttpClient()`
- [ ] `System.Text.Json` source generators used for high-throughput endpoints
- [ ] Response compression middleware enabled (Brotli/gzip)
- [ ] Caching strategy documented: what is cached, TTL, invalidation method
- [ ] `CancellationToken` propagated through the full call chain
- [ ] No `.Result` or `.Wait()` calls in application code
- [ ] Database indexes defined for all filtered/joined columns
- [ ] Load tests run before major releases (k6, NBomber, or equivalent)
- [ ] `dotnet-counters` or OpenTelemetry metrics monitored in production
- [ ] Large allocations in hot paths use `ArrayPool<T>` or `ObjectPool<T>`
