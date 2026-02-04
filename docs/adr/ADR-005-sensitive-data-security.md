# ADR-005: Sensitive Data Handling and Security Measures

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

During discovery, we learned that emails will contain sensitive data:
- ✅ Financial information (bank statements, invoices)
- ✅ Health data (personal health information)
- ✅ Legal/confidential documents

This creates specific security and privacy requirements:
- Data must be stored securely
- Access must be controlled
- Audit trail required
- Compliance considerations (HIPAA for health, financial regulations)

User chose to store **full email content** in vault (not just metadata).

---

## Decision

**Implement multi-layered security approach for Bronze Tier:**

1. **Local-First Architecture** - All data stays on local machine
2. **Full Content Storage** - Store complete emails for searchability
3. **File System Permissions** - Restrict vault access to user only
4. **Credential Security** - .env file with strict permissions
5. **Audit Logging** - All access logged with timestamps
6. **Git Encryption** - Sensitive files excluded from git or encrypted
7. **No Cloud Sync** - Vault stays local (no Dropbox, OneDrive, etc.)

---

## Rationale

### Why Local-First?

1. **Maximum Privacy**
   - Data never leaves user's machine
   - No third-party access
   - User has complete control
   - Complies with data residency requirements

2. **Regulatory Compliance**
   - HIPAA: PHI stays on controlled device
   - Financial: Sensitive financial data not transmitted
   - Legal: Attorney-client privilege maintained
   - GDPR: Data minimization and control

3. **Zero Trust in Cloud**
   - No reliance on cloud provider security
   - No risk of cloud breaches
   - No vendor lock-in
   - No subscription costs

### Why Full Content Storage?

1. **User Requirement**
   - User explicitly chose "Full email content"
   - Enables full-text search in Obsidian
   - Better context for AI processing
   - Complete audit trail

2. **Functionality**
   - Can re-process emails if classification improves
   - Can search historical emails
   - Can generate reports from full data
   - No need to re-fetch from Gmail

3. **Acceptable Risk**
   - Data is local (not transmitted)
   - File system permissions protect access
   - User's machine, user's responsibility
   - Can add encryption later if needed

---

## Security Measures

### 1. File System Permissions

**Vault Directory:**
```bash
# Windows 11 (PowerShell)
icacls "AI_Employee_Vault" /inheritance:r
icacls "AI_Employee_Vault" /grant:r "%USERNAME%:(OI)(CI)F"
```

**Effect:**
- Only user account can access vault
- No other users (even admins) can read
- Inheritance disabled (new files inherit restrictions)

### 2. Credential Management

**.env File:**
```bash
# .env permissions (Windows)
icacls ".env" /inheritance:r
icacls ".env" /grant:r "%USERNAME%:R"
```

**Contents:**
```env
# Gmail API Credentials
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json

# Vault Configuration
VAULT_PATH=./AI_Employee_Vault
```

**Never commit:**
- credentials.json
- token.json
- .env
- Any file with "token" or "secret" in name

### 3. Git Configuration

**.gitignore:**
```
# Credentials
.env
credentials.json
token.json
*.key
*.pem

# Sensitive Data (optional - user chose git as backup)
# AI_Employee_Vault/Logs/*.log
# AI_Employee_Vault/Done/*.md

# System Files
__pycache__/
*.pyc
.venv/
```

**Note:** User chose "Git as backup" so vault content WILL be committed. This is acceptable because:
- Repo is private
- User's personal machine
- Can add git-crypt later if needed

### 4. Audit Logging

**Log Format:**
```json
{
  "timestamp": "2026-02-04T10:30:00Z",
  "action": "email_processed",
  "email_id": "abc123",
  "from": "sender@example.com",
  "subject": "Invoice #1234",
  "classification": "HIGH",
  "contains_sensitive": true,
  "sensitive_types": ["financial"],
  "processed_by": "email-processor",
  "duration_seconds": 12.5
}
```

**Retention:** 90 days minimum

### 5. Sensitive Data Detection

**Patterns to Flag:**
```python
SENSITIVE_PATTERNS = {
    'financial': [
        r'\$\d{1,3}(,\d{3})*(\.\d{2})?',  # Dollar amounts
        r'account.*\d{4,}',                # Account numbers
        r'invoice|payment|transaction',    # Financial keywords
        r'routing.*\d{9}',                 # Routing numbers
    ],
    'health': [
        r'diagnosis|prescription|medical',
        r'patient|doctor|hospital',
        r'health.*record|PHI',
    ],
    'legal': [
        r'confidential|privileged',
        r'attorney.*client',
        r'legal.*advice',
        r'settlement|litigation',
    ]
}
```

