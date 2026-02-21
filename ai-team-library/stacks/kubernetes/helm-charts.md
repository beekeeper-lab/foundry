# Kubernetes Helm Charts

Standards for Helm chart development, templating, and release management.
Targets Helm 3.12+. All charts must be lintable with `helm lint --strict`.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Helm Version         | Helm 3.12+                              | ADR               |
| Chart API Version    | `apiVersion: v2`                        | Never             |
| Chart Repository     | OCI registry (private)                  | ADR               |
| Values Schema        | `values.schema.json` for all charts     | Never             |
| Template Testing     | `helm-unittest` + `helm lint --strict`  | ADR               |
| Release Strategy     | `helm upgrade --install --atomic`       | ADR               |
| Dependency Mgmt      | `Chart.yaml` dependencies (not requirements.yaml) | Never  |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| Helm 3               | Kustomize            | No templating needed; only overlays       |
| Helm 3               | Jsonnet / Tanka      | Highly dynamic manifests with logic       |
| OCI registry         | ChartMuseum          | Legacy infrastructure without OCI support |
| `helm-unittest`      | `helm template` + kube-score | Lightweight validation only       |

---

## Chart Structure

```
charts/
  app-name/
    Chart.yaml              # Chart metadata, version, dependencies
    Chart.lock               # Locked dependency versions
    values.yaml              # Default values (documented)
    values.schema.json       # JSON Schema for values validation
    templates/
      _helpers.tpl           # Template helpers and partials
      deployment.yaml
      service.yaml
      configmap.yaml
      hpa.yaml
      pdb.yaml
      networkpolicy.yaml
      serviceaccount.yaml
      ingress.yaml
      NOTES.txt              # Post-install usage notes
    tests/
      test-connection.yaml   # Helm test pod
    ci/
      dev-values.yaml        # CI test values per environment
      prod-values.yaml
```

**Rules:**
- One chart per deployable service. Do not create monolithic umbrella charts.
- `Chart.yaml` must include `appVersion` matching the application release.
- `values.yaml` must have comments documenting every configurable value.
- `values.schema.json` enforces types, required fields, and allowed values.
- Never commit `Chart.lock` changes without reviewing dependency updates.

---

## Chart.yaml

```yaml
apiVersion: v2
name: order-service
description: Order processing service for the ecommerce platform
type: application
version: 1.4.2          # Chart version (SemVer, bump on chart changes)
appVersion: "2.1.0"     # Application version (matches container image)
maintainers:
  - name: platform-team
    email: platform@example.com
dependencies:
  - name: postgresql
    version: "13.2.x"
    repository: "oci://registry.example.com/charts"
    condition: postgresql.enabled
```

**Rules:**
- `version` follows SemVer and increments on every chart change.
- `appVersion` matches the deployed application version.
- Use `condition` on optional dependencies to allow disabling them.
- Pin dependency versions with ranges (`13.2.x`) not exact (`13.2.24`).

---

## Values Design

```yaml
# values.yaml — well-structured defaults with documentation.

# -- Number of pod replicas (overridden by HPA when enabled)
replicaCount: 2

image:
  # -- Container image repository
  repository: registry.example.com/order-service
  # -- Image pull policy
  pullPolicy: IfNotPresent
  # -- Image tag (defaults to Chart appVersion)
  tag: ""

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

autoscaling:
  # -- Enable Horizontal Pod Autoscaler
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

serviceAccount:
  # -- Create a dedicated ServiceAccount
  create: true
  # -- Annotations for the ServiceAccount (e.g., IAM role)
  annotations: {}
  # -- ServiceAccount name (generated if not set)
  name: ""

ingress:
  # -- Enable ingress resource
  enabled: false
  className: nginx
  annotations: {}
  hosts:
    - host: order-service.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []
```

**Rules:**
- Every value must have a `# --` comment for `helm-docs` generation.
- Use nested structures: `image.repository`, `resources.requests.cpu`.
- Boolean toggles (`enabled: false`) gate optional resources.
- Default to safe, minimal values. Production overrides via environment values files.
- Never put secrets in `values.yaml`. Use external secret references.

