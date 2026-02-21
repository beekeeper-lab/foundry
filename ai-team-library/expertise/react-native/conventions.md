# React Native Stack Conventions

These conventions apply to all React Native mobile projects on this team. They are
opinionated by design -- consistency across the codebase matters more than individual
preference. Deviations require an ADR with justification.

---

## Defaults

| Category | Default | Alternatives (require ADR) |
|----------|---------|---------------------------|
| **Framework** | React Native 0.76+ (New Architecture enabled) | Expo managed workflow |
| **Language** | TypeScript in strict mode | — |
| **Navigation** | React Navigation 7+ (native stack) | React Native Navigation (Wix) |
| **State** | Local state first, TanStack Query for server state, Zustand for complex client state | Redux Toolkit, Jotai |
| **Styling** | StyleSheet.create with design tokens | NativeWind (Tailwind), Tamagui |
| **Testing (unit)** | Jest + React Native Testing Library | — |
| **Testing (e2e)** | Detox | Maestro, Appium |
| **Linting** | ESLint with `@react-native/eslint-config` | — |
| **Formatting** | Prettier with project-level config | — |
| **Package manager** | pnpm (lockfile committed) | yarn (classic or berry) |
| **CI builds** | Fastlane for iOS and Android | EAS Build (Expo) |

---

## 1. Project Structure

```
project-root/
  src/
    app/                    # App shell: navigation, providers, global config
      navigation/           # Navigator definitions (root, tab, stack)
      providers/            # Context providers (theme, auth, etc.)
    features/               # Feature modules (self-contained verticals)
      <feature-name>/
        components/         # Components scoped to this feature
        hooks/              # Hooks scoped to this feature
        screens/            # Screen components for this feature
        api.ts              # API calls for this feature
        types.ts            # Types scoped to this feature
        index.ts            # Public API of the feature
    components/             # Shared, reusable UI components
      ui/                   # Primitives (Button, TextInput, Card, etc.)
      layout/               # Layout components (SafeAreaWrapper, etc.)
    hooks/                  # Shared custom hooks
    lib/                    # Utilities, constants, helpers (no React)
    types/                  # Shared TypeScript types and interfaces
    services/               # Native module wrappers and platform services
  ios/                      # Xcode project and native iOS code
  android/                  # Gradle project and native Android code
  __tests__/                # Integration and snapshot tests
  e2e/                      # Detox end-to-end tests
  index.js                  # App entry point
  metro.config.js
  tsconfig.json
  babel.config.js
```

**Rules:**
- Organize by feature, not by file type. `features/checkout/` over
  `components/CheckoutForm` + `hooks/useCheckout` + `screens/CheckoutScreen`.
- A feature's `index.ts` is its public API. Other features import from the
  index, never from internal paths.
- Screen components live inside their feature's `screens/` directory. A screen
  is a top-level component that a navigator renders.
- Shared components live in `components/` only when used by two or more features.
  Do not preemptively generalize.
- Native module wrappers live in `services/` with a platform-agnostic TypeScript
  API. Never call native modules directly from components.

---

## 2. Component Patterns

### Functional Components Only

Class components are not used. All components are function components.

```tsx
// Good
export function OrderSummary({ orderId }: OrderSummaryProps) {
  // ...
}

// Also acceptable: arrow function for simple components
export const Badge = ({ label }: BadgeProps) => (
  <Text style={styles.badge}>{label}</Text>
);
```

### Screen Components

Screens are the top-level components rendered by navigators. They receive
navigation and route props.

```tsx
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { RootStackParamList } from "../navigation/types";

type Props = NativeStackScreenProps<RootStackParamList, "OrderDetail">;

export function OrderDetailScreen({ route, navigation }: Props) {
  const { orderId } = route.params;
  // ...
}
```

### Props

- Define props as a named type (not inline), suffixed with `Props`.
- Use destructuring in the function signature.
- Default values go in the destructuring, not `defaultProps`.

### Platform-Specific Components

When platform behavior diverges significantly, use platform-specific files.