**Action:** Add `contains_sensitive: true` to email frontmatter

### 6. Access Control

**Who Can Access:**
- ✅ User (primary account)
- ✅ Gmail Watcher (running as user)
- ✅ Claude Code (invoked by user)
- ❌ Other users on machine
- ❌ System services
- ❌ Network access

**How to Verify:**
```python
def verify_vault_permissions():
    """Verify vault has correct permissions"""
    vault_path = Path(os.getenv('VAULT_PATH'))

    # Check owner
    stat_info = vault_path.stat()
    if stat_info.st_uid != os.getuid():
        raise SecurityError("Vault not owned by current user")

    # Check permissions (Unix-like)
    if stat_info.st_mode & 0o077:
        raise SecurityError("Vault accessible by others")

    logging.info("Vault permissions verified")
```

---

## Consequences

### Positive

- ✅ Maximum data privacy (local-first)
- ✅ Regulatory compliance (HIPAA, financial)
- ✅ Full functionality (complete email content)
- ✅ User has complete control
- ✅ No cloud provider risk
- ✅ Audit trail for all access

### Negative

- ❌ No automatic cloud backup
- ❌ Data loss if machine fails (mitigated by git)
- ❌ Can't access from other devices
- ❌ User responsible for security
- ❌ No encryption at rest (yet)

### Mitigations

- Git commits provide backup
- Document backup procedures
- Add encryption option in Silver tier
- User education on security best practices
- Regular security audits

---

## Compliance Considerations

### HIPAA (Health Data)

**Requirements:**
- ✅ Access controls (file permissions)
- ✅ Audit logs (all access logged)
- ✅ Data integrity (git versioning)
- ⚠️ Encryption at rest (optional for Bronze, add later)
- ✅ Minimum necessary (only user accesses)

**Status:** Acceptable for personal use, not for covered entities

### Financial Regulations

**Requirements:**
- ✅ Secure storage (local, permissions)
- ✅ Access controls (user only)
- ✅ Audit trail (comprehensive logging)
- ✅ Data retention (configurable)

**Status:** Acceptable for personal financial data

### Legal/Attorney-Client Privilege

**Requirements:**
- ✅ Confidentiality (local storage, no transmission)
- ✅ Access controls (user only)
- ✅ No third-party access (local-first)

**Status:** Maintains privilege (consult attorney for specific cases)

---

## Future Enhancements (Silver/Gold)

### Encryption at Rest
- Use git-crypt for vault encryption
- Encrypt sensitive fields in markdown
- Full disk encryption (BitLocker on Windows)

### Access Logging
- Log all file access (not just processing)
- Detect unusual access patterns
- Alert on unauthorized access attempts

### Data Classification
- Automatic sensitivity scoring
- Different handling for different sensitivity levels
- Redaction options for sharing

### Secure Deletion
- Secure wipe for deleted emails
- Automatic purging of old sensitive data
- Compliance with data retention policies

---

## Security Checklist

### Setup Phase
- [ ] Set vault directory permissions (user only)
- [ ] Set .env file permissions (read-only)
- [ ] Verify .gitignore includes credentials
- [ ] Test file access from other user account (should fail)
- [ ] Enable Windows Defender real-time protection
- [ ] Disable cloud sync for vault directory

### Operational Phase
- [ ] Review audit logs weekly
- [ ] Rotate Gmail API credentials quarterly
- [ ] Update security patches monthly
- [ ] Backup vault to encrypted external drive monthly
- [ ] Review sensitive data handling quarterly

### Incident Response
- [ ] Document procedure for lost/stolen device
- [ ] Document procedure for suspected breach
- [ ] Document procedure for credential compromise
- [ ] Test incident response procedures

---

## User Responsibilities

1. **Physical Security**
   - Lock computer when away
   - Use strong Windows password
   - Enable BitLocker if possible

2. **Credential Security**
   - Never share Gmail credentials
   - Use 2FA on Gmail account
   - Rotate credentials regularly

3. **Backup Security**
   - Keep git repo private
   - Encrypt external backups
   - Store backups securely

4. **Monitoring**
   - Review audit logs regularly
   - Check for unusual activity
   - Report security concerns

---

## References

- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q29, Q30

---

**Status:** ✅ Accepted
**Review Date:** After Bronze Tier implementation, before handling real sensitive data
