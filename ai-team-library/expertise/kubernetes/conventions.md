# Kubernetes Stack Conventions

Non-negotiable defaults for Kubernetes workloads on this team. Targets
Kubernetes 1.28+ with cloud-agnostic manifests. Deviations require an ADR
with justification. "I prefer it differently" is not justification.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| K8s Version          | 1.28+ (latest stable)                  | ADR               |
| Manifest Format      | Plain YAML manifests                    | ADR               |
| Package Manager      | Helm 3                                  | ADR               |
| Container Runtime    | containerd                              | ADR               |
| Image Registry       | Private registry (no Docker Hub in prod)| Never             |
| Resource Limits      | Always set requests and limits          | Never             |
| Health Checks        | Liveness + readiness probes on every pod| Never             |
| Namespace Strategy   | One namespace per service per env       | ADR               |
| Config Management    | ConfigMaps + Secrets (external secrets) | ADR               |
| Pod Disruption       | PodDisruptionBudget on all prod services| Never             |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| Plain YAML           | Kustomize            | Environment overlays with minor diffs     |
| Helm 3               | Kustomize            | Simple apps needing only overlays         |
| Helm 3               | Jsonnet / cdk8s      | Complex programmatic manifest generation  |
| containerd           | CRI-O                | OpenShift or CRI-O-native clusters        |
| ConfigMaps           | Sealed Secrets / ESO | External secret management required       |
| kubectl apply        | ArgoCD / Flux        | GitOps continuous delivery                |

---

## Manifest Structure

```
k8s/
  base/
    namespace.yaml
    deployment.yaml
    service.yaml
    configmap.yaml
    hpa.yaml
    pdb.yaml
    networkpolicy.yaml
  overlays/
    dev/
      kustomization.yaml
      patches/
    staging/
      kustomization.yaml
      patches/
    production/
      kustomization.yaml
      patches/
  charts/
    app/
      Chart.yaml
      values.yaml
      templates/
```

**Rules:**
- Base manifests define the canonical workload. Overlays patch per environment.
- Never hardcode environment-specific values in base manifests.
- Use Kustomize or Helm values for environment differentiation.
- One resource per YAML file. Do not bundle multiple resources in a single file
  with `---` separators except for tightly coupled pairs (e.g., Service + Deployment
  in dev-only quick-start).

---

## Labels and Annotations

```yaml
metadata:
  labels:
    app.kubernetes.io/name: order-service
    app.kubernetes.io/version: "1.4.2"
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: ecommerce
    app.kubernetes.io/managed-by: helm
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

**Rules:**
- Use the `app.kubernetes.io/` label taxonomy on every resource.
- `app.kubernetes.io/name` is mandatory on all resources.
- `app.kubernetes.io/version` must match the container image tag.
- Use annotations for tooling metadata (Prometheus, Istio, cert-manager).
- Never use labels for data that changes frequently; labels are indexed.

---

## Resource Management

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Rules:**
- Always set both `requests` and `limits` for CPU and memory.
- Requests define scheduling guarantees. Set to the p50 steady-state usage.
- Memory limits should be 2-4x the request to handle spikes without OOM kills.
- CPU limits are optional in some strategies but always set requests.
- Use `LimitRange` to enforce defaults at the namespace level.
- Use `ResourceQuota` to cap total consumption per namespace.
- Never set CPU requests equal to limits unless latency-critical (Guaranteed QoS).

```yaml
# LimitRange — enforce per-pod defaults and caps.
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: order-service
spec:
  limits:
    - default:
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      type: Container
```

---

## Pod Spec Best Practices

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  labels:
    app.kubernetes.io/name: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: order-service
  template:
    metadata:
      labels:
        app.kubernetes.io/name: order-service
    spec:
      serviceAccountName: order-service
      automountServiceAccountToken: false
      terminationGracePeriodSeconds: 30
      containers:
        - name: order-service
          image: registry.example.com/order-service:1.4.2
          ports:
            - containerPort: 8080
              protocol: TCP
          env:
            - name: LOG_LEVEL
              value: "info"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: order-db-credentials
                  key: password
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 15
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 3
          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
            failureThreshold: 30
            periodSeconds: 2
```

