# AI-Assisted Code Review

Guidance on using AI tools to detect and eliminate common code review
anti-patterns. AI reviewers automate repetitive checks, freeing human reviewers
to focus on architecture, logic, and design decisions. Based on industry
experience and the CodeRabbit catalog of review anti-patterns.

---

## Defaults

- **AI role in review:** AI handles mechanical checks (style, complexity metrics,
  type safety, coupling analysis). Humans handle judgment calls (design trade-offs,
  business logic correctness, naming semantics).
- **Review priority:** AI findings are triaged by severity. Structural issues
  (god classes, shotgun surgery) outrank cosmetic issues (formatting, naming).
- **False positives:** AI suggestions are hints, not mandates. Reviewers dismiss
  false positives with a brief rationale so the team can tune detection over time.

---

## Anti-Patterns AI Can Detect

### God Class

A single class that accumulates too many responsibilities, growing to hundreds
of lines with dozens of methods and dependencies.

**Why it matters in review:** Reviewers often miss creeping complexity because
each individual PR adds "just one more method." AI tracks cumulative metrics
across PRs and flags when a class crosses complexity thresholds.

**AI detection signals:**
- Excessive line count, method count, or cyclomatic complexity
- High number of injected dependencies
- Class referenced from many unrelated modules

**Recommended action:** Split into smaller, single-purpose components. Each
class should have one reason to change.

### Spaghetti Code

Convoluted control flow with deeply nested conditionals, tangled loops, and
hidden dependencies through global or shared mutable state.

**Why it matters in review:** Human reviewers struggle to trace execution paths
through deeply nested logic. AI can analyze control flow graphs and flag
unreachable branches, excessive nesting depth, and complex predicate chains.

**AI detection signals:**
- Nesting depth exceeding 3-4 levels
- Functions with multiple exit points buried in nested conditions
- Reliance on global variables or module-level mutable state

**Recommended action:** Extract nested blocks into named functions. Replace
complex conditionals with guard clauses or strategy patterns. Eliminate global
state in favor of explicit parameter passing.

### Nit-Picking and Style Feedback

Reviewers spend disproportionate time on formatting, naming conventions, and
minor style issues instead of evaluating functionality and design.

**Why it matters in review:** Style debates consume review bandwidth and delay
merges. When AI handles style enforcement, human review time is redirected to
architecture, correctness, and performance.

**AI detection signals:**
- Inconsistent formatting (indentation, spacing, line length)
- Naming convention violations (casing, abbreviations, prefixes)
- Import ordering and grouping inconsistencies

**Recommended action:** Automate all style checks with linters and formatters
(ruff, black, prettier, eslint). Configure them as CI gates so style issues
never reach human reviewers. Reserve human review for semantic concerns.

### Primitive Obsession

Using raw primitive types (strings, integers, booleans) to represent domain
concepts that deserve their own types, losing validation, documentation, and
type safety.

**Why it matters in review:** Primitive obsession is subtle in individual PRs
— a new `str` parameter looks fine in isolation. AI can track patterns across
the codebase and flag when primitives are repeatedly used for the same domain
concept.

**AI detection signals:**
- Multiple function parameters of the same primitive type (e.g., three `str` args)
- String comparisons against known constant sets (should be enums)
- Numeric values passed without units or validation

**Recommended action:** Introduce domain-specific types (data classes, enums,
newtypes) that enforce constraints at construction time. This makes invalid
states unrepresentable and improves IDE support.

```python
# Primitive obsession: email is just a string
def notify_user(email: str, message: str, priority: int): ...

# Domain types: constraints enforced, parameters unambiguous
@dataclass(frozen=True)
class Email:
    value: str
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError(f"Invalid email: {self.value}")

class Priority(enum.IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

def notify_user(email: Email, message: str, priority: Priority): ...
```

### Shotgun Surgery

A single logical change requires modifications scattered across many files
and modules, indicating tight coupling and poor encapsulation.

**Why it matters in review:** Reviewers may approve a PR that touches only
some of the required files, missing necessary changes elsewhere. AI can
analyze dependency graphs and flag when a change to one module likely requires
corresponding changes in coupled modules.

**AI detection signals:**
- PRs that touch many files for a single logical change
- Repeated patterns of the same files changing together
- Functions that directly access internals of multiple other modules

**Recommended action:** Consolidate scattered logic behind a single interface
or service. Apply the facade pattern to decouple consumers from implementation
details. Use change coupling analysis to identify modules that should be merged.

---

## Do / Don't

- **Do** configure AI review tools as part of the CI pipeline so every PR
  gets automated analysis before human review begins.
- **Do** use AI to enforce measurable quality gates (complexity limits, nesting
  depth, parameter counts) that are tedious for humans to track.
- **Do** let AI handle style and formatting checks entirely — remove these
  from the human review checklist.
- **Do** review AI suggestions critically. Dismiss false positives with a
  brief note to improve future signal quality.
- **Don't** treat AI review as a replacement for human review. AI catches
  structural patterns; humans evaluate design intent and business correctness.
- **Don't** ignore AI findings because "it's just a tool." Cumulative metrics
  like class size and coupling are hard for humans to track across PRs.
- **Don't** let AI style enforcement become a bottleneck. Configure formatters
  to auto-fix on save or pre-commit, not just flag violations.

---

## Common Pitfalls

1. **Over-reliance on AI review.** The team stops doing thorough human review
   because "AI will catch it." AI misses business logic errors, subtle race
   conditions, and design intent violations. Solution: AI augments human review,
   it does not replace it.
2. **Alert fatigue.** Too many low-severity AI findings cause reviewers to
   ignore all suggestions. Solution: tune severity thresholds and suppress
   cosmetic findings that are already handled by formatters.
3. **Style wars by proxy.** Teams argue about AI tool configuration instead of
   about the code. Solution: agree on style rules once, codify them in config
   files, and stop debating.
4. **Ignoring cumulative metrics.** Each PR looks fine individually, but the
   class has grown from 200 to 800 lines over six months. Solution: configure
   AI to track trends, not just snapshots.
5. **Skipping refactoring recommendations.** AI flags a god class but the team
   defers action indefinitely. Solution: create backlog items for refactoring
   when AI flags structural issues above a severity threshold.

---

## Integration Checklist

- [ ] AI review tool is integrated into CI and runs on every PR
- [ ] Style and formatting checks are fully automated (no human review needed)
- [ ] Complexity thresholds are configured (cyclomatic complexity, nesting depth,
      class size, parameter count)
- [ ] Coupling analysis is enabled to detect shotgun surgery patterns
- [ ] AI findings are triaged by severity before reaching human reviewers
- [ ] False positive rate is monitored and tool configuration is tuned quarterly
- [ ] Human reviewers focus on design, logic, and business correctness
- [ ] Refactoring recommendations from AI are tracked in the team backlog
- [ ] Pre-commit hooks auto-fix formatting issues before code reaches review
- [ ] Team has agreed on which AI suggestions are mandatory vs advisory
