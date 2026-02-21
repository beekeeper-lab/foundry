# .NET MAUI Framework

Patterns and conventions for .NET MAUI (Multi-platform App UI) applications
targeting .NET 8+. Covers cross-platform development for iOS, Android, macOS,
and Windows from a single codebase. This guide assumes familiarity with the
core .NET stack conventions.

---

## Defaults

| Decision                | Default                                          | Alternatives                                |
|-------------------------|--------------------------------------------------|---------------------------------------------|
| Architecture            | MVVM with CommunityToolkit.Mvvm                  | MVU (Comet), ReactiveUI                     |
| Navigation              | Shell navigation                                 | NavigationPage, manual page pushing          |
| DI container            | `Microsoft.Extensions.DependencyInjection` (built-in) | — (no reason to change)                |
| Data binding            | Compiled bindings (`x:DataType`)                 | Reflection-based bindings (avoid)           |
| UI toolkit              | XAML with .NET MAUI controls                     | Blazor Hybrid, C# Markup (CommunityToolkit) |
| HTTP client             | `HttpClient` via `IHttpClientFactory`            | Refit                                       |
| Local storage           | SQLite via `sqlite-net-pcl`                      | LiteDB, Preferences API (key-value)        |
| Images                  | SVG via `MauiImage` build action                 | PNG with density variants                   |
| Fonts                   | Embedded fonts via `MauiFont` build action       | Platform-specific fonts                     |
| Testing                 | xUnit + NSubstitute (ViewModels), Appium (UI)    | Device runners, Xamarin.UITest              |

---

## Project Structure

```
Company.App/
  App.xaml(.cs)                  # Application entry point
  AppShell.xaml(.cs)             # Shell navigation structure
  MauiProgram.cs                 # Host builder, DI, configuration
  Platforms/
    Android/                     # Android-specific code
      MainActivity.cs
      AndroidManifest.xml
    iOS/                         # iOS-specific code
      AppDelegate.cs
      Info.plist
    MacCatalyst/                 # macOS-specific code
    Windows/                     # Windows-specific code
  Features/
    Orders/
      OrderListPage.xaml(.cs)    # View
      OrderListViewModel.cs      # ViewModel
      OrderDetailPage.xaml(.cs)
      OrderDetailViewModel.cs
    Settings/
      SettingsPage.xaml(.cs)
      SettingsViewModel.cs
  Services/
    IOrderService.cs             # Service interfaces
    OrderService.cs
    IConnectivityService.cs
  Models/
    Order.cs                     # Domain/data models
    OrderStatus.cs
  Controls/
    LoadingOverlay.xaml(.cs)      # Custom reusable controls
    StatusBadge.xaml(.cs)
  Converters/
    BoolToColorConverter.cs      # Value converters
    StatusToIconConverter.cs
  Resources/
    Styles/
      Colors.xaml
      Styles.xaml
    Fonts/
    Images/
    Raw/
Company.App.Tests/
  ViewModels/
    OrderListViewModelTests.cs
  Services/
    OrderServiceTests.cs
```

**Rules:**
- Organize by feature, not by technical layer. Each feature folder contains its
  pages and ViewModels together.
- Platform-specific code goes in `Platforms/` folders. Use partial classes and
  `#if` directives only when necessary.
- Resources (colors, styles, fonts, images) live in `Resources/` with proper
  build actions.
- ViewModels never reference UI types (`Page`, `View`, `Color`). They are
  pure .NET classes.

---

## MVVM with CommunityToolkit.Mvvm

### ViewModel Pattern

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace Company.App.Features.Orders;

public sealed partial class OrderListViewModel : ObservableObject
{
    private readonly IOrderService _orderService;
    private readonly IConnectivityService _connectivity;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(RefreshCommand))]
    private bool _isLoading;

    [ObservableProperty]
    private ObservableCollection<OrderSummary> _orders = [];

    [ObservableProperty]
    private string? _errorMessage;

    public OrderListViewModel(
        IOrderService orderService,
        IConnectivityService connectivity)
    {
        _orderService = orderService;
        _connectivity = connectivity;
    }

    [RelayCommand(CanExecute = nameof(CanRefresh))]
    private async Task RefreshAsync()
    {
        try
        {
            IsLoading = true;
            ErrorMessage = null;

            var result = await _orderService.GetOrdersAsync();
            Orders = new ObservableCollection<OrderSummary>(result);
        }
        catch (HttpRequestException)
        {
            ErrorMessage = "Unable to load orders. Check your connection.";
        }
        finally
        {
            IsLoading = false;
        }
    }

    private bool CanRefresh() => !IsLoading;

    [RelayCommand]
    private async Task SelectOrderAsync(OrderSummary order)
    {
        await Shell.Current.GoToAsync(
            $"{nameof(OrderDetailPage)}",
            new Dictionary<string, object> { ["Order"] = order });
    }
}
```

### Page Binding

```xml
<!-- OrderListPage.xaml -->
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:vm="clr-namespace:Company.App.Features.Orders"
             x:Class="Company.App.Features.Orders.OrderListPage"
             x:DataType="vm:OrderListViewModel"
             Title="Orders">

    <RefreshView Command="{Binding RefreshCommand}"
                 IsRefreshing="{Binding IsLoading}">
        <CollectionView ItemsSource="{Binding Orders}"
                        SelectionMode="Single"
                        SelectionChangedCommand="{Binding SelectOrderCommand}"
                        SelectionChangedCommandParameter="{Binding SelectedItem,
                            Source={RelativeSource Self}}">
            <CollectionView.ItemTemplate>
                <DataTemplate x:DataType="models:OrderSummary">
                    <Grid Padding="16,8" ColumnDefinitions="*,Auto">
                        <Label Text="{Binding OrderNumber}"
                               FontAttributes="Bold" />
                        <Label Grid.Column="1"
                               Text="{Binding Total, StringFormat='{0:C}'}" />
                    </Grid>
                </DataTemplate>
            </CollectionView.ItemTemplate>
            <CollectionView.EmptyView>
                <Label Text="No orders found."
                       HorizontalOptions="Center"
                       VerticalOptions="Center" />
            </CollectionView.EmptyView>
        </CollectionView>
    </RefreshView>
