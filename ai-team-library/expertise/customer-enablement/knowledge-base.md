# Knowledge Base Structure

A well-organized knowledge base reduces support ticket volume, accelerates
onboarding, and empowers customers to solve problems independently. Structure
determines findability — the best content is useless if nobody can locate it.

---

## Defaults

| Setting | Default | Alternatives |
|---------|---------|--------------|
| **Taxonomy** | Product-area hierarchy | Task-based, persona-based |
| **Search** | Full-text with faceted filters | AI-powered semantic search |
| **Content format** | Markdown with frontmatter | HTML, structured JSON |
| **Review cadence** | Quarterly accuracy audit | Monthly, triggered by product release |
| **Ownership model** | Product team owns content | Dedicated KB team, community-contributed |
| **Versioning** | Tied to product version | Evergreen (single version) |

---

## Information Architecture

### Tier 1 — Getting Started

Quick-start guides, installation instructions, and first-use walkthroughs.
Optimized for new users who need to reach first value fast. Every article answers
"how do I start doing X?"

### Tier 2 — How-To Guides

Task-oriented articles that solve a specific problem. Each article has a single
goal, clear prerequisites, numbered steps, and an expected outcome. Avoid mixing
conceptual explanation into how-to content.

### Tier 3 — Reference

API documentation, configuration options, permissions tables, and schema
definitions. Structured for lookup, not reading. Tables and code examples over
prose.

### Tier 4 — Conceptual / Explanatory

Architecture overviews, design decisions, and "why" content. Helps advanced
users understand the system model. Link to how-to guides for actionable steps.

### Tier 5 — Troubleshooting

Symptom-based articles organized by error message or observable behavior. Each
article follows: symptom → cause → resolution → prevention.

---

## Do / Don't

- **Do** write titles as questions or task statements ("How to configure SSO"
  not "SSO Configuration").
- **Do** include a last-updated date and content owner on every article.
- **Do** use consistent templates for each content tier. Structure reduces
  authoring friction and improves scannability.
- **Do** cross-link related articles. A how-to guide should link to its
  reference page and vice versa.
- **Do** track article-level analytics (views, search-to-click, helpfulness
  ratings) to prioritize updates.
- **Don't** duplicate content across articles. Use a single source of truth and
  link to it.
- **Don't** mix content tiers in one article (a how-to guide should not include
  three pages of conceptual background).
- **Don't** let articles go stale. Outdated content is worse than no content —
  it erodes trust.
- **Don't** organize solely by internal team structure. Customers do not know
  your org chart.

---

## Common Pitfalls

1. **Organizing by internal team, not customer task.** The knowledge base mirrors
   the engineering org chart. Customers search for what they want to do, not
   which team built it. Solution: organize by customer workflow and use case.
2. **No content review process.** Articles written at launch are never updated.
   Product changes silently invalidate documentation. Solution: tie content
   reviews to the release cycle. Every feature change triggers a KB audit task.
3. **Search returns irrelevant results.** Customers search, find nothing useful,
   and file a support ticket. Solution: analyze failed searches weekly. Create
   or update articles for the top unanswered queries.
4. **No feedback loop.** There is no way for customers to report inaccurate or
   missing content. Solution: add a "Was this helpful?" widget and a "Report an
   issue" link on every article.
5. **Content sprawl without governance.** Anyone can create articles but nobody
   retires them. The KB grows endlessly with contradictory information.
   Solution: assign content owners, enforce templates, and archive articles with
   zero views in 90 days.

---

## Article Template

```yaml
# Knowledge Base Article Template
metadata:
  title: "How to [accomplish specific task]"
  tier: how-to            # getting-started | how-to | reference | conceptual | troubleshooting
  product_area: billing
  tags:
    - invoices
    - payments
  author: support-team
  created: "2026-01-15"
  last_reviewed: "2026-01-15"
  applies_to: "v3.2+"     # product version

content:
  summary: >
    One-sentence description of what this article helps the customer do.

  prerequisites:
    - "Admin role required"
    - "Billing module enabled in account settings"

  steps:
    - step: 1
      action: "Navigate to Settings > Billing"
      detail: "You must have admin permissions to access this page."
    - step: 2
      action: "Click 'Create Invoice'"
      detail: "The invoice form opens with your default settings pre-filled."
    - step: 3
      action: "Fill in the line items and click 'Send'"
      detail: "The customer receives the invoice via email immediately."

  expected_outcome: >
    The invoice appears in the Sent tab and the customer receives an email
    with a payment link.

  related_articles:
    - "How to configure default billing settings"
    - "Invoice API reference"

  troubleshooting:
    - symptom: "Send button is grayed out"
      cause: "Missing required fields"
      resolution: "Ensure all required fields (customer, amount, due date) are filled"
```

---

## Content Audit Tracker

```yaml
# Quarterly Knowledge Base Audit
audit:
  quarter: "2026-Q1"
  owner: "KB Team Lead"
  scope: "All articles last reviewed before 2025-10-01"

  articles:
    - path: "/getting-started/quick-start"
      status: current
      views_90d: 1420
      helpfulness_rating: 0.87
      action: none

    - path: "/how-to/configure-sso"
      status: outdated
      views_90d: 890
      helpfulness_rating: 0.52
      action: rewrite
      notes: "SSO flow changed in v3.1, screenshots and steps are wrong"
      assigned_to: "security-team"
      due_date: "2026-02-01"

    - path: "/reference/legacy-api-v1"
      status: deprecated
      views_90d: 12
      helpfulness_rating: 0.30
      action: archive
      notes: "API v1 sunset 6 months ago. Add redirect to v2 reference."

  summary:
    total_articles: 245
    current: 198
    needs_update: 35
    archive_candidates: 12
```

---

## Alternatives

| Approach | When to consider |
|----------|-----------------|
| Wiki-style (community-edited) | Developer-focused products with active user communities |
| In-app contextual help | Products where users rarely leave the application |
| Video-first documentation | Visual products (design tools, dashboards) |
| AI chatbot over KB content | High support volume with repetitive questions |
| API-only reference (OpenAPI) | Developer platforms where code is the primary interface |

---

## Checklist

- [ ] Information architecture defined with clear content tiers
- [ ] Article templates created for each content tier
- [ ] Content ownership assigned (team or individual per product area)
- [ ] Search configured and tested for common customer queries
- [ ] Analytics tracking enabled (views, search queries, helpfulness ratings)
- [ ] Failed-search report reviewed weekly and gaps addressed
- [ ] Review cadence established and tied to product release cycle
- [ ] Feedback mechanism on every article (helpful/not helpful + report issue)
- [ ] Stale content policy defined (archive threshold, review triggers)
- [ ] Cross-linking between related articles verified
