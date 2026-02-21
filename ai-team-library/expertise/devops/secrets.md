# Secrets Management

Standards for storing, accessing, rotating, and auditing secrets.
No secret should ever exist in source code, logs, or unencrypted storage.

---

## Defaults

- **Primary store:** HashiCorp Vault for application secrets. GitHub Secrets for
  CI/CD pipeline secrets.
- **Access model:** Applications authenticate via OIDC or short-lived tokens.
  No long-lived API keys where avoidable.
- **Rotation policy:** Secrets rotate on a schedule (90 days max). Compromise
  triggers immediate rotation.
- **Encryption at rest:** All secret stores encrypt at rest with managed keys (KMS).

---

## Do / Don't

- **Do** use a secrets manager (Vault, AWS Secrets Manager, Azure Key Vault) for
  application runtime secrets.
- **Do** use GitHub organization-level secrets over repo-level secrets where the
  secret is shared across repos.
- **Do** scope secrets to the narrowest access possible (specific environment,
  specific job, specific repository).
- **Do** use OIDC federation for CI/CD to cloud providers instead of static credentials.
- **Do** audit secret access. Every read should produce a log entry.
- **Don't** commit secrets to version control. Ever. Not even "temporarily."
- **Don't** pass secrets as command-line arguments (they appear in process listings).
- **Don't** log secrets. Mask them in CI output with `::add-mask::`.
- **Don't** share secrets over Slack, email, or any unencrypted channel.
- **Don't** use the same secret value across environments.

---

## Common Pitfalls

1. **Secrets in `.env` files committed to git.** Even if removed later, they live in
   git history forever. Solution: `.env` in `.gitignore` from day one. Use
   `git-secrets` or `gitleaks` as a pre-commit hook.
2. **Overly broad IAM roles.** A CI job with `AdministratorAccess` because "it was
   easier." Solution: least-privilege IAM policies scoped to exactly what the job needs.
3. **No rotation plan.** Secrets are set once and forgotten. A leaked secret stays
   valid for years. Solution: automate rotation with Vault dynamic secrets or
   cloud-native rotation lambdas.
4. **Secrets in Docker images.** Build args or ENV instructions bake secrets into
   image layers. Solution: mount secrets at runtime, never at build time. Use
   Docker BuildKit secret mounts for build-time needs.
5. **Plain-text secrets in Terraform state.** Terraform state files contain resource
   attributes including secret values. Solution: encrypt state at rest, restrict
   state access to CI service accounts only.

---

## GitHub Actions OIDC Pattern

Eliminate static cloud credentials in CI by using OIDC federation.

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # required for OIDC
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-deploy
          aws-region: us-east-1
      - name: Deploy
        run: ./deploy.sh
```

---

## Vault Application Pattern

```python
# Application fetches secrets from Vault at startup
import hvac
import os

def get_db_credentials() -> dict:
    """Fetch short-lived database credentials from Vault."""
    client = hvac.Client(url=os.environ["VAULT_ADDR"])
    client.auth.approle.login(
        role_id=os.environ["VAULT_ROLE_ID"],
        secret_id=os.environ["VAULT_SECRET_ID"],
    )

    # Dynamic secret: Vault creates a temporary DB user
    response = client.secrets.database.generate_credentials(name="app-db-role")
    return {
        "username": response["data"]["username"],
        "password": response["data"]["password"],
        "ttl": response["lease_duration"],
    }
```

---

## Pre-commit Secret Scanning

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

Run in CI as a safety net:

```yaml
- name: Scan for secrets
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Alternatives

| Tool                  | When to consider                                  |
|-----------------------|---------------------------------------------------|
| AWS Secrets Manager   | AWS-native apps, automatic RDS rotation           |
| Azure Key Vault       | Azure-native apps                                 |
| GCP Secret Manager    | GCP-native apps                                   |
| SOPS                  | Encrypting secrets in git (GitOps workflows)      |
| Doppler               | SaaS secrets manager, quick onboarding            |

---

## Checklist

- [ ] `.gitignore` includes `.env`, `*.pem`, `*.key`, and credential files
- [ ] Pre-commit hook scans for secrets (gitleaks or git-secrets)
- [ ] CI pipeline scans for leaked secrets on every PR
- [ ] CI/CD uses OIDC federation -- no static cloud credentials
- [ ] Application secrets are fetched from a secrets manager at runtime
- [ ] Secrets are scoped per-environment (dev/staging/prod have separate values)
- [ ] Rotation schedule is documented and automated where possible
- [ ] Secret access is audited (Vault audit log, CloudTrail, etc.)
- [ ] Terraform state is encrypted at rest with restricted access
- [ ] No secrets appear in container images, logs, or CLI arguments
