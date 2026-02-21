# Microservices Service Mesh

Standards for service mesh adoption, mTLS, traffic management, and mesh
observability. A service mesh is not a default — adopt it when the complexity
is justified. See `conventions.md` for when to use a mesh versus simpler
alternatives.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Mesh Adoption        | No mesh (adopt only when justified)     | ADR               |
| Mesh Implementation  | Istio                                   | ADR               |
| mTLS                 | STRICT mode (mesh-wide)                 | Never             |
| Sidecar Injection    | Namespace-level auto-injection          | ADR               |
| Traffic Management   | VirtualService + DestinationRule        | ADR               |
| Canary Deployments   | Progressive traffic shifting (10→25→50→100%) | ADR          |
| Rate Limiting        | Mesh-level (Envoy filters)              | ADR               |
| Observability        | Mesh telemetry + OpenTelemetry          | ADR               |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| Istio                | Linkerd              | Simpler requirements, lower resource overhead |
| Istio                | Cilium Service Mesh  | eBPF-based, lower latency, no sidecars   |
| Istio                | Consul Connect       | Multi-cloud / non-Kubernetes environments |
| Sidecar proxy        | Ambient mesh (Istio) | Eliminate per-pod sidecar overhead        |
| VirtualService       | Gateway API (GAMMA)  | Standardized mesh routing (Kubernetes-native) |

### When to Adopt a Service Mesh

| Need                                    | Mesh Required? |
|-----------------------------------------|----------------|
| mTLS between all services               | Yes            |
| Fine-grained traffic control (canary, mirroring) | Yes   |
| Uniform resilience policies (retries, timeouts) | Consider |
| More than 20 services in production     | Consider       |
| Only 3-5 services                       | No — overkill  |
| Simple load balancing and health checks | No — use K8s   |

---

## mTLS (Mutual TLS)

### Mesh-Wide Strict mTLS

```yaml
# PeerAuthentication — enforce mTLS across the entire mesh.
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT

---
# Per-namespace override (e.g., allow plaintext for legacy service migration).
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: legacy-exception
  namespace: legacy-service
spec:
  mtls:
    mode: PERMISSIVE
```

**Rules:**
- Enable STRICT mTLS mesh-wide. All service-to-service traffic is encrypted.
- Use PERMISSIVE mode only during migration from non-mesh services. Set a deadline
  for migration to STRICT.
- The mesh handles certificate rotation automatically. Do not manage service TLS
  certificates manually.
- mTLS provides both encryption and mutual authentication — services verify each
  other's identity.
- Use `AuthorizationPolicy` to control which services can communicate (zero-trust).

### Authorization Policies

```yaml
# Only allow order-service to call payment-service.
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: payment-service-access
  namespace: payment-prod
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: payment-service
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/order-prod/sa/order-service"
      to:
        - operation:
            methods: ["POST"]
            paths: ["/v1/payments", "/v1/payments/*/refund"]
    - from:
        - source:
            principals:
              - "cluster.local/ns/admin-prod/sa/admin-service"
      to:
        - operation:
            methods: ["GET"]
            paths: ["/v1/payments/*"]
```

**Rules:**
- Default-deny: no traffic allowed unless explicitly permitted by AuthorizationPolicy.
- Scope authorization to specific HTTP methods and paths, not just service identity.
- Use service account principals for identity-based authorization.
- Review authorization policies as part of code review — they are security-critical.

---

## Traffic Management

### Canary Deployments

```yaml
# VirtualService — progressive traffic shifting for canary releases.
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: order-service
  namespace: order-prod
spec:
  hosts:
    - order-service
  http:
    - route:
        - destination:
            host: order-service
            subset: stable
          weight: 90
        - destination:
            host: order-service
            subset: canary
          weight: 10

---
# DestinationRule — define subsets for traffic splitting.
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: order-service
  namespace: order-prod
spec:
  host: order-service
  subsets:
    - name: stable
      labels:
        version: v1.4.2
    - name: canary
      labels:
        version: v1.5.0
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: DEFAULT
        maxRequestsPerConnection: 1000
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

**Rules:**
- Start canary at 10% traffic. Increase to 25%, 50%, 100% after observing metrics.
- Monitor error rate and latency for the canary subset before increasing traffic.
- Automate canary promotion with Flagger or Argo Rollouts.
- Always define outlier detection to eject unhealthy instances.
- Set connection pool limits to prevent a single destination from consuming all resources.

### Traffic Mirroring

```yaml
# Mirror production traffic to a shadow deployment for testing.
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: order-service
  namespace: order-prod
spec:
  hosts:
    - order-service
  http:
    - route:
        - destination:
            host: order-service
            subset: stable
      mirror:
        host: order-service
        subset: shadow
      mirrorPercentage:
        value: 10.0
