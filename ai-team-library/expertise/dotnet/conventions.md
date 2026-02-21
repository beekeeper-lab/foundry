# .NET Stack Conventions

These conventions are non-negotiable defaults for .NET applications on this
team. They target .NET 8+ and C# 12+. Deviations require an ADR with
justification. "I prefer it differently" is not justification.

---

## Defaults

| Setting                  | Value                         |
|--------------------------|-------------------------------|
| Target framework         | `net8.0` (or latest LTS)      |
| Language version          | C# 12+                        |
| Nullable reference types | `enable`                      |
| Implicit usings          | `enable`                      |
| Warnings as errors       | `true`                        |
| Analysis level           | `latest-recommended`          |
| DI container             | `Microsoft.Extensions.DependencyInjection` (built-in) |
| ORM                      | Entity Framework Core         |
| Logging                  | `ILogger<T>` (built-in)       |
| Test framework           | xUnit + FluentAssertions + NSubstitute |
| Code style               | `.editorconfig` + StyleCop.Analyzers |
| API style                | ASP.NET Core controllers (`[ApiController]`) |
| Health checks            | `/health/ready` + `/health/live` |
| Observability            | OpenTelemetry                 |
| CI format check          | `dotnet format --verify-no-changes` |

---

## Do / Don't

### Do

- Use `sealed` on every class unless explicitly designed for inheritance.
- Use `CancellationToken` in every async method signature and pass it through.
- Use file-scoped namespaces (`namespace Company.Project;`).
- Use primary constructors for DI where they improve readability.
- Use records for DTOs and value objects.
- Use `AsNoTracking()` for read-only EF Core queries.
- Validate configuration at startup with `ValidateOnStart()`.
- Group DI registrations into extension methods per feature.
- Use `IExceptionHandler` for centralized error handling.
- Log with structured logging and correlation IDs.

### Don't

- Don't inject `IServiceProvider` into application classes (service locator anti-pattern).
- Don't use lazy loading in EF Core -- use explicit `.Include()`.
- Don't put business logic in controllers.
- Don't use `#pragma warning disable` without a justifying comment.
- Don't use the null-forgiving operator (`!`) without a justifying comment.
- Don't read `IConfiguration` directly -- use `IOptions<T>`.
- Don't use `EnsureCreated()` in production -- use migrations.
- Don't return domain entities from controllers -- map to response DTOs.
- Don't add `<NoWarn>` to `.csproj` without a tracking issue.
- Don't use `Transient` lifetime unless a new instance per resolution is genuinely needed.

---

## 1. Project Structure

```
SolutionRoot/
  src/
    Company.Project.Api/          # ASP.NET Core web host (thin entry point)
      Program.cs                  # App builder, middleware pipeline, DI registration
      Controllers/                # API controllers (thin: validate, delegate, respond)
      Filters/                    # Action/exception filters
      Middleware/                  # Custom middleware
      appsettings.json            # Default configuration
      appsettings.Development.json
    Company.Project.Application/  # Business logic (use cases, services)
      Services/                   # Application services (orchestration)
      Interfaces/                 # Service and repository interfaces
      Models/                     # DTOs, request/response models
      Validators/                 # FluentValidation validators
    Company.Project.Domain/       # Domain entities, value objects, enums
      Entities/
      ValueObjects/
      Enums/
      Exceptions/                 # Domain-specific exceptions
    Company.Project.Infrastructure/ # Data access, external integrations
      Persistence/
        Configurations/           # EF Core entity configurations
        Repositories/             # Repository implementations
        Migrations/               # EF Core migrations
      ExternalServices/           # HTTP clients, message queue adapters
  tests/
    Company.Project.UnitTests/
    Company.Project.IntegrationTests/
    Company.Project.ArchTests/    # Architecture constraint tests (optional)
  Directory.Build.props           # Shared MSBuild properties
  .editorconfig                   # Code style enforcement
  SolutionName.sln
```

**Rules:**
- Follow Clean Architecture layering: Domain has no dependencies, Application
  depends on Domain, Infrastructure depends on Application, Api depends on all.
- One solution per repository. Use project references, not package references,
  for internal projects.
- Controllers are thin. They validate input, call an application service, and
  return a result. No business logic in controllers.
