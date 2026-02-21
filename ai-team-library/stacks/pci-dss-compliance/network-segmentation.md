# Network Segmentation

Standards for network security controls and segmentation to isolate the
cardholder data environment (CDE) from untrusted networks and other internal
systems. Network segmentation is not a PCI DSS requirement, but it is a
strongly recommended best practice that reduces the scope, cost, and complexity
of PCI DSS compliance.

---

## Defaults

- **Segmentation method:** Dedicated firewall/security appliance between the
  CDE and all other network segments.
- **Default deny:** All traffic to and from the CDE is denied by default;
  only explicitly authorized connections are permitted.
- **Validation:** Penetration testing must verify segmentation controls at
  least every six months (Requirement 11.4.5 for service providers) or
  annually (for merchants).
- **Documentation:** All network connections into and out of the CDE must be
  documented and justified.

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| Hardware firewall / next-gen firewall | Software-defined micro-segmentation | Cloud-native environments, container workloads, or when granular workload-level isolation is required |
| VLAN-based segmentation with ACLs | Physical network separation | Highest security environments or when logical controls cannot provide adequate isolation |
| DMZ for public-facing payment components | Reverse proxy with WAF | When a full DMZ architecture is impractical; ensure the WAF is PCI DSS compliant |
| Stateful packet inspection | Deep packet inspection (DPI) | When application-layer visibility is needed to detect data exfiltration or protocol abuse |

---

## Requirement 1 — Network Security Controls

PCI DSS v4.0 Requirement 1: Install and maintain network security controls.

| Sub-Requirement | Description |
|-----------------|-------------|
| **1.2** | Network security controls (NSCs) are configured and maintained |
| **1.2.1** | Configuration standards defined for all NSCs |
| **1.2.5** | All services, protocols, and ports allowed are identified, approved, and have a defined business need |
| **1.2.6** | Security features defined for insecure services, protocols, or ports |
| **1.2.7** | NSC configurations reviewed at least every six months |
| **1.3** | Network access to and from the CDE is restricted |
| **1.3.1** | Inbound traffic to the CDE is restricted to only what is necessary |
| **1.3.2** | Outbound traffic from the CDE is restricted to only what is necessary |
| **1.4** | Network connections between trusted and untrusted networks are controlled |
| **1.4.1** | NSCs implemented between trusted and untrusted networks |
| **1.4.2** | Inbound traffic from untrusted networks to trusted networks is restricted to authorized communications |
| **1.5** | Risks to the CDE from computing devices that connect to both untrusted networks and the CDE are mitigated |

---

## Segmentation Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Internet /    │     │  Corporate LAN  │
│   Untrusted     │     │  (Out of Scope) │
└────────┬────────┘     └────────┬────────┘
         │                       │
    ┌────▼────┐             ┌────▼────┐
    │  Edge   │             │ Internal│
    │Firewall │             │Firewall │
    └────┬────┘             └────┬────┘
         │                       │
    ┌────▼────────────────────────▼────┐
    │              DMZ                  │
    │  (Web servers, load balancers,   │
    │   reverse proxies)               │
    └────────────────┬─────────────────┘
                     │
                ┌────▼────┐
                │  CDE    │
                │Firewall │
                └────┬────┘
                     │
    ┌────────────────▼─────────────────┐
    │    Cardholder Data Environment    │
    │  (Payment apps, databases,       │
    │   tokenization servers)          │
    └──────────────────────────────────┘
