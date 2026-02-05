# ADR-002: Watcher Directly Invokes Claude Code (No Orchestrator)

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

The hackathon guide mentions both "Watchers" and an "Orchestrator" but doesn't clearly specify which tier requires which component. The guide shows:

```
Orchestrator.py (Master Process)
- Scheduling | Folder Watching | Process Management
```

This created ambiguity about whether Bronze Tier needs:
1. Just a watcher that creates files
2. Watcher + Orchestrator that triggers Claude
3. Watcher that directly invokes Claude

During discovery (Q18), user was asked about the workflow and chose: **"Watcher triggers Claude directly"**

---

## Decision

**Gmail Watcher will directly invoke Claude Code via subprocess when new emails are detected. No separate orchestrator for Bronze Tier.**

Architecture:
```
Gmail API → gmail_watcher.py → subprocess.run(['ccr code', '--skill', 'email-processor']) → Vault
```

---

## Rationale

### Why Direct Invocation?

1. **Simplicity for Bronze**
   - Bronze requirement: "One working Watcher script"
   - Single process is easier to develop, test, and debug
   - Fewer moving parts = fewer failure points
   - Matches user's "Bronze + practical additions" goal

2. **Immediate Processing**
   - No polling delay between detection and processing
   - Email detected → immediately processed
   - Better user experience for continuous monitoring

3. **Clear Responsibility**
   - Watcher owns the entire flow: detect → process → log
   - Single point of failure, single log file
   - Easier to troubleshoot issues

4. **No Folder Watching Needed**
   - Watcher knows when it creates files
   - No need to poll /Needs_Action folder
   - Reduces system overhead

### Why Not Orchestrator?

1. **Orchestrator is Silver Tier Complexity**
   - Needed for approval workflow management
   - Monitors /Pending_Approval → /Approved → trigger MCP
   - Bronze has no approval workflow (read-only)
   - Orchestrator would be idle 99% of the time

2. **YAGNI Principle**
   - "You Aren't Gonna Need It"
   - Don't build infrastructure before it's needed
   - Can add orchestrator in Silver when approval workflow is added

3. **Development Time**
   - Orchestrator would take 2-3 hours to build properly
   - That time better spent on classification quality
   - Aligns with tier-by-tier progression

---

## Consequences

### Positive

- ✅ Simpler architecture for Bronze
- ✅ Faster development (no orchestrator to build)
- ✅ Immediate email processing (no polling delay)
- ✅ Single process to manage and monitor
- ✅ Easier debugging (single log file)
- ✅ Lower system resource usage

### Negative

- ❌ Watcher becomes more complex (detection + invocation)
- ❌ Tight coupling between watcher and Claude Code
- ❌ Harder to add multiple watchers later (each needs invocation logic)
- ❌ No centralized scheduling or coordination

### Mitigations

- Keep invocation logic simple and reusable
- Extract invocation into a helper function/module
- Document the invocation pattern for future watchers
- Design for easy orchestrator addition in Silver

---

## Implementation Details

### Watcher Structure

```python
# gmail_watcher.py

import subprocess
import logging
from pathlib import Path

class GmailWatcher:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'

    def check_for_updates(self):
        """Poll Gmail API for new emails"""
        # ... Gmail API logic ...

    def create_action_file(self, email):
        """Create .md file in /Needs_Action"""
        filepath = self.needs_action / f'EMAIL_{email["id"]}.md'
        # ... write email data ...
        return filepath

    def invoke_claude(self, action_file: Path):
        """Invoke Claude Code to process the email"""
        try:
            result = subprocess.run(
                ['ccr', 'code', '--skill', 'email-processor', str(action_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logging.info(f"Processed {action_file.name}")
            else:
                logging.error(f"Claude failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logging.error(f"Claude timeout on {action_file.name}")
        except Exception as e:
            logging.error(f"Invocation error: {e}")

    def run(self):
        """Main watcher loop"""
        while True:
            new_emails = self.check_for_updates()
            for email in new_emails:
                action_file = self.create_action_file(email)
                self.invoke_claude(action_file)
            time.sleep(10)  # Check every 10 seconds
```

### Error Handling

- **Claude Code unavailable:** Log error, continue watching
- **Skill execution fails:** Log error, mark file for manual review
- **Timeout:** Log timeout, continue (don't block watcher)
- **Subprocess crash:** Catch exception, log, continue

## Alternatives Considered

### Alternative 1: Watcher Creates Files, Manual Claude Invocation
User manually runs Claude Code skills when they want to process emails.

**Rejected because:**
- Defeats purpose of "continuous monitoring"
- User wanted automatic processing
- Not practical for daily use
- Doesn't meet "Bronze + practical additions" goal

### Alternative 2: Watcher + Orchestrator (Full Architecture)
Build complete orchestrator from the start.

**Rejected because:**
- Over-engineering for Bronze
- Orchestrator has no work to do (no approval workflow)
- Violates tier-by-tier progression
- Would take 3-4 extra hours

### Alternative 3: File-Based Trigger
Watcher creates files, Claude watches folder with file system watcher.

**Rejected because:**
- Requires Claude Code to run continuously
- More complex than direct invocation
- Two processes instead of one
- Polling overhead on file system

---

## Upgrade Path to Silver

When adding orchestrator in Silver:

1. **Keep watcher's direct invocation for immediate processing**
   - Watcher still processes emails immediately
   - Orchestrator handles approval workflow separately

2. **Orchestrator responsibilities:**
   - Monitor /Pending_Approval folder
   - Detect approved files in /Approved
   - Invoke MCP servers for actions
   - Handle timeouts and rejections

3. **Separation of concerns:**
   - Watcher: Detection → Processing → Action files
   - Orchestrator: Approval monitoring → Action execution
   - No overlap, clean boundaries

---

## Testing Strategy

### Unit Tests
- Test `invoke_claude()` with mock subprocess
- Test error handling for various failure modes
- Test timeout handling

### Integration Tests
- Test watcher → Claude → vault workflow end-to-end
- Test with real Gmail API (test account)
- Test Claude Code skill execution

### Reliability Tests
- Run for 24 hours, verify no crashes
- Test with Claude Code unavailable
- Test with skill execution failures
- Test with network interruptions

---

## Success Criteria

1. ✅ Watcher detects new email within 10 seconds
2. ✅ Claude Code invoked automatically
3. ✅ Email processed and moved to /Done
4. ✅ Dashboard updated with new statistics
5. ✅ Watcher continues running after Claude errors
6. ✅ All actions logged properly

---

## References

- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q18, Q19, Q20
- [Component Tier Mapping](../architecture/component-tier-mapping.md) - Orchestrator section
- [Hackathon Guide](../Personal_AI_Employee_Hackathon_0_Building_Autonomous_FTEs_in_2026.md) - Orchestration Layer

---

**Status:** ✅ Accepted
**Review Date:** When starting Silver Tier implementation
