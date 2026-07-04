---
id: clean-code
category: Architecture & Patterns
entry: true
last-reviewed: 2026-07
---

# Clean Code Conventions

## Category
Architecture & Patterns

These conventions are language-agnostic rules for day-to-day coding. They
complement `principles.md` (the *why*) by spelling out the *what* and *when* --
the concrete decisions a developer makes dozens of times per hour. Deviations
require explicit justification in code review.

---

## Defaults

| Concern                          | Default                                                | Alternatives                                          |
|----------------------------------|--------------------------------------------------------|-------------------------------------------------------|
| Identifier length                | Descriptive; favor clarity over brevity                | Single-letter only for tight loop indices / math      |
| Function length                  | ~20 lines; one screenful without scrolling             | Longer if the function is a flat sequence of steps    |
| Function responsibility          | One level of abstraction per function                  | —                                                     |
| Public-function parameters       | 0–3; group into a value object beyond that             | Builder pattern for complex construction              |
| Comment purpose                  | Explain *why* (intent, constraints), never *what*      | Public-API docstrings describe contract, not intent   |
| Error handling                   | Fail fast at boundaries; let unexpected errors bubble  | Caller-side recovery only when domain-meaningful      |
| Test naming                      | `test_<unit>_<scenario>_<expected>` or `it_*_when_*`   | BDD `given/when/then` blocks for integration suites   |
| Refactoring cadence              | Continuous — Boy-Scout Rule on every touched file      | Dedicated refactor branches only for large reshapes   |
| Commit size                      | One logical change per commit; buildable at every step | Squash-merge preserves logical-change history in main |
| Review size                      | < 400 lines diff where possible                        | Split by concern: behavior, tests, formatting         |

---

## 1. Naming

**Rule:** a name should answer *what is this and why does it exist* without
requiring the reader to open the definition.

- **Variables / parameters:** noun phrases. `pending_orders`, `retry_limit`,
  `user_email`. Avoid generic names (`data`, `info`, `obj`, `temp`, `result`)
  unless scoped to a 3-line block where the meaning is obvious.
- **Functions:** verb phrases describing the effect. `send_invoice`,
  `parse_config`, `is_eligible`. Boolean accessors start with `is_`, `has_`,
  `should_`. Side-effecting functions start with a verb that names the effect
  (`persist_*`, `emit_*`, `notify_*`).
- **Classes / types:** singular nouns. `Order`, `PaymentGateway`,
  `RetryPolicy`. Resist `*Manager`, `*Helper`, `*Util` suffixes — they
  advertise that the class has no cohesive responsibility.
