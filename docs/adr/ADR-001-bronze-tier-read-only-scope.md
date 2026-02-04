# ADR-001: Bronze Tier Scope - Read-Only Email Monitoring

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

During initial discovery, there was ambiguity about whether Bronze Tier should include email sending capabilities. The user initially answered questions about email drafting and approval workflows, suggesting they expected sending functionality.

Upon reviewing the hackathon guide, we discovered:
- Bronze Tier: "One working Watcher script (Gmail OR file system monitoring)"
- Silver Tier: "One working MCP server for external action (e.g., sending emails)"

This created a decision point: stick to Bronze requirements or upgrade scope to Silver.

---

## Decision

**Bronze Tier will be READ-ONLY email monitoring with NO sending capabilities.**

Scope includes:
- ✅ Gmail API monitoring
- ✅ Email classification and prioritization
- ✅ Action item extraction
- ✅ Dashboard updates
- ✅ Creating summaries and plans
- ❌ Email sending (deferred to Silver)
- ❌ MCP servers (deferred to Silver)
- ❌ HITL approval workflow for sending (deferred to Silver)

---

## Rationale

### Why Read-Only?

1. **Hackathon Alignment**
   - Guide explicitly places "MCP server for external action (e.g., sending emails)" in Silver Tier
   - Bronze is about establishing foundation: perception and reasoning
   - Action layer comes in Silver with proper safeguards

2. **Risk Management**
   - Read-only operations have zero risk of unintended consequences
   - No chance of sending wrong email to wrong person
   - Safe to test with production email account
   - Can iterate and refine classification without worry

3. **Tier-by-Tier Progression**
   - User chose "tier-by-tier progression" approach
   - Perfect Bronze foundation before adding complexity
   - Easier to debug and validate each component
   - Clear success criteria for Bronze completion

4. **Time Management**
   - Bronze estimate: 8-12 hours
   - Adding email sending would push into Silver territory (20-30 hours)
   - Focus effort on quality monitoring and classification
   - Avoid scope creep

### Why Not Upgrade to Silver Immediately?

1. **Product Quality Focus**
   - User wants "production quality" and "hackathon → product path"
   - Better to have excellent Bronze than mediocre Silver
   - Establish solid foundation before adding complexity

2. **Learning Curve**
   - First time building this type of system
   - Read-only allows learning without risk
   - Can refine classification before adding actions

3. **Testing and Validation**
   - Easier to validate read-only system
   - Can run for days/weeks to ensure reliability
   - Build confidence before adding sending capability

---

## Consequences

### Positive

- ✅ Clear, achievable scope for Bronze
- ✅ Zero risk of unintended email sends
- ✅ Can test with production email safely
- ✅ Faster to implement and validate
- ✅ Solid foundation for Silver tier
- ✅ Meets hackathon Bronze requirements exactly

### Negative

- ❌ No immediate productivity gain from auto-replies
- ❌ Still need to manually send emails
- ❌ Less impressive demo than Silver tier
- ❌ Requires Silver tier work to get full value

### Mitigations

- Document upgrade path to Silver clearly
- Design architecture to make Silver additions easy
- Focus Bronze on excellent classification and insights
- Make Dashboard so useful that read-only provides value

---

## Alternatives Considered

### Alternative 1: Bronze+ (Hybrid)
Add email sending as "bonus feature" beyond Bronze requirements.

**Rejected because:**
- Violates tier-by-tier progression principle
- Adds significant complexity and risk
- Would take 15-20 hours, not 8-12
- Undermines the value of tier system

### Alternative 2: Minimal Silver
Do Bronze requirements + minimal email sending.

**Rejected because:**
- Email sending requires MCP server (significant work)
- Requires HITL approval workflow (more complexity)
- Would be incomplete Silver, not enhanced Bronze
- Better to have complete Bronze than incomplete Silver

---

## Implementation Notes

### What Bronze WILL Do

1. **Monitor Gmail continuously**
   - Poll every 2 minutes
   - Extract all relevant metadata
   - Create action files in vault

2. **Classify intelligently**
   - Priority levels (URGENT/HIGH/MEDIUM/LOW)
   - Sender categories (VIP/Business/Personal/Automated)
   - Keyword-based urgency detection

3. **Extract actionable information**
   - Questions that need answers
   - Deadlines and dates
   - Attachments requiring review
   - Tasks and requests

4. **Provide insights**
   - Dashboard with statistics
   - Recent activity timeline
   - Priority breakdown
   - Sender analysis

### What User Does Manually (Until Silver)

- Read email summaries in Obsidian
- Decide on responses
- Compose and send replies in Gmail
- Mark items as done in vault

---

## Success Criteria

Bronze Tier is successful when:

1. ✅ Gmail watcher runs continuously without crashes
2. ✅ All new emails appear in vault within 2 minutes
3. ✅ Classification accuracy > 90%
4. ✅ Dashboard updates automatically
5. ✅ Action items extracted correctly
6. ✅ Zero false positives on urgency
7. ✅ System runs for 7 days without manual intervention

---

## Future Work

### Silver Tier Additions
- Email MCP server for sending
- HITL approval workflow (/Pending_Approval, /Approved)
- Email drafting skill
- Orchestrator for approval management

### Upgrade Path
1. Keep all Bronze components unchanged
2. Add MCP server for Gmail sending
3. Add approval folders and workflow
4. Add email drafter skill
5. Add orchestrator to manage approvals
6. Test thoroughly before going live

---

## References

- [Hackathon Guide](../Personal_AI_Employee_Hackathon_0_Building_Autonomous_FTEs_in_2026.md) - Lines 118-150
- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q17
- [Component Tier Mapping](../architecture/component-tier-mapping.md)

---

**Status:** ✅ Accepted and Implemented
**Review Date:** After Bronze Tier completion