```

Key design principles:
1. **Defense in depth** — multiple layers of network security controls
2. **Default deny** — block all traffic, then allow only what is documented and justified
3. **Minimize CDE footprint** — keep the CDE as small as possible
4. **Dedicated management network** — manage CDE systems on a separate management VLAN
5. **No direct internet access from CDE** — route through proxies or gateways

---

## Firewall Rule Management

```yaml
# Example: CDE firewall rule structure
firewall_rules:
  # Inbound to CDE — only from DMZ payment components
  - name: "Allow HTTPS from DMZ to payment API"
    source: "10.1.0.0/24"       # DMZ subnet
    destination: "10.2.0.10"     # Payment API server
    port: 443
    protocol: TCP
    action: ALLOW
    justification: "Payment processing API receives transactions from web tier"
    owner: "payments-team"
    review_date: "2026-08-20"

  # Outbound from CDE — only to payment processor
  - name: "Allow HTTPS from CDE to processor"
    source: "10.2.0.0/24"       # CDE subnet
    destination: "203.0.113.50"  # Payment processor endpoint
    port: 443
    protocol: TCP
    action: ALLOW
    justification: "Transaction authorization with payment processor"
    owner: "payments-team"
    review_date: "2026-08-20"

  # Default deny — all other traffic
  - name: "Deny all other CDE traffic"
    source: "any"
    destination: "10.2.0.0/24"
    port: any
    protocol: any
    action: DENY
    justification: "Default deny policy for CDE"
```

Every firewall rule must include:
- Business justification for the connection
- Source and destination (specific IPs/subnets, not "any" except for deny rules)
- Specific ports and protocols (not "all")
- Named owner responsible for the rule
- Review date (at least every six months)

---

## Do / Don't

- **Do** implement network segmentation to reduce PCI DSS scope. A segmented
  CDE means fewer systems to assess, monitor, and harden.
- **Do** use a default-deny posture on all firewalls and access control lists
  protecting the CDE. Explicitly allow only required traffic.
- **Do** document every firewall rule with a business justification, owner,
  and review date. Undocumented rules must be investigated and removed.
- **Do** review NSC configurations at least every six months to ensure rules
  remain relevant and no unauthorized changes have been made.
- **Do** validate segmentation effectiveness through penetration testing at
  least annually (every six months for service providers).
- **Don't** use "any" as a source or destination in allow rules. Every
  permitted connection must specify the exact source and destination.
- **Don't** allow direct connections from untrusted networks to the CDE.
  All traffic must pass through a DMZ or equivalent intermediary.
- **Don't** allow CDE systems to have unrestricted outbound internet access.
  Limit outbound connections to specific, documented destinations.
- **Don't** rely solely on VLANs without access control lists. VLAN tagging
  alone does not constitute adequate segmentation — enforce rules at network
  security controls.

---

## Common Pitfalls

1. **Overly broad firewall rules.** Rules use "any" for source, destination,
   or port, negating the purpose of segmentation. Solution: review all rules,
   replace "any" with specific values, and remove rules without business
   justification.
2. **Stale rules.** Firewall rules accumulate over time and are never cleaned
   up. Decommissioned systems still have allow rules. Solution: enforce
   six-month rule reviews and tie rules to system inventories.
3. **Segmentation bypass via shared services.** DNS, NTP, or Active Directory
   servers span both CDE and non-CDE segments, creating bridging points.
   Solution: deploy dedicated instances of shared services within the CDE or
   use tightly controlled jump points.
4. **Missing outbound controls.** Inbound traffic is restricted but outbound
   traffic from the CDE is unrestricted. Solution: implement egress filtering
   to limit CDE outbound connections to known, required destinations.
5. **Cloud networking gaps.** Cloud VPCs and security groups are not configured
   with the same rigor as on-premises firewalls. Solution: apply identical
   segmentation principles to cloud environments — default deny, specific
   rules, documentation, and regular review.

---

## Checklist

- [ ] CDE network boundaries defined and documented
- [ ] Network diagram showing all connections to and from the CDE is current
- [ ] Firewalls / NSCs deployed at all CDE boundaries
- [ ] Default-deny policy implemented on all CDE-facing firewalls
- [ ] All firewall allow rules have documented business justification
- [ ] All firewall rules specify exact source, destination, port, and protocol
- [ ] Firewall rule owners assigned and rules reviewed at least every six months
- [ ] No direct connections from untrusted networks to the CDE
- [ ] Outbound CDE traffic restricted to documented destinations
- [ ] DMZ deployed for public-facing payment components
- [ ] Segmentation validated by penetration testing (annually / semi-annually for SPs)
- [ ] Wireless networks are segmented from the CDE (or documented as in-scope)
- [ ] Shared services (DNS, AD, NTP) do not bridge CDE and non-CDE segments
