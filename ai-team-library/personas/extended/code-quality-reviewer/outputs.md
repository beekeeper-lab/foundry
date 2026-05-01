# Code Quality Reviewer -- Outputs

This document enumerates every artifact the Code Quality Reviewer is responsible
for producing, including quality standards and who consumes each deliverable.

---

## 1. Code Review Comments

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Code Review Comments                               |
| **Cadence**        | One set per pull request reviewed                  |
| **Template**       | `personas/code-quality-reviewer/templates/review-comments.md` |
| **Format**         | Markdown (inline PR comments or standalone report) |

**Description.** Detailed, actionable feedback on a pull request's code changes.
Each comment identifies a specific issue, classifies its severity, explains why
it matters, and provides a concrete suggestion for resolution. Review comments
are the primary mechanism by which the Code Quality Reviewer communicates
findings to the developer.

**Quality Bar:**
- Every comment references a specific file and line range -- never a vague
  "somewhere in the auth module."
- Each comment is labeled with a severity prefix: `[blocking]`, `[suggestion]`,
  `[nit]`, or `[question]`.
- Blocking comments identify genuine risks (bugs, security issues, broken
  contracts), not style preferences.
- Suggestions include a rationale: what improves and why, not just what to
  change.
- Comments are phrased constructively -- "Consider renaming `x` to
  `validateOrderInput` to clarify intent" rather than "bad name."
- No false positives: the reviewer has verified that the flagged code actually
  exhibits the issue described.
- The complete set of comments covers correctness, readability, maintainability,
  and convention adherence for every file in the PR.

**Downstream Consumers:** Developer (for addressing feedback), Team Lead (for
quality trend tracking), Architect (when architectural violations are flagged).

---

## 2. Ship/No-Ship Checklist

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Ship/No-Ship Checklist                             |
| **Cadence**        | One per pull request reviewed                      |
| **Template**       | `personas/code-quality-reviewer/templates/ship-no-ship-checklist.md` |
| **Format**         | Markdown                                           |

**Description.** A structured go/no-go assessment that summarizes whether a pull
request is ready to merge. The checklist evaluates the PR against a defined set
of quality criteria and produces a clear verdict with rationale. This is the
final gate before code enters the main branch.

**Quality Bar:**
- Every checklist item is evaluated with a pass, fail, or not-applicable status.
- Failing items cross-reference the specific review comment that describes the
  issue.
- The overall verdict is one of: Ship (approve), Ship with Conditions (list
  non-blocking items to address post-merge), or No-Ship (list blocking items
  that must be resolved).
- No-Ship verdicts include a clear description of what must change before
  re-review.
- The checklist covers at minimum: correctness, test coverage, convention
  adherence, security considerations, and architectural alignment.
- The rationale explains the judgment, not just the outcome -- "No-Ship because
  the error path for null input is untested and the function is called from
  user-facing endpoints" rather than just "No-Ship: missing tests."

**Downstream Consumers:** Developer (for merge decision), Team Lead (for release
readiness), DevOps / Release Engineer (for deployment confidence).

---

## 3. Style Consistency Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Style Consistency Report                           |
| **Cadence**        | Per review cycle or when style drift is detected   |
| **Template**       | `personas/code-quality-reviewer/templates/style-consistency-checklist.md` |
| **Format**         | Markdown                                           |

**Description.** A report assessing how consistently the codebase adheres to the
project's coding standards and style guidelines. The report identifies patterns
of drift, documents specific deviations, and recommends whether the style guide
needs updating or the code needs correcting. This deliverable helps the team
maintain a uniform codebase that any developer can read without adjusting to
individual idiosyncrasies.

**Quality Bar:**
- Each deviation cites the specific style rule violated and the file(s) where
  the deviation occurs.
- Deviations are categorized: naming conventions, formatting, code organization,
  error handling patterns, import ordering, or documentation style.
- The report distinguishes between genuine drift (code that should be corrected)
  and emergent conventions (patterns that have become de facto standard and
  should be codified).
