# Encryption and Key Management

Standards for protecting cardholder data through strong cryptography, both at
rest (Requirement 3) and in transit (Requirement 4). Includes key management
lifecycle practices required by PCI DSS v4.0.

---

## Defaults

- **Encryption at rest:** AES-256 for stored PAN and any cardholder data
  requiring encryption.
- **Encryption in transit:** TLS 1.2 or higher for transmission of CHD over
  open, public networks.
- **Key management:** Dedicated hardware security modules (HSMs) for production
  cryptographic key storage and operations.
- **Key rotation:** Cryptographic keys rotated at least annually, or more
  frequently based on risk assessment and crypto-period policy.
- **Key custodians:** Split knowledge and dual control for all manual
  key-management operations.

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| AES-256 encryption at rest | AES-128 | Acceptable per NIST but AES-256 provides stronger long-term protection |
| HSM for key storage | Software-based key vault (e.g., HashiCorp Vault) | Lower-risk environments where HSM cost is prohibitive; ensure vault access is tightly controlled |
| TLS 1.3 for data in transit | TLS 1.2 | When legacy systems cannot support TLS 1.3; TLS 1.2 is the minimum acceptable |
| Tokenization to replace stored PAN | Format-preserving encryption (FPE) | When downstream systems require values that resemble a PAN format |
| Annual key rotation | Crypto-period-based rotation | When risk assessment or industry guidance recommends shorter crypto-periods |

---

## Requirement 3 — Protect Stored Account Data

| Sub-Requirement | Description |
|-----------------|-------------|
| **3.1** | Processes and mechanisms for protecting stored account data are defined and understood |
| **3.2** | Storage of account data is kept to a minimum |
| **3.2.1** | Data retention and disposal policies limit storage amount and retention time |
| **3.3** | SAD is not stored after authorization |
| **3.3.1** | Full contents of any track are not stored after authorization |
| **3.3.2** | Card verification code is not stored after authorization |
| **3.3.3** | PIN and PIN block are not stored after authorization |
| **3.4** | Access to displays of full PAN and ability to copy PAN is restricted |
| **3.4.1** | PAN is masked when displayed (first six / last four is the maximum shown) |
| **3.5** | PAN is secured wherever it is stored |
| **3.5.1** | PAN is rendered unreadable anywhere it is stored using strong cryptography, truncation, tokenization, or one-way hashing |
| **3.6** | Cryptographic keys used to protect stored account data are secured |
| **3.7** | Cryptographic keys and related key management processes are documented and implemented |

---

## Requirement 4 — Protect CHD in Transit

| Sub-Requirement | Description |
|-----------------|-------------|
| **4.1** | Processes and mechanisms for protecting CHD during transmission are defined |
| **4.2** | CHD is protected with strong cryptography during transmission over open, public networks |
| **4.2.1** | Strong cryptography is implemented to safeguard CHD during transmission over open, public networks |
| **4.2.1.1** | Trusted keys and certificates are maintained for all certificates used to protect CHD in transit |
| **4.2.1.2** | Certificates used to protect CHD in transit are confirmed as valid and not expired or revoked |
| **4.2.2** | PAN is secured with strong cryptography whenever it is sent via end-user messaging technologies |

---

## Key Management Lifecycle

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Generate  │──▶│  Store    │──▶│   Use    │──▶│  Rotate  │
│           │   │  (HSM)   │   │          │   │          │
└──────────┘   └──────────┘   └──────────┘   └─────┬────┘
                                                     │
                                              ┌──────▼────┐
                                              │  Archive / │
                                              │  Destroy   │
                                              └───────────┘
```

| Phase | Requirements |
|-------|-------------|
| **Generation** | Use FIPS 140-2/3 validated cryptographic modules or HSMs. Keys must have sufficient strength for the algorithm (e.g., 256-bit for AES-256). |
| **Storage** | Store keys in HSMs or encrypted key vaults. Key-encrypting keys (KEKs) must be at least as strong as the data-encrypting keys (DEKs). Never store keys in plaintext alongside encrypted data. |
| **Distribution** | Distribute keys using secure methods (e.g., key-loading devices, TLS-protected channels). Split knowledge and dual control for manual distribution. |
| **Use** | Enforce separation of key-encrypting keys and data-encrypting keys. Use keys only for their intended purpose (encryption, signing, etc.). |
| **Rotation** | Rotate keys at the end of their defined crypto-period (at least annually). Re-encrypt data with new keys or use key-wrapping to transition. |
| **Revocation** | Revoke compromised or suspected-compromised keys immediately. Revocation procedures must be documented and tested. |
| **Destruction** | Destroy retired keys using approved methods (zeroization in HSM, cryptographic erasure). Maintain destruction logs. |

---

## Code Examples

### PAN Masking

```python
def mask_pan(pan: str) -> str:
    """Mask PAN to show only first six and last four digits (PCI DSS 3.4.1).

    This is the maximum number of digits that may be displayed.
    Roles that do not have a legitimate business need should see
    fewer digits or a fully masked value.
    """
    if len(pan) < 13:
        raise ValueError("Invalid PAN length")
    return pan[:6] + "*" * (len(pan) - 10) + pan[-4:]


