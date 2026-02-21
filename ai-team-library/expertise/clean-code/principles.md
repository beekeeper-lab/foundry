# Clean Code Principles

Foundational engineering principles that apply to every codebase regardless of
language or framework. These are non-negotiable defaults. Deviations require
explicit justification in a code review comment.

---

## Defaults

- **Readability over cleverness.** Code is read 10x more often than it is written.
  Optimize for the reader.
- **Explicit over implicit.** A reader should understand what code does without
  tracing through multiple indirection layers.
- **Small, focused units.** Functions do one thing. Classes have one reason to change.
  Modules have one responsibility.
- **Tests are first-class code.** Test code follows the same quality standards as
  production code.

---

## Core Principles

### DRY -- Don't Repeat Yourself
Every piece of knowledge has a single, authoritative source. Duplication means
two places to update and one place you will forget.

**But:** Avoid premature DRY. Two similar-looking code blocks with different reasons
to change are not duplication -- they are coincidence. Extract only when you have
three or more instances with the same reason to change.

### KISS -- Keep It Simple, Stupid
The simplest solution that meets the requirements is the best solution. Complexity
is a cost paid on every future change.

### YAGNI -- You Aren't Gonna Need It
Do not build features, abstractions, or extension points for hypothetical future
requirements. Build what is needed now. Refactor when the need is proven.

### SOLID

| Principle                   | One-liner                                           |
|-----------------------------|-----------------------------------------------------|
| **S**ingle Responsibility   | A class has one reason to change.                   |
| **O**pen/Closed             | Open for extension, closed for modification.        |
| **L**iskov Substitution     | Subtypes are substitutable for their base types.    |
| **I**nterface Segregation   | Many specific interfaces beat one general interface.|
| **D**ependency Inversion    | Depend on abstractions, not concrete implementations.|

---

## Do / Don't

- **Do** name things by what they represent, not how they are implemented.
  `user_repository` not `user_db_handler`. `calculate_tax` not `tax_helper`.
- **Do** keep functions under 20 lines. If a function needs a comment explaining a
  section, extract that section into a named function.
- **Do** limit function parameters to 3. Use a data object if more are needed.
- **Do** return early to avoid deep nesting. Guard clauses at the top of a function.
- **Do** write pure functions where possible. Same input always produces same output,
  no side effects.
- **Don't** use abbreviations in names. `calculate_monthly_revenue` not `calc_m_rev`.
- **Don't** use magic numbers or strings. Define named constants.
- **Don't** mix levels of abstraction in a single function. A function should either
  orchestrate high-level steps or perform low-level operations, not both.
- **Don't** write comments that restate the code. Comments explain *why*, code
  explains *what*.

---

## Common Pitfalls

1. **Premature abstraction.** Creating an interface with one implementation "because
   we might need another later." Result: indirection with no benefit. Solution:
   extract the abstraction when the second implementation appears, not before.
2. **God class.** A single class that knows everything and does everything. 2000 lines,
   40 methods, 15 dependencies. Solution: identify distinct responsibilities and
   extract them into focused classes.
3. **Spaghetti dependencies.** Module A depends on B which depends on C which depends
   on A. Circular dependencies make code untestable and changes unpredictable.
   Solution: dependency inversion. Depend on abstractions. Break cycles with events
   or interfaces.
4. **Boolean blindness.** `process_order(order, true, false, true)` -- what do the
   booleans mean? Solution: use named parameters, enums, or distinct functions.
5. **Over-engineering.** Building a plugin system, event bus, and microservice
   architecture for a CRUD app with 3 entities. Solution: start simple. Refactor
   toward complexity only when the code tells you it is needed.

---

## Guard Clause Pattern

```python
# Bad: deep nesting
def process_payment(order):
    if order is not None:
        if order.status == "pending":
            if order.total > 0:
                charge(order)
                return "success"
            else:
                return "invalid_total"
        else:
            return "not_pending"
    else:
        return "no_order"

# Good: early returns flatten the logic
def process_payment(order):
    if order is None:
        return "no_order"
    if order.status != "pending":
        return "not_pending"
    if order.total <= 0:
        return "invalid_total"

    charge(order)
    return "success"
```

---

## Single Responsibility Example

```python
# Bad: one class doing validation, persistence, and notification
class OrderService:
    def create_order(self, data):
        # 20 lines of validation
        # 15 lines of database writes
        # 10 lines of email sending
        pass

# Good: each responsibility in its own unit
class OrderValidator:
    def validate(self, data) -> ValidationResult: ...

class OrderRepository:
    def save(self, order: Order) -> None: ...

class OrderNotifier:
    def notify_created(self, order: Order) -> None: ...

class OrderService:
    def __init__(self, validator, repository, notifier):
        self.validator = validator
        self.repository = repository
        self.notifier = notifier

    def create_order(self, data):
        result = self.validator.validate(data)
        if not result.is_valid:
            raise ValidationError(result.errors)
        order = Order.from_data(data)
        self.repository.save(order)
        self.notifier.notify_created(order)
        return order
```

---

## The Testing Pyramid

```
        /  E2E  \          Few, slow, expensive
       /----------\
      / Integration \      Moderate count, moderate speed
     /----------------\
    /    Unit Tests     \  Many, fast, cheap
   /____________________\
```

- **Unit tests (70%):** Test individual functions and classes in isolation.
- **Integration tests (20%):** Test interactions between components (DB, APIs).
- **E2E tests (10%):** Test complete user journeys through the running system.

---

## Checklist

- [ ] Functions are under 20 lines and do one thing
- [ ] Function parameters are 3 or fewer
- [ ] No magic numbers or strings -- named constants are used
- [ ] Guard clauses replace deep nesting
- [ ] Names describe intent, not implementation
- [ ] No circular dependencies between modules
- [ ] Comments explain *why*, not *what*
- [ ] Each class has a single reason to change
- [ ] Pure functions are preferred over stateful methods
- [ ] The testing pyramid is followed (many unit, few E2E)
