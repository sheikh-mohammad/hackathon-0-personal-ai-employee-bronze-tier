# Bronze Tier AI Employee - Project Decisions & Context

**Date Created:** 2026-02-04
**Tier:** Bronze (Foundation Level)
**Status:** Planning Phase

---

## Project Overview

Building a Personal AI Employee using Claude Code and Obsidian to automate personal tasks including email management, message monitoring, scheduling, and social media. This is the Bronze Tier implementation focusing on foundational capabilities.

---

## Discovery Session - Questions & Answers

### Session 1: Primary Goals & Setup

**Q1: What's your primary goal for this AI Employee? What do you want it to help you with first?**
- **Answer:** Personal tasks (emails, messages, scheduling, social media)
- **Decision:** Focus on personal automation rather than business operations initially

**Q2: Which service would you prefer to start monitoring first for your Bronze Tier watcher?**
- **Answer:** Gmail (Recommended)
- **Decision:** Implement Gmail watcher as the first monitoring service using Google APIs

**Q3: Have you already set up the required software from the prerequisites?**
- **Answer:**
  - ✅ Obsidian installed and vault created
  - ✅ Python 3.13+ installed
  - ✅ Node.js v24+ installed
- **Decision:** All prerequisites are in place, can proceed with implementation

**Q4: What's your comfort level with technical tasks like running Python scripts and using command line?**
- **Answer:** Intermediate - comfortable with basics
- **Decision:** Provide clear instructions with some technical detail, but include explanations for complex steps

---

### Session 2: Email Management Details

**Q5: What types of emails should your AI Employee monitor and create action items for?**
- **Answer:** (Multiple selections)
  - All unread emails
  - Important/urgent emails only
  - Specific senders (clients, boss, etc)
  - Emails with attachments/invoices
- **Decision:** Implement comprehensive email monitoring with classification logic to handle all these categories

**Q6: Which social media platforms do you want to integrate (can be added later)?**
- **Answer:** Not needed for Bronze
- **Decision:** Skip social media integration for Bronze Tier, focus on email and messaging

**Q7: How much autonomy should the AI have with your emails?**
- **Answer:** Reply to emails with Human in the Loop
- **Decision:** AI drafts replies but requires human approval before sending (HITL pattern)

**Q8: When should your AI Employee check and process your emails?**
- **Answer:** Continuous monitoring
- **Decision:** Implement continuous Gmail watcher that runs as a background process

---

### Session 3: Technical Configuration

**Q9: Do you already have Gmail API credentials set up, or do you need guidance on getting them?**
- **Answer:** Already have API credentials
- **Decision:** Use existing credentials.json file, no need for API setup guide

**Q10: How should the AI identify which emails are most important to you?**
- **Answer:** By classifying processing by AI and will be specified by me later in other files
- **Decision:** Implement AI-based classification system with configuration files that can be customized later

**Q11: What style of email responses do you typically send?**
- **Answer:** (Multiple selections)
  - Formal business responses
  - Casual/friendly tone
  - Mirror sender's style
- **Decision:** Implement adaptive response style that can match context and sender relationship

**Q12: How do you want to approve email replies before they're sent?**
- **Answer:** Approve in Obsidian, AI sends (Recommended)
- **Decision:** Implement file-based approval workflow: AI creates draft → user moves to /Approved → AI sends

---

### Session 4: Practical Setup

**Q13: Where should the AI Employee store its files and dashboard?**
- **Answer:** Use AI_Employee_Vault/ (Recommended)
- **Decision:** Use existing `AI_Employee_Vault/` directory in project root

**Q14: How do you want to test the system before going fully live?**
- **Answer:** Start with production emails
- **Decision:** Go live with real emails (ensure HITL approval is working correctly before any sends)

**Q15: Where should Gmail API credentials and sensitive data be stored?**
- **Answer:** .env file (Recommended)
- **Decision:** Create `.env` file in project root (add to .gitignore) for credentials

**Q16: How do you want to handle email classification and response rules initially?**
- **Answer:** Leave this for now. We will talk about it later
- **Decision:** Create placeholder configuration files with basic rules, document how to customize later

---

## Technical Decisions Summary

### Architecture Components

