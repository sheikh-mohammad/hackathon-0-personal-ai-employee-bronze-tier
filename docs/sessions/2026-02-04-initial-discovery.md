# Discovery Session - Initial Requirements Gathering

**Date:** 2026-02-04
**Session Type:** Initial Discovery
**Participants:** User, Claude Code
**Duration:** ~45 minutes

---

## Session Overview

Initial discovery session to understand user requirements, technical setup, and product vision for the Personal AI Employee project. This session established the foundation for Bronze Tier implementation.

---

## Questions & Answers

### Session 1: Primary Goals & Setup

**Q1: What's your primary goal for this AI Employee?**
- **Answer:** Personal tasks (emails, messages, scheduling, social media)
- **Context:** Focus on personal automation rather than business operations
- **Impact:** Determines use cases and feature prioritization

**Q2: Which service to start monitoring first?**
- **Answer:** Gmail (Recommended option)
- **Context:** User has Gmail API credentials already
- **Impact:** Gmail Watcher will be the first component built

**Q3: Software setup status?**
- **Answer:** All prerequisites installed
  - ✅ Obsidian with vault created
  - ✅ Python 3.13+
  - ✅ Node.js v24+
- **Impact:** Can proceed directly to implementation

**Q4: Technical comfort level?**
- **Answer:** Intermediate - comfortable with basics
- **Context:** Can run scripts, follow technical docs with guidance
- **Impact:** Documentation should be clear but can include technical details

---

### Session 2: Email Management Details

**Q5: What types of emails to monitor?**
- **Answer:** Multiple categories
  - All unread emails
  - Important/urgent emails
  - Specific senders (clients, boss, etc.)
  - Emails with attachments/invoices
- **Impact:** Need comprehensive classification system

**Q6: Social media integration?**
- **Answer:** Not needed for Bronze
- **Impact:** Defer to Silver/Gold tier

**Q7: Email autonomy level?**
- **Answer:** Reply to emails with Human in the Loop
- **Context:** Initially thought this was Bronze, but it's actually Silver tier
- **Impact:** Bronze will be read-only monitoring

**Q8: When to check emails?**
- **Answer:** Continuous monitoring
- **Impact:** Watcher needs to run as background process

---

### Session 3: Technical Configuration

**Q9: Gmail API credentials status?**
- **Answer:** Already have API credentials
- **Impact:** No need for API setup guide

**Q10: Email importance identification?**
- **Answer:** AI-based classification, will be specified later in config files
- **Impact:** Need flexible classification system with config files

**Q11: Email response style?**
- **Answer:** Multiple styles needed
  - Formal business responses
  - Casual/friendly tone
  - Mirror sender's style
- **Impact:** Adaptive response system (for Silver tier)

**Q12: Approval workflow preference?**
- **Answer:** Approve in Obsidian, AI sends
- **Context:** This is Silver tier functionality
- **Impact:** Bronze will focus on monitoring only

---

### Session 4: Practical Setup

**Q13: Vault location?**
- **Answer:** Use AI_Employee_Vault/ (existing)
- **Impact:** Use existing vault structure

**Q14: Testing approach?**
- **Answer:** Start with production emails
- **Impact:** Need robust error handling from day one

**Q15: Credentials storage?**
- **Answer:** .env file (gitignored)
- **Impact:** Standard secure credential management

**Q16: Classification rules?**
- **Answer:** Leave for later discussion
- **Impact:** Create placeholder config, document customization

---

### Session 5: Tier Clarification

**Q17: Bronze vs Silver tier scope?**
- **Answer:** Stick to Bronze Tier
- **Key Insight:** Email sending is Silver tier, not Bronze
- **Impact:** Bronze = read-only monitoring + classification

**Q18: Orchestrator requirement?**
- **Answer:** Use gmail_watcher script directly
- **Impact:** Watcher triggers Claude Code directly, no separate orchestrator

