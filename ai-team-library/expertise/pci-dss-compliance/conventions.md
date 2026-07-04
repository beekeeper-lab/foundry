---
id: pci-dss-compliance
category: Compliance & Governance
entry: true
last-reviewed: 2026-07
---

# PCI DSS Compliance Conventions

## Category
Compliance & Governance

Conventions for building and operating systems subject to PCI DSS v4.0 — the
standard that applies to all entities that store, process, or transmit
cardholder data (CHD) or sensitive authentication data (SAD). These are the
non-negotiable defaults for any payment-touching work; the sibling files hold
the full requirement tables, architectures, and code examples.

---

## Defaults

| Concern | Default |
|---------|---------|
| Standard version | PCI DSS v4.0.1 (June 2024; mandatory after March 31, 2025) |
| Scope | All components in or connected to the CDE — people, processes, technology |
| SAD (track data, CVV, PIN) | **Never stored after authorization** — no exceptions |
| Stored PAN | Rendered unreadable: strong cryptography (AES-256), truncation, tokenization, or one-way hashing (Req. 3.5) |
| PAN display masking | First six / last four digits is the maximum shown (Req. 3.4.1) |
| CHD in transit | TLS 1.2 minimum (prefer 1.3) over open, public networks; SSL/TLS 1.0/1.1 prohibited |
| Key storage | HSM or access-controlled key vault, never alongside encrypted data |
| Key rotation | At least annually, per documented crypto-period policy |
| Segmentation | Dedicated firewall between CDE and everything else; default deny both directions |
| Log retention | 12+ months, 3 months immediately available; daily log review |
| Vulnerability scans | Quarterly internal scans + quarterly external ASV scans |
| Penetration testing | Annually and after significant changes; segmentation testing included |
| Validation | Annual SAQ or ROC + signed AOC; SAQ type must match the actual data flow |

---

## 1. Scoping the CDE

- Identify every location where CHD is stored, processed, or transmitted, then
  every system component in the CDE, then all connected-to and
  security-impacting systems. Document and validate scope annually and after
  significant changes.
- Use network segmentation to minimize scope — a flat network puts the entire
  network in scope for PCI DSS.
- Eliminate SAD immediately after authorization; minimize stored PAN via
  tokenization or truncation. Less stored data means less exposure.
- Assign a dedicated PCI DSS compliance owner. Outsourcing card processing
  does not eliminate your obligations — you still validate your environment
  and manage third-party risk.

Full detail: `fundamentals.md` (12 requirements, CHD/SAD element table, scoping model).

---

## 2. Protecting Account Data (Requirements 3 & 4)

- Encrypt stored PAN with AES-256 (or truncate/tokenize/hash). Disk-level
  encryption alone (BitLocker, dm-crypt) does **not** satisfy Requirement 3.5 —
  apply column- or application-level encryption.
- Store keys in HSMs (FIPS 140-2/3 validated) or dedicated key vaults; enforce
  split knowledge and dual control for manual key operations; key-encrypting
  keys at least as strong as data-encrypting keys.
- Rotate keys at the end of their crypto-period (at least annually) and
  immediately on suspected compromise. Separate keys for test/dev vs production.
- TLS 1.2+ with strong cipher suites for all CHD in transit; maintain and
  monitor trusted certificates for expiry/revocation (Req. 4.2.1.1–4.2.1.2).

Full detail: `encryption-and-key-management.md` (key lifecycle, PAN masking and TLS code examples).

---

## 3. Network Segmentation (Requirement 1)

- Default deny on all CDE-facing firewalls; explicitly allow only documented,
  justified connections. Never "any" as source/destination/port in allow rules.
- Every firewall rule carries a business justification, named owner, and
  review date; NSC configurations reviewed at least every six months (Req. 1.2.7).
- No direct connections from untrusted networks to the CDE — route through a
  DMZ. Restrict outbound CDE traffic to documented destinations (egress filtering).
- VLAN tagging alone is not segmentation — enforce ACLs at network security
  controls. Don't let shared services (DNS, NTP, AD) bridge CDE and non-CDE segments.
- Validate segmentation via penetration testing annually (every six months for
  service providers, Req. 11.4.5).

Full detail: `network-segmentation.md` (Requirement 1 table, architecture diagram, rule template).

---

## 4. Logging, Monitoring, and Testing (Requirements 10 & 11)

- Enable audit logs on all CDE components; capture all CHD access, all admin
  actions, all auth attempts, all access to logs themselves (Req. 10.2.1.x).
- Each entry records timestamp (NTP-synchronized), user ID, event type,
  source/destination, component, and outcome (Req. 10.2.2). Never log PAN or SAD.
