# Researcher / Librarian -- Outputs

This document enumerates every artifact the Researcher / Librarian is
responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. Research Memo

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Research Memo                                      |
| **Cadence**        | One per research question or request               |
| **Template**       | `personas/researcher-librarian/templates/research-memo.md` |
| **Format**         | Markdown                                           |

**Description.** A structured document that answers a specific research question
posed by another persona. The research memo presents cited evidence, evaluates
source quality, and states confidence levels -- enabling the requester to make
an informed decision without conducting their own research.

**Quality Bar:**
- The original research question is restated at the top so the reader knows
  exactly what was investigated.
- Every factual claim is cited with a specific source (author, title, URL, date
  accessed).
- Source quality is assessed for each reference: official documentation,
  peer-reviewed, independent benchmark, vendor-sourced, blog post, or anecdotal.
- Confidence level is stated for each key finding: High (multiple independent
  authoritative sources), Medium (single authoritative source or multiple
  secondary sources), Low (limited or conflicting evidence).
- The memo is scoped to the question asked -- no tangential information that
  does not inform the decision.
- Actionable conclusions are stated clearly: "The evidence supports X over Y
  for this use case because..."

**Downstream Consumers:** Architect (for technology decisions), Team Lead (for
planning decisions), Developer (for implementation guidance), Security Engineer
(for security best practice context).

---

## 2. Decision Matrix

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Decision Matrix                                    |
| **Cadence**        | One per multi-option decision requiring structured comparison |
| **Template**       | `personas/researcher-librarian/templates/decision-matrix.md` |
| **Format**         | Markdown                                           |

**Description.** A structured comparison of multiple options against weighted
criteria, presented as a scored table. The decision matrix distills research
into a format that makes tradeoffs visible and enables the decision-maker to
see why one option scores higher than another.

**Quality Bar:**
- At least two options are compared, including "do nothing" or "status quo"
  when applicable.
- Criteria weights reflect project priorities and are agreed upon with the
  requesting persona before scoring.
- Each score is justified with a brief rationale or citation, not assigned
  without explanation.
- The matrix includes a summary identifying the highest-scoring option and the
  key differentiators.
- Scoring uses a consistent scale (e.g., 1-5) defined at the top of the
  matrix.
- Limitations of the analysis are stated: what factors were not evaluated
  and why.

**Downstream Consumers:** Architect (for build-vs-buy and technology selection),
Team Lead (for prioritization decisions), Business Analyst (for option
evaluation), Compliance / Risk Analyst (for regulatory option assessment).

---

## 3. Annotated Bibliography

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Annotated Bibliography                             |
| **Cadence**        | One per research domain or ongoing as references accumulate |
| **Template**       | `personas/researcher-librarian/templates/annotated-bibliography.md` |
| **Format**         | Markdown                                           |

**Description.** A curated list of references on a specific topic, where each
entry includes a citation, a summary of the source's content, and an assessment
of its relevance and reliability. The annotated bibliography serves as the
team's reference shelf -- a go-to resource when someone needs authoritative
sources on a given topic.

**Quality Bar:**
- Each entry includes: full citation (author, title, publisher/URL, date),
  two-to-four sentence summary, relevance rating (High/Medium/Low), and source
  quality assessment.
- Sources are organized by subtopic or theme, not listed in random order.
- The bibliography distinguishes between primary sources (official docs,
  specifications, peer-reviewed papers) and secondary sources (tutorials, blog
  posts, opinion pieces).
- Outdated sources are flagged with the date of last verification and a note
  about potential staleness.
- The bibliography is maintained over time: new sources are added, obsolete
  ones are marked as superseded.

**Downstream Consumers:** Architect (for design rationale sourcing), Developer
(for implementation references), Technical Writer (for documentation
references), Security Engineer (for security best practice sources).

---

## 4. Experiment Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Experiment Plan                                    |
| **Cadence**        | As needed when a question requires empirical validation |
| **Template**       | `personas/researcher-librarian/templates/experiment-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A structured plan for conducting a hands-on experiment or
proof-of-concept to answer a question that cannot be resolved through desk
research alone. The experiment plan defines what will be tested, how success
is measured, and what resources are needed -- ensuring that the experiment
produces actionable data rather than inconclusive impressions.

**Quality Bar:**
- The hypothesis is stated clearly: "We expect that X will outperform Y under
  conditions Z, measured by metric M."
- Success criteria are defined before the experiment begins, not
  retroactively fitted to the results.
- The experimental setup is described in enough detail that another team member
  could reproduce it.
- Resource requirements are estimated: time, infrastructure, personnel, and
  any costs.
- The plan includes a defined timebox to prevent open-ended experimentation.
- Expected outputs are specified: benchmark results, comparison data, or a
  go/no-go recommendation.

**Downstream Consumers:** Architect (for proof-of-concept validation), Developer
(for experiment execution), Team Lead (for resource allocation and scheduling).

---

## 5. Knowledge Base Entry

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Knowledge Base Entry                               |
| **Cadence**        | Ongoing; one per reusable finding or decision       |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A standalone entry in the team's shared knowledge base that
captures a finding, decision, or reference for future reuse. Knowledge base
entries prevent the team from re-researching the same question and ensure that
institutional knowledge survives personnel changes.

**Required Sections:**
1. **Topic** -- Clear, searchable title describing what this entry covers.
2. **Context** -- Why this knowledge was captured and what question it
   originally answered.
3. **Finding** -- The core information, presented concisely with citations.
4. **Applicability** -- When this finding applies and when it does not.
   Conditions, constraints, and expiration (e.g., "valid as of library
   version 4.x; re-evaluate for 5.x").
5. **References** -- Links to the original research memo, decision matrix,
   or external sources that support this entry.

**Quality Bar:**
- The entry is self-contained: a reader can understand it without reading the
  original research memo.
- The topic title is specific enough to be found via keyword search.
- Applicability conditions are explicit so the reader knows whether the finding
  is relevant to their situation.
- An expiration or review date is set for findings about fast-moving
  technologies.
- The entry does not duplicate another knowledge base entry. If related entries
  exist, they are cross-referenced.

**Downstream Consumers:** All personas (for self-service knowledge retrieval),
Technical Writer (for documentation sourcing), new team members (for onboarding
context).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository or the team's shared knowledge base.
- Research memos are stored in `docs/research/` with descriptive filenames
  (e.g., `research-memo-cache-strategy-comparison.md`).
- Decision matrices are stored alongside the research memos they support or
  in the requesting persona's documentation area.
- The knowledge base is organized by topic, not by date. Entries should be
  findable by someone who does not know when the research was conducted.
- Annotated bibliographies are living documents: update them as new sources
  are found rather than creating a new bibliography for each request.
- All citations include enough information to locate the source independently
  (URL, author, title, and access date at minimum).
