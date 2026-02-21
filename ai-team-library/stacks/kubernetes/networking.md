# Kubernetes Networking

Standards for Services, Ingress, DNS, load balancing, and service mesh
configuration. Cloud-agnostic defaults with notes on provider-specific
considerations.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Service Type         | `ClusterIP` (internal)                  | ADR               |
| Ingress Controller   | NGINX Ingress Controller                | ADR               |
| TLS Termination      | Ingress-level with cert-manager         | ADR               |
| DNS                  | CoreDNS (cluster default)               | Never             |
| Service Mesh         | None (add only when needed)             | ADR               |
| Load Balancing       | Ingress controller (not per-service LB) | ADR               |
| Certificate Mgmt     | cert-manager with Let's Encrypt         | ADR               |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| NGINX Ingress        | Traefik              | Middleware-heavy routing requirements     |
| NGINX Ingress        | Envoy Gateway        | Gateway API adoption                     |
| NGINX Ingress        | Cloud LB (ALB/NLB)   | Cloud-native with provider annotations   |
| No service mesh      | Istio                | mTLS, traffic shaping, observability      |
| No service mesh      | Linkerd              | Lightweight mTLS and observability        |
| cert-manager         | Manual certs         | Air-gapped environments                  |
| Ingress              | Gateway API          | Multi-tenant or advanced routing          |

---

## Services

```yaml
# ClusterIP — default for internal communication.
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: order-service-prod
  labels:
    app.kubernetes.io/name: order-service
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: order-service
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
    - name: grpc
      port: 9090
      targetPort: 9090
      protocol: TCP

---
# Headless service — for StatefulSet DNS or direct pod addressing.
apiVersion: v1
kind: Service
metadata:
  name: order-db
  namespace: order-service-prod
spec:
  type: ClusterIP
  clusterIP: None
  selector:
    app.kubernetes.io/name: order-db
  ports:
    - name: postgres
      port: 5432
      targetPort: 5432
```

**Rules:**
- Default to `ClusterIP`. Use `NodePort` only for development.
- Never use `LoadBalancer` per service in production. Route through Ingress.
- Always name ports (`name: http`, `name: grpc`). Named ports are required by
  Istio and improve readability.
- Use `targetPort` to decouple internal container ports from service ports.
- Use headless services (`clusterIP: None`) for StatefulSets and direct pod DNS.

---

## Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: order-service
  namespace: order-service-prod
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-example-com-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /orders
            pathType: Prefix
            backend:
              service:
                name: order-service
                port:
                  number: 80
          - path: /orders
            pathType: Exact
            backend:
              service:
                name: order-service
                port:
                  number: 80
```

**Rules:**
- Always use `ingressClassName` (not the deprecated `kubernetes.io/ingress.class`
  annotation).
- Enforce TLS on all production ingresses. Use cert-manager for automated
  certificate provisioning.
- Set `ssl-redirect: "true"` to force HTTPS.
- Use `Prefix` path type for API routes and `Exact` for specific endpoints.
- Configure rate limiting at the ingress level for public-facing endpoints.
- Set `proxy-body-size` to prevent oversized request attacks.

---

## Gateway API (Future Standard)

```yaml
# Gateway — cluster-level entry point.
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: main-gateway
  namespace: gateway-system
spec:
  gatewayClassName: nginx
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls:
        mode: Terminate
        certificateRefs:
          - name: api-example-com-tls
      allowedRoutes:
        namespaces:
          from: Selector
          selector:
            matchLabels:
              gateway-access: "true"

---
# HTTPRoute — namespace-level routing.
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: order-service-route
  namespace: order-service-prod
spec:
  parentRefs:
    - name: main-gateway
      namespace: gateway-system
  hostnames:
    - "api.example.com"
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /orders
      backendRefs:
        - name: order-service
          port: 80
```

**Rules:**
- Gateway API is the successor to Ingress. Adopt when the team is ready.
- Gateways are cluster infrastructure (managed by platform team).
- HTTPRoutes are namespace-scoped (managed by service teams).
- Use `allowedRoutes` to control which namespaces can attach to a Gateway.

---

## DNS and Service Discovery

```yaml
# Pod DNS config — reduce unnecessary DNS lookups.
spec:
  dnsConfig:
    options:
      - name: ndots
        value: "2"
  dnsPolicy: ClusterFirst
