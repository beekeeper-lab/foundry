# .NET Testing

Testing strategy and patterns for .NET 8+ applications. xUnit is the default
framework. Every layer has a corresponding test strategy. Tests that cannot
run without manual intervention are not tests.

---

## Defaults

| Setting              | Value                                           |
|----------------------|-------------------------------------------------|
| Framework            | xUnit 2.x                                       |
| Assertions           | FluentAssertions                                |
| Mocking              | NSubstitute                                     |
| Integration host     | `WebApplicationFactory<Program>`                |
| Database containers  | Testcontainers for .NET                         |
| Coverage target      | 80% line coverage on new code                   |
| Coverage tool        | Coverlet (via `dotnet test --collect:"XPlat Code Coverage"`) |
| Architecture tests   | NetArchTest.Rules                               |
| Naming convention    | `MethodName_Scenario_ExpectedBehavior`          |
| Test structure       | Arrange-Act-Assert                              |

---

## Do / Don't

### Do

- Use `[Fact]` for single-case tests and `[Theory]` with `[InlineData]` or
  `[MemberData]` for parameterized tests.
- Name tests clearly: `CreateOrder_WhenItemOutOfStock_ThrowsInvalidOperationException`.
- Test one logical behavior per test method. Multiple FluentAssertions on the
  same result object are fine.
- Use `CancellationToken.None` explicitly in test code to show intent.
- Use `Substitute.For<T>()` for mocking interfaces -- never mock concrete classes.
- Run integration tests against real infrastructure via Testcontainers.
- Use `IClassFixture<T>` for expensive shared setup (database, web host).

### Don't

- Don't test private methods. Test the public API that exercises them.
- Don't use `Thread.Sleep` or `Task.Delay` in tests. Use `async` assertions
  or polling with timeout.
- Don't share mutable state between tests. xUnit creates a new class instance
  per test by default -- use that.
- Don't mock types you don't own (e.g., `HttpClient`). Wrap them in your own
  interface.
- Don't write tests that depend on execution order.
- Don't use `InMemoryDatabase` for EF Core integration tests -- behavior
  differs from real databases. Use Testcontainers.

---

## Unit Test Example

```csharp
public sealed class OrderServiceTests
{
    private readonly IOrderRepository _repository = Substitute.For<IOrderRepository>();
    private readonly ILogger<OrderService> _logger = Substitute.For<ILogger<OrderService>>();
    private readonly OrderService _sut;

    public OrderServiceTests()
    {
        _sut = new OrderService(_repository, _logger);
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
        result.Total.Should().Be(99.99m);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-5)]
    public async Task CreateOrder_WhenQuantityInvalid_ThrowsArgumentException(int quantity)
    {
        // Arrange
        var request = new CreateOrderRequest("SKU-001", quantity);

        // Act
        var act = () => _sut.CreateAsync(request, CancellationToken.None);

        // Assert
        await act.Should().ThrowAsync<ArgumentException>()
            .WithMessage("*quantity*");
    }
}
```

---

## Integration Test Example

```csharp
public sealed class OrdersEndpointTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client = factory.WithWebHostBuilder(builder =>
    {
        builder.ConfigureServices(services =>
        {
            // Replace the real DB with a Testcontainers PostgreSQL instance
            services.RemoveAll<DbContextOptions<AppDbContext>>();
            services.AddDbContext<AppDbContext>(options =>
                options.UseNpgsql(TestDatabase.ConnectionString));
        });
    }).CreateClient();

    [Fact]
    public async Task GetOrder_WhenExists_Returns200WithOrder()
    {
        // Arrange -- seed via the API or direct DB access
        var createResponse = await _client.PostAsJsonAsync("/api/orders",
            new { Sku = "WIDGET-01", Quantity = 3 });
        var created = await createResponse.Content.ReadFromJsonAsync<OrderResponse>();

        // Act
        var response = await _client.GetAsync($"/api/orders/{created!.Id}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var order = await response.Content.ReadFromJsonAsync<OrderResponse>();
        order!.Sku.Should().Be("WIDGET-01");
    }
}
```

---

## Test Organization

```
tests/
  Company.Project.UnitTests/
    Services/
      OrderServiceTests.cs
    Domain/
      OrderTests.cs
      MoneyValueObjectTests.cs
  Company.Project.IntegrationTests/
    Endpoints/
      OrdersEndpointTests.cs
    Repositories/
      OrderRepositoryTests.cs
    Fixtures/
      TestDatabase.cs           # Testcontainers setup
  Company.Project.ArchTests/
    LayerDependencyTests.cs     # NetArchTest rules
```

---

## Common Pitfalls

1. **InMemoryDatabase lies** -- It does not enforce foreign keys, unique
   constraints, or transactions. Tests pass but production fails. Use
   Testcontainers with the real database engine.
2. **Over-mocking** -- Mocking every dependency creates brittle tests that
   break on refactoring. Mock only external boundaries (DB, HTTP, message bus).
3. **Testing implementation, not behavior** -- Verifying that a specific method
   was called N times couples tests to internals. Assert on observable outcomes.
4. **Flaky time-dependent tests** -- Use `TimeProvider` (.NET 8+) or inject a
   clock abstraction instead of relying on `DateTime.UtcNow`.
5. **Ignoring test output** -- xUnit's `ITestOutputHelper` captures per-test
   output. Use it instead of `Console.WriteLine`, which may interleave.
6. **Missing CancellationToken in mocks** -- Forgetting `Arg.Any<CancellationToken>()`
   in NSubstitute setups causes silent null returns.

---

## Alternatives

| Tool              | When to consider                                  |
|-------------------|---------------------------------------------------|
| NUnit             | Team preference; use `[TestCase]` instead of `[InlineData]` |
| Moq               | Established teams already using it (avoid mixing mocking libs) |
| Shouldly          | Alternative assertion library with different syntax |
| Bogus             | Generating realistic fake data for complex test scenarios |
| Verify            | Snapshot/approval testing for serialized outputs   |
| Stryker.NET       | Mutation testing to verify test effectiveness      |

---

## Checklist

- [ ] Unit test project references only Application and Domain (not Infrastructure)
- [ ] Integration test project uses `WebApplicationFactory<Program>`
- [ ] Database tests use Testcontainers, not InMemoryDatabase
- [ ] All async tests use `async Task`, never `async void`
- [ ] Coverage collected with Coverlet in CI (`--collect:"XPlat Code Coverage"`)
- [ ] Coverage threshold (80%) enforced in CI pipeline
- [ ] Architecture tests verify layer dependency rules
- [ ] No `Thread.Sleep` or hardcoded delays in test code
- [ ] Test naming follows `MethodName_Scenario_ExpectedBehavior`
- [ ] Flaky tests are quarantined and tracked, not ignored
- [ ] `IClassFixture<T>` used for shared expensive resources
- [ ] Tests run in parallel by default (xUnit default); shared state is avoided
