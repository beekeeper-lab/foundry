# Audit Logging and Monitoring

Standards for logging, monitoring, and testing security of systems and networks
within the cardholder data environment (CDE). PCI DSS v4.0 Requirements 10 and
11 establish the controls for detecting anomalies, investigating incidents, and
validating the effectiveness of security measures.

---

## Defaults

- **Log aggregation:** Centralized log management system (SIEM) collecting logs
  from all CDE system components.
- **Time synchronization:** NTP from authoritative time sources; all CDE systems
  synchronized to the same time reference.
- **Log retention:** Audit logs retained for at least 12 months, with a minimum
  of 3 months immediately available for analysis.
- **Review frequency:** Logs reviewed at least daily for security events.
  Automated alerting supplements but does not replace daily review.
- **File integrity monitoring (FIM):** Deployed on all critical system files,
  configuration files, and content files within the CDE.

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| SIEM (e.g., Splunk, Elastic SIEM) | Cloud-native logging (e.g., AWS CloudTrail + GuardDuty) | Cloud-only CDE where cloud-native tools provide equivalent detection and retention capabilities |
| Daily manual log review | Automated anomaly detection with human escalation | High-volume environments where manual review is impractical; automated detection must be tuned and validated |
| Agent-based FIM | Agentless FIM via API or snapshot comparison | Container or serverless workloads where traditional agents cannot be installed |
| Quarterly internal vulnerability scans | Continuous vulnerability scanning | High-change environments where quarterly scans miss vulnerabilities introduced between scans |

---

## Requirement 10 — Log and Monitor All Access

| Sub-Requirement | Description |
|-----------------|-------------|
| **10.1** | Processes and mechanisms for logging and monitoring are defined and documented |
| **10.2** | Audit logs are implemented to support the detection of anomalies and suspicious activity |
| **10.2.1** | Audit logs are enabled and active for all system components in the CDE |
| **10.2.1.1** | Audit logs capture all individual user access to cardholder data |
| **10.2.1.2** | Audit logs capture all actions taken by any individual with administrative access |
| **10.2.1.3** | Audit logs capture all access to audit logs |
| **10.2.1.4** | Audit logs capture all invalid logical access attempts |
| **10.2.1.5** | Audit logs capture all changes to identification and authentication credentials |
| **10.2.1.6** | Audit logs capture all initialization, stopping, or pausing of audit logs |
| **10.2.1.7** | Audit logs capture all creation and deletion of system-level objects |
| **10.2.2** | Audit logs record sufficient detail for each auditable event |
| **10.3** | Audit logs are protected from destruction and unauthorized modifications |
| **10.3.1** | Read access to audit log files is limited to those with a job-related need |
| **10.3.2** | Audit log files are protected from unauthorized modification |
| **10.3.3** | Audit log files are promptly backed up to a centralized log server or media that is difficult to alter |
| **10.3.4** | File integrity monitoring (FIM) or change detection is used on audit logs |
| **10.4** | Audit logs are reviewed to identify anomalies or suspicious activity |
| **10.4.1** | Audit logs are reviewed at least once daily (automated or manual) |
| **10.4.2** | Logs of all other system components are reviewed periodically |
| **10.5** | Audit log history is retained and available for analysis |
| **10.5.1** | Retain audit log history for at least 12 months, with at least 3 months immediately available |
| **10.6** | Time-synchronization technology synchronizes clocks on all systems |
| **10.7** | Failures of critical security control systems are detected, reported, and responded to promptly |

---

## Requirement 11 — Test Security Regularly

| Sub-Requirement | Description |
|-----------------|-------------|
| **11.1** | Processes and mechanisms for regularly testing security are defined and documented |
| **11.2** | Wireless access points are identified and monitored |
| **11.3** | External and internal vulnerabilities are regularly identified, prioritized, and addressed |
| **11.3.1** | Internal vulnerability scans performed at least quarterly |
| **11.3.2** | External vulnerability scans performed at least quarterly by an ASV |
| **11.4** | External and internal penetration testing is regularly performed |
| **11.4.1** | Penetration testing methodology defined and implemented |
| **11.4.3** | External penetration testing performed at least annually and after significant changes |
| **11.4.4** | Internal penetration testing performed at least annually and after significant changes |
| **11.4.5** | Segmentation penetration testing performed to verify segmentation controls |
| **11.5** | Network intrusions and unexpected file changes are detected and responded to |
| **11.5.1** | Intrusion-detection/prevention techniques detect and alert on intrusions into the CDE |
| **11.5.2** | Change-detection mechanism (FIM) deployed to alert on unauthorized modification of critical files |
| **11.6** | Unauthorized changes on payment pages are detected and responded to |

---

## Log Event Format

Every audit log entry must include the following fields (Requirement 10.2.2):

```json
{
  "timestamp": "2026-02-20T14:30:00.000Z",
  "user_id": "jsmith",
  "event_type": "user_access",
  "event_description": "Accessed cardholder data record",
  "source_ip": "10.2.0.45",
  "destination_ip": "10.2.0.10",
  "component": "payment-api",
  "outcome": "success",
  "data_affected": "CHD_record_id:98765"
}
```