```

**Rules:**
- Use traffic mirroring to test new versions with real production traffic without
  affecting users. Mirrored responses are discarded.
- Mirror a small percentage (5-10%) to avoid doubling infrastructure load.
- Ensure the shadow service does not write to production databases or send real
  notifications.

### Fault Injection (Testing)

```yaml
# Inject faults to test resilience — staging/test environments only.
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: inventory-service
  namespace: order-staging
spec:
  hosts:
    - inventory-service
  http:
    - fault:
        delay:
          percentage:
            value: 10
          fixedDelay: 3s
        abort:
          percentage:
            value: 5
          httpStatus: 503
      route:
        - destination:
            host: inventory-service
```

**Rules:**
- Never inject faults in production. Use staging or dedicated chaos environments.
- Test circuit breakers by injecting delays and 503 errors.
- Test timeout behavior by injecting delays exceeding the caller's timeout.
- Combine with observability to verify alerts fire correctly during fault injection.

---

## Mesh-Level Resilience

```yaml
# DestinationRule — mesh-level retries, timeouts, and circuit breaking.
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: inventory-service
  namespace: inventory-prod
spec:
  host: inventory-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 2s
      http:
        maxRequestsPerConnection: 100
        maxRetries: 3
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 30
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: "5xx,reset,connect-failure,retriable-4xx"
```

**Rules:**
- Configure resilience at the mesh level for uniform behavior across all services.
- Use mesh-level retries only if application-level retries are not configured.
  Do not stack both — this causes retry amplification.
- Outlier detection ejects unhealthy pods from the load balancing pool. Set
  `maxEjectionPercent` to avoid ejecting all instances during widespread issues.
- Set `perTryTimeout` on retries so each attempt has a bounded duration.

---

## Do / Don't

### Do
- Adopt a service mesh only when the complexity is justified (mTLS, traffic control, 20+ services).
- Enable STRICT mTLS mesh-wide for encryption and mutual authentication.
- Use AuthorizationPolicy for zero-trust service-to-service access control.
- Use canary deployments with progressive traffic shifting for safe rollouts.
- Monitor mesh control plane health (Istiod CPU, memory, xDS push latency).
- Test resilience patterns with mesh-level fault injection in staging.

### Don't
- Add a mesh to a system with fewer than 5 services. The overhead is not justified.
- Use PERMISSIVE mTLS in production long-term. It is a migration aid, not a final state.
- Stack mesh-level retries with application-level retries. Choose one layer.
- Inject faults in production. Use staging or dedicated chaos environments.
- Ignore sidecar resource consumption. Each Envoy sidecar uses CPU and memory.
- Skip authorization policies. mTLS authenticates identity but does not authorize access.
- Manage TLS certificates manually when the mesh automates rotation.

---

## Common Pitfalls

1. **Premature mesh adoption** — Adding Istio to a system with 3 services. The
   operational complexity (control plane, sidecars, CRDs) outweighs the benefits.
   Fix: start without a mesh. Adopt when mTLS or traffic control becomes essential.

2. **Retry amplification** — Application retries 3x and mesh retries 3x, causing 9x
   load on the downstream service. Fix: configure retries at one layer only —
   either application or mesh, not both.

3. **Sidecar resource starvation** — Envoy sidecars have no resource limits and
   compete with the application container for CPU and memory. Fix: set resource
   requests and limits on sidecar containers via `sidecar.istio.io/proxy*` annotations.

4. **PERMISSIVE mTLS in production** — Intended as a migration step but never moved
   to STRICT. Plaintext traffic flows unencrypted alongside mTLS.
   Fix: set a migration deadline and enforce STRICT after all services are onboarded.

5. **Missing authorization policies** — mTLS is enabled but any service can call any
   other service. Lateral movement is unrestricted.
   Fix: define default-deny AuthorizationPolicies and explicitly allow required paths.

6. **Control plane overload** — Too many configuration changes or too many sidecars
   overwhelm Istiod. xDS push latency increases, causing stale routing.
   Fix: monitor Istiod metrics, size the control plane for the number of sidecars.

---

## Checklist

- [ ] Service mesh adoption justified by an ADR with clear rationale.
- [ ] STRICT mTLS enabled mesh-wide; PERMISSIVE only for active migrations.
- [ ] AuthorizationPolicies enforce zero-trust (default deny, explicit allow).
- [ ] Sidecar injection enabled at namespace level with resource limits.
- [ ] Canary deployment strategy defined with progressive traffic shifting.
- [ ] Outlier detection configured to eject unhealthy instances.
- [ ] No stacked retries — retries configured at one layer only (app or mesh).
- [ ] Mesh control plane (Istiod) monitored for CPU, memory, and xDS latency.
- [ ] Fault injection tests run in staging to validate resilience patterns.
- [ ] Traffic mirroring used for shadow testing new versions.
- [ ] Mesh telemetry integrated with existing OpenTelemetry pipeline.
- [ ] Sidecar resource requests and limits set via pod annotations.