1. **Knowledge Base:** AI_Employee_Vault/ (Obsidian vault)
2. **Reasoning Engine:** Claude Code
3. **Primary Watcher:** Gmail Watcher (Python script)
4. **Action Layer:** Email MCP server for sending
5. **Approval System:** File-based HITL workflow

### Folder Structure (Bronze Tier)

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status summary
├── Company_Handbook.md       # Rules and guidelines
├── Inbox/                    # New items detected by watchers
├── Needs_Action/             # Items requiring processing
├── Plans/                    # Claude's execution plans
├── Pending_Approval/         # Drafts awaiting approval
├── Approved/                 # Approved actions ready to execute
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
```

### Security & Privacy

- **Credentials:** Stored in `.env` file (gitignored)
- **Approval Required:** All email sends require human approval
- **Audit Logging:** All actions logged to /Logs
- **Local-First:** All data stays on local machine

### Email Processing Workflow

1. **Detection:** Gmail Watcher polls for new emails (every 10 seconds)
2. **Classification:** AI categorizes by importance, sender, content type
3. **Action Creation:** Creates .md file in /Needs_Action
4. **Reasoning:** Claude Code reads and creates response plan
5. **Draft Creation:** AI writes draft reply to /Pending_Approval
6. **Human Review:** User reviews draft in Obsidian
7. **Approval:** User moves file to /Approved
8. **Execution:** Email MCP sends the approved reply

### Response Style Guidelines

- **Business contacts:** Formal, professional tone
- **Personal contacts:** Casual, friendly tone
- **Unknown senders:** Match their style and formality
- **Adaptive:** AI analyzes sender relationship and context

---

## Current Project State

### Existing Files
- ✅ `AI_Employee_Vault/` - Obsidian vault created
- ✅ `AI_Employee_Vault/Dashboard.md` - Exists
- ✅ `AI_Employee_Vault/Company_Handbook.md` - Exists
- ✅ `pyproject.toml` - Python project configured
- ✅ `.venv/` - Virtual environment set up
- ⚠️ `docs/` - Empty, needs documentation
- ⚠️ `AGENTS.md` - Empty
- ⚠️ `README.md` - Empty

### What Needs to Be Built

1. **Gmail Watcher Script** (`watchers/gmail_watcher.py`)
   - Poll Gmail API for new emails
   - Create action files in vault
   - Run continuously as background process

2. **Orchestrator** (`orchestrator.py`)
   - Monitor vault folders
   - Trigger Claude Code when needed
   - Handle approval workflow
   - Manage email sending

3. **Email MCP Server** (Node.js)
   - Send approved emails via Gmail API
   - Handle attachments
   - Log all sends

4. **Configuration Files**
   - `.env` for credentials
   - Email classification rules
   - Response templates
   - Sender priority lists

5. **Claude Code Skills**
   - Email classification skill
   - Response drafting skill
   - Dashboard update skill

6. **Documentation**
   - Setup instructions
   - Usage guide
   - Troubleshooting guide

---

## Bronze Tier Success Criteria

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [ ] One working Watcher script (Gmail monitoring)
- [ ] Claude Code successfully reading from and writing to the vault
- [ ] Basic folder structure: /Inbox, /Needs_Action, /Done
- [ ] All AI functionality implemented as Agent Skills
- [ ] Human-in-the-loop approval workflow working
- [ ] Email drafting and sending capability
- [ ] Audit logging in place

---

## Next Steps

1. Create vault folder structure
2. Set up .env file with Gmail credentials
3. Implement Gmail Watcher script
4. Create Email MCP server
5. Build Orchestrator
6. Create Claude Code skills for email processing
7. Test end-to-end workflow with real emails
8. Document usage and troubleshooting

---

## Notes & Considerations

- **Safety First:** HITL approval is mandatory for all sends in Bronze Tier
- **Continuous Monitoring:** Watcher needs process manager (PM2) for reliability
- **Classification:** Will be refined over time based on user feedback
- **Extensibility:** Architecture designed to add more watchers (WhatsApp, file system) later
- **Learning:** System will improve as user approves/rejects drafts

---

## Questions for Later Discussion

1. Specific email addresses/domains to prioritize
2. Detailed classification rules and keywords
3. Response templates for common scenarios
4. Scheduling preferences (if any)
5. Integration with calendar/tasks (future enhancement)

---

**Last Updated:** 2026-02-04
**Next Review:** After Bronze Tier implementation complete
