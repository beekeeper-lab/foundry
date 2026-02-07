# Threat Modeling

Standards for identifying, analyzing, and mitigating threats during design.
Threat modeling happens before code is written, not after a breach.

---

## Defaults

- **Methodology:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure,
  Denial of Service, Elevation of Privilege).
- **When:** Every new feature, every new service, every significant architecture change.
- **Participants:** Architect, lead developer, security engineer. Product owner for
  risk acceptance decisions.
- **Output:** Threat model document stored alongside the design doc in the repo.
  Each threat has a severity, mitigation, and owner.

---

## STRIDE Categories

| Category               | Threat question                                     | Typical mitigation           |
|------------------------|-----------------------------------------------------|------------------------------|
| **S**poofing           | Can an attacker pretend to be another user/service?  | Authentication, mTLS         |
| **T**ampering          | Can data be modified in transit or at rest?           | Integrity checks, signatures |
| **R**epudiation        | Can an actor deny performing an action?              | Audit logging, non-repudiation|
| **I**nformation Disclosure | Can sensitive data be exposed?                   | Encryption, access controls  |
| **D**enial of Service  | Can the system be made unavailable?                  | Rate limiting, scaling       |
| **E**levation of Privilege | Can a user gain unauthorized access?             | Authorization, least privilege|

---

## Do / Don't

- **Do** create a data flow diagram (DFD) before applying STRIDE. You cannot threat
  model what you cannot see.
- **Do** enumerate trust boundaries. Every point where data crosses a boundary is an
  attack surface.
- **Do** assign a severity to each threat (Critical, High, Medium, Low) using impact
  and likelihood.
- **Do** track mitigations as actionable work items, not vague statements.
- **Do** review the threat model when the architecture changes.
- **Don't** threat model in a vacuum. Include developers who know the system internals.
- **Don't** accept risk without explicit sign-off from a product owner or security lead.
- **Don't** treat threat modeling as a one-time ceremony. Update it as the system evolves.
- **Don't** model only external threats. Insider threats and supply chain attacks matter.

---

## Common Pitfalls

1. **Analysis paralysis.** The team models every conceivable threat and never ships.
   Solution: focus on the top 10 threats by severity. Iterate in later sessions.
2. **DFD is too abstract.** A single box labeled "backend" hides all the interesting
   attack surface. Solution: decompose to the level of individual services, data stores,
   and external integrations.
3. **Mitigations are "we'll fix it later."** Threats are identified but never addressed.
   Solution: every mitigation becomes a tracked ticket with a sprint assignment.
4. **No follow-up.** The model is created once and forgotten. A new API endpoint is
   added six months later with no threat review. Solution: make threat model updates
   a required checklist item for architecture changes.
5. **Confusing threats with vulnerabilities.** A threat is what an attacker wants to
   do. A vulnerability is a weakness they exploit. Keep them separate in your model.

---

## Threat Modeling Process

### Step 1: Draw the Data Flow Diagram

```
  [User Browser]
       |
       | HTTPS (TLS 1.3)
       v
  [API Gateway]  ---- trust boundary ----
       |
       | JWT (internal)
       v
  [Order Service] ----> [Database]
       |                    ^
       | gRPC (mTLS)        | encrypted at rest
       v                    |
  [Payment Service] ----> [Audit Log]
       |
       | HTTPS
       v
  [External Payment Provider]  ---- trust boundary ----
```

### Step 2: Apply STRIDE to Each Element

```markdown
## Threat: Spoofed API requests (Spoofing)
- **Target:** API Gateway
- **Attack:** Attacker forges JWT tokens to impersonate users.
- **Severity:** Critical
- **Mitigation:** Validate JWT signature with RS256. Verify issuer, audience,
  and expiry. Reject tokens signed with "none" algorithm.
- **Owner:** @backend-team
- **Status:** Mitigated (JWT validation middleware deployed)

## Threat: Tampered order data (Tampering)
- **Target:** Order Service -> Database
- **Attack:** SQL injection modifies order totals.
- **Severity:** High
- **Mitigation:** Parameterized queries for all database access. ORM-only
  data access layer. No raw SQL.
- **Owner:** @backend-team
- **Status:** Mitigated (ORM enforced, raw SQL blocked by linter rule)
```

### Step 3: Prioritize and Track

Rank threats by `impact x likelihood`. Critical and High threats must be mitigated
before the feature launches. Medium threats are tracked for the next iteration.

---

## Threat Model Document Template

```markdown
# Threat Model: [Feature/Service Name]
**Date:** YYYY-MM-DD
**Participants:** [names]
**Status:** Draft | Reviewed | Accepted

## System Overview
[Brief description and link to architecture diagram]

## Data Flow Diagram
[Embed or link to DFD]

## Trust Boundaries
1. External internet -> API Gateway
2. API Gateway -> Internal services
3. Internal services -> External providers

## Threats
| ID  | Category | Description         | Severity | Mitigation       | Owner | Status    |
|-----|----------|---------------------|----------|------------------|-------|-----------|
| T01 | Spoofing | Forged JWT tokens   | Critical | JWT RS256 validation | @team | Mitigated |
| T02 | Tampering| SQL injection       | High     | Parameterized queries | @team | Mitigated |

## Accepted Risks
[List any threats accepted with justification and sign-off]
```

---

## Alternatives

| Methodology       | When to consider                                    |
|-------------------|-----------------------------------------------------|
| PASTA             | Risk-centric, business-impact focused modeling      |
| Attack Trees      | Analyzing a specific, known attack goal in depth    |
| LINDDUN           | Privacy-focused threat modeling                     |
| VAST              | Scaling threat modeling across large organizations  |

---

## Checklist

- [ ] Data flow diagram is created before threat analysis begins
- [ ] Trust boundaries are explicitly identified and labeled
- [ ] STRIDE is applied to each component and data flow
- [ ] Each threat has severity, mitigation, owner, and status
- [ ] Critical and High threats are mitigated before feature launch
- [ ] Risk acceptance decisions have explicit sign-off
- [ ] Threat model is stored in the repository alongside design docs
- [ ] Threat model is reviewed when architecture changes
- [ ] Mitigations are tracked as work items with sprint assignments
- [ ] The team reviews the threat model at least once per quarter
