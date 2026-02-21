# Kubernetes Operations

Standards for scaling, monitoring, upgrades, operators, and day-2 operations.
Cloud-agnostic patterns for production Kubernetes clusters.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Autoscaling          | HPA (CPU/memory metrics)                | ADR               |
| Monitoring           | Prometheus + Grafana                    | ADR               |
| Log Aggregation      | Cluster-level (Fluentd/Fluent Bit)      | ADR               |
| Deployment Strategy  | RollingUpdate                           | ADR               |
| Cluster Upgrades     | One minor version at a time             | Never             |
| Operators            | Only for stateful workloads (DB, MQ)    | ADR               |
| Backup               | Velero for cluster state                | ADR               |
| Cost Management      | Resource requests = scheduling budget   | Never             |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| HPA                  | KEDA                 | Event-driven or queue-based scaling       |
| HPA                  | VPA                  | Right-sizing pods (not horizontal scale)  |
| Prometheus           | Datadog / New Relic  | Managed monitoring preferred              |
| RollingUpdate        | Blue-Green           | Zero-downtime with instant rollback       |
| RollingUpdate        | Canary (Argo/Flagger)| Progressive delivery with metrics gates   |
| Fluentd              | Vector               | High-throughput log pipelines             |
| Velero               | Kasten K10           | Application-aware backup/restore          |

---

## Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service
  namespace: order-service-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 2
  maxReplicas: 20
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 25
          periodSeconds: 120
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

**Rules:**
- Set `minReplicas` >= 2 for production workloads (availability).
- Set CPU target at 70% utilization as a starting point. Tune based on load testing.
- Configure `scaleDown.stabilizationWindowSeconds` to prevent flapping (300s default).
- Scale up aggressively, scale down conservatively.
- Use `autoscaling/v2` API for multiple metrics and custom metrics support.
- Do not set `replicas` in Deployment when HPA is active — HPA controls the count.

---

## Pod Disruption Budgets

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service
  namespace: order-service-prod
spec:
  minAvailable: "50%"
  selector:
    matchLabels:
      app.kubernetes.io/name: order-service

# Alternative: maxUnavailable for large replica sets.
# spec:
#   maxUnavailable: 1
#   selector:
#     matchLabels:
#       app.kubernetes.io/name: order-service
```

**Rules:**
- Every production Deployment must have a PDB.
- Use `minAvailable` for small replica sets (2-5 pods).
- Use `maxUnavailable` for large replica sets (>10 pods) to allow faster drains.
- Never set `minAvailable` equal to `replicas` — it blocks node drains entirely.
- PDBs protect against voluntary disruptions (node drain, upgrades), not crashes.

---

## Deployment Strategies

```yaml
# RollingUpdate — default, zero-downtime.
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

**Strategy selection:**

| Strategy      | Use When                              | Trade-off                  |
|---------------|---------------------------------------|----------------------------|
| RollingUpdate | Default for all services              | Gradual; two versions coexist briefly |
| Recreate      | Stateful apps that can't run two versions | Downtime during rollout  |
| Blue-Green    | Instant rollback required             | 2x resource cost during deploy |
| Canary        | Risk-sensitive changes, gradual rollout| Requires traffic splitting |

**Rules:**
- Use `maxSurge: 1, maxUnavailable: 0` for zero-downtime rolling updates.
- Use `Recreate` only for workloads with exclusive resource locks (database
  migrations, single-writer patterns).
- Add `preStop` lifecycle hooks for graceful connection draining:

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sh", "-c", "sleep 5"]
```

---

## Monitoring and Observability

```yaml
# ServiceMonitor — Prometheus scrape configuration.
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: order-service
  namespace: order-service-prod
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: order-service
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
```

**Key metrics to monitor:**

| Metric                           | Alert Threshold            |
|----------------------------------|----------------------------|
| Container restarts               | > 3 in 15 minutes          |
| Pod CPU utilization              | > 85% sustained 10 min     |
| Pod memory utilization           | > 90% sustained 5 min      |
| Pod pending (unschedulable)      | > 0 for 5 minutes          |
| HPA at max replicas              | Sustained 15 minutes       |
| PVC usage                        | > 85%                      |
| Node NotReady                    | Any node for 5 minutes     |
| API server request latency (p99) | > 1s                       |

**Rules:**
- Expose `/metrics` endpoint on every service (Prometheus format).
- Use `ServiceMonitor` CRDs for Prometheus Operator scrape config.
- Set up alerts for the metrics above as a baseline.
- Use Grafana dashboards per service and per namespace.
- Retain metrics for 15 days minimum, 90 days for capacity planning.
- Use labels to correlate metrics across services (`app`, `namespace`, `pod`).

---

## Operators

```yaml
# Example: Using a PostgreSQL operator.
apiVersion: acid.zalan.do/v1
kind: postgresql
metadata:
  name: order-db
  namespace: order-service-prod