- Infrastructure details (EF Core, HTTP clients) never leak into Application
  or Domain layers. Use interfaces defined in Application, implemented in
  Infrastructure.

---

## 2. Coding Standards

### Naming

| Element          | Convention        | Example                      |
|------------------|-------------------|------------------------------|
| Namespaces       | `PascalCase`      | `Company.Project.Application`|
| Classes          | `PascalCase`      | `OrderService`               |
| Interfaces       | `IPascalCase`     | `IOrderRepository`           |
| Methods          | `PascalCase`      | `GetOrderByIdAsync`          |
| Properties       | `PascalCase`      | `OrderTotal`                 |
| Private fields   | `_camelCase`      | `_orderRepository`           |
| Parameters       | `camelCase`       | `orderId`                    |
| Constants        | `PascalCase`      | `MaxRetryCount`              |
| Async methods    | `PascalCase` + `Async` suffix | `ProcessOrderAsync` |

### General Rules

- Use `var` when the type is obvious from the right-hand side. Use explicit
  types when it aids readability.
- Use file-scoped namespaces (`namespace Company.Project;` not the block form).
- Use primary constructors for dependency injection where appropriate.
- Prefer records for DTOs and value objects. Use classes for entities with
  identity and mutable state.
- Use `sealed` on classes that are not designed for inheritance. This is the
  default posture.
- Use expression-bodied members for single-line methods and properties.
- Nullable reference types are enabled project-wide (`<Nullable>enable</Nullable>`).
  No suppression operators (`!`) without a justifying comment.

---

## 3. Formatting and Analysis

**Tools: .editorconfig + built-in analyzers + StyleCop.Analyzers.**

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <AnalysisLevel>latest-recommended</AnalysisLevel>
  </PropertyGroup>
</Project>
```

**Rules:**
- `TreatWarningsAsErrors: true`. No warnings in CI. Fix them or suppress with
  documented justification.
- `.editorconfig` enforces consistent formatting across IDEs. Commit it.
- Use `dotnet format` in CI to verify formatting. Reject unformatted code.
- No `#pragma warning disable` without a comment explaining why the suppression
  is necessary and a tracking issue if the underlying cause should be fixed.

---

## 4. Dependency Injection

**Use the built-in Microsoft.Extensions.DependencyInjection container.**

```csharp
// Program.cs
builder.Services.AddScoped<IOrderRepository, OrderRepository>();
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddHttpClient<IPaymentClient, PaymentClient>(client =>
{
    client.BaseAddress = new Uri(config.PaymentServiceUrl);
    client.Timeout = TimeSpan.FromSeconds(10);
});
```

**Rules:**
- Register services with the appropriate lifetime: Scoped for request-bound
  services (repositories, DbContext), Singleton for stateless shared services,
  Transient only when a new instance per resolution is genuinely needed.
- Do not inject `IServiceProvider` into application classes (service locator
  anti-pattern). Use constructor injection exclusively.
- Group registrations into extension methods: `builder.Services.AddPersistence(config)`
  rather than a 200-line `Program.cs`.
- Validate all service registrations at startup in development using
  `builder.Host.UseDefaultServiceProvider(o => o.ValidateOnBuild = true)`.

---

## 5. Configuration

**Use the Options pattern with validation.**

```csharp
public class DatabaseOptions
{
    public const string Section = "Database";

    [Required]
    public required string ConnectionString { get; init; }

    [Range(1, 100)]
    public int MaxPoolSize { get; init; } = 20;
}

// Registration
builder.Services
    .AddOptions<DatabaseOptions>()
    .BindConfiguration(DatabaseOptions.Section)
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

**Rules:**
- All configuration sections are strongly typed with validation.
- `ValidateOnStart()` is mandatory. Fail fast on missing or invalid config.
- Never read `IConfiguration` directly in application code. Inject
  `IOptions<T>`, `IOptionsSnapshot<T>`, or `IOptionsMonitor<T>`.
- Secrets use User Secrets in development and a secrets manager (Azure Key
  Vault, AWS Secrets Manager) in production. Never in `appsettings.json`.

---

## 6. Entity Framework Core

**Rules:**
- Use Fluent API configuration in `IEntityTypeConfiguration<T>` classes, not
  data annotations on entities. Keep domain entities clean of persistence
  concerns.
- Migrations are committed to the repository. Never use `EnsureCreated()` in
  production.
- Use `AsNoTracking()` for read-only queries. Tracked queries are for writes
  only.
- Avoid lazy loading. Use explicit `.Include()` for related data. Lazy loading
  hides N+1 queries.
- Use `IQueryable` only within the repository layer. Application services
  receive materialized collections or domain objects.
- Define indexes explicitly in entity configurations for all columns used in
  WHERE clauses or JOIN conditions.

---

## 7. API Design

**Follow REST conventions with consistent response shapes.**

```csharp
// Consistent error response
public record ProblemResponse(
    string Type,
    string Title,
    int Status,
    string Detail,
    string? Instance = null
);

