# .NET Blazor Framework

Patterns and conventions for Blazor applications targeting .NET 8+. Covers
Blazor Server, Blazor WebAssembly (WASM), and the unified Blazor Web App model
introduced in .NET 8. This guide assumes familiarity with the core .NET stack
conventions.

---

## Defaults

| Decision                | Default                                          | Alternatives                              |
|-------------------------|--------------------------------------------------|-------------------------------------------|
| Hosting model           | Blazor Web App (Server + WASM per-page)          | Blazor Server only, Blazor WASM standalone |
| Render mode             | InteractiveServer (default), InteractiveWebAssembly per-component | Static SSR for content-heavy pages       |
| State management        | Cascading parameters + scoped services           | Fluxor, Blazor-State                      |
| Component library       | MudBlazor                                        | Radzen, Syncfusion, Ant Design Blazor     |
| Forms & validation      | EditForm + DataAnnotationsValidator              | FluentValidation + custom validator       |
| HTTP client             | `HttpClient` via `IHttpClientFactory`            | RestSharp, Refit                          |
| Authentication          | ASP.NET Core Identity + AuthenticationStateProvider | OIDC with Duende IdentityServer, Auth0   |
| JS interop              | `IJSRuntime` (minimal, isolated JS modules)      | JS initializers                           |
| CSS isolation           | Scoped CSS (`.razor.css`)                        | Tailwind CSS, CSS-in-C# (BlazorStyled)   |
| Real-time               | SignalR (built-in for Blazor Server)             | WebSockets, SSE                           |

---

## Render Modes (.NET 8+)

```csharp
// App.razor — set global default
<Routes @rendermode="InteractiveServer" />

// Per-component override
<Counter @rendermode="InteractiveWebAssembly" />

// Static SSR for pages that don't need interactivity
<ProductCatalog @rendermode="@null" />
```

**Rules:**
- Default to `InteractiveServer` for internal apps where latency to the server
  is low and real-time updates matter.
- Use `InteractiveWebAssembly` for components that must work offline or reduce
  server load.
- Use Static SSR (`@null`) for content-heavy pages that don't need interactivity
  (marketing pages, documentation).
- Never mix render modes within the same component hierarchy without
  understanding serialization boundaries.

---

## Component Design

### Component Structure

```csharp
// Components/Orders/OrderList.razor
@namespace Company.Project.Components.Orders

<div class="order-list">
    @if (_orders is null)
    {
        <LoadingSpinner />
    }
    else if (_orders.Count == 0)
    {
        <EmptyState Message="No orders found." />
    }
    else
    {
        <table class="table">
            <thead>
                <tr>
                    <th>Order #</th>
                    <th>Date</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                @foreach (var order in _orders)
                {
                    <OrderRow Order="order" OnSelect="HandleSelect" />
                }
            </tbody>
        </table>
    }
</div>

@code {
    [Parameter, EditorRequired]
    public required Guid CustomerId { get; set; }

    [Inject]
    private IOrderService OrderService { get; set; } = default!;

    private List<OrderSummary>? _orders;

    protected override async Task OnInitializedAsync()
    {
        _orders = await OrderService.GetByCustomerAsync(CustomerId);
    }

    private void HandleSelect(OrderSummary order)
    {
        NavigationManager.NavigateTo($"/orders/{order.Id}");
    }
}
```

### Code-Behind Pattern (for complex components)

```csharp
// OrderList.razor.cs
public sealed partial class OrderList : ComponentBase
{
    [Parameter, EditorRequired]
    public required Guid CustomerId { get; set; }

    [Inject]
    private IOrderService OrderService { get; set; } = default!;

    [Inject]
    private NavigationManager NavigationManager { get; set; } = default!;

    private List<OrderSummary>? _orders;

    protected override async Task OnInitializedAsync()
    {
        _orders = await OrderService.GetByCustomerAsync(CustomerId);
    }

    private void HandleSelect(OrderSummary order)
    {
        NavigationManager.NavigateTo($"/orders/{order.Id}");
    }
}
```

---

## Do / Don't

### Do

- Use `[EditorRequired]` on all mandatory `[Parameter]` properties.
- Use `sealed partial class` for code-behind files.
- Use scoped CSS (`.razor.css`) for component-specific styles.
- Dispose services and event handlers by implementing `IAsyncDisposable`.
- Use `OnParametersSetAsync` instead of `OnInitializedAsync` when the component
  reacts to parameter changes.