```
Button/
  Button.tsx          # Shared logic
  Button.ios.tsx      # iOS-specific rendering (if needed)
  Button.android.tsx  # Android-specific rendering (if needed)
```

For minor differences, use `Platform.select` or `Platform.OS` inline.

---

## 3. Navigation

**Default: React Navigation with native stack.**

### Navigator Structure

Define a typed navigation hierarchy. All navigators are strongly typed.

```tsx
// navigation/types.ts
export type RootStackParamList = {
  Home: undefined;
  OrderDetail: { orderId: string };
  Settings: undefined;
};

export type MainTabParamList = {
  Feed: undefined;
  Orders: undefined;
  Profile: undefined;
};
```

### Navigator Rules

- Use `createNativeStackNavigator` for stack navigators (native performance).
- Use `createBottomTabNavigator` for tab bars.
- Keep the navigation tree shallow. Avoid nesting more than three navigators deep.
- Define screen options at the navigator level for consistency, override at
  the screen level only when necessary.
- Deep linking configuration lives in `app/navigation/linking.ts`.

### Navigation Patterns

```tsx
// Type-safe navigation
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";

type Nav = NativeStackNavigationProp<RootStackParamList>;

function OrderCard({ orderId }: { orderId: string }) {
  const navigation = useNavigation<Nav>();

  const handlePress = () => {
    navigation.navigate("OrderDetail", { orderId });
  };

  return <Pressable onPress={handlePress}>...</Pressable>;
}
```

- Always use typed navigation hooks. Untyped `navigation.navigate("OrderDetail")`
  silently accepts wrong param shapes.
- Use `Pressable` over `TouchableOpacity` for touch targets (more flexible,
  better accessibility support).

---

## 4. Native Modules

### When to Use Native Modules

Use native modules only when JavaScript cannot provide the required
functionality: camera, biometrics, Bluetooth, background tasks, or
performance-critical computation.

### Integration Rules

- Wrap every native module in a TypeScript service layer in `services/`.
  Components never call native APIs directly.
- Handle platform availability gracefully. Check `Platform.OS` and module
  availability before calling native code.
- Prefer well-maintained community modules (`react-native-camera`,
  `react-native-reanimated`, `react-native-mmkv`) over writing custom native
  code.
- When writing custom native modules, use the New Architecture (Turbo Modules
  and Fabric) for type-safe, synchronous calls.

```tsx
// services/biometrics.ts
import ReactNativeBiometrics from "react-native-biometrics";

const biometrics = new ReactNativeBiometrics();

export async function authenticate(): Promise<boolean> {
  const { available } = await biometrics.isSensorAvailable();
  if (!available) return false;

  const { success } = await biometrics.simplePrompt({
    promptMessage: "Confirm identity",
  });
  return success;
}
```

### Native Dependencies Checklist

Before adding a native dependency:
1. Verify it supports both iOS and Android.
2. Verify it supports the New Architecture (Fabric/Turbo Modules).
3. Check maintenance status (last release, open issues).
4. Run `pod install` (iOS) and confirm the Android build succeeds.
5. Test on real devices, not just simulators.

---

## 5. Performance

### Rendering

- **Use `FlatList` for long lists.** Never use `ScrollView` with `.map()` for
  lists of unknown or large length.
- **Provide `keyExtractor` and `getItemLayout`** on `FlatList` for optimal
  scroll performance.
- **Memoize list items.** Wrap list item components in `React.memo` and keep
  their props primitives or stable references.
- **Avoid inline functions in render.** Move callbacks to `useCallback` when
  passed as props to memoized children.

```tsx
// Good: memoized list item with stable callback
const OrderItem = React.memo(function OrderItem({ id, title, onPress }: OrderItemProps) {
  return (
    <Pressable onPress={() => onPress(id)}>
      <Text>{title}</Text>
    </Pressable>
  );
});

function OrderList({ orders }: { orders: Order[] }) {
  const handlePress = useCallback((id: string) => {
    navigation.navigate("OrderDetail", { orderId: id });
  }, [navigation]);

  const renderItem = useCallback(
    ({ item }: { item: Order }) => (
      <OrderItem id={item.id} title={item.title} onPress={handlePress} />
    ),
    [handlePress],
  );

  return (
    <FlatList
      data={orders}
      renderItem={renderItem}
      keyExtractor={(item) => item.id}
    />
  );
}
```