// Controller pattern
[ApiController]
[Route("api/[controller]")]
public class OrdersController(IOrderService orderService) : ControllerBase
{
    [HttpGet("{id:guid}")]
    [ProducesResponseType<OrderResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType<ProblemResponse>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetById(Guid id, CancellationToken ct)
    {
        var order = await orderService.GetByIdAsync(id, ct);
        return order is null ? NotFound() : Ok(order);
    }
}
```

**Rules:**
- Use `[ApiController]` attribute for automatic model validation and problem
  details responses.
- Accept `CancellationToken` in all async controller actions and pass it
  through the call chain.
- Use `ProducesResponseType` attributes for OpenAPI documentation.
- Return `IActionResult` from controllers, not domain types directly.
- Use RFC 7807 Problem Details for error responses.
- API versioning is required for any API with external consumers.

---

## 8. Error Handling

```csharp
// Domain exception
public class OrderNotFoundException(Guid orderId)
    : DomainException($"Order '{orderId}' not found")
{
    public Guid OrderId { get; } = orderId;
}

// Global exception handler (middleware or IExceptionHandler in .NET 8+)
public class GlobalExceptionHandler : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext context, Exception exception, CancellationToken ct)
    {
        var (statusCode, detail) = exception switch
        {
            DomainException e => (StatusCodes.Status400BadRequest, e.Message),
            NotFoundException e => (StatusCodes.Status404NotFound, e.Message),
            _ => (StatusCodes.Status500InternalServerError, "An unexpected error occurred"),
        };

        context.Response.StatusCode = statusCode;
        await context.Response.WriteAsJsonAsync(
            new ProblemResponse("error", "Error", statusCode, detail), ct);
        return true;
    }
}
```

**Rules:**
- Define domain-specific exception classes inheriting from a base
  `DomainException`.
- Use `IExceptionHandler` (.NET 8+) for global exception handling. Do not
  catch exceptions in individual controllers.
- Log unhandled exceptions at Error level with full stack trace. Log expected
  exceptions at Warning or Info level.
- Never expose internal exception details to API consumers. Return generic
  messages for 500 errors.

---

## 9. Testing

**Framework: xUnit + FluentAssertions + NSubstitute.**

```csharp
public class OrderServiceTests
{
    private readonly IOrderRepository _repository = Substitute.For<IOrderRepository>();
    private readonly OrderService _sut;

    public OrderServiceTests()
    {
        _sut = new OrderService(_repository);
    }

    [Fact]
    public async Task GetByIdAsync_WhenOrderExists_ReturnsOrder()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var expected = new Order { Id = orderId, Total = 99.99m };
        _repository.GetByIdAsync(orderId, Arg.Any<CancellationToken>())
            .Returns(expected);

        // Act
        var result = await _sut.GetByIdAsync(orderId, CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(orderId);
    }
}
```

**Rules:**
- Use `[Fact]` for single-case tests, `[Theory]` with `[InlineData]` for
  parameterized tests.
- Follow Arrange-Act-Assert pattern. One logical assertion per test (multiple
  FluentAssertions calls on the same result are fine).
- Name tests: `MethodName_Scenario_ExpectedBehavior`.
- Unit tests mock external dependencies via interfaces. Integration tests use
  `WebApplicationFactory<Program>` with real database (Testcontainers).
- Aim for 80% line coverage on new code. Use branch coverage as the more
  meaningful metric.
- Architecture tests (using NetArchTest or ArchUnitNET) enforce layer
  dependency rules: Domain must not reference Infrastructure.

---

## 10. Health Checks and Observability

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "database")
    .AddUrlGroup(new Uri(paymentServiceUrl), name: "payment-service");

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = _ => true,
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse,
});

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false, // Liveness: app is running, no dependency checks
});
```