- Use `EventCallback<T>` for child-to-parent communication.
- Use `CascadingValue` sparingly — only for truly cross-cutting concerns like
  theme or auth state.
- Use `@key` directive on repeated elements to help the diffing algorithm.
- Use `NavigationManager` for programmatic navigation; avoid raw JS `window.location`.
- Use `StreamRendering` attribute for pages with slow async data loading.

### Don't

- Don't call `StateHasChanged()` from `OnInitializedAsync` — it's called
  automatically after lifecycle methods.
- Don't use `IJSRuntime` to manipulate the DOM. Use Blazor's declarative model.
- Don't create God components with 500+ lines. Split into focused child components.
- Don't pass mutable objects as `[Parameter]` — use immutable records or `EventCallback`
  for updates.
- Don't use `Task.Run` in Blazor Server — it wastes thread pool threads when
  the circuit is already async.
- Don't catch exceptions silently in components — use `ErrorBoundary` components.
- Don't reference `HttpContext` in interactive components — it's only available
  during static SSR.
- Don't use `InvokeAsync(() => StateHasChanged())` as a fix for threading issues —
  fix the underlying design.

---

## State Management

### Scoped Services (Recommended Default)

```csharp
// Services/AppState.cs
public sealed class AppState
{
    public event Action? OnChange;

    private string _searchTerm = string.Empty;

    public string SearchTerm
    {
        get => _searchTerm;
        set
        {
            _searchTerm = value;
            OnChange?.Invoke();
        }
    }
}

// Registration
builder.Services.AddScoped<AppState>();

// Usage in component
@implements IDisposable
@inject AppState State

<input @bind="State.SearchTerm" @bind:event="oninput" />

@code {
    protected override void OnInitialized()
    {
        State.OnChange += StateHasChanged;
    }

    public void Dispose()
    {
        State.OnChange -= StateHasChanged;
    }
}
```

### Cascading Parameters (for theme/auth)

```csharp
// App.razor
<CascadingValue Value="_theme" Name="AppTheme">
    <Router AppAssembly="typeof(App).Assembly">
        ...
    </Router>
</CascadingValue>

// Any descendant component
[CascadingParameter(Name = "AppTheme")]
private Theme Theme { get; set; } = default!;
```

---

## Forms and Validation

```csharp
<EditForm Model="_model" OnValidSubmit="HandleSubmit" FormName="CreateOrder">
    <DataAnnotationsValidator />
    <ValidationSummary />

    <div class="form-group">
        <label for="product">Product</label>
        <InputText id="product" @bind-Value="_model.ProductName" class="form-control" />
        <ValidationMessage For="() => _model.ProductName" />
    </div>

    <div class="form-group">
        <label for="quantity">Quantity</label>
        <InputNumber id="quantity" @bind-Value="_model.Quantity" class="form-control" />
        <ValidationMessage For="() => _model.Quantity" />
    </div>

    <button type="submit" class="btn btn-primary">Create</button>
</EditForm>

@code {
    private CreateOrderModel _model = new();

    private async Task HandleSubmit()
    {
        await OrderService.CreateAsync(_model);
        NavigationManager.NavigateTo("/orders");
    }
}
```

---

## JavaScript Interop

```csharp
// Isolated JS module (preferred)
// wwwroot/js/clipboard.js
export function copyToClipboard(text) {
    return navigator.clipboard.writeText(text);
}

// Component
@inject IJSRuntime JS
@implements IAsyncDisposable

@code {
    private IJSObjectReference? _module;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            _module = await JS.InvokeAsync<IJSObjectReference>(
                "import", "./js/clipboard.js");
        }
    }

    private async Task CopyText(string text)
    {
        if (_module is not null)
        {
            await _module.InvokeVoidAsync("copyToClipboard", text);
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_module is not null)
        {
            await _module.DisposeAsync();
        }
    }
}
```

**Rules:**
- Always use isolated JS modules (`import`) over global `<script>` tags.
- Dispose `IJSObjectReference` in `IAsyncDisposable`.
- Never call JS interop in `OnInitializedAsync` — the DOM isn't ready. Use
  `OnAfterRenderAsync(firstRender: true)`.
- Minimize JS interop surface. If Blazor can do it, don't use JS.