</ContentPage>
```

---

## Dependency Injection

```csharp
// MauiProgram.cs
public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("Inter-Regular.ttf", "InterRegular");
                fonts.AddFont("Inter-Bold.ttf", "InterBold");
            });

        // Services
        builder.Services.AddSingleton<IConnectivityService, ConnectivityService>();
        builder.Services.AddSingleton<IOrderService, OrderService>();
        builder.Services.AddHttpClient("Api", client =>
        {
            client.BaseAddress = new Uri("https://api.example.com/");
            client.Timeout = TimeSpan.FromSeconds(15);
        });

        // ViewModels (Transient — new instance per navigation)
        builder.Services.AddTransient<OrderListViewModel>();
        builder.Services.AddTransient<OrderDetailViewModel>();

        // Pages (Transient — new instance per navigation)
        builder.Services.AddTransient<OrderListPage>();
        builder.Services.AddTransient<OrderDetailPage>();

#if DEBUG
        builder.Logging.AddDebug();
#endif

        return builder.Build();
    }
}
```

**Rules:**
- ViewModels and Pages are registered as `Transient`. Each navigation creates
  a fresh instance, avoiding stale state.
- Services are `Singleton` (stateless) or `Scoped` (if tied to a session).
- Use `IHttpClientFactory` for HTTP clients. Never create `HttpClient` directly.
- Configure platform-specific services using `#if ANDROID`, `#if IOS`, etc.

---

## Shell Navigation

```csharp
// AppShell.xaml.cs
public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();

        // Register routes for pages not in the Shell visual hierarchy
        Routing.RegisterRoute(nameof(OrderDetailPage), typeof(OrderDetailPage));
    }
}

// Navigate with parameters
await Shell.Current.GoToAsync($"{nameof(OrderDetailPage)}?id={orderId}");

// Receive parameters via query attributes
[QueryProperty(nameof(OrderId), "id")]
public sealed partial class OrderDetailViewModel : ObservableObject
{
    [ObservableProperty]
    private string? _orderId;

    partial void OnOrderIdChanged(string? value)
    {
        if (value is not null)
        {
            LoadOrderCommand.Execute(null);
        }
    }
}
```

---

## Do / Don't

### Do

- Use `x:DataType` on every XAML page and `DataTemplate` for compiled bindings.
- Use `CommunityToolkit.Mvvm` source generators (`[ObservableProperty]`,
  `[RelayCommand]`) to reduce boilerplate.
- Use `IConnectivity` to check network state before HTTP calls.
- Use `SecureStorage` for tokens and secrets. Never store sensitive data in
  `Preferences`.
- Use `WeakReferenceMessenger` for cross-ViewModel communication.
- Use `OnAppearing`/`OnDisappearing` for page lifecycle, not constructor/finalizer.
- Dispose subscriptions and event handlers in `OnDisappearing`.
- Test ViewModels in isolation — they should have zero MAUI dependencies.
- Use `DeviceInfo` and `DeviceDisplay` for platform-aware behavior.
- Use `MauiImage` build action for SVGs — they auto-resize per platform density.

### Don't

- Don't put business logic in code-behind (`.xaml.cs`) files. Code-behind
  should only contain UI wiring that can't be done in XAML.
- Don't use reflection-based bindings (missing `x:DataType`). They're slower
  and don't produce compile-time errors.
- Don't use `Device.BeginInvokeOnMainThread` — use `MainThread.InvokeOnMainThreadAsync`.
- Don't create custom renderers — use Handlers (the MAUI replacement).
- Don't reference `Android.*` or `UIKit.*` namespaces in shared code. Use
  dependency injection and interfaces to abstract platform APIs.
- Don't store large objects in `Preferences` — use SQLite or file storage.
- Don't ignore the back button. Handle `Shell.BackButtonBehavior` for
  custom navigation flows.
- Don't block the UI thread with synchronous I/O. All I/O must be async.

---

## Platform-Specific Code