### Bridge and Architecture

- **Minimize bridge crossings.** Batch state updates. Avoid sending large
  JSON payloads across the bridge on every frame.
- **Use `react-native-reanimated` for animations.** Worklet-based animations
  run on the UI thread and avoid bridge overhead entirely.
- **Use `react-native-mmkv` for synchronous storage.** AsyncStorage is slow
  for frequent reads. MMKV provides synchronous, type-safe storage.
- **Enable the New Architecture** (Fabric renderer + Turbo Modules) for
  synchronous native calls and improved rendering performance.
- **Enable Hermes.** Hermes is the default JS engine. Verify it is enabled in
  `android/app/build.gradle` and `ios/Podfile`.

### Images

- Use `react-native-fast-image` for cached, performant image loading.
- Resize images server-side. Do not send full-resolution images to mobile.
- Use `resizeMode="cover"` or `"contain"` explicitly -- do not rely on defaults.

### Startup

- Minimize work in the root component. Defer non-critical initialization.
- Use `react-native-splash-screen` or the built-in splash screen API to
  cover initialization time.
- Lazy-load feature modules that are not needed on the first screen.

---

## 6. Testing

### Unit and Component Tests

**Tools: Jest + React Native Testing Library.**

- Test behavior, not implementation. "When the user taps Submit, the
  `onSubmit` callback fires with form data" -- not "the internal state
  changes to X."
- Use `@testing-library/react-native`. Do not use Enzyme or shallow rendering.
- Query elements by `testID`, role, or text. Prefer accessible queries.
- Mock native modules in `jest.setup.ts` to avoid crashes in the test
  environment.

```tsx
import { render, fireEvent } from "@testing-library/react-native";
import { OrderCard } from "./OrderCard";

test("navigates to order detail on press", () => {
  const onPress = jest.fn();
  const { getByText } = render(
    <OrderCard orderId="123" title="Order #123" onPress={onPress} />,
  );

  fireEvent.press(getByText("Order #123"));
  expect(onPress).toHaveBeenCalledWith("123");
});
```

### End-to-End Tests

**Tool: Detox.**

- E2E tests live in `e2e/` and cover critical user journeys (onboarding,
  login, core transaction flows).
- Run E2E tests on CI against both iOS simulator and Android emulator.
- Keep E2E tests to the minimum set that catches integration failures unit
  tests cannot. They are expensive to run and maintain.
- Use `device.reloadReactNative()` between test suites for a clean state.

```ts
// e2e/login.test.ts
describe("Login flow", () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true });
  });

  it("should log in with valid credentials", async () => {
    await element(by.id("email-input")).typeText("user@example.com");
    await element(by.id("password-input")).typeText("password123");
    await element(by.id("login-button")).tap();
    await expect(element(by.id("home-screen"))).toBeVisible();
  });
});
```

### Device Testing

- Test on real devices before every release. Simulators do not catch
  performance issues, touch responsiveness problems, or native module bugs.
- Maintain a test matrix: minimum supported OS versions for both platforms,
  plus current release.
- Test on low-end devices to catch performance regressions.

---

## 7. Styling

**Approach: `StyleSheet.create` with design tokens.**

- Use `StyleSheet.create` for all styles. It validates styles at compile time
  and enables optimizations.
- Define shared design tokens (colors, spacing, typography) in
  `src/lib/tokens.ts` as plain objects.
- Do not use inline style objects. They create new references every render.

```tsx
// lib/tokens.ts
export const colors = {
  primary: "#007AFF",
  background: "#FFFFFF",
  text: "#1C1C1E",
  border: "#E5E5EA",
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;

// OrderCard.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors, spacing } from "@/lib/tokens";

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
    backgroundColor: colors.background,
    borderRadius: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: "600",
    color: colors.text,
  },
});
```

