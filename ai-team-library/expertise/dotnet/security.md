# .NET Security

Security practices for .NET 8+ applications. Security is not a feature to add
later -- it is baked into every layer from the start. These rules apply to all
services regardless of whether they face the public internet.

---

## Defaults

| Concern                | Default                                        |
|------------------------|------------------------------------------------|
| Authentication         | JWT Bearer tokens via ASP.NET Core Identity or external IdP |
| Authorization          | Policy-based authorization (`[Authorize(Policy = "...")]`) |
| Secrets management     | User Secrets (dev), Azure Key Vault / AWS Secrets Manager (prod) |
| HTTPS                  | Enforced in all environments                   |
| CORS                   | Explicit allowlist -- never `AllowAnyOrigin` with credentials |
| Input validation       | FluentValidation + `[ApiController]` model binding |
| Dependency scanning    | `dotnet list package --vulnerable` in CI       |
| Static analysis        | Roslyn security analyzers (`Microsoft.CodeAnalysis.NetAnalyzers`) |
| Data protection        | ASP.NET Core Data Protection API for encryption at rest |
| Rate limiting          | Built-in `RateLimiter` middleware (.NET 7+)    |

---

## Do / Don't

### Do

- Validate all input at the API boundary before it reaches application services.
- Use parameterized queries and EF Core (never string concatenation for SQL).
- Store secrets in a vault, never in `appsettings.json`, environment variables
  in plain text, or source control.
- Enforce HTTPS with `app.UseHttpsRedirection()` and HSTS headers.
- Use the `[Authorize]` attribute on all controllers/endpoints by default.
  Add `[AllowAnonymous]` only where explicitly needed.
- Return generic error messages to clients for 500-level errors.
- Log security events (failed auth, authorization denials) at Warning level.
- Pin NuGet package versions and audit with `dotnet list package --vulnerable`.

### Don't

- Don't store passwords in plain text. Use `PasswordHasher<T>` or an external IdP.
- Don't disable SSL validation, even in development.
- Don't use `AllowAnyOrigin()` with `AllowCredentials()` in CORS -- browsers
  block it and it signals a misconfiguration.
- Don't log sensitive data (tokens, passwords, PII, connection strings).
- Don't catch and swallow `SecurityException` or `UnauthorizedAccessException`.
- Don't trust client-side validation alone. Always re-validate server-side.
- Don't embed secrets in Dockerfiles or CI pipeline definitions.

---

## Authentication Setup

```csharp
// Program.cs -- JWT Bearer authentication
builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Auth:Authority"];
        options.Audience = builder.Configuration["Auth:Audience"];
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30),
        };
    });

builder.Services.AddAuthorizationBuilder()
    .AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"))
    .AddPolicy("CanManageOrders", policy =>
        policy.RequireClaim("permission", "orders:write"));
```

---

## Input Validation and SQL Injection Prevention

```csharp
// FluentValidation validator -- runs before the service layer
public sealed class CreateOrderRequestValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderRequestValidator()
    {
        RuleFor(x => x.Sku)
            .NotEmpty()
            .MaximumLength(50)
            .Matches(@"^[A-Z0-9\-]+$").WithMessage("SKU contains invalid characters.");

        RuleFor(x => x.Quantity)
            .InclusiveBetween(1, 10_000);
    }
}

// EF Core parameterized query -- safe by default
var orders = await context.Orders
    .Where(o => o.CustomerId == customerId && o.Status == status)
    .AsNoTracking()
    .ToListAsync(ct);

// NEVER do this:
// var sql = $"SELECT * FROM Orders WHERE CustomerId = '{customerId}'";
```

---

## Security Headers Middleware

```csharp
// Middleware to add security headers
app.Use(async (context, next) =>
{
    context.Response.Headers.Append("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Append("X-Frame-Options", "DENY");
    context.Response.Headers.Append("Referrer-Policy", "strict-origin-when-cross-origin");
    context.Response.Headers.Append("Permissions-Policy",
        "camera=(), microphone=(), geolocation=()");
    await next();
});

app.UseHsts(); // HTTP Strict Transport Security
app.UseHttpsRedirection();
```

---

## Common Pitfalls

1. **Secrets in appsettings.json** -- Even `appsettings.Development.json` gets
   committed. Use User Secrets for local dev, vault for deployed environments.
2. **Over-permissive CORS** -- Starting with `AllowAnyOrigin` during
   development and forgetting to lock it down. Set explicit origins from the start.
3. **Missing authorization on new endpoints** -- Add `[Authorize]` globally via
   `builder.Services.AddAuthorizationBuilder().SetFallbackPolicy(...)` and
   opt out with `[AllowAnonymous]` where needed.
4. **Logging PII** -- Structured logging makes it easy to accidentally include
   user email, IP, or tokens. Use a log scrubbing filter or destructure policy.
5. **Stale dependencies** -- Known CVEs in NuGet packages. Run
   `dotnet list package --vulnerable` weekly and in every CI build.
6. **JWT misconfiguration** -- Disabling audience or issuer validation
   "to make it work" in development. Validate everything in every environment.
7. **Mass assignment** -- Binding request bodies directly to domain entities
   allows clients to set fields they should not. Always bind to DTOs and map explicitly.

---

## Alternatives

| Tool                     | When to consider                              |
|--------------------------|-----------------------------------------------|
| Duende IdentityServer    | Self-hosted OAuth2/OIDC server                |
| Auth0 / Entra ID         | Managed identity provider                     |
| NWebsec                  | Additional security header middleware         |
| HtmlSanitizer            | Sanitizing user-generated HTML content        |
| Snyk / Dependabot        | Automated dependency vulnerability monitoring |

---

## Checklist

- [ ] HTTPS enforced with HSTS in all environments
- [ ] Authentication configured with JWT Bearer or cookie auth
- [ ] Authorization uses policy-based `[Authorize]` with fallback policy
- [ ] Secrets stored in User Secrets (dev) and vault (prod) -- never in config files
- [ ] Input validation runs at API boundary (FluentValidation or DataAnnotations)
- [ ] All database queries use parameterized queries / EF Core -- no raw string SQL
- [ ] CORS configured with explicit origin allowlist
- [ ] Security headers set (X-Content-Type-Options, X-Frame-Options, HSTS)
- [ ] `dotnet list package --vulnerable` runs in CI and fails on Critical/High
- [ ] Security analyzers enabled (`AnalysisLevel: latest-recommended`)
- [ ] Failed authentication/authorization attempts logged at Warning level
- [ ] No PII or secrets in log output
- [ ] Rate limiting enabled on public-facing endpoints
- [ ] Anti-forgery tokens used for cookie-authenticated form submissions
