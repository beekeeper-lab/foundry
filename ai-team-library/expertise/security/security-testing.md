# Security Testing

Standards for integrating security testing into the development lifecycle.
Security testing is continuous, automated, and part of the pipeline -- not a
periodic manual exercise.

---

## Defaults

- **SAST (Static Application Security Testing):** Runs on every PR. Blocks merge on
  Critical/High findings.
- **SCA (Software Composition Analysis):** Runs on every PR and on a daily schedule
  for new CVE disclosures.
- **DAST (Dynamic Application Security Testing):** Runs against staging after every
  deployment.
- **Secret scanning:** Pre-commit hook + CI pipeline check.
- **Baseline:** OWASP Top 10 coverage as the minimum for all testing tools.

---

## Testing Types

### SAST -- Find Bugs in Your Code
Static analysis scans source code for vulnerabilities without executing it. Catches
SQL injection, XSS, insecure deserialization, hardcoded secrets.

```yaml
# GitHub Actions SAST example with Semgrep
- name: SAST scan
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/owasp-top-ten
      p/security-audit
```

### SCA -- Find Bugs in Your Dependencies
Scans dependency manifests and lock files against CVE databases. Most exploited
vulnerabilities come from known CVEs in third-party libraries.

```yaml
# GitHub Actions SCA example
- name: Dependency audit
  run: |
    # Python
    pip-audit --require-hashes -r requirements.lock

    # Node
    npm audit --audit-level=high

    # General (Trivy)
    trivy fs --severity HIGH,CRITICAL --exit-code 1 .
```

### DAST -- Find Bugs at Runtime
Dynamic analysis tests a running application by sending malicious requests. Catches
issues that static analysis misses: misconfigured headers, authentication bypasses,
CORS issues.

```yaml
# DAST with OWASP ZAP against staging
- name: DAST scan
  uses: zaproxy/action-full-scan@v0.9.0
  with:
    target: "https://staging.example.com"
    rules_file_name: "zap-rules.tsv"
    allow_issue_writing: false
```

---

## Do / Don't

- **Do** run SAST and SCA on every PR. Fast feedback prevents security debt.
- **Do** tune SAST rules to reduce false positives. A noisy scanner gets ignored.
- **Do** fail the build on Critical and High severity findings.
- **Do** maintain a suppression file for acknowledged false positives, with
  justification and expiry date for each suppression.
- **Do** run dependency scans on a schedule (daily) to catch newly disclosed CVEs.
- **Don't** treat security testing as a replacement for secure design. Testing finds
  bugs; design prevents categories of bugs.
- **Don't** suppress findings without a documented justification and review.
- **Don't** run DAST against production unless you have explicit authorization and
  controls in place.
- **Don't** rely on a single tool. SAST, SCA, and DAST find different classes of bugs.
- **Don't** ignore Medium findings indefinitely. Triage and schedule them.

---

## Common Pitfalls

1. **Scanner overload.** Three SAST tools, two SCA tools, all dumping hundreds of
   findings. Nobody reads any of them. Solution: pick one tool per category. Tune
   it. Own the output.
2. **False positive fatigue.** Developers suppress all findings because 80% are false
   positives. Solution: invest time in custom rules and suppressions. A well-tuned
   scanner with 20 real findings beats a default scanner with 500 noise findings.
3. **SCA findings with no upgrade path.** A critical CVE in a dependency, but the
   fix requires a major version bump that breaks your code. Solution: track these
   as tech debt with a remediation deadline. Consider patching or replacing the
   dependency.
4. **DAST runs too slow for CI.** A full DAST scan takes 2 hours and blocks deploys.
   Solution: run a baseline (fast) scan in CI and a full scan nightly or weekly.
5. **No triage process.** Findings accumulate in a dashboard nobody checks. Solution:
   security findings go through the same triage and sprint planning as bugs.

---

## Recommended Tool Stack

| Category          | Primary tool  | Alternatives                          |
|-------------------|---------------|---------------------------------------|
| SAST              | Semgrep       | CodeQL, SonarQube, Snyk Code          |
| SCA               | Trivy         | Snyk, Dependabot, pip-audit, npm audit|
| DAST              | OWASP ZAP     | Burp Suite, Nuclei                    |
| Secret scanning   | Gitleaks      | TruffleHog, git-secrets               |
| Container scanning| Trivy         | Grype, Snyk Container                 |

---

## Triage Severity Matrix

| Scanner severity | Response time       | Action                              |
|-----------------|---------------------|-------------------------------------|
| Critical        | Block merge / 24h   | Fix immediately or revert the change|
| High            | Block merge / 7 days| Fix in current sprint               |
| Medium          | 30 days             | Schedule in backlog                 |
| Low             | 90 days             | Address opportunistically           |

---

## Checklist

- [ ] SAST runs on every PR and blocks merge on Critical/High
- [ ] SCA runs on every PR and on a daily schedule
- [ ] DAST runs against staging after each deployment
- [ ] Secret scanning runs as a pre-commit hook and in CI
- [ ] Container images are scanned before deployment
- [ ] False positive suppressions include justification and expiry dates
- [ ] Security findings feed into the team's triage and sprint planning
- [ ] SAST rules are tuned to the project (custom rules where needed)
- [ ] A dependency update strategy exists for CVE remediation
- [ ] Quarterly review of scanner effectiveness (false positive rate, missed findings)
