# Vue Testing

Testing conventions for Vue 3 projects using Vitest and Vue Test Utils.
Companion to `conventions.md`.

---

## Philosophy

- Test components through their public contract: rendered output, emitted
  events, and user interactions. Do not assert on internal refs, computed
  values, or method calls — those are implementation details that make
  refactors break green tests.
- Prefer fewer, behavior-shaped tests over many micro-assertions. A test
  named "emits select when a row is clicked" survives a rewrite of the
  component internals; "sets selectedIndex to 2" does not.
- The unit under test is usually a component *plus* its child presentation
  components. Shallow rendering hides real integration bugs; stub only the
  expensive or irrelevant (charts, editors, router views).
- Run tests in a fast DOM environment (`environment: 'jsdom'` or
  `happy-dom` in `vitest.config.ts`). Reserve real-browser testing for a
  thin end-to-end layer (Playwright/Cypress) outside the unit suite.

---

## Component Testing Patterns

Mount, interact, assert on output:

```ts
import { mount } from '@vue/test-utils'
import UserList from './UserList.vue'

it('emits select with the clicked user', async () => {
  const users = [{ id: 1, name: 'Ada' }, { id: 2, name: 'Grace' }]
  const wrapper = mount(UserList, { props: { users } })

  await wrapper.get('[data-testid="user-2"]').trigger('click')

  expect(wrapper.emitted('select')).toEqual([[users[1]]])
})
```

**Rules:**

- Select elements with `data-testid` attributes or accessible roles/text,
  not CSS classes — classes change for styling reasons.
- Always `await` interactions (`trigger`, `setValue`, `setProps`) so the
  DOM reflects the update before you assert. When mutating reactive state
  directly, `await nextTick()` (or `flushPromises()` after async work).
- Assert emitted events with `wrapper.emitted('event-name')`, including
  payloads. This is the component's output contract.
- Test props by mounting with different `props` and asserting rendered
  differences — not by reading `wrapper.vm`.
- For `defineModel`/`v-model` components, pass `modelValue` plus an
  `'onUpdate:modelValue'` handler (or assert the emitted update event).
- Global concerns (plugins, stubs, provides) go in `mountOptions.global`:

  ```ts
  mount(Comp, {
    global: {
      plugins: [createTestingPinia()],
      stubs: { RouterLink: true },
      provide: { [themeKey as symbol]: fakeTheme },
    },
  })
  ```

- Components using the router: in unit tests, stub `RouterLink` and mock
  `useRouter`/`useRoute` (`vi.mock('vue-router')`) rather than wiring a
  real router. Use a real memory-history router only in integration-style
  tests that assert navigation.

---

## Testing Composables

- A composable that uses no lifecycle hooks or provide/inject is a plain
  function — call it directly in the test and assert on the returned refs.
- A composable that registers lifecycle hooks or injections needs a host
  component. Use a tiny inline harness:

  ```ts
  import { defineComponent } from 'vue'
  import { mount } from '@vue/test-utils'

  function withSetup<T>(composable: () => T) {
    let result!: T
    const wrapper = mount(defineComponent({
      setup() {
        result = composable()
        return () => null
      },
    }))
    return { result, wrapper }
  }

  it('cleans up its interval on unmount', () => {
    vi.useFakeTimers()
    const { wrapper } = withSetup(() => usePolling(fetcher, 1000))
    wrapper.unmount()
    vi.advanceTimersByTime(5000)
    expect(fetcher).not.toHaveBeenCalled()
  })
  ```

- Always test the cleanup path (unmount) for composables that own timers,
  listeners, or subscriptions — leaks are their most common defect.
- Drive time with `vi.useFakeTimers()`; never real sleeps in unit tests.

---

## Testing Pinia Stores

Two distinct layers — keep them separate:

**1. The store itself.** Instantiate a fresh Pinia per test and exercise the
real store logic:

```ts
import { setActivePinia, createPinia } from 'pinia'

beforeEach(() => setActivePinia(createPinia()))

it('applies a discount to the total', () => {
  const cart = useCartStore()
  cart.add({ id: 1, price: 100 })
  cart.applyDiscount(0.1)
  expect(cart.total).toBe(90)
})
```

Mock only the store's external edges (API clients), not the store.

**2. Components that use stores.** Use `createTestingPinia` from
`@pinia/testing` so actions are auto-stubbed and initial state is injectable:

```ts
mount(Checkout, {
  global: {
    plugins: [createTestingPinia({
      initialState: { cart: { items: [item] } },
      stubActions: true,
    })],
  },
})
expect(useCartStore().submit).toHaveBeenCalledOnce()
```

Assert that the component *called* the action with the right arguments;
the action's behavior is already covered by the store's own tests.

---

## Do / Don't

**Do:**
- Query by `data-testid`, role, or visible text.
- `await` every interaction; use `flushPromises()` after mocked async calls.
- Give each test a fresh Pinia (`setActivePinia` or `createTestingPinia`).
- Use fake timers for anything time-based.
- Keep a small e2e layer for real-browser flows; keep the unit suite fast.

**Don't:**
- Assert on `wrapper.vm` internals or private refs.
- Use `shallowMount` as the default — stub selectively instead.
- Share Pinia or module-level state across tests.
- Re-test store logic through every component that touches the store.
- Snapshot entire component trees as a substitute for targeted assertions.

---

## Checklist

- [ ] `vitest.config.ts` uses the project's Vite config and a DOM environment
- [ ] Component tests assert rendered output and emitted events only
- [ ] Selectors use `data-testid`/roles/text, not styling classes
- [ ] Composables with lifecycle hooks tested via a host-component harness
- [ ] Composable cleanup (unmount) paths covered
- [ ] Store logic tested on fresh Pinia instances with mocked API edges
- [ ] Component-store interaction tested with `createTestingPinia`
- [ ] Fake timers for polling/debounce; no real sleeps
- [ ] Suite runs headless and green in CI
