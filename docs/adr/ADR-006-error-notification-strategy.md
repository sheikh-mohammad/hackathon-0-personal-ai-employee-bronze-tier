# ADR-006: Error Notification and Monitoring Strategy

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

For a production-quality system handling variable email volume with continuous monitoring (every 10 seconds), robust error notification is important. User selected multiple notification channels:
- Dashboard alerts
- Email notifications
- Desktop notifications
- Log files

The system needs to notify the user of critical issues while avoiding notification spam.

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
1. **CRITICAL:** System down, watcher crashed, Gmail API auth failure
2. **ERROR:** Processing failures, skill failures, repeated errors
3. **WARNING:** Performance degradation, queue backlog, rate limits approaching
4. **INFO:** Normal operations, successful processing, statistics

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
⚠️ CRITICAL: Gmail Watcher stopped at 10:45 AM
❌ ERROR: Failed to process 3 emails in last hour

## System Health
- Watcher Status: 🟢 Running
- Last Check: 8 seconds ago
- Queue Size: 1 email
- Avg Processing Time: 8.2s
- Emails Today: 12
```

### Email Notifications
- Subject: `[AI Employee] {Severity}: {Title}`
- Sent via Gmail API to user's email
- Rate limited: max 5 per hour

### Desktop Notifications
- Windows 10/11 toast notifications (using plyer or win10toast library)
- Only for CRITICAL severity
- Action buttons: "View Dashboard", "Dismiss"
- Example: "AI Employee Alert: Gmail Watcher has stopped"

---

## Success Criteria

1. ✅ Critical errors trigger all channels within 30 seconds
2. ✅ User receives email notifications for errors
3. ✅ Dashboard shows current alerts prominently
4. ✅ Desktop notifications appear for critical issues
5. ✅ No notification spam (rate limited appropriately)
6. ✅ All notifications logged for review

---

## References

- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q34 (error notification channels)
- [Component Tier Mapping](../architecture/component-tier-mapping.md)
- Windows Notifications: plyer library or win10toast
- Python logging module documentation

---

**Status:** ✅ Accepted
**Review Date:** After first week of Bronze Tier operation