- Forward logs over encrypted transport to a centralized SIEM where write
  access is restricted; FIM on audit logs and critical system files.
- Review logs at least daily (Req. 10.4.1) — automated alerting supplements
  but does not replace review. Retain 12+ months with 3 months immediately available.
- Quarterly internal vulnerability scans, quarterly external ASV scans, annual
  internal and external penetration testing, IDS/IPS in the CDE, and payment
  page change detection (Req. 11.6).

Full detail: `audit-logging.md` (Requirements 10/11 tables, log event format, monitoring architecture).

---

## 5. Compliance Validation (SAQ / ROC)

- Confirm SAQ eligibility with your acquirer; select the SAQ type that matches
  your exact payment flow (A, A-EP, B, B-IP, C, C-VT, P2PE, or D). If the flow
  doesn't match a description exactly, use SAQ D.
- Level 1 merchants (>6M transactions/year) require an annual ROC by a QSA/ISA;
  most SAQ types also require passing quarterly ASV scans.
- A "Yes" answer means fully implemented, tested, and maintained — not planned.
  Compensating controls must meet the intent and rigor of the original
  requirement and be documented in Appendix B and C.
- Re-assess every requirement each cycle; compliance is continuous, not an
  annual snapshot.

Full detail: `saq-guidance.md` (SAQ type table, decision tree, merchant levels, compensating controls).

---

## Do / Don't

**Do:**
- Scope the CDE before any compliance work; segmentation drives scope down.
- Eliminate SAD immediately after authorization and verify by scanning.
- Render stored PAN unreadable with strong cryptography, truncation, or tokenization.
- Store keys in HSMs/key vaults with split knowledge and dual control.
- Enforce TLS 1.2+ for CHD in transit; monitor certificate validity.
- Review logs daily; retain 12 months; keep clocks NTP-synchronized.
- Document every firewall rule with justification, owner, and review date.
- Verify third-party service providers' PCI DSS compliance and contract for it.

**Don't:**
- Store SAD after authorization — ever, in any store, log, file, or cache.
- Log PAN or SAD in application logs, error messages, or debug output.
- Rely on disk-level encryption alone to meet Requirement 3.5.
- Use SSL, TLS 1.0, or TLS 1.1 for CHD transmission.
- Use "any" in firewall allow rules or leave CDE outbound traffic unrestricted.
- Share cryptographic keys between test/development and production.
- Select a simpler SAQ type than your payment flow warrants.
- Treat compliance as an annual event rather than a continuous state.

---

## Common Pitfalls

1. **Scope creep from flat networks.** Without segmentation, every system is
   in scope. Implement and validate segmentation to isolate the CDE.
2. **SAD or PAN in logs.** Debug logging captures track data, CVV, or full PAN,
   creating an extra storage location. Sanitize logs and scan for PAN patterns.
3. **Keys stored alongside data.** Encryption keys live in the same database or
   filesystem as the encrypted PAN. Move them to an HSM or key vault.
4. **Disk-encryption-only approach.** Transparent disk encryption doesn't stop
   logical access by OS users; PCI DSS doesn't accept it alone for stored PAN.
5. **Stale or overly broad firewall rules.** "Any" rules and rules for
   decommissioned systems negate segmentation. Enforce six-month rule reviews.
6. **Clock drift.** Unsynchronized CDE clocks make cross-component incident
   correlation impossible. Enforce NTP and monitor drift.
7. **Wrong SAQ type / scope underestimation.** Map the exact CHD flow and
   include connected-to systems before selecting an SAQ.
8. **Ignoring third-party risk.** Inventory all providers with CHD access,
   verify compliance status, and include PCI DSS requirements in contracts.

---

## Checklist

- [ ] CDE identified, documented, and all CHD/SAD data flows mapped
- [ ] Network segmentation implemented, default deny, validated by pen testing
- [ ] SAD verified not stored after authorization (all locations scanned)
- [ ] Stored PAN rendered unreadable (encryption, truncation, tokenization, or hashing)
- [ ] Keys in HSM/key vault; rotation at least annual; split knowledge and dual control
- [ ] TLS 1.2+ enforced for CHD in transit; legacy protocols disabled; certs monitored
- [ ] PAN masked on display (max first six / last four); no PAN/SAD in logs
- [ ] Audit logs on all CDE components, centralized, FIM-protected, reviewed daily
- [ ] Log retention 12+ months with 3 months immediately available; NTP on all systems
- [ ] Quarterly internal scans and external ASV scans passing
- [ ] Annual penetration testing (application + network + segmentation)
- [ ] Correct SAQ type (or ROC) with signed AOC; compensating controls documented
- [ ] PCI DSS compliance owner assigned; third-party providers inventoried and verified
- [ ] Incident response plan covers payment card breach procedures
