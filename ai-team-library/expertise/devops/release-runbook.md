# Release Runbook

Standards for versioning, releasing, and rolling back deployments.
Every release is repeatable, auditable, and reversible.

---

## Defaults

- **Versioning:** Semantic Versioning (semver). `MAJOR.MINOR.PATCH`.
- **Tagging:** Git tags trigger production release pipelines. Tags are annotated,
  not lightweight.
- **Changelog:** Auto-generated from conventional commits. Maintained in `CHANGELOG.md`.
- **Rollback:** Every deployment must support rollback to the previous version within
  5 minutes. Rollback is a deployment of the previous known-good artifact, not a
  code revert.
- **Release cadence:** Continuous delivery to staging. Production releases weekly or
  on-demand with approval.

---

## Do / Don't

- **Do** use conventional commits (`feat:`, `fix:`, `chore:`, `breaking:`) to
  automate changelogs and version bumps.
- **Do** tag releases from `main` only. Never tag from a feature branch.
- **Do** include a rollback step in every deployment pipeline.
- **Do** deploy with canary or blue-green strategy in production.
- **Do** document the blast radius of each release (which services, which users).
- **Don't** release on Fridays or before holidays unless it is a critical hotfix.
- **Don't** skip staging. Hotfixes go through staging with an expedited approval.
- **Don't** delete old container image tags. Retain at least the last 10 releases
  for rollback.
- **Don't** combine infrastructure changes and application changes in a single release.

---

## Common Pitfalls

1. **No rollback plan.** The team discovers rollback is impossible after a failed
   deploy because database migrations are irreversible. Solution: write all migrations
   as forward-compatible. Test rollback in staging before every release.
2. **Manual version bumps.** Developer forgets to bump the version, or bumps it wrong.
   Solution: automate version calculation from conventional commits.
3. **Big-bang releases.** Weeks of changes deployed at once. Debugging failures is
   near impossible. Solution: release small, release often.
4. **Changelog is always out of date.** Solution: generate it automatically from
   commit history. No manual changelog editing.
5. **Rollback restores code but not data.** Schema changes make the old code
   incompatible. Solution: separate schema migrations from code deploys. Deploy
   schema first (backward-compatible), then code, then remove old schema.

---

## Release Pipeline

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]

jobs:
  validate-tag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify tag is on main
        run: |
          BRANCH=$(git branch -r --contains ${{ github.ref }} | grep 'origin/main')
          if [ -z "$BRANCH" ]; then
            echo "Tag must be on main branch" && exit 1
          fi

  build-and-publish:
    needs: validate-tag
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build container image
        run: |
          VERSION=${GITHUB_REF_NAME#v}
          docker build -t registry.example.com/app:$VERSION .
          docker tag registry.example.com/app:$VERSION registry.example.com/app:latest
          docker push registry.example.com/app:$VERSION
          docker push registry.example.com/app:latest

  deploy-production:
    needs: build-and-publish
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy with canary
        run: |
          VERSION=${GITHUB_REF_NAME#v}
          deploy.sh --env production --tag $VERSION --strategy canary --weight 10
      - name: Smoke test canary
        run: smoke-test.sh --target canary.example.com
      - name: Promote canary to full
        run: deploy.sh --env production --tag $VERSION --strategy canary --weight 100
```

---

## Rollback Procedure

```bash
#!/usr/bin/env bash
# rollback.sh -- Roll back to the previous release
set -euo pipefail

CURRENT=$(kubectl get deployment app -o jsonpath='{.spec.template.spec.containers[0].image}')
PREVIOUS=$(kubectl rollout history deployment/app --revision=$(($(kubectl rollout history deployment/app | tail -2 | head -1 | awk '{print $1}') )))

echo "Current:  $CURRENT"
echo "Rolling back to previous revision..."

kubectl rollout undo deployment/app
kubectl rollout status deployment/app --timeout=120s

echo "Rollback complete. Run smoke tests to verify."
```

Key principle: rollback deploys a known-good artifact. It does not revert commits
or cherry-pick fixes under pressure.

---

## Database Migration Strategy

Migrations and code deploys are separate events:

1. **Phase 1 -- Expand:** Deploy migration that adds new columns/tables. Old code
   continues to work (backward-compatible).
2. **Phase 2 -- Migrate:** Deploy new code that writes to new schema.
3. **Phase 3 -- Contract:** After verification period, deploy migration that removes
   old columns (only when rollback window has passed).

This pattern ensures you can always roll back the code without schema conflicts.

---

## Alternatives

| Tool                    | When to consider                               |
|-------------------------|------------------------------------------------|
| semantic-release        | Fully automated npm/GitHub releases            |
| release-please (Google) | PR-based release workflow for GitHub           |
| Argo Rollouts           | Kubernetes-native canary and blue-green deploys|
| Flux / ArgoCD           | GitOps-based deployment for Kubernetes         |

---

## Checklist

- [ ] Conventional commit format is enforced (commitlint or CI check)
- [ ] Version is calculated automatically from commit history
- [ ] Releases are tagged from `main` with annotated git tags
- [ ] Changelog is auto-generated and included in GitHub Release notes
- [ ] Container images retain at least 10 previous versions
- [ ] Production deploys use canary or blue-green strategy
- [ ] Rollback can be executed within 5 minutes
- [ ] Database migrations are backward-compatible (expand/migrate/contract)
- [ ] Rollback is tested in staging before every production release
- [ ] Post-deploy smoke tests run automatically
- [ ] On-call is notified before and after production deploys