### Using Partial Classes

```csharp
// Services/IDeviceOrientationService.cs
public interface IDeviceOrientationService
{
    DeviceOrientation GetOrientation();
}

// Platforms/Android/Services/DeviceOrientationService.cs
public sealed partial class DeviceOrientationService : IDeviceOrientationService
{
    public DeviceOrientation GetOrientation()
    {
        var orientation = Platform.CurrentActivity?.Resources?.Configuration?.Orientation;
        return orientation == global::Android.Content.Res.Orientation.Landscape
            ? DeviceOrientation.Landscape
            : DeviceOrientation.Portrait;
    }
}

// Platforms/iOS/Services/DeviceOrientationService.cs
public sealed partial class DeviceOrientationService : IDeviceOrientationService
{
    public DeviceOrientation GetOrientation()
    {
        var orientation = UIDevice.CurrentDevice.Orientation;
        return orientation is UIDeviceOrientation.LandscapeLeft
            or UIDeviceOrientation.LandscapeRight
            ? DeviceOrientation.Landscape
            : DeviceOrientation.Portrait;
    }
}
```

---

## Local Data with SQLite

```csharp
public sealed class LocalDatabase
{
    private SQLiteAsyncConnection? _database;

    private async Task<SQLiteAsyncConnection> GetConnectionAsync()
    {
        if (_database is not null)
            return _database;

        var dbPath = Path.Combine(
            FileSystem.AppDataDirectory, "app.db3");

        _database = new SQLiteAsyncConnection(dbPath,
            SQLiteOpenFlags.ReadWrite |
            SQLiteOpenFlags.Create |
            SQLiteOpenFlags.SharedCache);

        await _database.CreateTableAsync<CachedOrder>();
        return _database;
    }

    public async Task<List<CachedOrder>> GetOrdersAsync()
    {
        var db = await GetConnectionAsync();
        return await db.Table<CachedOrder>().ToListAsync();
    }

    public async Task SaveOrderAsync(CachedOrder order)
    {
        var db = await GetConnectionAsync();
        await db.InsertOrReplaceAsync(order);
    }
}
```

---

## Common Pitfalls

1. **Missing compiled bindings** — Omitting `x:DataType` silently falls back to
   reflection bindings, which are slower and don't produce compile-time errors
   for typos. Always set `x:DataType`.
2. **Main thread violations** — Updating UI-bound properties from background
   threads causes crashes on iOS/Android. Use `MainThread.InvokeOnMainThreadAsync`
   or ensure `ObservableProperty` changes happen on the UI thread.
3. **Hot Restart vs Hot Reload confusion** — Hot Reload updates XAML and some C#
   live. Hot Restart redeploys the app. Structural changes (new pages, DI
   registrations) require a full rebuild.
4. **Oversized images** — Shipping full-resolution PNGs for all platforms bloats
   the app. Use SVGs with `MauiImage` build action for automatic density-aware
   resizing.
5. **Ignoring lifecycle** — Not unsubscribing from `MessagingCenter` or events
   in `OnDisappearing` causes memory leaks and duplicate handlers.
6. **Platform-specific crashes** — Code that works on one platform may crash on
   another. Test on all target platforms regularly, not just at release time.
7. **Storing secrets in Preferences** — `Preferences` is plaintext on most
   platforms. Use `SecureStorage` for tokens, passwords, and API keys.
8. **Blocking the UI with sync calls** — Synchronous HTTP or database calls
   freeze the UI. All I/O operations must use `async`/`await`.

---

## Alternatives

| Approach                   | When to consider                                      |
|----------------------------|-------------------------------------------------------|
| Blazor Hybrid              | Web developers building mobile/desktop apps           |
| Avalonia UI                | Cross-platform desktop (Linux support, no mobile)     |
| Uno Platform               | UWP/WinUI XAML skills, broader platform reach         |
| Xamarin.Forms (legacy)     | Existing Xamarin apps not yet migrated                 |
| Flutter / React Native     | Teams with stronger Dart/JavaScript skills            |

---

## Checklist

- [ ] `x:DataType` set on all XAML pages and DataTemplates (compiled bindings)
- [ ] ViewModels use `CommunityToolkit.Mvvm` source generators
- [ ] ViewModels contain zero references to MAUI UI types
- [ ] Pages and ViewModels registered as Transient in DI
- [ ] Services registered as Singleton (stateless) or Scoped
- [ ] Shell navigation configured with registered routes
- [ ] Sensitive data stored in `SecureStorage`, not `Preferences`
- [ ] HTTP calls use `IHttpClientFactory`, not `new HttpClient()`
- [ ] Network connectivity checked before API calls (`IConnectivity`)
- [ ] Event handlers unsubscribed in `OnDisappearing`
- [ ] Images use SVG with `MauiImage` build action
- [ ] Platform-specific code isolated in `Platforms/` with partial classes
- [ ] All I/O operations are async — no blocking calls on UI thread
- [ ] App tested on all target platforms (not just one)
- [ ] `MainThread.InvokeOnMainThreadAsync` used for UI updates from background threads
