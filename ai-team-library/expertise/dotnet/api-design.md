# .NET API Design

Guidelines for designing HTTP APIs with ASP.NET Core. Covers both controller-based
and minimal API approaches, request/response contracts, versioning, and
documentation. Consistency across endpoints matters more than any single rule.

---

## Defaults

| Decision              | Default                                         |
|-----------------------|-------------------------------------------------|
| API style             | Controller-based with `[ApiController]`         |
| Routing               | `api/{version}/[controller]` with attribute routing |
| Serialization         | `System.Text.Json` with camelCase               |
| Error format          | RFC 7807 Problem Details                        |
| Validation            | FluentValidation + `[ApiController]` auto-validation |
| Documentation         | OpenAPI via Swashbuckle or NSwag                |
| Versioning            | URL segment (`/api/v1/orders`) for external APIs |
| Authentication        | JWT Bearer with policy-based authorization      |
| Rate limiting         | Built-in `RateLimiter` middleware               |
| Pagination            | Cursor-based for large datasets; offset for admin UIs |

---

## Do / Don't

### Do

- Use `[ApiController]` on every controller for automatic model validation and
  Problem Details responses.
- Accept `CancellationToken` in every async action and pass it through the
  entire call chain.
- Annotate every action with `[ProducesResponseType]` for accurate OpenAPI docs.
- Use `TypedResults` in minimal APIs for compile-time return type checking.
- Return `IActionResult` from controllers. Map domain objects to response DTOs.
- Use route constraints (`{id:guid}`, `{slug:regex(^[a-z0-9-]+$)}`) to reject
  invalid inputs before the action body executes.
- Version any API with external consumers from day one.

### Don't

- Don't return domain entities directly from controllers -- always map to DTOs.
- Don't use `[FromBody]` on `GET` requests.
- Don't mix minimal APIs and controllers in the same project without clear separation.
- Don't use `200 OK` for every response. Use `201 Created`, `204 No Content`, `404 Not Found` appropriately.
- Don't accept unbounded collections. Always require pagination parameters.
- Don't return stack traces or internal exception messages in error responses.

---

## Controller-Based API Example

```csharp
[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public sealed class OrdersController(IOrderService orderService) : ControllerBase
{
    /// <summary>Creates a new order.</summary>
    [HttpPost]
    [ProducesResponseType<OrderResponse>(StatusCodes.Status201Created)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> Create(
        [FromBody] CreateOrderRequest request, CancellationToken ct)
    {
        var order = await orderService.CreateAsync(request, ct);
        return CreatedAtAction(nameof(GetById), new { id = order.Id }, order);
    }

    /// <summary>Retrieves an order by ID.</summary>
    [HttpGet("{id:guid}")]
    [ProducesResponseType<OrderResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetById(Guid id, CancellationToken ct)
    {
        var order = await orderService.GetByIdAsync(id, ct);
        return order is null ? NotFound() : Ok(order);
    }

    /// <summary>Lists orders with cursor-based pagination.</summary>
    [HttpGet]
    [ProducesResponseType<PagedResponse<OrderSummary>>(StatusCodes.Status200OK)]
    public async Task<IActionResult> List(
        [FromQuery] string? cursor,
        [FromQuery] int limit = 25,
        CancellationToken ct = default)
    {
        var page = await orderService.ListAsync(cursor, Math.Clamp(limit, 1, 100), ct);
        return Ok(page);
    }
}
```

---

## Minimal API Example

```csharp
// Program.cs or a separate route group file
var orders = app.MapGroup("api/v1/orders")
    .RequireAuthorization()
    .WithTags("Orders");

orders.MapGet("{id:guid}", async (Guid id, IOrderService svc, CancellationToken ct) =>
{
    var order = await svc.GetByIdAsync(id, ct);
    return order is null
        ? Results.NotFound()
        : Results.Ok(order);
})
.WithName("GetOrderById")
.Produces<OrderResponse>(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);

orders.MapPost("", async (CreateOrderRequest req, IOrderService svc, CancellationToken ct) =>
{
    var order = await svc.CreateAsync(req, ct);
    return Results.CreatedAtRoute("GetOrderById", new { id = order.Id }, order);
})
.Produces<OrderResponse>(StatusCodes.Status201Created)
.ProducesValidationProblem();
```

---

## Response Contracts

```csharp
// Standard paginated response
public sealed record PagedResponse<T>(
    IReadOnlyList<T> Items,
    string? NextCursor,
    int TotalCount
);

// Standard error response (RFC 7807)
// ASP.NET Core generates this automatically with [ApiController],
// but customize via ProblemDetailsOptions for consistency:
builder.Services.AddProblemDetails(options =>
{
    options.CustomizeProblemDetails = ctx =>
    {
        ctx.ProblemDetails.Extensions["traceId"] =
            ctx.HttpContext.TraceIdentifier;
    };
});
```

---

## Versioning Strategy

```csharp
// URL-based versioning (preferred for external APIs)
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
})
.AddApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV";
    options.SubstituteApiVersionInUrl = true;
});
```

---

## Common Pitfalls

1. **Missing CancellationToken** -- Without it, the server continues processing
   after the client disconnects. Thread it through every async call.
2. **Leaking domain models** -- Returning entities exposes internal structure
   and creates breaking changes when the domain evolves. Always map to DTOs.
3. **Inconsistent error shapes** -- Some endpoints return Problem Details,
   others return custom objects. Use `AddProblemDetails()` globally.
4. **Unbounded queries** -- An endpoint that returns all records. Always
   enforce pagination with a sensible maximum (e.g., `limit` clamped to 100).
5. **Ignoring HTTP semantics** -- `POST` that returns `200` instead of `201`,
   `DELETE` that returns the deleted entity instead of `204`. Follow RFC 7231.
6. **Swallowing validation errors** -- Not using `[ApiController]` means
   `ModelState` errors are silently ignored. Always apply the attribute.

---

## Alternatives

| Approach             | When to consider                                |
|----------------------|-------------------------------------------------|
| Minimal APIs         | Simple services, lambda-style handlers, rapid prototyping |
| gRPC                 | Internal service-to-service with strong contracts |
| GraphQL (HotChocolate) | Client-driven queries with complex nested data |
| Header-based versioning | Internal APIs where URL changes are disruptive |
| OData                | When clients need ad-hoc query capabilities     |

---

## Checklist

- [ ] All controllers have `[ApiController]` and `[Route]` attributes
- [ ] Every async action accepts `CancellationToken`
- [ ] Every action has `[ProducesResponseType]` annotations
- [ ] Error responses use RFC 7807 Problem Details
- [ ] Domain entities never appear in API responses -- DTOs only
- [ ] Pagination enforced with clamped `limit` parameter
- [ ] API versioning configured for external-facing endpoints
- [ ] OpenAPI document generated and verified in CI
- [ ] Request/response examples included in OpenAPI via XML docs or attributes
- [ ] Rate limiting applied to public endpoints
- [ ] CORS configured with explicit origin allowlist
- [ ] `CreatedAtAction`/`CreatedAtRoute` used for `POST` endpoints returning `201`