- **Constants:** `UPPER_SNAKE` (or the language's established idiom). Include
  units in the name when units matter: `TIMEOUT_MS`, `MAX_BATCH_BYTES`.
- **Booleans:** express a positive statement. Use `is_enabled`, not
  `is_not_disabled`. Negated flags invert the reader's reasoning.
- **Abbreviations:** only widely-understood ones (`url`, `id`, `db`, `json`).
  Otherwise spell it out. `cfg`, `mgr`, `ctx` (outside tight scopes) belong in
  the dustbin.

Rename aggressively. Renaming is usually a one-command refactor with full IDE
support; unclear names compound forever.

---

## 2. Comments and Documentation

**Rule:** the code is the truth. Comments are for intent, constraints, and
surprises the code cannot express.

- **Write a comment when:** a decision is non-obvious (cite the ticket,
  benchmark, or incident), a workaround exists for an external bug, an
  invariant must hold for correctness, or a performance choice overrides the
  obvious structure.
- **Do not write a comment that restates the code.** `// increment counter`
  above `counter += 1` is noise that rots when the code changes.
- **Public-API docstrings** describe the contract: parameters, return shape,
  raised errors, side effects. They do not describe the implementation.
- **`TODO` / `FIXME`** must include an owner and a ticket link. Orphan TODOs
  become permanent archaeological layers. Prefer filing a ticket and deleting
  the TODO.
- **Commit messages** are first-class documentation. The subject line states
  the change; the body states the motivation. Future-you will read these,
  often during an incident.

---

## 3. Function Size and Responsibility

**Rule:** a function does one thing, at one level of abstraction, and its
name fully describes that thing.

- Target ~20 lines. When a function exceeds a screenful, the usual cause is
  multiple responsibilities: extract helpers whose names narrate the steps.
- Keep a single level of abstraction per function. If a function mixes
  high-level coordination (`charge_customer(...)`) with low-level mechanics
  (byte-shuffling, SQL string building), extract the low level.
- Prefer pure functions where possible. A pure function is trivial to test,
  reason about, and reuse.
- Limit parameters to three. Beyond that, introduce a value object or
  builder. Long parameter lists hide structure and make call sites unreadable.
- Return values, don't mutate parameters, unless mutation is the documented
  point of the function (e.g., a sort-in-place).
- Avoid output parameters and boolean "mode" flags — each flag usually means
  two functions fighting to share one body.

---

## 4. Error Handling

**Rule:** errors are a feature of the domain, not an afterthought.

- **Validate at boundaries.** Parse external input (HTTP, CLI, files, queues)
  into trusted domain types at the edge; interior code assumes validity.
- **Fail fast** on programmer errors (nulls where values are required,
  impossible states). Do not paper over bugs with default values.
- **Catch narrowly.** Catch the specific exception type you can recover
  from. Bare `except` / `catch (Exception)` swallows bugs.
- **Preserve the cause chain.** Use `raise X from err` / `throw new X(msg,
  {cause: err})` / equivalent. Stack traces are evidence.
- **Distinguish expected from unexpected.** Expected failures (invalid user
  input, payment declined) are part of the happy-path API surface; unexpected
  failures log, alert, and bubble to a top-level handler that returns a
  sanitized response.
- **Never log and re-raise.** Pick one. Double-logging turns one incident
  into N duplicated noise entries.

---

## 5. Testing

**Rule:** tests describe behavior, not implementation. A rename or refactor
should not rewrite the test.

- **Name tests by behavior:** `test_refund_credits_original_payment_method`,
  not `test_refund_1`. The test name is the first documentation a future
  developer reads.
- **Arrange / Act / Assert** with blank-line separators. One logical assertion
  per test (not necessarily one `assert` call — one *concept*).
- **Test at the right layer.** Unit tests cover branching logic on small
  surfaces; integration tests cover the contract with external systems using
  real dependencies (containers, in-memory databases). Mock only at owned
  seams — do not mock libraries or the language's standard library.
- **No shared mutable state between tests.** Fixtures produce fresh instances;
  `setUp`/`tearDown` that mutates module-level state is a flaky test waiting
  to happen.
- **Cover the edge, not just the middle.** Empty inputs, boundary values,
  unicode, timezone flips, concurrent access where relevant.
- **Treat test code like production code.** Refactor duplicated setup into
  fixtures / factories. Fix flakes the day they appear.

---

## 6. Refactoring Cadence

**Rule:** refactor continuously, in small commits, alongside the feature
work that motivates it.

- **Boy-Scout Rule:** leave the file cleaner than you found it. A small
  rename, an extracted helper, a deleted dead branch — each touch pays down a
  tiny bit of entropy.
- **Separate refactor commits from behavior commits.** A commit that both
  moves code and changes what it does hides the review target. Land the
  mechanical refactor first (reviewer checks nothing changed), then land the
  behavior change (reviewer focuses on semantics).
- **Refactor before, not during, a feature.** When a feature is awkward to
  add, the code is telling you the shape is wrong. Refactor to the shape that
  makes the feature easy, *then* add it.
- **Delete mercilessly.** Dead code, unused flags, orphan tests, stale
  fixtures. Version control remembers; your head does not need to.
- **Avoid big-bang rewrites.** Strangler-fig refactors (replace piece by
  piece behind an interface) beat rewrites nine times out of ten.

---

## Precedence

When this pack's generic guidance conflicts with a language or framework
pack selected in the same composition, the **language pack wins** — idiom
beats generality (e.g. Dart's camelCase constants over UPPER_SNAKE).

## Do / Don't

**Do:**
- Name things after *what they are* and *why they exist*.
- Keep functions small, single-purpose, and at one level of abstraction.
- Write comments that explain *why*; let names explain *what*.
- Fail fast at boundaries; catch narrowly; preserve cause chains.
- Name tests after observable behavior, not implementation.
- Refactor in small commits alongside the work that motivates it.
- Delete dead code the moment you notice it.

**Don't:**
- Use generic names (`data`, `info`, `tmp`, `manager`) outside a 3-line scope.
- Write comments that restate what the code already says.
- Write 200-line functions with nested conditionals and boolean mode flags.
- Catch broad exception types to "be safe."
- Mock your way around a slow or flaky integration test.
- Schedule refactoring as a standalone quarterly project — do it daily.
- Leave orphan `TODO` / `FIXME` markers without an owner and ticket link.

---

## Common Pitfalls

1. **"I'll rename it later."** Later never comes. Renaming is cheap with IDE
   support; unclear names compound across every subsequent read.

2. **Comments as apologies.** A comment explaining why a 400-line function is
   confusing is not a fix. Extract the helpers; delete the apology.

3. **Mocking what you don't own.** Tests that mock a library lock in today's
   understanding of that library's behavior. When the library changes, the
   mock silently lies. Mock at the seams you own; use the real dependency (or
   a faithful fake) at owned seams you don't.

4. **Boolean "mode" parameters.** `send_email(to, subject, body, dry_run=True)`
   is two functions wearing one coat. Split into `send_email` and
   `render_email`.

5. **Catching `Exception` to avoid crashes.** A catch-all swallows the stack
   trace of the *one* bug you needed to see. Crash loudly in development;
   catch narrowly in production at the request/job boundary only.

6. **Refactor-as-side-quest.** Mixing a rename, a restructure, and a behavior
   change in one diff makes review impossible. Land each in its own commit
   (or PR) so the reviewer can focus.

7. **Dead code kept "just in case."** Dead code has a maintenance cost
   (compilers type-check it, linters scan it, readers read it) and zero
   value. Version control remembers; delete it.

8. **One-assertion dogma.** The rule is one *concept* per test, not one
   `assert` call. Asserting three fields of one returned object is one
   concept; asserting a side effect and a return value is two.

---

## Checklist

- [ ] Every identifier names *what it is* and *why it exists* without
      requiring the reader to open the definition.
- [ ] No generic names (`data`, `info`, `tmp`, `manager`, `util`) outside a
      3-line scope.
- [ ] Public functions have 0–3 parameters; anything larger uses a value
      object.
- [ ] No function exceeds one screenful without a *why* comment at the top.
- [ ] Comments explain intent, constraints, or surprises — not what the code
      already says.
- [ ] Every `TODO` / `FIXME` has an owner and a ticket link.
- [ ] External input is validated at the boundary into trusted domain types.
- [ ] No bare `catch (Exception)` / `except:` outside a top-level boundary
      handler.
- [ ] Errors preserve cause chains (`raise ... from err` / equivalent).
- [ ] Tests are named by behavior; no `test_1`, `test_foo_works`.
- [ ] No shared mutable state between tests; fixtures produce fresh
      instances.
- [ ] Dead code, unused flags, and orphan tests deleted when noticed.
- [ ] Refactor and behavior changes land in separate commits.
