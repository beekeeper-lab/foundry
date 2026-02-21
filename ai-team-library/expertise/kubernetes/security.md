# Kubernetes Security

Non-negotiable security standards for Kubernetes workloads. Covers RBAC,
Pod Security Standards, network policies, secrets management, and supply chain
security. Cloud-agnostic. Deviations require an ADR with justification.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Pod Security         | Pod Security Standards (`restricted`)   | ADR               |
| RBAC                 | Namespace-scoped roles (least privilege)| Never             |
| Network Policy       | Default-deny ingress and egress         | Never             |
| Secrets              | External Secrets Operator (ESO)         | ADR               |
| Image Signing        | Cosign + admission policy              | ADR               |
| Admission Control    | Kyverno or OPA Gatekeeper              | ADR               |
| Service Accounts     | Dedicated per workload, no auto-mount  | Never             |
| Runtime Security     | Seccomp + AppArmor profiles            | ADR               |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| Pod Security Standards | OPA Gatekeeper     | Fine-grained custom policies beyond PSS  |
| Kyverno              | OPA Gatekeeper       | Team already invested in Rego            |
| ESO                  | Sealed Secrets       | No external secret store available        |
| ESO                  | Vault CSI Provider   | HashiCorp Vault as primary secret store   |
| Cosign               | Notary v2            | Registry-native signing required          |

---

## RBAC

```yaml
# Role — namespace-scoped, least privilege.
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: order-service-reader
  namespace: order-service-prod
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list"]

---
# RoleBinding — binds Role to ServiceAccount.
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: order-service-reader-binding
  namespace: order-service-prod
subjects:
  - kind: ServiceAccount
    name: order-service
    namespace: order-service-prod
roleRef:
  kind: Role
  name: order-service-reader
  apiGroup: rbac.authorization.k8s.io
```

**Rules:**
- Use `Role` + `RoleBinding` (namespace-scoped) by default. Use `ClusterRole`
  + `ClusterRoleBinding` only for cluster-wide resources.
- Grant the minimum verbs needed: `get`, `list`, `watch` for read-only; add
  `create`, `update`, `patch`, `delete` only when required.
- Never bind `cluster-admin` to application workloads.
- Never use wildcard `*` in `apiGroups`, `resources`, or `verbs`.
- Audit RBAC bindings quarterly. Remove unused bindings.
- Use `system:serviceaccount:<namespace>:<name>` format for cross-namespace
  bindings (rare; requires ADR).

---

## Pod Security Standards

```yaml
# Namespace — enforce restricted Pod Security Standard.
apiVersion: v1
kind: Namespace
metadata:
  name: order-service-prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

```yaml
# Pod spec — compliant with restricted PSS.
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: order-service
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
```

**Rules:**
- All production namespaces must enforce the `restricted` Pod Security Standard.
- Use `baseline` for development/staging if `restricted` is impractical.
- Set `runAsNonRoot: true` and specify a non-root `runAsUser`.
- Set `readOnlyRootFilesystem: true` and mount `emptyDir` for writable paths.
- Drop all capabilities (`drop: ["ALL"]`). Add back only what is required.
- Set `allowPrivilegeEscalation: false` on every container.
- Use `RuntimeDefault` seccomp profile at minimum.

---

## Network Policies

```yaml
# Default deny — block all ingress and egress.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: order-service-prod
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress

---
# Allow specific ingress — only from API gateway.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-from-gateway
  namespace: order-service-prod
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: order-service
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              app.kubernetes.io/name: api-gateway
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: api-gateway
      ports:
        - protocol: TCP
          port: 8080

---
# Allow egress — DNS + specific backends.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress-order-service
  namespace: order-service-prod
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: order-service
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    - to:
        - namespaceSelector:
            matchLabels:
              app.kubernetes.io/name: postgres
      ports:
        - protocol: TCP
          port: 5432
```

**Rules:**
- Start with default-deny for both ingress and egress in every namespace.
- Explicitly allow only required traffic paths.
- Always allow DNS egress (UDP/TCP 53 to kube-dns) or pods cannot resolve names.
- Use both `namespaceSelector` and `podSelector` for cross-namespace rules.
- Test network policies in staging before enforcing in production.
- Ensure the CNI plugin supports NetworkPolicy (Calico, Cilium, etc.).

---

## Secrets Management

```yaml
# ExternalSecret — pulls from external store (AWS SM, Vault, GCP SM).
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: order-db-credentials
  namespace: order-service-prod
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: cluster-secret-store
    kind: ClusterSecretStore
  target:
    name: order-db-credentials
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: /prod/order-service/db-password
    - secretKey: username
      remoteRef:
        key: /prod/order-service/db-username
