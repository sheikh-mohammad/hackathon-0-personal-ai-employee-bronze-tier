# ADR-006: Error Notification and Monitoring Strategy

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

For a production-quality system handling 50-100 emails/day with sensitive data, robust error notification is critical. User selected multiple notification channels:
- Dashboard alerts
- Email notifications  
- Desktop notifications
- Log files

---

## Decision

**Implement multi-channel error notification system with severity-based routing:**

| Severity | Dashboard | Email | Desktop | Log |
|----------|-----------|-------|---------|-----|
| CRITICAL | ✅ | ✅ | ✅ | ✅ |
| ERROR | ✅ | ✅ | ❌ | ✅ |
| WARNING | ✅ | ❌ | ❌ | ✅ |
| INFO | ❌ | ❌ | ❌ | ✅ |

**Notification Types:**
1. **CRITICAL:** System down, data loss risk, security breach
2. **ERROR:** Processing failures, API errors, skill failures  
3. **WARNING:** Performance degradation, queue backlog, rate limits
4. **INFO:** Normal operations, successful processing

---

## Rationale

### Why Multi-Channel?

1. **Redundancy** - If one channel fails, others still work
2. **Context-Appropriate** - Different channels for different urgency levels
3. **Severity-Based** - Don't spam user with low-priority notifications

### Channel Selection

- **Dashboard:** Persistent, contextual, no external dependencies
- **Email:** Can receive when away, includes full details
- **Desktop:** Immediate attention for critical issues
- **Logs:** Complete audit trail, debugging information

---

## Implementation

### Dashboard Alerts Section
```markdown
## Alerts
<!-- Critical and error alerts appear here -->

## System Health
- Watcher Status: 🟢 Running
- Last Check: 2 minutes ago
- Queue Size: 2 emails
- Avg Processing Time: 18.5s
```

### Email Notifications
- Subject: `[AI Employee] {Severity}: {Title}`
- Sent via Gmail API to user's email
- Rate limited: max 5 per hour

### Desktop Notifications
- Windows 10/11 toast notifications
- Only for CRITICAL severity
- Action buttons: "View Dashboard", "Dismiss"

---

## Success Criteria

1. ✅ Critical errors trigger all channels within 30 seconds
2. ✅ User receives email notifications for errors
3. ✅ Dashboard shows current alerts
4. ✅ Desktop notifications appear for critical issues
5. ✅ No notification spam (rate limited)
6. ✅ All notifications logged to audit trail

---

## References

- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q27
- Windows Notifications API
- Plyer Library for cross-platform notifications

---

**Status:** ✅ Accepted
**Review Date:** After first week of operation
