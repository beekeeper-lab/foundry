# Definition of Done

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | [YYYY-MM-DD]                   |
| Owner         | [DoD author or team lead]      |
| Related links | [issue/PR/ADR URLs]            |
| Status        | Draft / Reviewed / Approved    |

## Purpose

*A shared agreement on what "done" means at each level of work. Prevents ambiguity, reduces rework, and ensures consistent quality. Customize each section to fit your project's needs.*

---

## Story-Level Definition of Done

*Every user story must meet these criteria before it can be considered complete.*

- [ ] Acceptance criteria met and verified
- [ ] Code written and committed to the feature branch
- [ ] Unit tests written and passing
- [ ] Code reviewed and approved by at least one other team member
- [ ] No new linting or static analysis warnings introduced
- [ ] Documentation updated if behavior changed (inline comments, API docs)
- [ ] Tested in a development or staging environment
- [ ] Accessibility requirements met (if UI change)
- [ ] Product owner or stakeholder has accepted the result

---

## Feature-Level Definition of Done

*A feature (spanning multiple stories) must meet these criteria before it is considered complete.*

- [ ] All constituent stories meet the story-level DoD
- [ ] Integration tests pass across all stories in the feature
- [ ] End-to-end user flow tested and verified
- [ ] Performance benchmarks met (response time, resource usage)
- [ ] Security review completed (if applicable)
- [ ] Feature flag or rollout strategy configured (if applicable)
- [ ] User-facing documentation or help content updated
- [ ] Cross-browser or cross-platform testing completed (if UI)
- [ ] Feature demo delivered to stakeholders

---

## Release-Level Definition of Done

*A release must meet these criteria before it can be deployed to production.*

- [ ] All included features meet the feature-level DoD
- [ ] Full regression test suite passes
- [ ] Release notes written and reviewed
- [ ] Database migrations tested in staging (if applicable)
- [ ] Deployment runbook updated and reviewed
- [ ] Rollback procedure documented and verified
- [ ] Monitoring and alerting configured for new functionality
- [ ] Compliance and audit requirements satisfied (if applicable)
- [ ] Stakeholder sign-off obtained
- [ ] Release tagged in version control

---

## Customization Notes

*Adapt these checklists to your project. Consider adding or removing items based on:*

- Team size and structure
- Regulatory or compliance requirements
- Deployment frequency and strategy
- Whether the project includes a UI, API, or both
- Security sensitivity of the system