---

## 8. TypeScript

- **Strict mode enabled.** `"strict": true` in `tsconfig.json`. No exceptions.
- Use `type` over `interface` unless you need declaration merging.
- No `any`. Use `unknown` and narrow with type guards.
- Navigation types are defined in a central `navigation/types.ts` file and
  shared across all navigators and screens.
- Platform-specific types use conditional types or discriminated unions.

---

## Do / Don't

### Do

- Use `FlatList` (or `SectionList`) for all dynamic lists.
- Use `react-native-reanimated` for all animations.
- Use `Pressable` over `TouchableOpacity` for touch targets.
- Use typed navigation hooks -- never pass untyped route params.
- Wrap native modules in TypeScript service layers.
- Test on real devices before every release.
- Use `StyleSheet.create` for all styles.
- Enable Hermes and the New Architecture.
- Use `React.memo` on `FlatList` item components.
- Handle safe areas with `react-native-safe-area-context`.

### Don't

- Don't use `ScrollView` with `.map()` for lists of unknown length.
- Don't call native modules directly from components -- use service wrappers.
- Don't use inline style objects -- they defeat memoization.
- Don't nest navigators more than three levels deep.
- Don't use `AsyncStorage` for frequent reads -- use MMKV.
- Don't skip `pod install` after adding iOS dependencies.
- Don't test only on simulators -- real devices catch different bugs.
- Don't use `Animated` from React Native core -- use Reanimated instead.
- Don't pass complex objects as navigation params -- pass IDs and fetch data
  on the destination screen.
- Don't ignore `Platform.OS` checks when behavior differs between iOS and Android.

---

## Common Pitfalls

1. **ScrollView with `.map()` for long lists.** Renders all items at once,
   causing memory pressure and jank. Use `FlatList` which virtualizes the list
   and only renders visible items.
2. **Inline style objects.** `style={{ padding: 16 }}` creates a new object
   every render, defeating `React.memo` on child components. Move styles to
   `StyleSheet.create`.
3. **Untyped navigation params.** Passing `navigation.navigate("Detail", { id })`
   without typed param lists silently accepts wrong shapes and causes runtime
   crashes when the destination screen reads missing params.
4. **Bridge overhead on animations.** Using the `Animated` API from React Native
   core sends animation frames across the bridge, causing dropped frames.
   `react-native-reanimated` runs animations on the UI thread via worklets.
5. **Missing `keyExtractor` on FlatList.** Without it, React Native uses array
   indices, causing incorrect recycling when items are inserted or removed.
6. **Forgetting `pod install`.** Adding a native dependency on iOS requires
   running `cd ios && pod install`. Builds fail with cryptic linker errors
   when this step is skipped.
7. **Testing only on simulators.** Simulators do not accurately represent
   touch latency, memory constraints, or native module behavior. Performance
   issues that are invisible in the simulator appear on low-end real devices.
8. **Large navigation params.** Passing full objects (user profiles, order data)
   as navigation params serializes them into the navigation state. Pass IDs
   and fetch data on the destination screen instead.

---

## Checklist

Before merging any React Native PR, verify:

- [ ] Components are functional (no class components)
- [ ] TypeScript strict mode enabled, no `any` types
- [ ] Navigation is fully typed with `ParamList` definitions
- [ ] No `ScrollView` + `.map()` for dynamic lists -- `FlatList` used instead
- [ ] `FlatList` items wrapped in `React.memo` with `keyExtractor` provided
- [ ] Animations use `react-native-reanimated`, not the core `Animated` API
- [ ] Native modules wrapped in TypeScript service layers
- [ ] Styles use `StyleSheet.create` -- no inline style objects
- [ ] Tests pass on both iOS and Android (`jest --coverage`)
- [ ] E2E tests cover critical user journeys (Detox)
- [ ] Tested on real devices (not just simulators)
- [ ] `pod install` run after any iOS dependency change
- [ ] No complex objects in navigation params -- IDs only
- [ ] Safe areas handled with `react-native-safe-area-context`
- [ ] Hermes enabled on both platforms
