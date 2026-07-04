---
id: vue
category: Frameworks
applies_to:
  - developer
  - tech-qa
  - architect
entry: true
last-reviewed: 2026-07
---

# Vue Conventions

## Category
Frameworks

These conventions target Vue 3 (3.4+) with the Composition API. They are the
non-negotiable defaults for Vue projects on this team. Deviations require an
ADR with justification. The Options API is legacy: maintain it where it exists,
do not write new code in it.

---

## Defaults

| Concern            | Default Tool / Approach                          |
|--------------------|--------------------------------------------------|
| Vue version        | Vue 3.4+ (Composition API only for new code)     |
| Component authoring| SFCs with `<script setup lang="ts">`             |
| Language           | TypeScript (strict)                              |
| State management   | Pinia (setup-store syntax)                       |
| Build tool         | Vite                                             |
| Routing            | vue-router 4                                     |
| Testing            | Vitest + Vue Test Utils                          |
| Lint               | ESLint flat config + `eslint-plugin-vue`         |
| Formatting         | Prettier (or ESLint stylistic) — pick one, in CI |

---

## 1. SFC Structure and Composition API Discipline

- Block order in every SFC: `<script setup>`, then `<template>`, then `<style scoped>`.
- Component files are `PascalCase.vue`; use multi-word names (`UserCard.vue`,
  not `Card.vue`) to avoid colliding with future HTML elements.
- Inside `<script setup>`, keep a consistent order: imports, props/emits/models,
  composables, local state, computed, watchers, functions, lifecycle hooks.
- Keep components small. When a component grows past roughly 200 lines of
  script, extract logic into composables or split the component.
- `<style>` blocks are `scoped` by default. Global styles live in dedicated
  stylesheet files, not in component SFCs.
- No logic in templates beyond simple expressions. Anything with a ternary
  inside a ternary becomes a `computed`.

---

## 2. Composables

- Composables live in `composables/` (or a feature folder), are named
  `useThing.ts`, and export a single `useThing()` function.
- A composable returns an object of refs and functions — never a `reactive`
  object, which loses reactivity when destructured by the caller.
- Composables that register lifecycle hooks or `watch` must be called
  synchronously during `setup()`, not inside callbacks or `await` continuations.
- Accept refs or getters as arguments and normalize with `toValue()` so
  callers can pass plain values, refs, or `() => value`.
- A composable owns its cleanup: clear timers, abort fetches, and remove
  listeners in `onScopeDispose`/`onUnmounted`.

---

## 3. State with Pinia

- Use setup-store syntax: `defineStore('cart', () => { ... })` returning
  state refs, computeds (getters), and functions (actions).
- Store IDs are unique kebab-case or camelCase strings; store files are
  `stores/<name>.ts` exporting `use<Name>Store`.
- Never destructure reactive state directly from a store instance — use
  `storeToRefs(store)` for state/getters; actions can be destructured freely.
- Local component state stays local. Promote to a Pinia store only when
  state is shared across routes or unrelated component trees.
- Server data belongs in a data-fetching layer (composable or query library),
  not mirrored wholesale into Pinia. Pinia holds client/UI state and
  cross-cutting session state.

---

## 4. Reactivity Rules

- Default to `ref()` for all reactive state, including objects. Use
  `reactive()` only for a stable, never-reassigned object whose identity you
  control — and never destructure it.
- Deriving state? Use `computed()`. Never manually sync one ref from another
  with a watcher when a computed expresses the same relationship.
- `watch` with an explicit source for targeted side effects; `watchEffect`
  only for effects whose dependency set is genuinely dynamic. Prefer `watch`
  when in doubt — implicit dependency tracking hides bugs.
- Watch reactive-object properties via a getter: `watch(() => obj.prop, ...)`.
  Passing `obj.prop` directly passes a plain value and never fires.
- Mutate arrays and objects in place or replace `ref.value` wholesale; both
  are fine. What is not fine is holding a stale destructured copy.

---

## 5. Component Communication and Typing

- Props down, events up. Type both with the generic type-only syntax:

  ```ts
  const props = defineProps<{ items: Item[]; dense?: boolean }>()
  const emit = defineEmits<{ select: [item: Item]; close: [] }>()
  ```