```

**Service DNS patterns:**
- Same namespace: `order-service` or `order-service.order-service-prod`
- Cross namespace: `order-service.order-service-prod.svc.cluster.local`
- External: Use FQDN with trailing dot: `api.external.com.`

**Rules:**
- Use short names for same-namespace communication.
- Use FQDNs with `.svc.cluster.local` suffix for cross-namespace calls.
- Set `ndots: 2` to reduce DNS query amplification for external domains.
- Use `ExternalName` services to alias external endpoints with internal DNS names.
- Never hardcode pod IPs. Always use Service DNS names.

---

## TLS and Certificates

```yaml
# cert-manager ClusterIssuer — automated TLS with Let's Encrypt.
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v2.api.letsencrypt.org/directory
    email: platform@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            ingressClassName: nginx

---
# Certificate — explicit certificate resource.
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: api-example-com
  namespace: order-service-prod
spec:
  secretName: api-example-com-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - api.example.com
    - "*.api.example.com"
  renewBefore: 720h  # 30 days before expiry
```

**Rules:**
- Use cert-manager for all TLS certificate lifecycle management.
- Use `ClusterIssuer` for org-wide issuers, `Issuer` for namespace-scoped.
- Set `renewBefore` to rotate certificates well before expiry.
- Use ACME HTTP-01 solver for publicly accessible endpoints.
- Use DNS-01 solver for wildcard certificates or private endpoints.

---

## Do / Don't

### Do
- Use `ClusterIP` services by default. Route external traffic through Ingress.
- Enforce TLS on all production Ingresses with cert-manager.
- Name all service ports for compatibility with service meshes and debugging.
- Set `ndots: 2` in pod DNS config to reduce DNS lookup amplification.
- Use Network Policies to restrict traffic between services (see security.md).
- Plan for Gateway API adoption as the Ingress successor.

### Don't
- Create a `LoadBalancer` Service per microservice. Use a shared Ingress controller.
- Hardcode pod IPs or node IPs in application configuration.
- Skip TLS for internal service-to-service communication in multi-tenant clusters.
- Use `ExternalIPs` on Services — it bypasses load balancing and is a security risk.
- Expose services on `NodePort` in production (port range 30000-32767 is fragile).
- Ignore DNS TTLs when migrating services — stale caches cause outages.

---

## Common Pitfalls

1. **DNS resolution timeout with high ndots** — Default `ndots: 5` causes 4-5
   DNS queries per external lookup. Set `ndots: 2` or use FQDNs with trailing dots.
2. **Ingress TLS secret missing** — Ingress references a TLS secret that doesn't
   exist or hasn't been provisioned by cert-manager. Check certificate readiness
   with `kubectl get certificate`.
3. **Service port name mismatch** — Istio requires named ports matching protocol
   (`http-`, `grpc-`, `tcp-`). Unnamed ports default to TCP and break routing.
4. **Session affinity not configured** — WebSocket or stateful connections need
   `sessionAffinity: ClientIP` or Ingress sticky sessions annotation.
5. **Cross-namespace service access blocked** — NetworkPolicy blocks cross-namespace
   traffic by default with deny-all policies. Add explicit egress/ingress rules.
6. **Ingress path conflicts** — Multiple Ingresses with overlapping paths on the
   same host cause unpredictable routing. Use a single Ingress per host or
   distinct path prefixes.

---

## Checklist

- [ ] All services use `ClusterIP` type (no direct `LoadBalancer` per service).
- [ ] Ingress controller deployed and `ingressClassName` specified.
- [ ] TLS enforced on all production Ingresses with `ssl-redirect: "true"`.
- [ ] cert-manager provisioning and renewing certificates automatically.
- [ ] All service ports named (`http`, `grpc`, `metrics`).
- [ ] Pod DNS `ndots` set to 2 for services making external calls.
- [ ] Cross-namespace communication uses FQDN `.svc.cluster.local`.
- [ ] No hardcoded pod or node IPs in application configuration.
- [ ] Rate limiting configured on public-facing Ingresses.
- [ ] Gateway API evaluated for future adoption.