| Field | PCI DSS Reference | Description |
|-------|-------------------|-------------|
| `timestamp` | 10.2.2 | Date and time of event (synchronized via NTP) |
| `user_id` | 10.2.2 | User identification (unique per Requirement 8) |
| `event_type` | 10.2.2 | Type of event (access, modification, deletion, authentication, etc.) |
| `event_description` | 10.2.2 | Description of the event |
| `source_ip` | 10.2.2 | Origination of event (IP address, device) |
| `destination_ip` | 10.2.2 | Affected resource or system component |
| `component` | 10.2.2 | Identity of the system component where the event occurred |
| `outcome` | 10.2.2 | Success or failure indication |

---

## Monitoring Architecture

```
┌─────────────────────────────────────────────────┐
│                CDE Systems                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Payment  │ │ Database │ │ Tokenization     │ │
│  │ App      │ │ Server   │ │ Server           │ │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│       │             │                │           │
│       └─────────────┼────────────────┘           │
│                     │                            │
│              ┌──────▼──────┐                     │
│              │  Log Agent  │  (FIM + log fwd)    │
│              └──────┬──────┘                     │
└─────────────────────┼───────────────────────────┘
                      │  Encrypted transport (TLS)
               ┌──────▼──────┐
               │    SIEM     │
               │  (Central   │
               │   log mgmt) │
               └──────┬──────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼───┐  ┌─────▼────┐  ┌────▼──────┐
   │ Alert  │  │ Dashboard│  │ Long-term │
   │ Engine │  │ & Review │  │ Archive   │
   └────────┘  └──────────┘  │ (12 mo+)  │
                             └───────────┘
```

---

## Do / Don't

- **Do** log all access to cardholder data, all administrative actions, and all
  authentication attempts (successful and failed) within the CDE.
- **Do** protect audit logs from tampering. Send logs to a centralized system
  where write access is restricted, and use FIM to detect unauthorized changes.
- **Do** synchronize clocks across all CDE systems using NTP. Inconsistent
  timestamps make incident investigation extremely difficult.
- **Do** review logs at least daily for security events. Use automated alerting
  to surface critical events, but ensure human review is part of the process.
- **Do** retain audit logs for at least 12 months, with the most recent
  3 months immediately available for analysis without restoration from archives.
- **Do** perform quarterly internal vulnerability scans and quarterly external
  ASV scans. Remediate critical and high vulnerabilities promptly.
- **Don't** allow audit logs to be modified or deleted by the systems or users
  they are monitoring. Logs must be tamper-evident.
- **Don't** log cardholder data (PAN, SAD) in audit logs. Log the event
  metadata (who, what, when, where) without including the actual sensitive data.
- **Don't** skip log review because "nothing ever happens." PCI DSS requires
  daily review, and unreviewed logs cannot detect breaches.
- **Don't** neglect file integrity monitoring. FIM on critical system files
  and audit logs is required, not optional.

---

## Common Pitfalls

1. **Logging CHD in audit logs.** Debug logging captures full PAN or SAD,
   creating an additional storage location for cardholder data. Solution:
   implement log sanitization rules and scan logs regularly for PAN patterns.
2. **Insufficient log retention.** Logs are rotated and deleted before the
   12-month retention period. Solution: configure log archival with at least
   12-month retention and verify 3-month immediate availability.
3. **Clock drift.** CDE systems are not synchronized, making it impossible to
   correlate events across components during an investigation. Solution: enforce
   NTP synchronization and monitor for time drift.
4. **Alert fatigue.** Too many low-fidelity alerts cause security teams to
   ignore the SIEM. Solution: tune detection rules, prioritize alerts by
   severity, and establish clear escalation procedures.
5. **Penetration testing scope gaps.** Penetration tests cover the application
   layer but not the network segmentation or internal CDE systems. Solution:
   ensure penetration testing methodology covers both application and network
   layers, including segmentation validation.

---

## Checklist

- [ ] Audit logs enabled on all CDE system components
- [ ] All required event types captured (access, admin actions, auth attempts, log access, object changes)
- [ ] Log entries include all required fields (timestamp, user, event type, source, outcome, component)
- [ ] Logs forwarded to centralized SIEM via encrypted transport
- [ ] Audit logs protected from unauthorized modification and deletion
- [ ] FIM deployed on audit log files and critical system files
- [ ] Log review performed at least daily (automated + human)
- [ ] Audit log retention configured for 12+ months (3 months immediately available)
- [ ] Time synchronization (NTP) configured on all CDE systems
- [ ] Critical security control failures detected, alerted, and responded to
- [ ] Internal vulnerability scans performed quarterly and after significant changes
- [ ] External ASV scans performed quarterly with passing results
- [ ] Penetration testing performed annually (and after significant changes)
- [ ] Segmentation testing performed to verify CDE isolation
- [ ] IDS/IPS deployed to detect and alert on network intrusions in the CDE
- [ ] Payment page change detection implemented (Requirement 11.6)
