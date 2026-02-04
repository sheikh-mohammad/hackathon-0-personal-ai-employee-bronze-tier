# ADR-003: Multiple Focused Skills vs Single All-in-One Skill

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

Claude Code allows implementing AI functionality as "Agent Skills" - reusable, documented capabilities that can be invoked by name. The hackathon guide requires: "All AI functionality should be implemented as Agent Skills."

For Bronze Tier email processing, we need to:
1. Classify emails (priority, category, urgency)
2. Process emails (extract info, create summaries)
3. Update Dashboard (statistics, recent activity)

This can be architected as:
- **Option A:** Single skill that does everything
- **Option B:** Multiple focused skills, each with specific responsibility
- **Option C:** Hybrid approach with some combined skills

During discovery (Q25), user chose: **"Multiple focused skills (Recommended)"**

---

## Decision

**Implement Bronze Tier functionality as THREE focused skills:**

1. **`email-classifier`** - Classify emails by priority and category
2. **`email-processor`** - Process emails and extract actionable information
3. **`dashboard-updater`** - Update Dashboard with statistics and activity

Each skill has a single, well-defined responsibility.

---

## Rationale

### Why Multiple Focused Skills?

1. **Single Responsibility Principle**
   - Each skill does one thing well
   - Easier to understand, test, and debug
   - Changes to classification don't affect dashboard updates
   - Clear boundaries and interfaces

2. **Reusability**
   - `email-classifier` can be used by other watchers (WhatsApp, LinkedIn)
   - `dashboard-updater` can aggregate from multiple sources
   - Skills become building blocks for future features

3. **Testability**
   - Can test classification accuracy independently
   - Can verify dashboard updates without processing emails
   - Easier to write unit tests for focused functionality

4. **Maintainability**
   - Smaller, focused code is easier to maintain
   - Can improve one skill without touching others
   - Clear ownership and documentation per skill

5. **Composability**
   - Watcher can invoke skills in sequence or parallel
   - Can skip steps if needed (e.g., skip dashboard update)
   - Flexible orchestration for different workflows

6. **Product Quality Goal**
   - User wants "production quality" code
   - Modular architecture is more professional
   - Easier to extend for Silver/Gold tiers

### Why Not Single All-in-One Skill?

1. **Violates SRP**
   - One skill doing classification + processing + dashboard = too much
   - Hard to test individual components
   - Changes have wider blast radius

2. **Poor Reusability**
   - Can't reuse classification for other email sources
   - Can't reuse dashboard updates for other data
   - Monolithic skills don't compose well

3. **Harder to Debug**
   - If something fails, harder to isolate the issue
   - Logs mix concerns (classification + processing + dashboard)
   - Can't test components independently

---

## Skill Specifications

### Skill 1: `email-classifier`

**Purpose:** Classify a single email by priority and category

**Input:**
- Email markdown file path in /Needs_Action

**Output:**
- Updated email file with classification metadata:
  ```yaml
  priority: URGENT | HIGH | MEDIUM | LOW
  category: VIP | BUSINESS | PERSONAL | AUTOMATED
  urgency_keywords: [list of detected keywords]
  requires_response: true | false
  ```

**Logic:**
1. Read email file and Company_Handbook.md rules
2. Analyze sender, subject, content
3. Check for urgency keywords (urgent, asap, critical, etc.)
4. Categorize sender (VIP list, business domain, personal, automated)
5. Determine priority level based on rules
6. Update email file frontmatter with classification

**Success Criteria:**
- Classification accuracy > 90%
- Processes email in < 5 seconds
- Handles edge cases gracefully

---

### Skill 2: `email-processor`

**Purpose:** Extract actionable information from classified email

**Input:**
- Classified email markdown file path

**Output:**
- Updated email file with extracted information:
  ```yaml
  action_items: [list of tasks/questions]
  deadlines: [list of dates with context]
  key_people: [mentioned names/contacts]
  attachments_summary: [what attachments contain]
  suggested_response: [brief response suggestion]
  ```
- Plan file in /Plans with detailed analysis

**Logic:**
1. Read classified email file
2. Extract questions that need answers
3. Identify deadlines, dates, time-sensitive items
4. Detect requests and action items
5. Summarize attachments (if any)
6. Suggest response approach (for Silver tier)
7. Create Plan.md with detailed breakdown
8. Move email file to /Done

**Success Criteria:**
- Extracts all action items correctly
- Identifies 95%+ of deadlines
- Creates useful, actionable plans

---

### Skill 3: `dashboard-updater`

**Purpose:** Update Dashboard.md with current statistics and activity