**Rules:**
- Every service exposes `/health/ready` (readiness: all dependencies available)
  and `/health/live` (liveness: process is running).
- Use structured logging with Serilog or the built-in `ILogger<T>`.
- Include correlation IDs in all log entries and propagate them across HTTP
  calls.
- Expose metrics (request duration, error rates) via OpenTelemetry.
- Configure request logging middleware to log method, path, status code, and
  duration for every request.

---

## 11. CI/CD Patterns

**Pipeline stages (in order):**

1. **Restore** -- `dotnet restore`. Uses lockfile if present.
2. **Build** -- `dotnet build --no-restore --warnaserror`. Fail on any warning.
3. **Format Check** -- `dotnet format --verify-no-changes`. Fail on any
   violation.
4. **Unit Tests** -- `dotnet test` with coverage collection. Fail on any
   failure or coverage below threshold.
5. **Integration Tests** -- Run against containerized dependencies. Fail on any
   failure.
6. **Security Scan** -- `dotnet list package --vulnerable`. Fail on Critical
   or High.
7. **Publish** -- `dotnet publish` for deployment artifact.
8. **Deploy** -- Only after all previous stages pass.

**Rules:**
- CI uses the same .NET SDK version pinned in `global.json`.
- Multi-stage Docker builds: SDK image for build, runtime image for
  deployment. Final image contains only the published output.
- No `<NoWarn>` in `.csproj` files without a documented justification and
  tracking issue.

---

## Common Pitfalls

1. **Captive dependency** -- Injecting a `Scoped` service into a `Singleton`.
   The scoped service is captured for the application lifetime and behaves like
   a singleton. Enable `ValidateScopes` in development to catch this.
2. **Async void** -- `async void` methods swallow exceptions silently. Always
   return `Task` or `Task<T>`. The only exception is event handlers.
3. **Forgetting CancellationToken** -- Omitting `CancellationToken` means the
   server does unnecessary work after a client disconnects. Thread it through
   every async call.
4. **N+1 queries in EF Core** -- Accessing navigation properties without
   `.Include()` causes one query per row. Use EF Core logging in development
   to spot extra queries.
5. **Blocking on async code** -- Calling `.Result` or `.Wait()` on a `Task`
   causes deadlocks in ASP.NET Core. Use `await` all the way up.
6. **Leaking connection strings** -- Logging the full `DbContext` options or
   exception details can expose connection strings. Sanitize logs.
7. **Over-scoping DbContext** -- Registering `DbContext` as Singleton causes
   thread-safety issues. Always use `AddDbContext` (Scoped by default).
8. **Missing .editorconfig** -- Without it, formatting depends on each
   developer's IDE settings. Commit `.editorconfig` from day one.

---

## Checklist

Use this checklist when setting up a new .NET project or reviewing an existing one.

- [ ] `global.json` pins .NET SDK version
- [ ] `Directory.Build.props` sets `TreatWarningsAsErrors`, `Nullable`, `AnalysisLevel`
- [ ] `.editorconfig` committed with team formatting rules
- [ ] `StyleCop.Analyzers` NuGet package added to all projects
- [ ] Solution follows Clean Architecture folder structure
- [ ] `ValidateOnBuild = true` enabled in development
- [ ] All configuration classes use Options pattern with `ValidateOnStart()`
- [ ] No secrets in `appsettings.json` -- User Secrets or vault only
- [ ] `IExceptionHandler` registered for global error handling
- [ ] `/health/ready` and `/health/live` endpoints mapped
- [ ] OpenTelemetry configured for traces and metrics
- [ ] Correlation ID middleware wired in the pipeline
- [ ] `CancellationToken` threaded through all async controller actions
- [ ] EF Core entity configurations use Fluent API, not data annotations
- [ ] Read-only queries use `AsNoTracking()`
- [ ] CI pipeline includes restore, build, format check, test, security scan
- [ ] `dotnet format --verify-no-changes` runs in CI
- [ ] `dotnet list package --vulnerable` runs in CI
- [ ] Multi-stage Dockerfile uses runtime image for final stage
- [ ] Architecture tests enforce layer dependency rules
