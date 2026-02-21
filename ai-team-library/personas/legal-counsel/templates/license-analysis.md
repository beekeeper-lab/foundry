# IP & Licensing Analysis

## Metadata

| Field         | Value                                          |
|---------------|-------------------------------------------------|
| Date          | [YYYY-MM-DD]                                    |
| Analyst       | [Name / role of reviewing counsel]              |
| Related links | [Dependency manifest, project license, prior analyses] |
| Status        | Draft / Reviewed / Final                        |

## Project Licensing Context

| Field                  | Value                                     |
|------------------------|-------------------------------------------|
| Project license        | [e.g., MIT, Apache-2.0, Proprietary]      |
| Distribution model     | [SaaS / Desktop / Library / Internal only] |
| Modification policy    | [Are third-party components modified?]     |
| Bundling policy        | [Are components bundled or dynamically linked?] |

## Dependency License Inventory

*List all third-party dependencies with their license identifiers.*

| # | Component | Version | License (SPDX) | Usage | Modified | Compatibility | Status |
|---|-----------|---------|----------------|-------|----------|---------------|--------|
| 1 | [Package name] | [X.Y.Z] | [MIT] | [Bundled / Linked / SaaS] | [Yes / No] | [Compatible / Conflict / Review needed] | [Compliant / Action required] |
| 2 | [Package name] | [X.Y.Z] | [Apache-2.0] | [Usage] | [Y/N] | [Compatibility] | [Status] |
| 3 | [Package name] | [X.Y.Z] | [GPL-3.0-only] | [Usage] | [Y/N] | [Compatibility] | [Status] |

## License Obligation Summary

*For each license type in use, summarize the obligations.*

### [License Name (SPDX ID)]

- **Attribution required:** [Yes / No — include copyright notice and license text]
- **Source disclosure:** [Yes / No — conditions under which source must be provided]
- **Derivative work provisions:** [What constitutes a derivative work under this license]
- **Patent grant:** [Yes / No — scope of patent license granted]
- **Copyleft scope:** [None / File-level / Library-level / Strong copyleft]
- **Redistribution conditions:** [Conditions for redistribution]
- **Restrictions:** [Any field-of-use or other restrictions]

## Compatibility Analysis

*Assess whether all dependency licenses are compatible with the project's outbound license.*

| Dependency License | Project License | Compatible | Rationale |
|-------------------|-----------------|------------|-----------|
| [MIT]             | [Project license] | [Yes] | [MIT is permissive, compatible with all outbound licenses] |
| [GPL-3.0-only]   | [Project license] | [No — if proprietary] | [GPL requires derivative works to be GPL-licensed] |

## Attribution Requirements

*Compile all attribution obligations into a single actionable list.*

| # | Component | Required Attribution | Location |
|---|-----------|---------------------|----------|
| 1 | [Package] | [Copyright notice + license text] | [NOTICE file / About page / Documentation] |
| 2 | [Package] | [Attribution text] | [Location] |

## Findings and Recommendations

| # | Finding | Severity | Recommendation |
|---|---------|----------|----------------|
| 1 | [Describe the IP or licensing issue] | High / Medium / Low | [Specific action to resolve] |
| 2 | [Finding] | [Severity] | [Recommendation] |

## Definition of Done

- [ ] All third-party dependencies inventoried with license identifiers
- [ ] License compatibility assessed for every dependency
- [ ] Copyleft obligations documented for applicable licenses
- [ ] Attribution requirements compiled into actionable list
- [ ] Conflicts flagged with remediation recommendations
- [ ] Analysis reviewed by a second party
