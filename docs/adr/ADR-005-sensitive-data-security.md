# ADR-005: Sensitive Data Handling and Security Measures

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

During discovery, we initially discussed that emails might contain sensitive data:
- Financial information (bank statements, invoices)
- Health data (personal health information)
- Legal/confidential documents

However, upon further consideration (Q37 in discovery session), the user decided to **simplify the approach** and not implement complicated audit logging and enhanced security measures for Bronze Tier.

User chose to store **full email content** in vault (not just metadata) for better searchability and functionality.

**Key Decision:** Keep security simple for Bronze Tier, focus on basic protections rather than enterprise-grade compliance measures.

---

## Decision

**Implement simplified security approach for Bronze Tier:**

1. **Local-First Architecture** - All data stays on local machine
2. **Full Content Storage** - Store complete emails for searchability
3. **File System Permissions** - Restrict vault access to user only (Windows 11)
4. **Credential Security** - .env file with gitignore
5. **Basic Logging** - Simple operation logs (not comprehensive audit trail)
6. **Git Backup** - Vault committed to private git repo
7. **No Cloud Sync** - Vault stays local (no Dropbox, OneDrive, etc.)

**Explicitly NOT implementing for Bronze:**
- ❌ Comprehensive audit logging
- ❌ HIPAA compliance measures
- ❌ Encryption at rest
- ❌ Sensitive data detection/flagging
- ❌ Complex access control systems

---

## Rationale

### Why Simplified Approach?

1. **Bronze Tier Focus**
   - Focus on core functionality first
   - Avoid over-engineering
   - Get working system quickly
   - Can enhance security in Silver/Gold

2. **Personal Use Context**
   - User's personal email, not enterprise
   - User has physical control of machine
   - No regulatory compliance requirements for personal use
   - User responsible for their own data

3. **Complexity vs Value**
   - Comprehensive audit logging adds significant complexity
   - HIPAA compliance not needed for personal use
   - Encryption at rest can be added later if needed
   - Basic protections sufficient for Bronze

4. **Development Time**
   - Simplified security saves 4-6 hours of development
   - Time better spent on core email processing features
   - Aligns with tier-by-tier progression approach

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

### 4. Basic Logging

**Log Format:**
```json
{
  "timestamp": "2026-02-04T10:30:00Z",
  "action": "email_processed",
  "email_id": "abc123",
  "from": "sender@example.com",
  "subject": "Invoice #1234",
  "classification": "HIGH",
  "duration_seconds": 8.5
}
```

**Retention:** Keep logs for debugging, no specific retention policy

**Note:** This is basic operational logging, not comprehensive audit logging.

### 5. Sensitive Data Detection

**Not implemented for Bronze Tier.**

Rationale:
- Adds complexity without clear benefit for personal use
- User can manually identify sensitive emails
- Can add in Silver/Gold if needed
- Focus Bronze effort on core functionality

~~**Patterns to Flag:**~~
~~```python~~
~~SENSITIVE_PATTERNS = {~~
~~    'financial': [...],~~
~~    'health': [...],~~
~~    'legal': [...]~~
~~}~~
~~```~~

### 6. Access Control

**Who Can Access:**
- ✅ User (primary account on Windows 11)
- ✅ Gmail Watcher (running as user)
- ✅ Claude Code (invoked by user)
- ❌ Other users on machine (via file permissions)

**How to Verify:**
```powershell
# Windows 11 - Check vault permissions
icacls "AI_Employee_Vault"
# Should show only current user has access
```

---

## Consequences

### Positive

- ✅ Maximum data privacy (local-first)
- ✅ Simple, maintainable security model
- ✅ Full functionality (complete email content)
- ✅ User has complete control
- ✅ No cloud provider risk
- ✅ Basic logging for debugging
- ✅ Faster development (no complex security)
- ✅ Appropriate for personal use

### Negative

- ❌ No automatic cloud backup
- ❌ Data loss if machine fails (mitigated by git)
- ❌ Can't access from other devices
- ❌ User responsible for security
- ❌ No encryption at rest
- ❌ No comprehensive audit trail
- ❌ Not suitable for enterprise/compliance use

### Mitigations

- Git commits provide backup
- Document backup procedures
- Add encryption option in Silver/Gold tier if needed
- Add comprehensive audit logging in Silver/Gold if needed
- User education on basic security practices
- Can upgrade security measures based on actual needs

---

## Compliance Considerations

**Not applicable for Bronze Tier.**

This is a personal use system, not an enterprise or healthcare system. The user is managing their own personal email on their own machine.

### Future Considerations (Silver/Gold)

If the system is later used in a professional/enterprise context, consider:
- HIPAA compliance measures (if handling PHI)
- Financial regulations compliance (if handling client financial data)
- Legal/attorney-client privilege protections (if handling legal communications)

For Bronze Tier personal use, basic security measures are sufficient.

---

## Future Enhancements (Silver/Gold)

### Encryption at Rest
- Use git-crypt for vault encryption
- Encrypt sensitive fields in markdown
- Full disk encryption (BitLocker on Windows)

### Comprehensive Audit Logging
- Log all file access (not just processing)
- Detect unusual access patterns
- Alert on unauthorized access attempts
- Compliance-grade audit trails

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

### Operational Phase
- [ ] Review logs weekly for errors
- [ ] Rotate Gmail API credentials quarterly
- [ ] Update security patches monthly
- [ ] Backup vault to git regularly (automatic via commits)

### Incident Response
- [ ] Document procedure for lost/stolen device
- [ ] Document procedure for credential compromise

---

## User Responsibilities

1. **Physical Security**
   - Lock computer when away
   - Use strong Windows password
   - Consider enabling BitLocker

2. **Credential Security**
   - Never share Gmail credentials
   - Use 2FA on Gmail account
   - Rotate credentials periodically

3. **Backup Security**
   - Keep git repo private
   - Store backups securely

4. **Monitoring**
   - Review logs for errors
   - Check for unusual activity

---

## References

- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q37 (commented out), Q38, Q40
- [Component Tier Mapping](../architecture/component-tier-mapping.md)
- [Hackathon Guide](../../Personal_AI_Employee_Hackathon_0_Building_Autonomous_FTEs_in_2026.md) - Security section

---

**Status:** ✅ Accepted
**Review Date:** After Bronze Tier implementation, before moving to Silver
