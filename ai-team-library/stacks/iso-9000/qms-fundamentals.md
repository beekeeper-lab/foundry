# Quality Management System Fundamentals

Standards and principles for implementing and maintaining a Quality Management
System (QMS) aligned with the ISO 9000 family of standards. A QMS provides the
framework for consistent quality in products, services, and processes.

---

## Defaults

- **Standard:** ISO 9001:2015 (requirements) backed by ISO 9000:2015
  (fundamentals and vocabulary).
- **Approach:** Process-based, applying the Plan-Do-Check-Act (PDCA) cycle.
- **Scope:** All processes that affect product/service quality, from design
  through delivery and post-delivery support.
- **Management commitment:** Top management must demonstrate leadership and
  commitment to the QMS. This is not optional.

---

## Seven Quality Management Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Customer Focus** | Understand current and future customer needs. Meet requirements and exceed expectations. |
| 2 | **Leadership** | Leaders establish unity of purpose and direction. Create conditions for people to achieve quality objectives. |
| 3 | **Engagement of People** | Competent, empowered, and engaged people at all levels are essential. |
| 4 | **Process Approach** | Consistent and predictable results are achieved when activities are managed as interrelated processes. |
| 5 | **Improvement** | Successful organizations maintain an ongoing focus on improvement. |
| 6 | **Evidence-Based Decision Making** | Decisions based on analysis and evaluation of data are more likely to produce desired results. |
| 7 | **Relationship Management** | Manage relationships with interested parties (suppliers, partners) to optimize their impact on performance. |

---

## Plan-Do-Check-Act (PDCA) Cycle

```
    ┌──────────┐
    │   PLAN   │  Establish objectives, processes, and resources
    │          │  needed to deliver results
    └────┬─────┘
         │
    ┌────▼─────┐
    │    DO    │  Implement what was planned
    │          │
    └────┬─────┘
         │
    ┌────▼─────┐
    │  CHECK   │  Monitor and measure processes and results
    │          │  against policies, objectives, and requirements
    └────┬─────┘
         │
    ┌────▼─────┐
    │   ACT    │  Take actions to improve performance
    │          │  as necessary
    └──────────┘
```

### Applying PDCA to Software Projects

| Phase | Activities |
|-------|-----------|
| **Plan** | Define quality objectives, acceptance criteria, coding standards, review processes, test plans |
| **Do** | Implement code, run builds, execute test suites, conduct code reviews |
| **Check** | Analyze test results, review metrics (defect density, code coverage), audit compliance |
| **Act** | Address nonconformities, update processes, refine standards based on lessons learned |

---

## Do / Don't

- **Do** define a clear quality policy that is understood at all levels.
- **Do** establish measurable quality objectives tied to customer satisfaction.
- **Do** document processes at the level needed for consistency — not more, not less.
- **Do** assign process owners who are accountable for process performance.
- **Do** conduct management reviews at planned intervals.
- **Don't** treat the QMS as a documentation exercise. The system must drive actual
  quality improvement, not just produce paper.
- **Don't** implement ISO 9001 requirements in isolation from daily operations.
  Integrate them into how work is actually done.
- **Don't** delegate quality management entirely to a "quality department."
  Quality is everyone's responsibility.
- **Don't** confuse compliance with certification. You can comply with ISO 9001
  without pursuing formal certification.

---

## Common Pitfalls

1. **Documentation overload.** Teams create excessive documentation that nobody
   reads or maintains. Solution: document what adds value. ISO 9001:2015 reduced
   mandatory documentation compared to 2008.
2. **Management lip service.** Leadership endorses the QMS but does not allocate
   resources or participate in reviews. Solution: make management review a
   calendar event with documented outcomes and action items.
3. **Treating audits as threats.** Teams hide problems before audits instead of
   using them as improvement opportunities. Solution: foster a culture where
   nonconformities are welcomed as learning opportunities.
4. **Static QMS.** The system is implemented once and never updated. Solution:
   schedule periodic reviews, track improvement actions, and update processes
   when the business changes.
5. **Ignoring context.** The QMS does not consider the organization's context,
   interested parties, or risk landscape. Solution: Clause 4 of ISO 9001:2015
   requires understanding context — take it seriously.

---

## ISO 9001:2015 Clause Structure

| Clause | Title | Key Requirement |
|--------|-------|-----------------|
| 4 | Context of the Organization | Understand internal/external issues and interested parties |
| 5 | Leadership | Quality policy, roles, responsibilities, authorities |
| 6 | Planning | Address risks and opportunities, quality objectives |
| 7 | Support | Resources, competence, awareness, communication, documented information |
| 8 | Operation | Operational planning, requirements, design, production, release |
| 9 | Performance Evaluation | Monitoring, measurement, analysis, internal audit, management review |
| 10 | Improvement | Nonconformity, corrective action, continual improvement |

---

## Risk-Based Thinking

ISO 9001:2015 integrates risk-based thinking throughout the standard (replacing
the separate "preventive action" requirement from 2008).

- **Identify risks** to QMS objectives during planning (Clause 6.1)
- **Assess impact and likelihood** — prioritize risks that could affect
  product/service conformity or customer satisfaction
- **Plan actions** to address risks — preventive measures, contingency plans
- **Implement and monitor** — track effectiveness of risk treatments
- **Review** during management reviews — update risk assessments as context changes

This does not require a formal risk management framework (like ISO 31000), but
the thinking must be demonstrably applied.

---

## Checklist

- [ ] Quality policy is defined, documented, and communicated
- [ ] Quality objectives are measurable and aligned with the quality policy
- [ ] Process approach is applied — processes are identified, sequenced, and managed
- [ ] Risks and opportunities are identified and addressed
- [ ] Resources (people, infrastructure, environment) are adequate
- [ ] Competence requirements are defined and verified for all roles
- [ ] Management reviews are conducted at planned intervals
- [ ] Continual improvement is demonstrated through measurable results
- [ ] Customer satisfaction is monitored and acted upon
- [ ] The QMS is integrated into daily operations, not a parallel system