- Recommendations are actionable: "Update `conventions.md` to allow both styles"
  or "Refactor these 4 files to match the documented pattern."
- The report includes a consistency score or summary metric so trends can be
  tracked across review cycles.
- Automated linter and formatter coverage gaps are identified -- rules that
  should be enforced by tooling but are not.

**Downstream Consumers:** Developer (for style corrections), Team Lead (for
codebase health tracking), Architect (for convention decisions).

---

## 4. Suggested Diffs

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Suggested Diffs                                    |
| **Cadence**        | As needed during pull request reviews              |
| **Template**       | `personas/code-quality-reviewer/templates/suggested-diffs.md` |
| **Format**         | Markdown with fenced code blocks                   |

**Description.** Concrete code patches that demonstrate a recommended
improvement. When a review comment identifies a non-trivial issue where the fix
is not obvious, the reviewer provides a suggested diff showing exactly what the
improved code would look like. Suggested diffs reduce ambiguity and accelerate
the review-rework cycle.

**Quality Bar:**
- The diff compiles and passes existing tests when applied. The reviewer has
  verified this mentally or by inspection, not guessed.
- The diff addresses only the issue described in the associated review comment --
  no scope creep or unrelated cleanup.
- The diff preserves existing behavior unless the review comment explicitly
  describes an intentional behavior change with rationale.
- Before and after code is shown in fenced code blocks with the correct language
  tag for syntax highlighting.
- Variable names, error messages, and comments in the diff follow the project's
  conventions.
- The diff is accompanied by a one-sentence explanation of what it changes and
  why.

**Downstream Consumers:** Developer (for implementing improvements), Code
Quality Reviewer (for verifying rework in subsequent review rounds).

---

## 5. Review Summary / Verdict

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Review Summary / Verdict                           |
| **Cadence**        | One per pull request reviewed                      |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A concise summary of the entire review, aggregating findings
into a single document that stakeholders can read without wading through
individual comments. The summary captures the overall quality assessment,
highlights patterns, and records positive observations alongside issues.

**Required Sections:**
1. **PR Reference** -- PR number, title, author, and link to the originating
   task or story.
2. **Scope** -- Files and components reviewed, with note of any files excluded
   and why.
3. **Blocking Issues** -- Numbered list of issues that must be resolved before
   merge, each with file location and one-sentence description.
4. **Non-Blocking Suggestions** -- Numbered list of improvements that are
   recommended but not required for merge.
5. **Positive Observations** -- What was done well. Specific examples of clean
   code, good test coverage, or thoughtful error handling.
6. **Verdict** -- Ship, Ship with Conditions, or No-Ship, with a one-paragraph
   rationale.

**Quality Bar:**
- The summary is self-contained: a reader who has not seen the individual
  comments understands the state of the PR.
- Blocking and non-blocking issues are clearly separated -- no ambiguity about
  what must be fixed.
- Positive observations are specific, not generic. "The retry logic in
  `OrderService.submit()` correctly uses exponential backoff with jitter" rather
  than "Good code."
- The verdict is consistent with the findings. A No-Ship verdict has at least
  one blocking issue. A Ship verdict has zero blocking issues.
- Patterns across findings are noted: "Three of the five issues involve missing
  null checks on API responses -- consider adding a shared validation helper."

**Downstream Consumers:** Developer (for rework planning), Team Lead (for
review queue and quality metrics), Architect (for systemic pattern awareness).

---

## Output Format Guidelines

- Review comments are posted inline on the pull request in the team's code
  hosting platform, with a summary comment at the top of the PR.
- Ship/No-Ship checklists are attached to the PR as a top-level comment or
  included in the review summary.
- Style consistency reports are stored in the project repository under
  `docs/quality/` or filed as issues when they require action.
- Suggested diffs use fenced code blocks with the appropriate language tag and
  are posted as part of inline review comments.
- All severity labels use the standard prefixes: `[blocking]`, `[suggestion]`,
  `[nit]`, `[question]`.
- When recurring patterns are identified across multiple reviews, file a
  separate issue or style guide update rather than repeating the same feedback
  on every PR.
