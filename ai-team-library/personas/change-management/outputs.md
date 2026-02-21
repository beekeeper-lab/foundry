# Change Management / Adoption Lead — Outputs

This document enumerates every artifact the Change Management / Adoption Lead is
responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. Change Management Strategy

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Change Management Strategy                         |
| **Cadence**        | One per project or major initiative; updated as scope changes |
| **Template**       | `personas/change-management/templates/change-strategy.md` |
| **Format**         | Markdown                                           |

**Description.** The overarching plan that defines the change management approach
for a project or initiative. It identifies what is changing, who is affected, what
risks exist, and how the organization will be guided from the current state to the
target state. The strategy is the backbone document that all other change
artifacts reference.

**Quality Bar:**
- Clearly states the change objective and links it to business outcomes.
- Identifies all affected stakeholder groups with their current state and
  desired future state.
- Includes a phased timeline aligned to the project delivery milestones.
- Risk and resistance factors are identified with mitigation approaches.
- Success criteria are defined with measurable adoption metrics.
- Sponsorship model is documented: who sponsors, what they do, and how often
  they are engaged.

**Downstream Consumers:** Team Lead (for delivery alignment), Architect (for
rollout sequencing constraints), stakeholders/sponsors (for endorsement and
resource allocation), Technical Writer (for documentation planning).

---

## 2. Stakeholder Analysis

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Stakeholder Analysis                               |
| **Cadence**        | At project start; refreshed when stakeholder landscape changes |
| **Template**       | `personas/change-management/templates/stakeholder-analysis.md` |
| **Format**         | Markdown                                           |

**Description.** A structured assessment of all stakeholder groups affected by or
influential over the change. For each group, the analysis captures their current
awareness, level of support, concerns, influence, and the engagement approach
needed to move them toward active adoption.

**Quality Bar:**
- Every affected group is listed — no implicit "everyone else" category.
- Each group has a documented current position (supportive, neutral, resistant)
  with evidence or rationale for the assessment.
- Influence and impact ratings are justified, not arbitrary.
- Engagement actions are specific: "Monthly demo to operations managers" not
  "engage stakeholders."
- The analysis distinguishes between sponsors (authority), champions (influence),
  and end users (adoption).
- Refresh dates are noted for reassessment as the project evolves.

**Downstream Consumers:** Team Lead (for stakeholder management), Business
Analyst (for requirements alignment), all personas (for understanding who is
affected and how).

---