---

## Authentication and Authorization

```csharp
// Program.cs
builder.Services.AddCascadingAuthenticationState();
builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = IdentityConstants.ApplicationScheme;
    options.DefaultSignInScheme = IdentityConstants.ExternalScheme;
}).AddIdentityCookies();

// Protect a page
@attribute [Authorize(Roles = "Admin")]
@page "/admin/dashboard"

// Conditional rendering
<AuthorizeView>
    <Authorized>
        <p>Welcome, @context.User.Identity?.Name</p>
    </Authorized>
    <NotAuthorized>
        <p>Please log in.</p>
    </NotAuthorized>
</AuthorizeView>
```

---

## Error Handling

```csharp
// Wrap component trees in ErrorBoundary
<ErrorBoundary @ref="_errorBoundary">
    <ChildContent>
        <OrderList CustomerId="@_customerId" />
    </ChildContent>
    <ErrorContent Context="ex">
        <div class="alert alert-danger">
            <p>Something went wrong loading orders.</p>
            <button class="btn btn-link" @onclick="Recover">Try again</button>
        </div>
    </ErrorContent>
</ErrorBoundary>

@code {
    private ErrorBoundary? _errorBoundary;

    private void Recover()
    {
        _errorBoundary?.Recover();
    }
}
```

---

## Common Pitfalls

1. **Render mode mismatch** — A component using `InteractiveServer` cannot contain
   a child using `InteractiveWebAssembly` (or vice versa) without crossing a
   serialization boundary. Plan render mode boundaries at the page level.
2. **Memory leaks from event handlers** — Forgetting to unsubscribe from events
   in `Dispose()` keeps the component alive in Blazor Server, leaking memory
   per circuit.
3. **Oversized WASM downloads** — Blazor WASM ships the .NET runtime to the
   browser. Trim unused assemblies with `<PublishTrimmed>true</PublishTrimmed>`
   and enable AOT compilation for performance-critical paths.
4. **Calling StateHasChanged from background threads** — In Blazor Server,
   `StateHasChanged` must be called on the synchronization context. Use
   `InvokeAsync(() => StateHasChanged())` from background threads.
5. **Overusing CascadingValue** — Every cascading value triggers re-renders in
   all descendant components. Use `IsFixed="true"` for values that never change.
6. **Large ViewState in forms** — Blazor Server serializes form state over
   SignalR. Keep form models small and avoid binding to complex object graphs.
7. **Missing @key on loops** — Without `@key`, Blazor's diffing algorithm may
   reuse DOM elements incorrectly, causing visual glitches in dynamic lists.
8. **Synchronous JS interop on WASM** — `IJSInProcessRuntime` blocks the single
   browser thread. Use async `IJSRuntime` unless synchronous calls are mandatory.

---

## Alternatives

| Approach                  | When to consider                                     |
|---------------------------|------------------------------------------------------|
| Blazor Server only        | Internal apps with reliable network, real-time needs |
| Blazor WASM standalone    | Offline-capable apps, static hosting, API-backed SPAs |
| Blazor Hybrid (MAUI)      | Desktop/mobile apps with web UI skills               |
| React/Angular + .NET API  | When the team has stronger JS/TS frontend skills     |
| Razor Pages (server-side) | Simple CRUD apps without complex interactivity       |

---

## Checklist

- [ ] Render mode chosen per-page/component based on interactivity requirements
- [ ] Components use `[EditorRequired]` on mandatory parameters
- [ ] Components implement `IDisposable`/`IAsyncDisposable` for cleanup
- [ ] Scoped CSS files created for component-specific styles
- [ ] `ErrorBoundary` wraps component trees that can fail
- [ ] JS interop uses isolated modules, not global scripts
- [ ] JS interop calls only in `OnAfterRenderAsync`, never in `OnInitializedAsync`
- [ ] Forms use `EditForm` with `DataAnnotationsValidator`
- [ ] Authentication uses `AuthorizeView` and `[Authorize]` attributes
- [ ] State management uses scoped services, not excessive cascading values
- [ ] `@key` directive used on all `@foreach` rendered elements
- [ ] WASM builds trimmed with `PublishTrimmed` enabled
- [ ] SignalR reconnection configured for Blazor Server apps
- [ ] `StreamRendering` used for pages with slow async data
- [ ] No `HttpContext` references in interactive components
