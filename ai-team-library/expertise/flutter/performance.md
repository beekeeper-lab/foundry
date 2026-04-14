# Flutter Performance Conventions

## Core Principles

1. **Minimize rebuilds.** Flutter is fast when the widget tree diffs efficiently.
   Every unnecessary rebuild wastes frames.
2. **Keep the main isolate free.** Long-running computation blocks the UI thread
   at 16ms per frame (60fps). Offload heavy work to isolates.
3. **Measure before optimizing.** Use DevTools, not intuition. Profile on real
   devices, not emulators.

---

## Widget Rebuild Optimization

### Use `const` Everywhere Possible

```dart
// Good: const prevents rebuild of this subtree
return Column(
  children: [
    const AppHeader(),           // Never rebuilds
    OrderList(orders: orders),   // Only rebuilds when orders change
    const FooterLinks(),         // Never rebuilds
  ],
);
```

`const` widgets are canonicalized — Flutter reuses the same instance and skips
the entire subtree during diffing.

### Granular Rebuilds with Riverpod

```dart
// Bad: entire screen rebuilds when any part of the order changes
class OrderScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final order = ref.watch(orderProvider); // Watches everything
    return Column(
      children: [
        Text(order.title),
        Text(order.status.name),
        Text('\$${order.total}'),
      ],
    );
  }
}

// Good: only the status widget rebuilds when status changes
class OrderStatusBadge extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(
      orderProvider.select((order) => order.status),
    );
    return Chip(label: Text(status.name));
  }
}
```

### Rules

- Use `ref.watch(provider.select(...))` to watch only the specific field a
  widget needs.
- Split large widgets into smaller `ConsumerWidget` classes so only the
  relevant subtree rebuilds.
- Use `RepaintBoundary` around complex or frequently animating subtrees to
  isolate repaints.
- Never use `setState` to trigger rebuilds that Riverpod can handle.

---

## Lists and Scrolling

### Use `ListView.builder` for Dynamic Lists

```dart
// Good: only visible items are built
ListView.builder(
  itemCount: orders.length,
  itemBuilder: (context, index) => OrderTile(
    key: ValueKey(orders[index].id),
    order: orders[index],
  ),
);

// Bad: all items built at once
ListView(
  children: orders.map((o) => OrderTile(order: o)).toList(),
);
```

### Rules

- Use `ListView.builder` or `SliverList.builder` for lists of unknown or large
  length. They virtualize and only build visible items.
- Provide `itemExtent` or `prototypeItem` when all items have the same height —
  this skips layout computation for off-screen items.
- Use `ValueKey` with a stable identifier on list items. Index-based keys cause
  incorrect recycling when the list is reordered.
- Use `AutomaticKeepAliveClientMixin` sparingly — only for items with expensive
  state that must survive scrolling off-screen (e.g., video players).
- For very large lists (10,000+ items), consider pagination or lazy loading
  rather than loading all data into memory.

---

## Images and Assets

### Efficient Image Loading

```dart
// Use cached_network_image for remote images
CachedNetworkImage(
  imageUrl: product.imageUrl,
  width: 120,
  height: 120,
  fit: BoxFit.cover,
  placeholder: (context, url) => const ShimmerPlaceholder(),
  errorWidget: (context, url, error) => const Icon(Icons.broken_image),
);
```

### Rules

- Use `cached_network_image` for all remote images. It handles caching, placeholder
  display, and error states.
- Specify `width` and `height` on images. Without explicit dimensions, Flutter
  triggers layout reflows when images load.
- Resize images server-side. Do not download full-resolution images for thumbnails.
- Use vector assets (SVG via `flutter_svg`) for icons and illustrations. They
  scale without quality loss and are smaller than bitmaps.
- Precache critical images with `precacheImage()` during splash/loading screens.
- Use `AssetImage` with resolution-aware variants (`2.0x/`, `3.0x/`) for local
  assets.

---

## Isolates for Heavy Computation

```dart
// Dart 3+: use Isolate.run for one-shot computation
Future<List<Order>> parseOrders(String jsonString) async {
  return Isolate.run(() {
    final list = jsonDecode(jsonString) as List;
    return list.map((e) => OrderDto.fromJson(e as Map<String, dynamic>).toDomain()).toList();
  });
}
```

### Rules

- Offload JSON parsing of large payloads (>1MB) to a separate isolate.
- Use `Isolate.run` (Dart 3+) for one-shot computation. It handles spawning and
  cleanup automatically.
- Do not use isolates for trivial operations — the overhead of message passing
  exceeds the benefit for small payloads.
- Profile first. Most JSON parsing and list operations complete well within
  16ms on modern devices.

---

## Animation Performance

```dart
// Use AnimatedContainer for implicit animations
AnimatedContainer(
  duration: const Duration(milliseconds: 300),
  curve: Curves.easeInOut,
  height: isExpanded ? 200 : 60,
  color: isSelected ? theme.colorScheme.primaryContainer : theme.colorScheme.surface,
);
```

### Rules

- Prefer implicit animations (`AnimatedContainer`, `AnimatedOpacity`,
  `AnimatedSwitcher`) for simple transitions. They are declarative and
  automatically optimized.
- Use `AnimationController` + `AnimatedBuilder` for complex, coordinated
  animations. Avoid `addListener` + `setState` — it rebuilds the entire widget.
- Use `RepaintBoundary` around animated widgets to prevent repainting siblings.
- Target 60fps. Use DevTools performance overlay to identify jank.
- Avoid animating layout-triggering properties (`width`, `height`, `padding`)
  on complex subtrees. Prefer `Transform` and `Opacity` which only affect
  compositing.

---

## Startup Performance

### Rules

- Minimize work in `main()`. Initialize only essential services (error reporting,
  storage) before `runApp()`.
- Use `ensureInitialized()` only when required by plugins. Do not call it
  reflexively.
- Defer non-critical initialization. Load feature-specific data when the feature
  is first accessed, not at startup.
- Use deferred loading (`deferred as`) for large feature modules that are not
  needed on the first screen.
- Measure startup time with `flutter run --trace-startup`. Profile the timeline
  in DevTools.
- Use a native splash screen (`flutter_native_splash`) to cover initialization.
  Do not show a blank frame.

---

## Network Performance

### Rules

- Use `dio` interceptors for request/response logging, auth token injection,
  and retry logic. Do not duplicate this in every API call.
- Implement request cancellation with `CancelToken` for screens that can be
  navigated away from before the request completes.
- Cache responses where appropriate (e.g., product catalogs). Use HTTP cache
  headers or a local database.
- Batch related API calls with `Future.wait` when they are independent.
- Implement pagination for list endpoints. Do not fetch unbounded data sets.
- Compress request bodies for large payloads. Use gzip encoding.

---

## Profiling Checklist

- [ ] Profile on a real device (not emulator), preferably a low-end device
- [ ] Use DevTools Performance overlay to check for jank (frames >16ms)
- [ ] Use DevTools Widget Inspector to find unnecessary rebuilds
- [ ] Check memory usage with DevTools Memory tab — look for leaks
- [ ] Verify image sizes match display dimensions (no oversized downloads)
- [ ] Measure app startup time with `--trace-startup`
- [ ] Test scrolling performance on long lists with real data volumes
- [ ] Verify animations run at 60fps using DevTools timeline