spec:
  teamId: "order-team"
  numberOfInstances: 3
  volume:
    size: 50Gi
    storageClass: ssd
  postgresql:
    version: "16"
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: "2"
      memory: 4Gi
```

**Rules:**
- Use operators only for stateful workloads: databases, message queues, caches.
- Prefer managed cloud services over self-managed operators when available.
- Evaluate operators for maturity, maintenance status, and community support.
- Never write a custom operator for problems solved by Deployments + Jobs.
- Pin operator versions and test upgrades in staging before production.

---

## Cluster Upgrades

**Upgrade process:**
1. Review Kubernetes changelog for deprecations and breaking changes.
2. Upgrade control plane one minor version at a time (1.28 → 1.29, not 1.28 → 1.30).
3. Run `kubectl convert` or `kubent` to detect deprecated API usage.
4. Upgrade staging cluster first. Run full test suite.
5. Upgrade production control plane.
6. Drain and upgrade worker nodes (rolling, one node pool at a time).
7. Verify all workloads healthy post-upgrade.

**Rules:**
- Never skip minor versions. Upgrade sequentially.
- Test upgrades in a non-production cluster first.
- Run API deprecation checks (`kubent`) before upgrading.
- Maintain n-1 version compatibility for client tools (`kubectl`, Helm).
- Schedule upgrade windows with PDB-aware node drains.

---

## Resource Right-Sizing

```bash
# Check actual vs requested resources.
kubectl top pods -n order-service-prod

# Use VPA in recommendation mode to get suggestions.
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: order-service-vpa
  namespace: order-service-prod
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  updatePolicy:
    updateMode: "Off"  # Recommendation only, no auto-apply.
```

**Rules:**
- Review resource utilization monthly. Over-provisioning wastes money.
- Use VPA in `Off` mode for recommendations without automatic changes.
- Set requests to p50 usage and limits to p99 + headroom.
- Never set requests higher than limits.
- Use `kubectl top` and Prometheus metrics to baseline actual usage.

---

## Do / Don't

### Do
- Set up HPA for all stateless services with `minReplicas >= 2`.
- Create PodDisruptionBudgets for all production Deployments.
- Use `maxSurge: 1, maxUnavailable: 0` for zero-downtime rolling updates.
- Monitor pod restarts, CPU, memory, and HPA saturation.
- Upgrade clusters one minor version at a time with staging validation.
- Use `preStop` hooks for graceful connection draining.
- Run VPA in recommendation mode to right-size resources.

### Don't
- Set HPA `minReplicas: 1` in production — one pod means one failure away from outage.
- Set PDB `minAvailable` equal to replica count — it blocks all node drains.
- Use `Recreate` strategy for stateless services — it causes unnecessary downtime.
- Skip minor Kubernetes versions during upgrades.
- Deploy operators for every stateless workload — Deployments are simpler.
- Ignore resource right-sizing — over-provisioning costs compound.
- Use `kubectl edit` to change production resources — all changes via Git.

---

## Common Pitfalls

1. **HPA flapping** — Scale-down happens too fast, causing oscillation. Set
   `scaleDown.stabilizationWindowSeconds` to 300+ seconds.
2. **Node drain blocked by PDB** — PDB `minAvailable` set too high prevents
   node maintenance. Ensure PDB allows at least one pod disruption.
3. **Upgrade breaks deprecated APIs** — Kubernetes removes APIs after deprecation
   period. Run `kubent` before upgrading to find affected manifests.
4. **StatefulSet stuck on update** — StatefulSets update pods in reverse ordinal
   order. A stuck pod blocks all subsequent updates. Check pod health individually.
5. **HPA and VPA conflict** — Do not use HPA and VPA on the same metric (CPU).
   Use HPA for horizontal scaling and VPA in recommendation mode only.
6. **Rolling update causes downtime** — App doesn't handle SIGTERM gracefully.
   Add `preStop` sleep and handle SIGTERM in the application for connection draining.
7. **Persistent volume stuck in Terminating** — PV finalizer prevents deletion
   while a pod still references it. Delete the pod first, then the PVC.

---

## Checklist

- [ ] HPA configured for all stateless production workloads.
- [ ] `minReplicas >= 2` for all production HPAs.
- [ ] PodDisruptionBudget defined for every production Deployment.
- [ ] Deployment strategy set (`RollingUpdate` with `maxUnavailable: 0`).
- [ ] `preStop` lifecycle hooks configured for graceful shutdown.
- [ ] Prometheus `ServiceMonitor` scraping `/metrics` on every service.
- [ ] Alerts configured for restarts, CPU, memory, HPA max, pending pods.
- [ ] Grafana dashboards per service and per namespace.
- [ ] Cluster upgrade plan documented (sequential minor versions).
- [ ] VPA running in recommendation mode for resource right-sizing.
- [ ] All production changes applied via Git (no `kubectl edit` or `kubectl apply` ad-hoc).
