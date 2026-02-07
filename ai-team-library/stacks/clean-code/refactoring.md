# Refactoring

Standards for when, why, and how to refactor code. Refactoring is changing the
internal structure of code without changing its external behavior. It is a
disciplined practice, not a euphemism for rewriting.

---

## Defaults

- **Precondition:** Adequate test coverage exists before refactoring begins.
  If tests are missing, write them first.
- **Scope:** Refactor in small, verifiable steps. Each step is a commit that
  passes all tests. No "big bang" refactors that touch 50 files in one commit.
- **Trigger:** Refactoring is triggered by a concrete need (the code needs to
  change, and its current structure makes the change hard), not by aesthetic
  preference.
- **Boy Scout Rule:** Leave the code a little better than you found it. Small
  improvements during feature work compound over time.

---

## When to Refactor (Triggers)

| Trigger                         | Signal                                          |
|---------------------------------|-------------------------------------------------|
| **Rule of Three**               | You are about to duplicate logic a third time.  |
| **Preparatory refactoring**     | The current structure makes a planned change hard.|
| **Comprehension refactoring**   | You had to read a function three times to understand it.|
| **Performance refactoring**     | Profiling identified a specific bottleneck.      |
| **Code review feedback**        | A reviewer flags a design smell.                 |
| **Test difficulty**             | Writing a test requires extensive mocking or setup.|

When **not** to refactor:
- The code works, is rarely changed, and is well-tested. Leave it alone.
- You are under deadline pressure with no test coverage. Fix the deadline or
  write tests first.
- You are about to replace the component entirely. Refactoring doomed code is waste.

---

## Do / Don't

- **Do** refactor in a separate commit (or PR) from feature changes. Mixing
  behavior changes with structural changes makes review and debugging harder.
- **Do** run tests after every small step. If a test fails, undo the last step.
- **Do** use automated refactoring tools in your IDE. Rename, extract, inline,
  and move operations are safer when tool-assisted.
- **Do** communicate refactoring intent in the commit message. "Refactor: extract
  OrderValidator from OrderService" not "cleanup."
- **Do** measure complexity before and after. Refactoring should reduce measurable
  complexity (cyclomatic, coupling, line count).
- **Don't** refactor without tests. You will introduce bugs you cannot detect.
- **Don't** refactor and change behavior in the same step. One or the other.
- **Don't** chase perfection. Good enough and well-tested beats perfect and late.
- **Don't** refactor code you do not understand. Read it, test it, then refactor it.
- **Don't** refactor everything at once. Pick the highest-impact smell and address it.

---

## Common Pitfalls

1. **Refactoring without tests.** The most common and most costly mistake. You
   restructure a function and silently change its behavior. Nobody notices until
   production breaks. Solution: characterization tests capture existing behavior
   before you touch anything.
2. **Big-bang refactors.** "Let's redesign the whole module this sprint." It drags
   on for weeks, creates merge conflicts, and ships bugs. Solution: strangler fig
   pattern -- build the new structure alongside the old, migrate incrementally,
   delete the old when it is empty.
3. **Refactoring as procrastination.** Polishing code instead of delivering the
   feature. Solution: timebox refactoring. The Boy Scout Rule means 15 minutes of
   improvement, not a 3-day detour.
4. **No measurable improvement.** The code is "cleaner" by opinion but complexity
   metrics are the same. Solution: define success criteria before starting.
   "Reduce OrderService from 400 lines to under 100" is measurable.
5. **Refactoring public APIs without coordination.** Internal refactoring is safe.
   Changing function signatures, removing parameters, or renaming public methods
   breaks consumers. Solution: use deprecation warnings and migration periods
   for public API changes.

---

## Key Refactoring Techniques

### Extract Function
The most common and most valuable refactoring. Take a block of code and move it
into a named function.

```python
# Before: mixed levels of abstraction
def process_order(order):
    # validate
    if not order.items:
        raise ValueError("Empty order")
    if order.total <= 0:
        raise ValueError("Invalid total")
    # save
    db.execute("INSERT INTO orders ...", order.to_dict())
    # notify
    email_service.send(order.customer_email, "Order confirmed", render_template(order))

# After: each step is a named function
def process_order(order):
    validate_order(order)
    save_order(order)
    notify_customer(order)

def validate_order(order):
    if not order.items:
        raise ValueError("Empty order")
    if order.total <= 0:
        raise ValueError("Invalid total")

def save_order(order):
    db.execute("INSERT INTO orders ...", order.to_dict())

def notify_customer(order):
    email_service.send(order.customer_email, "Order confirmed", render_template(order))
```

### Replace Conditional with Polymorphism
When a `switch` or `if/elif` chain selects behavior based on a type field,
replace it with polymorphism.

```python
# Before: type-checking conditional
def calculate_area(shape):
    if shape.type == "circle":
        return math.pi * shape.radius ** 2
    elif shape.type == "rectangle":
        return shape.width * shape.height
    elif shape.type == "triangle":
        return 0.5 * shape.base * shape.height

# After: polymorphism
class Circle:
    def area(self) -> float:
        return math.pi * self.radius ** 2

class Rectangle:
    def area(self) -> float:
        return self.width * self.height

class Triangle:
    def area(self) -> float:
        return 0.5 * self.base * self.height
```

### Introduce Parameter Object
Group related parameters into a single object.

### Replace Magic Number with Named Constant
Give meaning to literal values.

### Move Method
Move a method to the class that owns the data it operates on.

### Strangler Fig (for large refactors)
1. Build the new implementation alongside the old.
2. Route new callers to the new implementation.
3. Migrate existing callers incrementally.
4. Delete the old implementation when no callers remain.

---

## Refactoring Workflow

```
1. Identify the smell (code review, metrics, difficulty writing a test)
2. Write characterization tests if coverage is insufficient
3. Plan the refactoring (target structure, success criteria)
4. Execute in small steps, running tests after each step
5. Commit each step separately with a descriptive message
6. Measure: did complexity decrease? Is the test easier to write now?
7. Open a focused PR: refactoring only, no behavior changes
```

---

## Alternatives

| Tool / Resource             | Use case                                       |
|-----------------------------|-------------------------------------------------|
| IDE refactoring tools       | Automated rename, extract, inline, move         |
| rope (Python)               | Python-specific refactoring library              |
| jscodeshift (JavaScript)    | Large-scale automated JS/TS code transformations |
| Sourcegraph                 | Find all usages across repos before renaming     |
| Martin Fowler's catalog     | Comprehensive reference for refactoring patterns |

---

## Checklist

- [ ] Test coverage is adequate before refactoring begins
- [ ] Refactoring is in a separate commit/PR from behavior changes
- [ ] Each refactoring step is small enough to verify independently
- [ ] Tests pass after every step
- [ ] Commit messages describe the structural change clearly
- [ ] Complexity metrics are measured before and after
- [ ] IDE refactoring tools are used for rename, extract, and move operations
- [ ] Large refactors use the strangler fig approach (incremental migration)
- [ ] No public API changes without deprecation warnings
- [ ] The refactoring addresses a specific, identified smell (not aesthetic preference)