---

## Template Helpers

```yaml
# templates/_helpers.tpl

{{/*
Expand the name of the chart.
*/}}
{{- define "app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels applied to all resources.
*/}}
{{- define "app.labels" -}}
helm.sh/chart: {{ include "app.chart" . }}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Values.image.tag | default .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels (subset of common labels for matchLabels).
*/}}
{{- define "app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

**Rules:**
- Use `_helpers.tpl` for all reusable template logic.
- Truncate names to 63 characters (Kubernetes name limit).
- Separate selector labels from informational labels.
- Use `default` for fallback values rather than complex conditionals.

---

## Release Management

```bash
# Lint before every release.
helm lint charts/order-service --strict --values charts/order-service/ci/prod-values.yaml

# Dry-run to preview changes.
helm upgrade order-service charts/order-service \
  --namespace order-service-prod \
  --values production-values.yaml \
  --dry-run --diff

# Atomic release — rolls back automatically on failure.
helm upgrade --install order-service charts/order-service \
  --namespace order-service-prod \
  --values production-values.yaml \
  --atomic \
  --timeout 5m \
  --wait
```

**Rules:**
- Always use `--atomic` for production releases. It rolls back on failure.
- Always use `--wait` to ensure pods are ready before marking success.
- Set `--timeout` appropriate to the application's startup time.
- Use `helm diff` plugin to preview changes before applying.
- Never use `helm install` in CI/CD. Use `helm upgrade --install` for idempotency.
- Store release values in version control, never pass `--set` flags in CI.

---

## Do / Don't

### Do
- Validate all charts with `helm lint --strict` and `helm template` in CI.
- Use `values.schema.json` to catch invalid configuration early.
- Use `helm-unittest` for testing template output against expected YAML.
- Package charts as OCI artifacts and push to a private registry.
- Use `helm diff` to review changes before applying to production.
- Pin chart dependency versions and review updates explicitly.

### Don't
- Use `helm install` without `--atomic` in production.
- Pass secrets via `--set` flags (visible in process listing and shell history).
- Create umbrella charts that deploy entire platforms. One chart per service.
- Use `lookup` in templates — it breaks `helm template` and GitOps workflows.
- Skip `values.schema.json`. Invalid values cause runtime failures.
- Commit environment-specific values into the chart itself.

---

## Common Pitfalls

1. **Release stuck in PENDING_UPGRADE** — A failed release without `--atomic`
   leaves the release in a broken state. Fix with `helm rollback <release> <rev>`
   or `helm uninstall` and reinstall.
2. **Template rendering differs from apply** — `helm template` does not have
   cluster access, so `lookup` and capabilities checks behave differently.
   Avoid `lookup` in templates.
3. **Values merging surprises** — Helm deep-merges values files. A partial
   override of a nested object replaces the entire object. Use `--values`
   ordering carefully (last file wins).
4. **CRDs not upgraded** — Helm does not upgrade CRDs after initial install.
   Manage CRD lifecycle separately from the chart.
5. **Chart version not bumped** — OCI registries reject pushes with duplicate
   versions. Always bump `version` in `Chart.yaml` on every change.

---

## Checklist

- [ ] `Chart.yaml` has correct `version` and `appVersion`.
- [ ] `values.yaml` documents every value with `# --` comments.
- [ ] `values.schema.json` validates all required fields and types.
- [ ] `helm lint --strict` passes with no warnings.
- [ ] `helm-unittest` tests cover critical template branches.
- [ ] Chart packaged and pushed to OCI registry.
- [ ] Production releases use `--atomic --wait --timeout`.
- [ ] No secrets in `values.yaml` or passed via `--set`.
- [ ] Dependency versions pinned in `Chart.yaml` with `Chart.lock` committed.
- [ ] `NOTES.txt` provides post-install instructions.
