# Anti-Patterns and Code Smells

A catalog of recurring bad practices and the code smells that signal them.
Recognizing these patterns is the first step toward better code. Based on
Martin Fowler's refactoring catalog and common industry experience.

---

## Defaults

- **Response to a smell:** Investigate, not panic. A code smell is a hint, not a
  conviction. Context determines whether action is needed.
- **Severity classification:** Smells that affect correctness are fixed immediately.
  Smells that affect maintainability are tracked and addressed during refactoring
  windows.
- **Detection:** Automated where possible (linters, complexity metrics). Human
  judgment for structural and design smells.

---

## Code Smells (Implementation Level)

### Long Method
A function exceeding 20-30 lines that requires scrolling to understand.

**Symptom:** Comments separating "sections" within a function.
**Fix:** Extract each section into a named function. The function name replaces
the comment.

### Long Parameter List
A function with more than 3 parameters.

**Symptom:** Callers frequently pass `None` or default values for unused parameters.
**Fix:** Introduce a parameter object (data class / struct) that groups related
parameters.

```python
# Smell: too many parameters
def create_user(name, email, phone, address, city, state, zip_code, country):
    ...

# Fix: parameter object
@dataclass
class UserProfile:
    name: str
    email: str
    phone: str
    address: Address

def create_user(profile: UserProfile):
    ...
```

### Magic Numbers and Strings
Literal values embedded in logic with no explanation.

```python
# Smell
if retries > 3:
    sleep(86400)

# Fix
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 86400

if retries > MAX_RETRIES:
    sleep(RETRY_BACKOFF_SECONDS)
```

### Feature Envy
A method that uses more data from another class than from its own.

**Fix:** Move the method to the class whose data it actually uses.

### Shotgun Surgery
A single change requires editing many files across the codebase.

**Fix:** Consolidate the scattered logic into a single module or class.

---

## Code Smells (Design Level)

### God Class / Blob
One class that handles too many responsibilities. Typically 500+ lines, 20+
methods, 10+ dependencies.

**Symptom:** Every new feature touches this class. Tests for this class are slow
and brittle.
**Fix:** Identify distinct responsibilities. Extract each into its own class.
Use composition in the original class to delegate.

### Primitive Obsession
Using primitive types (strings, ints) to represent domain concepts.

```python
# Smell: email is just a string -- no validation, easy to mix up with other strings
def send_invoice(email: str, amount: float, currency: str): ...

# Fix: domain types enforce constraints
@dataclass(frozen=True)
class Email:
    value: str
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

def send_invoice(email: Email, total: Money): ...
```

### Inappropriate Intimacy
Two classes that know too much about each other's internals, accessing private
fields or relying on implementation details.

**Fix:** Define a clean public interface. If two classes are deeply coupled,
consider merging them or introducing a mediator.

### Speculative Generality
Abstractions, interfaces, parameters, and extension points built for requirements
that do not exist yet.

**Symptom:** A `PluginManager` with one plugin. A `StrategyFactory` with one strategy.
Unused method parameters "for future use."
**Fix:** Delete it. Re-add it when (if) the need materializes.

---

## Architectural Anti-Patterns

### Spaghetti Architecture
No clear module boundaries. Any component calls any other component. The dependency
graph is a tangled web.

**Fix:** Define module boundaries. Enforce dependency rules (inner modules do not
depend on outer modules). Use a linter or architecture test to detect violations.

### Big Ball of Mud
The entire application is one deployment unit with no internal structure. Changes
anywhere can break anything.

**Fix:** Identify bounded contexts. Extract modules with explicit interfaces.
Start with logical separation before considering physical separation (microservices).

### Golden Hammer
Using the same technology or pattern for every problem because the team is
comfortable with it.

**Symptom:** A message queue used for synchronous request/response. A relational
database used as a job queue. A microservice for a static lookup table.
**Fix:** Match the tool to the problem. Evaluate alternatives before defaulting.

### Lava Flow
Dead code, unused configurations, and abandoned experiments that nobody dares to
remove because "it might be needed."

**Fix:** If it is not covered by tests and not referenced by live code, delete it.
Version control preserves history.

---

## Do / Don't

- **Do** use automated tools to detect measurable smells (cyclomatic complexity,
  line count, parameter count, dependency depth).
- **Do** address smells incrementally. Refactor as you touch code, not in dedicated
  "cleanup sprints" that never get prioritized.
- **Do** use code review as the primary mechanism for catching design-level smells.
- **Don't** refactor code that is not covered by tests. Write the tests first.
- **Don't** treat every smell as urgent. Stable, working code that is merely
  imperfect can wait for a natural refactoring opportunity.
- **Don't** introduce new anti-patterns while fixing old ones. Have a clear
  target design before starting a refactor.

---

## Common Pitfalls

1. **Refactoring without tests.** You fix the smell and introduce a bug because there
   were no tests to catch the regression. Solution: write characterization tests
   before refactoring.
2. **Cosmetic refactoring over structural refactoring.** Renaming variables feels
   productive but does not address the god class. Solution: prioritize smells by
   impact on change frequency and bug rate.
3. **Smell blindness.** The team stops seeing the god class because they have
   worked with it for years. Solution: fresh eyes via code review, pair programming,
   or periodic architecture reviews.
4. **Over-correction.** Splitting a god class into 30 tiny classes with no cohesion.
   Solution: group by responsibility, not by arbitrary size limits.
5. **Chasing metrics.** Reducing cyclomatic complexity by extracting trivial one-liner
   functions that obscure the logic. Solution: metrics are signals, not targets.

---

## Detection Tools

| Smell                 | Automated detection                           |
|-----------------------|-----------------------------------------------|
| Long method           | Linter rule: max function length               |
| High complexity       | Cyclomatic complexity metric (radon, ESLint)   |
| Long parameter list   | Linter rule: max parameters                    |
| Dead code / lava flow | Coverage reports, unused import/variable checks|
| Dependency cycles     | Architecture linters (deptry, madge, NDepend)  |
| Duplicate code        | CPD (Copy-Paste Detector), Semgrep, jscpd      |

---

## Checklist

- [ ] Cyclomatic complexity is monitored and flagged above threshold (10+)
- [ ] No function exceeds 30 lines without a documented exception
- [ ] No function has more than 3 parameters
- [ ] No class exceeds 300 lines without a plan to decompose
- [ ] Dead code is deleted, not commented out
- [ ] Primitive obsession is addressed with domain types for core concepts
- [ ] Code review explicitly checks for design-level smells
- [ ] Refactoring is done only when adequate test coverage exists
- [ ] Dependency cycles between modules are detected and prohibited by CI
- [ ] Smells are tracked alongside bugs in the team's backlog