```

**Rules:**
- Never store secrets in Git, ConfigMaps, or plain environment variables in manifests.
- Use External Secrets Operator to sync secrets from an external store.
- Set `refreshInterval` to rotate secrets without pod restarts.
- Use `creationPolicy: Owner` so the ExternalSecret owns the Kubernetes Secret.
- Encrypt etcd at rest for the cluster.
- Restrict Secret access via RBAC — only the owning service's ServiceAccount.

---

## Image Supply Chain Security

```bash
# Sign images with Cosign.
cosign sign --key cosign.key registry.example.com/order-service:1.4.2

# Verify signatures before admission.
cosign verify --key cosign.pub registry.example.com/order-service:1.4.2
```

```yaml
# Kyverno policy — require signed images.
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-cosign-signature
      match:
        any:
          - resources:
              kinds: ["Pod"]
      verifyImages:
        - imageReferences: ["registry.example.com/*"]
          attestors:
            - entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      ...
                      -----END PUBLIC KEY-----
```

**Rules:**
- Sign all production images with Cosign or Notary v2.
- Enforce signature verification via admission controller (Kyverno/Gatekeeper).
- Scan images for CVEs in CI (Trivy, Grype) and block critical/high findings.
- Use minimal base images (distroless, Alpine, or scratch).
- Never pull from public registries in production. Mirror approved images.

---

## Do / Don't

### Do
- Apply default-deny NetworkPolicies in every namespace before deploying workloads.
- Use Pod Security Standards at the `restricted` level for production.
- Run containers as non-root with read-only root filesystems.
- Rotate secrets automatically via External Secrets Operator.
- Sign and verify container images before deployment.
- Scan images for vulnerabilities in the CI pipeline.
- Audit RBAC bindings and remove unused permissions quarterly.

### Don't
- Use `cluster-admin` ClusterRoleBinding for application workloads.
- Store secrets in ConfigMaps, environment variables, or Git.
- Run containers as root or with `privileged: true`.
- Use wildcard `*` in RBAC rules.
- Skip network policies — "we'll add them later" means never.
- Disable Pod Security Standards to work around deployment failures.
- Pull images from unauthenticated public registries in production.

---

## Common Pitfalls

1. **Overly permissive RBAC** — ClusterRoleBindings with wildcard access grant
   far more than needed. Audit with `kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa>`.
2. **Network policies not enforced** — The CNI plugin must support NetworkPolicy.
   Flannel (default) does not. Use Calico, Cilium, or Antrea.
3. **Secrets visible in pod spec** — Kubernetes Secrets are base64-encoded, not
   encrypted. Anyone with pod read access can see them. Restrict with RBAC and
   encrypt etcd at rest.
4. **Privilege escalation via writable root FS** — An attacker in a container
   with a writable filesystem can modify binaries. Use `readOnlyRootFilesystem: true`.
5. **Service account token auto-mounted** — Default behavior mounts a token into
   every pod. Set `automountServiceAccountToken: false` unless API access is needed.
6. **Unsigned images deployed** — Without admission control, anyone can deploy
   any image. Enforce image signature verification in production.

---

## Checklist

- [ ] Default-deny NetworkPolicy applied to every namespace.
- [ ] Pod Security Standards enforced (`restricted` for prod, `baseline` for dev).
- [ ] All containers run as non-root with `readOnlyRootFilesystem: true`.
- [ ] Capabilities dropped (`drop: ["ALL"]`); only required caps added back.
- [ ] `automountServiceAccountToken: false` on all pods not needing API access.
- [ ] RBAC uses namespace-scoped Roles with least-privilege verbs.
- [ ] No wildcard `*` in RBAC rules.
- [ ] Secrets managed via External Secrets Operator (not in Git or ConfigMaps).
- [ ] etcd encryption at rest enabled.
- [ ] Container images signed and verified via admission controller.
- [ ] Images scanned for CVEs in CI; critical/high findings block deployment.
- [ ] Minimal base images (distroless/Alpine/scratch) used.
