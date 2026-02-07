# Security Engineer -- Outputs

This document enumerates every artifact the Security Engineer is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Threat Model

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Threat Model                                       |
| **Cadence**        | One per component or feature handling sensitive data |
| **Template**       | `personas/security-engineer/templates/threat-model.md` |
| **Format**         | Markdown                                           |

**Description.** A structured analysis of the threats a component or feature
faces, the assets at risk, the attack vectors, and the mitigations in place or
required. The threat model is the foundation of all other security work -- it
tells the team what they are defending and against whom.

**Quality Bar:**
- Assets are identified and ranked by sensitivity (e.g., user credentials >
  session tokens > usage analytics).
- Threat actors are characterized with realistic capabilities, not just
  "attacker." Distinguish between unauthenticated external attackers,
  authenticated users abusing their access, and compromised internal services.
- Each threat has: a description, the asset at risk, the attack vector, the
  likelihood (Low/Medium/High), the impact (Low/Medium/High), and the
  mitigation (existing or required).
- Mitigations are specific and actionable: "Implement rate limiting of 10
  requests/minute on the login endpoint" not "Add rate limiting."
- The model uses a recognized methodology (STRIDE, DREAD, or attack trees).
- Data flow diagrams identify trust boundaries where input validation and
  authorization checks are required.
- The model is reviewed by the Architect for completeness and the Developer
  for feasibility of mitigations.

**Downstream Consumers:** Architect (for design decisions), Developer (for
security requirements), Tech QA (for security test cases), Team Lead (for
risk-based prioritization).

---

## 2. Security Review

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Security Review Report                             |
| **Cadence**        | Per PR or change set touching security-critical code |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown or PR comment                             |

**Description.** A focused review of code or configuration changes for security
implications. Security reviews are triggered by changes to authentication,
authorization, cryptography, data handling, input parsing, or infrastructure
configuration.

**Required Sections:**
1. **Scope** -- What was reviewed (files, components, configuration).
2. **Findings** -- Each finding with: description, severity (Critical, High,
   Medium, Low, Informational), affected code location, and recommended fix.
3. **Positive Observations** -- Security practices done well. Reinforcing good
   behavior is as important as catching bad behavior.
4. **Verdict** -- Approve, Approve with Conditions (list the conditions), or
   Block (list the blocking findings that must be resolved).

**Quality Bar:**
- Every finding references a specific code location (file and line range).
- Severity is calibrated to actual exploitability, not theoretical worst case.
- Recommended fixes are concrete: "Use parameterized queries instead of string
  concatenation in `UserRepository.findByEmail()`" not "Fix SQL injection."
- The review covers the OWASP Top 10 categories relevant to the change.
- Blocking findings have clear resolution criteria.

**Downstream Consumers:** Developer (for remediation), Code Quality Reviewer
(for review decisions), Team Lead (for risk tracking).

---

## 3. Vulnerability Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Vulnerability Report                               |
| **Cadence**        | As vulnerabilities are discovered or reported       |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A detailed report of a specific vulnerability found in the
system, whether through code review, dependency scanning, penetration testing,
or external disclosure. The report provides enough information for the team to
understand the risk and remediate it.

**Required Sections:**
1. **Summary** -- One sentence describing the vulnerability.
2. **Severity** -- Using CVSS or equivalent scoring, with justification.
3. **Affected Component** -- Specific service, endpoint, library, or
   configuration.
4. **Attack Scenario** -- Step-by-step description of how an attacker could
   exploit this vulnerability. Be specific about preconditions and required
   access level.
5. **Impact** -- What an attacker gains: data access, privilege escalation,
   denial of service, code execution.
6. **Remediation** -- Specific fix with code examples or configuration changes.
   Include both the immediate fix and any defense-in-depth improvements.
7. **Workaround** -- If a fix cannot be deployed immediately, what temporary
   mitigation reduces the risk?
8. **Timeline** -- Discovery date, disclosure date, expected fix date.

**Quality Bar:**
- The attack scenario is reproducible by the development team.
- Severity scoring accounts for the actual deployment context, not just the
  generic vulnerability description.
- Remediation includes a verification step: how to confirm the fix works.
- Related vulnerabilities (same class of bug elsewhere in the codebase) are
  investigated and noted.

**Downstream Consumers:** Developer (for remediation), Team Lead (for
prioritization), DevOps-Release (for emergency patching if needed).

---

## 4. Dependency Audit

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Dependency Security Audit                          |
| **Cadence**        | Once per cycle; additionally when major dependencies change |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** An assessment of the security posture of the project's
third-party dependencies. Identifies known vulnerabilities, outdated packages,
and supply chain risks.

**Required Sections:**
1. **Scan Results** -- Output from dependency scanning tools (npm audit,
   pip-audit, dotnet list package --vulnerable, or equivalent), summarized by
   severity.
2. **Action Items** -- For each finding: upgrade path, alternative package, or
   acceptance rationale.
3. **Supply Chain Risks** -- Dependencies with concerning signals: unmaintained
   packages, single-maintainer projects, recent ownership changes.
4. **License Review** -- Any dependencies with licenses incompatible with the
   project's license.

**Quality Bar:**
- All Critical and High severity vulnerabilities have a resolution plan with
  a deadline.
- "Accept risk" decisions include a documented rationale and an expiration
  date for re-evaluation.
- The audit covers both direct and transitive dependencies.
- Scan tooling is automated and runs in CI.

**Downstream Consumers:** Developer (for dependency updates), Team Lead (for
risk tracking), Architect (for technology decisions).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository or filed in the issue tracker.
- Threat models live in `docs/security/` alongside the components they analyze.
- Security reviews may be inline PR comments for small changes or standalone
  documents for large reviews.
- Vulnerability reports for Critical and High severity are communicated to the
  Team Lead immediately upon discovery, not batched for end-of-cycle reporting.
- Use the threat model template when it exists. Consistency in threat modeling
  makes review and comparison across components possible.