- Use `withDefaults` (or 3.5 reactive-props-destructure where adopted
  project-wide) for prop defaults — pick one style per project.
- Two-way bindings use `defineModel<T>()`, not hand-rolled
  `modelValue`/`update:modelValue` pairs.
- Never mutate props. If a child needs to change a value, emit an event or
  use `defineModel`.
- Reach for provide/inject only for genuine subtree-wide context (theme,
  form context), always with an `InjectionKey<T>` for type safety.
  Cross-tree communication goes through Pinia, not an event bus.

---

## 6. Routing

- Routes are typed and named; navigate with `{ name: 'user-detail', params }`,
  not string paths, so refactors don't silently break links.
- Lazy-load route components: `component: () => import('./views/UserDetail.vue')`.
- Route params arrive as strings — parse and validate them at the view
  boundary, not deep in child components.
- Auth and permission checks live in navigation guards (`router.beforeEach`
  or per-route `beforeEnter`), not scattered through components.
- Views (route targets) live in `views/` or `pages/` and stay thin: they wire
  route params to feature components and own page-level data loading.

---

## Do / Don't

**Do:**
- Write all new components as `<script setup lang="ts">` SFCs.
- Default to `ref()`; reach for `reactive()` only with documented reason.
- Use `storeToRefs()` when pulling state out of a Pinia store.
- Type props and emits with the generic type-only declarations.
- Use `computed()` for derived state instead of watcher-synced refs.
- Use `key` with stable IDs in `v-for` — never the array index for mutable lists.
- Clean up side effects in composables (`onScopeDispose`, `AbortController`).

**Don't:**
- Mix Options API into new code, or mix `this` into `<script setup>`.
- Destructure `reactive()` objects or store instances and expect reactivity.
- Put `v-if` and `v-for` on the same element.
- Mutate props in a child component.
- Use `watchEffect` for what an explicit `watch` source expresses better.
- Build a global event bus — use Pinia or provide/inject.
- Fetch data in deeply nested components; own it at the view or composable layer.

---

## Common Pitfalls

1. **`reactive()` misuse.** `const { count } = reactive({ count: 0 })` gives a
   dead plain number. Same for spreading (`...state`) into another object.
   Default to `ref()`; if you must share a reactive object, pass the object
   itself or convert with `toRefs()`.

2. **Losing reactivity via store destructuring.** `const { user } = useAuthStore()`
   silently disconnects `user` from the store. Always `storeToRefs(store)`
   for state and getters.

3. **`watch` on a plain property.** `watch(obj.prop, cb)` passes the current
   value, not a source, and never fires. Use a getter: `watch(() => obj.prop, cb)`.

4. **`watchEffect` over-firing.** Because it tracks everything it touches,
   an incidental read (e.g. logging another ref) adds a hidden trigger.
   Effects that fetch on change should use `watch` with explicit sources.

5. **`v-if` with `v-for` on one element.** In Vue 3, `v-if` evaluates first
   and cannot see the loop variable. Filter in a `computed`, or move `v-if`
   to a wrapping `<template>` element.

6. **Index as `v-for` key on mutable lists.** Reorders and deletions reuse
   the wrong DOM/component state. Use a stable unique ID.

7. **Async setup without a plan.** Code after `await` in `<script setup>`
   runs outside the sync setup window; lifecycle hooks registered there are
   lost, and the component needs `<Suspense>`. Prefer fetching in a
   composable with `onMounted` or a query library unless Suspense is a
   deliberate, project-wide choice.

---

## Checklist

- [ ] All new components use `<script setup lang="ts">`
- [ ] ESLint flat config with `eslint-plugin-vue` passing in CI
- [ ] State defaults to `ref()`; every `reactive()` has a justification
- [ ] No destructuring of reactive objects or store instances (use `storeToRefs`)
- [ ] Props/emits typed via generic declarations; two-way via `defineModel`
- [ ] Derived state uses `computed`, not watcher-synced refs
- [ ] `watch` sources are refs or getters; `watchEffect` used sparingly
- [ ] No `v-if` + `v-for` on the same element; stable `v-for` keys
- [ ] Route components lazy-loaded; params validated at the view boundary
- [ ] Composables clean up their side effects
- [ ] Vitest + Vue Test Utils suite green in CI (see `testing.md`)
