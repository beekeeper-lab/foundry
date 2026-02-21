# Skill: IP & Licensing Analysis

## Description

Performs intellectual property and licensing analysis for software projects, covering
open source license compatibility, software patents, trade secrets, copyright
ownership, and contributor license agreements (CLAs). The skill evaluates a
project's IP posture by examining dependencies, contributions, and licensing
declarations, then produces a structured assessment with risks, recommendations,
and actionable remediation steps. This is the Legal Counsel persona's primary
analytical tool for IP and licensing matters.

## Trigger

- Invoked by the `/ip-licensing` slash command.
- Called by the Legal Counsel persona when a project introduces new dependencies, changes its license, or onboards external contributors.
- Should be re-run when the dependency tree changes significantly or when new contribution agreements are needed.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| project_context | File path | Yes | `ai/context/project.md` or equivalent describing the project's purpose, domain, and distribution model |
| dependency_manifest | File path | Yes | Package manifest (e.g., `pyproject.toml`, `package.json`, `Cargo.toml`) listing project dependencies |
| project_license | String | No | The project's declared outbound license (e.g., "MIT", "Apache-2.0", "GPL-3.0-only"); detected from LICENSE file if not provided |
| contribution_policy | File path | No | Existing CLA, DCO, or contributor guidelines (e.g., `CONTRIBUTING.md`) |
| patent_concerns | String | No | Specific patent-related questions or known patent encumbrances to evaluate |
| scope | String | No | Limit analysis to a specific area (e.g., "license-compatibility", "cla-review", "trade-secrets") |

## Process

### Phase 1: Project IP Inventory

1. **Identify the outbound license** -- Determine the project's declared license from the LICENSE file, package manifest, or SPDX headers. Verify consistency across all license declarations (README, manifest, file headers). Flag any discrepancies.

2. **Catalog inbound dependencies** -- Parse the dependency manifest to produce a complete list of direct and transitive dependencies. For each dependency, identify its license using SPDX identifiers. Flag dependencies with no license, custom licenses, or licenses that could not be determined.

3. **Map copyright ownership** -- Identify who owns the copyright in the project's codebase:
   - Original authors and their employment status (work-for-hire vs. individual)
   - Third-party code incorporated (vendored, copied, or forked)
   - Generated code (AI-generated, code generators) and its copyright implications
   - Contribution history and whether contributors assigned or retained copyright

### Phase 2: License Compatibility Analysis

4. **Evaluate license compatibility** -- For each inbound dependency license, determine compatibility with the project's outbound license using these rules:
   - **Permissive to permissive** (MIT, BSD, ISC, Apache-2.0): Generally compatible; verify attribution requirements are met.
   - **Permissive to copyleft** (MIT → GPL): Compatible; permissive code can be included in copyleft projects.
   - **Copyleft to permissive** (GPL → MIT): **Incompatible**; copyleft obligations propagate and prevent relicensing under a permissive license.
   - **Weak copyleft** (LGPL, MPL-2.0): Compatible when used as a library with dynamic linking; incompatible when modified and statically linked without source disclosure.
   - **Network copyleft** (AGPL-3.0): Triggers disclosure obligations for network-accessible services, even without binary distribution.
   - **Apache-2.0 and GPL-2.0-only**: **Incompatible** due to patent retaliation clause conflict; Apache-2.0 is compatible with GPL-3.0-or-later.
   - **Dual-licensed dependencies**: Evaluate each license option; use the compatible one and document the choice.
   - **Custom or proprietary licenses**: Require manual legal review; flag as high risk.

5. **Check attribution and notice requirements** -- Verify that all required attributions, copyright notices, and license texts are included in the project's distribution artifacts. Common requirements:
   - MIT/BSD: Include copyright notice and license text in distributions.
   - Apache-2.0: Include NOTICE file, copyright notice, and license text; state changes to Apache-licensed files.
   - GPL/LGPL: Include complete corresponding source code offer; preserve copyright notices.
   - MPL-2.0: Distribute modified MPL files under MPL; may combine with other licenses at the project level.

### Phase 3: Patent and Trade Secret Assessment

6. **Assess patent exposure** -- Evaluate patent-related risks:
   - **Patent grants in licenses**: Apache-2.0 includes an explicit patent grant; MIT and BSD do not. Identify dependencies where patent exposure is not covered by the license.
   - **Patent retaliation clauses**: Apache-2.0 and GPL-3.0 include patent retaliation (license terminates if the licensee initiates patent litigation). Document which dependencies carry this clause.
   - **Known patent encumbrances**: If `patent_concerns` input is provided, evaluate the specific patents against the project's functionality. Identify potential freedom-to-operate issues.
   - **Standard-essential patents (SEPs)**: If the project implements standards (e.g., codecs, protocols), flag potential SEP exposure and FRAND licensing obligations.

