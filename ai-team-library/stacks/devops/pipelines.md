# CI/CD Pipelines

Standards for continuous integration and continuous delivery pipelines.
GitHub Actions is the primary CI/CD platform. Deviations require an ADR.

---

## Defaults

- **Platform:** GitHub Actions (self-hosted runners for builds exceeding 10 min).
- **Trigger model:** Push to `main` triggers deploy to staging. Tags (`v*`) trigger
  production deploy. Pull requests trigger build + test only.
- **Artifact format:** Container images tagged with git SHA and semantic version.
- **Timeout:** Every job has an explicit `timeout-minutes`. Default cap is 15 min.
- **Concurrency:** Use `concurrency` groups to cancel superseded runs on the same branch.

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: Setup runtime
        uses: actions/setup-node@v4  # or setup-python, etc.
        with:
          node-version-file: .node-version
      - name: Install dependencies
        run: npm ci
      - name: Lint
        run: npm run lint
      - name: Test
        run: npm test -- --coverage
      - name: Build artifact
        run: npm run build
```

---

## Do / Don't

- **Do** keep pipeline definitions in the repo alongside the code they build.
- **Do** pin action versions to a full SHA, not a mutable tag.
  `uses: actions/checkout@b4ffde65f...` not `uses: actions/checkout@v4`.
- **Do** separate build, test, lint, and deploy into distinct jobs with explicit
  dependencies (`needs:`).
- **Do** cache dependencies (pip cache, npm cache, Docker layer cache).
- **Don't** put secrets in pipeline YAML. Use GitHub Secrets or a vault.
- **Don't** allow pipelines that only run on `main` -- PRs must get the same checks.
- **Don't** use `continue-on-error: true` without a documented reason.
- **Don't** run deploy steps directly in a PR pipeline.

---

## Common Pitfalls

1. **Flaky tests blocking deploys.** Quarantine flaky tests with a label; fix them
   within one sprint or delete them. Never add `retry` to mask instability.
2. **Monolith pipelines.** A single 45-minute job means slow feedback. Split into
   parallel jobs: lint, unit test, integration test, build.
3. **No artifact provenance.** If you cannot trace a running container back to a
   specific commit, your pipeline is incomplete. Tag images with the git SHA.
4. **Drift between PR checks and deploy checks.** The deploy pipeline should reuse
   the same build artifact that passed PR checks, not rebuild from scratch.
5. **Secret sprawl.** Secrets added ad-hoc to individual repos. Use organization-level
   secrets or a centralized vault with OIDC federation.

---

## Pipeline Stages (Recommended Order)

```
checkout → install → lint → unit-test → build → integration-test → publish → deploy
```

Each stage produces a clear pass/fail. Later stages depend on earlier ones.

```yaml
# Multi-stage deploy example
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4
      - name: Build and push image
        id: meta
        run: |
          TAG="${GITHUB_SHA::8}"
          docker build -t registry.example.com/app:$TAG .
          docker push registry.example.com/app:$TAG
          echo "tags=$TAG" >> "$GITHUB_OUTPUT"

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: deploy.sh --env staging --tag ${{ needs.build.outputs.image-tag }}

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production   # requires manual approval
    steps:
      - name: Deploy to production
        run: deploy.sh --env production --tag ${{ needs.build.outputs.image-tag }}
```

---

## Alternatives

| Tool              | When to consider                                    |
|-------------------|-----------------------------------------------------|
| GitLab CI         | GitLab-hosted repos, need built-in registry          |
| Azure DevOps      | Deep Azure ecosystem integration                     |
| CircleCI          | Complex parallelism or orb ecosystem                 |
| Buildkite         | High-volume builds needing self-hosted agent control |

---

## Checklist

- [ ] Every repo has a CI workflow that runs on PRs and `main`
- [ ] Action versions are pinned to commit SHAs
- [ ] Jobs have explicit `timeout-minutes`
- [ ] Concurrency groups prevent redundant parallel runs
- [ ] Artifacts are tagged with git SHA for traceability
- [ ] Secrets are never hardcoded in workflow files
- [ ] Cache steps are configured for dependency installation
- [ ] Deploy jobs use GitHub Environments with protection rules
- [ ] Pipeline runs are visible and linked from PR status checks
- [ ] Flaky test quarantine process is documented and enforced