**Q19: Watchdog requirement?**
- **Answer:** Not needed for Bronze
- **Impact:** Defer to Gold tier

**Q20: Email processing workflow?**
- **Answer:** Watcher triggers Claude directly
- **Impact:** Simplified architecture for Bronze

**Q21: Tier ambition?**
- **Answer:** Bronze + practical additions
- **Impact:** Add useful features beyond minimum requirements

---

### Session 6: Implementation Details

**Q22: How to invoke Claude Code?**
- **Answer:** Using Claude Code Router (CCR)
- **Impact:** Need to understand CCR invocation from Python

**Q23: Documentation structure?**
- **Answer:** Different folders for different purposes
  - Q&A sessions
  - ADR (Architecture Decision Records)
  - Guides and setup instructions
- **Impact:** Professional documentation structure needed

**Q24: Practical additions?**
- **Answer:** All selected
  - Smart classification
  - Dashboard statistics
  - Action item extraction
  - Daily summary (deferred - not for Bronze)
- **Impact:** Enhanced Bronze tier with useful features

**Q25: Skills organization?**
- **Answer:** Multiple focused skills
- **Impact:** Modular skill architecture

**Q26: Action items storage?**
- **Answer:** Will discuss later
- **Impact:** Design flexible storage system

---

### Session 7: Product Vision

**Q27: Long-term product vision?**
- **Answer:** Personal use, production quality
- **Impact:** Build for reliability and maintainability

**Q28: Development practices?**
- **Answer:** All professional practices
  - Git best practices
  - Automated testing
  - Code quality tools
  - Production error handling
- **Impact:** Set up proper development infrastructure

**Q29: Product roadmap approach?**
- **Answer:** Tier-by-tier progression
- **Impact:** Perfect Bronze, then move to Silver, then Gold

**Q30: Quality standard?**
- **Answer:** Hackathon → Product path
- **Impact:** Start functional, document for evolution to production

---

## Key Decisions Summary

### Scope Decisions
1. **Bronze Tier Only** - Read-only email monitoring, no sending
2. **Gmail First** - Start with Gmail watcher, defer other services
3. **Continuous Monitoring** - Background process, not scheduled
4. **No Orchestrator** - Watcher invokes Claude directly
5. **No Watchdog** - Defer to Gold tier

### Technical Decisions
1. **Claude Code Router (CCR)** - For LLM flexibility
2. **Multiple Skills** - Modular architecture
3. **AI Classification** - Flexible, config-driven
4. **Local-First** - All data in Obsidian vault
5. **.env Credentials** - Standard secure storage

### Product Decisions
1. **Production Quality** - Professional development practices
2. **Tier-by-Tier** - Perfect each tier before advancing
3. **Well Documented** - Comprehensive docs for evolution
4. **Tested** - Automated testing from the start
5. **Maintainable** - Code quality tools and standards

### Feature Decisions
1. **Smart Classification** - Priority levels, sender categories
2. **Dashboard Statistics** - Email counts, trends
3. **Action Item Extraction** - Automatic task identification
4. **Daily Summary** - Deferred to post-Bronze

---

## Open Questions

1. **Action Items Storage** - Where/how to store extracted action items?
2. **Classification Rules** - Specific rules and keywords to use?
3. **CCR Invocation** - Exact syntax for calling CCR from Python?
4. **Priority Contacts** - Specific email addresses/domains to prioritize?
5. **Dashboard Layout** - Exact structure and sections?

---

## Next Steps

1. Create ADR documents for key architectural decisions
2. Set up professional docs structure
3. Create component breakdown (Bronze vs Silver vs Gold)
4. Design Bronze tier architecture
5. Create implementation roadmap

---

## Notes

- User is serious about this being a product, not just a hackathon submission
- Quality and maintainability are priorities
- Documentation is critical for future evolution
- Testing and error handling are non-negotiable
- Architecture should support tier-by-tier growth

---

**Session Status:** ✅ Complete
**Next Session:** Architecture design and component breakdown