7. **Evaluate trade secret protections** -- Assess whether the project's distribution model and licensing are consistent with trade secret protection:
   - Open source distribution eliminates trade secret protection for disclosed code.
   - SaaS/hosted models may preserve trade secret status for server-side code not distributed to users.
   - Identify any proprietary algorithms, business logic, or data that should remain confidential and verify they are not inadvertently exposed through open source dependencies, debug logs, or API responses.
   - Review `.gitignore`, build configurations, and distribution packaging to ensure confidential material is excluded.

### Phase 4: Contributor Agreements and Governance

8. **Review contributor license agreements** -- Evaluate the project's contributor governance:
   - **No CLA/DCO**: Contributors retain copyright; project has an implied license from the contribution. Risk: contributor could revoke or dispute the license grant. Suitable only for permissive-licensed projects with low litigation risk.
   - **Developer Certificate of Origin (DCO)**: Lightweight attestation (Signed-off-by) that the contributor has the right to submit the code under the project's license. Lower friction than CLA; does not transfer copyright.
   - **Contributor License Agreement (CLA)**: Formal agreement granting the project a license to the contribution (or assigning copyright). Provides stronger legal protection but adds friction. Evaluate whether a CLA is needed based on project size, contribution model, and risk tolerance.
   - **Copyright assignment**: Contributor transfers copyright to the project entity. Strongest protection but highest friction; appropriate for foundations or projects that may need to relicense.
   - Recommend the appropriate mechanism based on the project's governance model, risk tolerance, and distribution strategy.

9. **Assess inbound contribution compliance** -- For existing contributions, verify:
   - All contributions have the required sign-off or CLA on file.
   - Third-party code brought in by contributors is license-compatible.
   - AI-generated contributions are flagged and their IP implications documented (copyright status of AI-generated code varies by jurisdiction).

### Phase 5: Produce Assessment

10. **Compile the IP & licensing assessment** -- Produce the complete assessment document with:
    - Executive summary with overall IP risk level (Critical/High/Medium/Low).
    - License compatibility matrix (dependency × outbound license).
    - List of incompatible or high-risk dependencies with remediation options.
    - Patent exposure summary.
    - Trade secret posture evaluation.
    - CLA/DCO recommendation with rationale.
    - Attribution compliance checklist.
    - Prioritized action items with owners and deadlines.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| ip_assessment | Markdown file | Complete IP & licensing assessment with compatibility matrix, risks, and recommendations |
| license_matrix | Section in assessment | Dependency-by-dependency license compatibility table with SPDX identifiers and status |
| attribution_checklist | Section in assessment | Checklist of attribution and notice requirements with compliance status |
| action_items | Section in assessment | Prioritized remediation items for identified IP risks |

## Quality Criteria

- Every direct dependency is evaluated for license compatibility with the project's outbound license, using SPDX identifiers.
- License compatibility determinations cite the specific clause or interaction that drives the conclusion (e.g., "GPL-3.0 Section 5(c) requires source distribution"), not just a compatible/incompatible label.
- Patent exposure assessment distinguishes between licenses with explicit patent grants (Apache-2.0) and those without (MIT, BSD).
- Trade secret analysis is specific to the project's distribution model (open source, SaaS, hybrid) and identifies concrete exposure vectors.
- CLA/DCO recommendation includes a rationale tied to the project's governance model, contributor base, and risk tolerance.
- Attribution checklist is actionable: each item specifies what must be included, where, and in what format.
- Every Critical or High risk has at least one specific remediation option with concrete steps.
- The assessment does not provide legal advice; it frames analysis as risk identification and recommendations for legal review.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `NoDependencyManifest` | No package manifest found or provided | Provide the path to the project's dependency manifest (e.g., `pyproject.toml`, `package.json`) |
| `NoProjectLicense` | Project has no declared license and none could be detected | Add a LICENSE file to the project root with the intended license; consult stakeholders on license choice |
| `UnresolvableLicense` | A dependency's license could not be determined from its package metadata | Manually inspect the dependency's repository for license information; flag for legal review if ambiguous |
| `ScopeNotFound` | The specified scope does not match a recognized analysis area | Use one of: "license-compatibility", "patents", "trade-secrets", "copyright", "cla-review", or omit for full analysis |
| `ConflictingLicenseDeclarations` | Project declares different licenses in different locations (e.g., LICENSE says MIT but manifest says Apache-2.0) | Reconcile license declarations to a single consistent license across all project files |

## Dependencies

- Project context and dependency manifest from the project repository
- SPDX License List for standardized license identification
- Compliance / Risk Analyst persona for regulatory overlay (e.g., export control, data protection implications of licensing)
- Security Engineer persona for patent and vulnerability intersection (e.g., dependencies with known CVEs that also have licensing issues)
- Architect persona for understanding the distribution model and component boundaries
