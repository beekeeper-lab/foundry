# Decision Matrix

## Metadata

| Field         | Value                                        |
|---------------|----------------------------------------------|
| Date          | [YYYY-MM-DD]                                 |
| Owner         | [Researcher name / role]                      |
| Related links | [Issue/ticket, research memo, ADRs]           |
| Status        | Draft / Reviewed / Approved                  |

## Decision Context

*Describe the decision to be made, why it matters, and any constraints.*

- **Problem**: [What problem are we solving or what choice must be made?]
- **Constraints**: [Budget, timeline, team skills, existing commitments, regulatory requirements]
- **Stakeholders**: [Who is affected by or will make this decision?]

## Evaluation Criteria

*Define the criteria used to compare options. Assign a weight (1-5) reflecting relative importance.*

| Criterion | Weight (1-5) | Description |
|-----------|-------------|-------------|
| [e.g., Ease of adoption] | [3] | [How quickly the team can start using this effectively] |
| [e.g., Long-term maintainability] | [4] | [Effort to maintain over 2+ years] |
| [e.g., Community and ecosystem] | [2] | [Size of community, availability of plugins and integrations] |
| [e.g., Performance] | [3] | [Throughput, latency, resource efficiency for our workload] |
| [e.g., Cost] | [4] | [Licensing, infrastructure, and operational costs] |

## Options Comparison

*Score each option 1-5 per criterion. Multiply by weight for the weighted score.*

| Criterion | Weight | [Option A] | [Option B] | [Option C] |
|-----------|--------|-----------|-----------|-----------|
| [Criterion 1] | [w] | [1-5] | [1-5] | [1-5] |
| [Criterion 2] | [w] | [1-5] | [1-5] | [1-5] |
| [Criterion 3] | [w] | [1-5] | [1-5] | [1-5] |
| [Criterion 4] | [w] | [1-5] | [1-5] | [1-5] |
| [Criterion 5] | [w] | [1-5] | [1-5] | [1-5] |
| **Weighted Total** | | **[sum]** | **[sum]** | **[sum]** |

*Weighted total = sum of (weight x score) for each criterion.*

## Analysis

*Discuss the key differentiators that the numbers alone do not capture.*

- **[Option A]**: [Key strengths and weaknesses not fully reflected in scores]
- **[Option B]**: [Key strengths and weaknesses]
- **[Option C]**: [Key strengths and weaknesses]

## Risks Per Option

*Identify the most significant risks for each option.*

| Option | Risk | Likelihood | Impact | Mitigation |
|--------|------|-----------|--------|------------|
| [Option A] | [Risk description] | Low / Medium / High | Low / Medium / High | [How to address] |
| [Option B] | [Risk description] | [Likelihood] | [Impact] | [Mitigation] |
| [Option C] | [Risk description] | [Likelihood] | [Impact] | [Mitigation] |

## Recommendation

*State the recommended option with rationale, or indicate this is presented without recommendation.*

[Recommended option and why, OR "Presented without recommendation -- decision deferred to [role/team]."]

## Definition of Done

- [ ] Decision context and constraints are clearly stated
- [ ] Criteria are defined with weights justified by project priorities
- [ ] All viable options are included and scored
- [ ] Scores are based on evidence, not assumptions
- [ ] Risks are identified for each option
- [ ] Analysis captures qualitative factors beyond the scores
- [ ] Matrix reviewed by at least one stakeholder before final decision