# Example: mask_pan("4111111111111111") -> "411111******1111"
```

### TLS Configuration (Nginx)

```nginx
# PCI DSS 4.2.1 — Strong cryptography for CHD in transit
server {
    listen 443 ssl;
    server_name payments.example.com;

    # Minimum TLS 1.2, prefer TLS 1.3
    ssl_protocols TLSv1.2 TLSv1.3;

    # Strong cipher suites only
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers on;

    # HSTS — enforce HTTPS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;

    ssl_certificate     /etc/ssl/certs/payments.crt;
    ssl_certificate_key /etc/ssl/private/payments.key;
}
```

### Encryption at Rest (Python with Fernet)

```python
from cryptography.fernet import Fernet

# In production, retrieve the key from an HSM or secure key vault —
# never hardcode or store alongside encrypted data.
def encrypt_pan(pan: str, key: bytes) -> bytes:
    """Encrypt PAN for storage (PCI DSS 3.5.1)."""
    f = Fernet(key)
    return f.encrypt(pan.encode())


def decrypt_pan(token: bytes, key: bytes) -> str:
    """Decrypt PAN when authorized access is required."""
    f = Fernet(key)
    return f.decrypt(token).decode()
```

---

## Do / Don't

- **Do** use strong cryptography (AES-256) to render stored PAN unreadable.
  This is a core PCI DSS requirement with no exceptions.
- **Do** store cryptographic keys in HSMs or dedicated, access-controlled key
  vaults. Never store keys in application code, configuration files, or
  alongside the encrypted data they protect.
- **Do** enforce TLS 1.2 as the minimum for all transmissions of CHD over
  open, public networks. Prefer TLS 1.3 where possible.
- **Do** rotate cryptographic keys at least annually and immediately upon
  suspected compromise.
- **Do** implement split knowledge and dual control for manual key management
  operations. No single person should have access to a complete key.
- **Do** mask PAN when displayed — first six and last four is the maximum.
  Provide fewer digits to roles that do not have a business need.
- **Don't** store SAD (track data, CVV, PIN) after authorization under any
  circumstances. This applies to all storage — databases, logs, files, caches.
- **Don't** use deprecated protocols (SSL, TLS 1.0, TLS 1.1) for transmitting
  CHD. These have known vulnerabilities and are explicitly prohibited.
- **Don't** use the same encryption key for both test/development and
  production environments.
- **Don't** rely on disk-level encryption alone (e.g., BitLocker, dm-crypt)
  to meet Requirement 3.5. Disk encryption protects against physical theft
  but not against logical access by authorized OS users. Apply
  column-level or application-level encryption to the PAN.

---

## Common Pitfalls

1. **Keys stored alongside data.** Encryption keys are in the same database
   or filesystem as the encrypted PAN. Solution: store keys in a dedicated
   HSM or key vault, separate from the data they protect.
2. **Disk-encryption-only approach.** Organizations use full-disk encryption
   and consider PAN "rendered unreadable." PCI DSS does not accept transparent
   disk encryption alone because users with OS access can read the data.
   Solution: implement column-level, application-level, or tokenization-based
   protection.
3. **Expired or self-signed certificates.** TLS certificates are not monitored
   and expire, or self-signed certificates are used in production without
   proper trust chain management. Solution: automate certificate lifecycle
   management and use certificates from trusted CAs.
4. **No key rotation.** Encryption keys have been in use since initial
   deployment and have never been rotated. Solution: define a crypto-period
   policy, rotate keys at least annually, and implement automated rotation
   where possible.
5. **PAN in logs.** Application logs, error messages, or debug output contain
   full PAN values. Solution: implement automated log scanning to detect and
   alert on PAN patterns, and train developers to never log cardholder data.

---

## Checklist

- [ ] Strong cryptography (AES-256 or equivalent) used to render stored PAN unreadable
- [ ] SAD is verified not stored after authorization (all storage locations scanned)
- [ ] Key management procedures documented covering the full lifecycle
- [ ] Cryptographic keys stored in HSMs or access-controlled key vaults
- [ ] Split knowledge and dual control enforced for manual key operations
- [ ] Key rotation performed at least annually (crypto-period policy defined)
- [ ] Key-encrypting keys are at least as strong as data-encrypting keys
- [ ] TLS 1.2+ enforced for all CHD transmission over open, public networks
- [ ] SSL, TLS 1.0, and TLS 1.1 disabled on all systems
- [ ] TLS certificates monitored for expiration and revocation
- [ ] PAN masking enforced on all displays (maximum: first six, last four)
- [ ] No PAN in application logs, error messages, or debug output
- [ ] Disk-level encryption supplemented by column/application-level encryption
- [ ] Test/development environments use separate keys from production