## 3. Communication Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Communication Plan                                 |
| **Cadence**        | One per change initiative; updated as milestones shift |
| **Template**       | `personas/change-management/templates/communication-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A schedule of communications that keeps all stakeholder groups
informed, prepared, and engaged throughout the change lifecycle. Each entry
specifies the audience, message, channel, timing, and owner. The plan ensures
that the right people hear the right message at the right time through the right
channel.

**Quality Bar:**
- Every stakeholder group from the stakeholder analysis has at least one
  communication touchpoint.
- Messages are tailored to the audience: executives receive impact summaries,
  managers receive team guidance, end users receive practical instructions.
- Timing is tied to delivery milestones: communications precede rather than
  follow technical changes.
- Channels are appropriate for the audience: not everything is an email.
- Each communication has an owner responsible for drafting, approving, and
  sending.
- Feedback mechanisms are included: how recipients can ask questions or raise
  concerns.

**Downstream Consumers:** Team Lead (for milestone alignment), Technical Writer
(for content creation), stakeholders/sponsors (for review and approval of
messages directed at their teams).

---

## 4. Training Program

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Training Program                                   |
| **Cadence**        | One per change initiative; modules added as features are delivered |
| **Template**       | `personas/change-management/templates/training-program.md` |
| **Format**         | Markdown                                           |

**Description.** A structured enablement program that equips affected users with
the knowledge and skills to operate effectively in the new model. The program
defines learning objectives, delivery methods, materials, schedules, and
assessment criteria. Training is behavior change, not information transfer — the
program must include opportunities for practice and feedback.

**Quality Bar:**
- Learning objectives are stated as observable behaviors: "After training, the
  user can [do X] using [tool/process Y]" not "understand the new system."
- Delivery methods match the content and audience: hands-on workshops for
  process changes, self-paced guides for tool changes, coaching for role changes.
- Materials are practical and task-oriented: job aids, quick-reference cards,
  walkthroughs — not slide decks alone.
- A schedule is defined that places training close to (but before) go-live so
  skills are fresh when needed.
- Assessment criteria define how training effectiveness is measured: completion
  rates, skill demonstrations, or post-training task performance.
- Accessibility needs are addressed: format, language, and scheduling
  accommodate all affected users.

**Downstream Consumers:** End users (as participants), Technical Writer (for
documentation and job aids), UX/UI Designer (for workflow alignment), Team Lead
(for scheduling and resource allocation).

---

## 5. Adoption Metrics Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Adoption Metrics Report                            |
| **Cadence**        | Weekly or biweekly during rollout; monthly post-go-live |
| **Template**       | `personas/change-management/templates/adoption-metrics.md` |
| **Format**         | Markdown                                           |

**Description.** A periodic report that tracks whether the target population is
actually using the new system, process, or workflow as intended. The report
compares current adoption levels against targets, identifies groups or areas that
are lagging, and recommends corrective actions. Adoption metrics are the primary
evidence that change management is working.

**Quality Bar:**
- Metrics are behavioral and observable: login rates, feature usage, process
  compliance rates, support ticket volumes — not self-reported satisfaction alone.
- Baselines are established before go-live so progress can be measured.
- Targets are defined for each metric with timeframes.
- Data is segmented by stakeholder group, team, or region to identify pockets
  of non-adoption.
- Each report includes an interpretation section: what the numbers mean and
  what actions are recommended.
- Trends are shown over time, not just point-in-time snapshots.

**Downstream Consumers:** Team Lead (for project status), stakeholders/sponsors
(for adoption visibility), Developer (for usage-related insights), UX/UI
Designer (for usability-related adoption gaps).

---

## 6. Resistance Mitigation Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Resistance Mitigation Plan                         |
| **Cadence**        | Created during change strategy; updated as new resistance surfaces |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A targeted plan that identifies anticipated and observed sources
of resistance to the change, diagnoses their root causes, and defines specific
actions to address each. Resistance is signal — this plan transforms that signal
into actionable mitigations.

**Required Sections:**
1. **Resistance Inventory** — Each source of resistance with: the affected group,
   the observed or anticipated behavior, the root cause (capability gap, unclear
   benefit, loss of autonomy, process concern, change fatigue), and severity.
2. **Mitigation Actions** — For each resistance source: the specific action,
   owner, timeline, and expected outcome.
3. **Escalation Criteria** — When resistance requires escalation to sponsors or
   leadership and the process for doing so.
4. **Progress Tracking** — Status of each mitigation action and whether
   resistance levels are decreasing.

**Quality Bar:**
- Root causes are diagnosed, not assumed. "People resist change" is not a root
  cause analysis.
- Mitigation actions are specific and assigned to individuals, not generic
  recommendations.
- Severity is assessed based on the group's influence and the impact on adoption
  if the resistance is not addressed.
- The plan is a living document updated as new resistance surfaces during
  rollout.

**Downstream Consumers:** Team Lead (for risk management), stakeholders/sponsors
(for escalation handling), all personas (for awareness of adoption risks).

---

## Output Format Guidelines

- All deliverables are written in Markdown and stored in the project repository
  under `docs/change-management/` or a dedicated change management folder.
- The change management strategy is the master document — all other artifacts
  reference it for context and alignment.
- Communication plans and training programs are living documents updated as the
  delivery timeline evolves.
- Adoption metrics reports are versioned by date and kept as a historical
  record to show trends.
- Stakeholder analysis documents are treated as sensitive — they contain
  assessments of individuals' positions and should not be shared broadly without
  the Change Management Lead's approval.
- All documents use plain language appropriate for a mixed technical and
  non-technical audience unless specifically targeted at a technical group.