**Rules:**
- Always use a dedicated `ServiceAccount`. Never use the `default` account.
- Set `automountServiceAccountToken: false` unless the pod needs API access.
- Always use image tags with specific versions or digests. Never use `:latest`.
- Define `livenessProbe`, `readinessProbe`, and `startupProbe` for every container.
- Use `startupProbe` for slow-starting apps to avoid premature liveness kills.
- Set `terminationGracePeriodSeconds` to match the app's graceful shutdown time.
- Pull secrets from Secrets, not environment variables or ConfigMaps.

---

## Namespaces

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: order-service-prod
  labels:
    app.kubernetes.io/part-of: ecommerce
    environment: production
    pod-security.kubernetes.io/enforce: restricted
```

**Rules:**
- One namespace per service per environment: `<service>-<env>`.
- Apply Pod Security Standards labels at the namespace level.
- Use `ResourceQuota` on every production namespace.
- Never deploy workloads to `default`, `kube-system`, or `kube-public`.

---

## Do / Don't

### Do
- Pin image versions with SHA digests in production: `image: registry.example.com/app@sha256:abc123`.
- Use `PodDisruptionBudget` for all production deployments with `minAvailable` or `maxUnavailable`.
- Define anti-affinity rules to spread replicas across nodes and zones.
- Use `topologySpreadConstraints` for even distribution across failure domains.
- Set `revisionHistoryLimit` to a reasonable number (3-5) to limit etcd bloat.
- Use `preStop` lifecycle hooks for graceful connection draining.
- Run containers as non-root with a read-only root filesystem.

### Don't
- Use `:latest` tags. They are non-deterministic and break rollback.
- Deploy without resource requests and limits. Unbounded pods cause noisy-neighbor problems.
- Store secrets in ConfigMaps or plain environment variables in manifests.
- Use `hostNetwork`, `hostPID`, or `hostIPC` unless absolutely required (and document why).
- Run privileged containers in production. Use fine-grained capabilities instead.
- Skip health checks. Pods without probes receive traffic before they're ready.
- Hardcode replica counts. Use HPA for dynamic scaling.

---

## Common Pitfalls

1. **OOMKilled pods** — Memory limits set too low relative to actual usage. Profile
   the application under load before setting limits. Set limits to 2-4x the request.
2. **CrashLoopBackOff from liveness probe** — Liveness probe fires before the app
   finishes starting. Use `startupProbe` with a generous `failureThreshold` for
   slow-starting applications.
3. **Evicted pods on node pressure** — Pods without resource requests are
   BestEffort QoS and evicted first. Always set requests to get Burstable or
   Guaranteed QoS.
4. **Broken rolling updates** — `maxSurge` and `maxUnavailable` both set to 0
   deadlocks the rollout. Set `maxSurge: 1, maxUnavailable: 0` for zero-downtime
   or `maxSurge: 0, maxUnavailable: 1` for resource-constrained clusters.
5. **ConfigMap/Secret changes not propagating** — Deployments don't restart when a
   ConfigMap changes. Use a checksum annotation or Reloader to trigger rollouts.
6. **DNS resolution failures** — `ndots:5` default causes excessive DNS lookups for
   external domains. Set `ndots: 2` or use FQDNs with trailing dots.
7. **Zombie processes** — Container PID 1 doesn't reap children by default. Use
   `shareProcessNamespace: true` or a proper init system (tini, dumb-init).

---

## Checklist

- [ ] All images use specific version tags or SHA digests (no `:latest`).
- [ ] Resource `requests` and `limits` set on every container.
- [ ] `livenessProbe`, `readinessProbe`, and `startupProbe` defined.
- [ ] Dedicated `ServiceAccount` per workload; `automountServiceAccountToken: false`.
- [ ] `PodDisruptionBudget` configured for production deployments.
- [ ] `app.kubernetes.io/*` labels applied to all resources.
- [ ] Namespace-level `ResourceQuota` and `LimitRange` in place.
- [ ] Pod Security Standards enforced at namespace level (`restricted` for prod).
- [ ] Anti-affinity or `topologySpreadConstraints` spread pods across zones.
- [ ] `terminationGracePeriodSeconds` matches app graceful shutdown time.
- [ ] No secrets in ConfigMaps, plain env vars, or committed manifests.
- [ ] `revisionHistoryLimit` set (3-5) on Deployments.