**Input:**
- Vault path (reads from /Done, /Needs_Action, /Plans)

**Output:**
- Updated Dashboard.md with:
  - Current timestamp
  - Email counts (today, this week)
  - Priority breakdown
  - Category breakdown
  - Recent activity (last 10 items)
  - Urgent items requiring attention

**Logic:**
1. Read Dashboard.md current state
2. Scan /Done folder for processed emails
3. Scan /Needs_Action for pending items
4. Calculate statistics (counts, breakdowns)
5. Generate recent activity timeline
6. Identify urgent items
7. Update Dashboard.md with new data

**Success Criteria:**
- Dashboard always shows accurate counts
- Updates complete in < 3 seconds
- Handles concurrent updates gracefully

---

## Invocation Flow

### Sequential Processing (Bronze Tier)

```python
# In gmail_watcher.py

def process_email(email_file: Path):
    """Process a new email through the skill pipeline"""

    # Step 1: Classify
    subprocess.run([
        'ccr', '--skill', 'email-classifier',
        str(email_file)
    ])

    # Step 2: Process
    subprocess.run([
        'ccr', '--skill', 'email-processor',
        str(email_file)
    ])

    # Step 3: Update Dashboard
    subprocess.run([
        'ccr', '--skill', 'dashboard-updater',
        str(vault_path)
    ])
```

### Error Handling

- If classifier fails: Log error, mark for manual review, skip processor
- If processor fails: Email stays classified, can retry processing
- If dashboard fails: Log error, doesn't affect email processing

---

## Consequences

### Positive

- ✅ Clean, modular architecture
- ✅ Each skill is testable independently
- ✅ Skills are reusable across watchers
- ✅ Easy to improve individual components
- ✅ Clear separation of concerns
- ✅ Professional code structure
- ✅ Easier to onboard contributors

### Negative

- ❌ More files to manage (3 skills vs 1)
- ❌ More invocations (3 subprocess calls vs 1)
- ❌ Slightly more complex orchestration
- ❌ Need to handle inter-skill dependencies

### Mitigations

- Document skill interfaces clearly
- Create helper function for skill invocation
- Add integration tests for full pipeline
- Monitor total processing time (should be < 15 seconds)

---

## Alternatives Considered

### Alternative 1: Single All-in-One Skill

**Pros:**
- Simpler invocation (one call)
- Fewer files to manage
- Faster execution (no subprocess overhead)

**Cons:**
- Violates SRP
- Hard to test components
- Poor reusability
- Harder to maintain

**Rejected because:** User wants production quality, modular architecture is more professional

### Alternative 2: Two Skills (Classify+Process, Dashboard)

**Pros:**
- Fewer skills than three
- Still separates dashboard concerns
- Simpler than three skills

**Cons:**
- Classify+Process still does too much
- Can't reuse classifier independently
- Harder to test classification accuracy

**Rejected because:** Still violates SRP, doesn't maximize reusability

---

## Future Extensions

### Silver Tier Additions

Add new skills:
- `email-drafter` - Generate reply drafts
- `approval-checker` - Monitor approval workflow

Existing skills remain unchanged, just add new ones.

### Gold Tier Additions

Add new skills:
- `business-auditor` - Weekly business analysis
- `invoice-tracker` - Track invoices and payments

Classifier and processor can be reused for other data sources.

---

## Testing Strategy

### Unit Tests (Per Skill)

**email-classifier:**
- Test with urgent keywords → URGENT priority
- Test with VIP sender → VIP category
- Test with newsletter patterns → LOW priority
- Test edge cases (empty email, malformed data)

**email-processor:**
- Test action item extraction accuracy
- Test deadline detection (various date formats)
- Test with emails containing no action items
- Test attachment summarization

**dashboard-updater:**
- Test statistics calculation accuracy
- Test with empty vault
- Test with large number of emails
- Test concurrent update handling

### Integration Tests

- Test full pipeline: classify → process → dashboard
- Test with real Gmail API data
- Test error recovery (skill failures)
- Test performance (end-to-end < 15 seconds)

---

## Success Criteria

1. ✅ All three skills implemented and documented
2. ✅ Each skill passes unit tests
3. ✅ Full pipeline passes integration tests
4. ✅ Skills are reusable (can invoke independently)
5. ✅ Clear documentation for each skill
6. ✅ Error handling works correctly

---

## References

- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q25
- [Hackathon Guide](../Personal_AI_Employee_Hackathon_0_Building_Autonomous_FTEs_in_2026.md) - Agent Skills requirement
- [Claude Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

**Status:** ✅ Accepted
**Review Date:** After Bronze Tier implementation
