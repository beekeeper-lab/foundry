# .NET Architecture

Architectural patterns and layering rules for .NET 8+ applications. This guide
enforces Clean Architecture with explicit dependency direction and testability
as a first-class concern.

---

## Defaults

| Decision               | Default                                      |
|------------------------|----------------------------------------------|
| Architecture style     | Clean Architecture (Onion)                   |
| Solution layout        | Four projects: Domain, Application, Infrastructure, Api |
| Dependency direction   | Inward only -- outer layers depend on inner   |
| Communication style    | Synchronous in-process; async messaging for cross-service |
| Mediator               | None by default (add MediatR only when command/query separation justifies it) |
| Mapping                | Manual mapping methods; add Mapster or AutoMapper only at scale |
| Domain modeling        | Rich domain entities with behavior; anemic models are a code smell |

---

## Layers and Dependency Rules

```
┌─────────────────────────────────┐
│           Api / Host            │  ASP.NET Core entry point, controllers,
│                                 │  middleware, DI wiring
├─────────────────────────────────┤
│         Infrastructure          │  EF Core, HTTP clients, file I/O,
│                                 │  message brokers
├─────────────────────────────────┤
│          Application            │  Use cases, service interfaces,
│                                 │  DTOs, validation
├─────────────────────────────────┤
│            Domain               │  Entities, value objects, domain
│                                 │  events, enums, exceptions
└─────────────────────────────────┘
```

**Rules:**
- Domain references nothing. No NuGet packages except pure abstractions.
- Application references Domain only. Defines interfaces (e.g., `IOrderRepository`)
  that Infrastructure implements.
- Infrastructure references Application (for interfaces) and Domain (for entities).
- Api references all layers but only to wire DI. Controllers call Application
  services, never Infrastructure directly.

### Enforcing with Architecture Tests

```csharp
using NetArchTest.Rules;

[Fact]
public void Domain_ShouldNotReference_Infrastructure()
{
    var result = Types.InAssembly(typeof(Order).Assembly)
        .ShouldNot()
        .HaveDependencyOn("Company.Project.Infrastructure")
        .GetResult();

    result.IsSuccessful.Should().BeTrue();
}

[Fact]
public void Application_ShouldNotReference_Api()
{
    var result = Types.InAssembly(typeof(IOrderService).Assembly)
        .ShouldNot()
        .HaveDependencyOn("Company.Project.Api")
        .GetResult();

    result.IsSuccessful.Should().BeTrue();
}
```

---

## Do / Don't

### Do

- Define all service and repository interfaces in the Application layer.
- Use the Domain layer for business rules -- entities should validate their own invariants.
- Keep the Api layer thin: validate input, delegate to Application, return result.
- Group related classes by feature (vertical slices) within each layer when the project grows beyond 10-15 services.
- Use `internal` visibility for Infrastructure implementations; expose only via DI.
- Wire all cross-cutting concerns (logging, auth, caching) in the Api layer's pipeline.

### Don't

- Don't reference `Microsoft.EntityFrameworkCore` from the Domain project.
- Don't put business logic in controllers or repositories.
- Don't create a "Shared" or "Common" project that everything references -- it becomes a dumping ground.
- Don't use static service locators. Constructor injection is the only path.
- Don't add MediatR, AutoMapper, or CQRS unless the project genuinely needs them. Start simple.

---

## Vertical Slice Organization

When a layer grows large, organize by feature rather than by technical role.

```
Company.Project.Application/
  Orders/
    CreateOrderCommand.cs
    CreateOrderHandler.cs
    GetOrderQuery.cs
    GetOrderHandler.cs
    OrderResponse.cs
    OrderValidator.cs
  Products/
    GetProductQuery.cs
    GetProductHandler.cs
    ProductResponse.cs
```

This keeps related code together and makes it easy to find everything about a feature.

---

## Service Registration Pattern

```csharp
// Infrastructure/DependencyInjection.cs
namespace Company.Project.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services, IConfiguration config)
    {
        services.AddDbContext<AppDbContext>(options =>
            options.UseNpgsql(config.GetConnectionString("Default")));

        services.AddScoped<IOrderRepository, OrderRepository>();
        services.AddScoped<IProductRepository, ProductRepository>();

        services.AddHttpClient<IPaymentGateway, StripePaymentGateway>(client =>
            client.BaseAddress = new Uri(config["Payment:BaseUrl"]!));

        return services;
    }
}

// Program.cs -- clean and readable
builder.Services.AddInfrastructure(builder.Configuration);
builder.Services.AddApplicationServices();
```

---

## Common Pitfalls

1. **Leaky abstractions** -- Returning `IQueryable<T>` from repository
   interfaces couples Application to EF Core. Return `IReadOnlyList<T>` or
   domain objects instead.
2. **God services** -- An `OrderService` with 30 methods. Split into focused
   use-case classes (`CreateOrderHandler`, `CancelOrderHandler`).
3. **Circular project references** -- Usually means a type is in the wrong
   layer. Move the shared abstraction to Application or Domain.
4. **Over-engineering** -- Adding CQRS, event sourcing, and a message bus on
   day one. Start with direct method calls and refactor when complexity demands it.
5. **Fat controllers** -- Controllers that contain try/catch, mapping,
   validation, and orchestration. Move all of it to Application services.
6. **Shared DTOs across layers** -- Application DTOs and API response models
   should be separate. API models can evolve independently of internal contracts.

---

## Alternatives

| Pattern           | When to consider                                    |
|-------------------|-----------------------------------------------------|
| Vertical Slices   | When features are independent and cross-cutting concerns are minimal |
| CQRS              | When read and write models diverge significantly     |
| Hexagonal Ports/Adapters | Equivalent to Clean Architecture; use team preference |
| Modular Monolith  | When you need service boundaries without microservice overhead |

---

## Checklist

- [ ] Solution has exactly four projects: Domain, Application, Infrastructure, Api
- [ ] Domain project has zero NuGet package references (except analyzers)
- [ ] All repository and service interfaces live in Application
- [ ] All interface implementations live in Infrastructure
- [ ] Controllers contain no business logic -- only validation, delegation, response mapping
- [ ] Architecture tests enforce layer dependency rules in CI
- [ ] Each layer has its own `DependencyInjection` extension method for service registration
- [ ] No `IQueryable<T>` leaks past repository boundaries
- [ ] No static service locators or ambient context patterns
- [ ] Cross-cutting concerns (logging, auth, caching) wired in Api middleware pipeline
