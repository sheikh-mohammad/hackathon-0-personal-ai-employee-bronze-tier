# Component Tier Mapping

**Purpose:** Define which components belong to which hackathon tier to avoid scope creep and ensure clear progression.

**Last Updated:** 2026-02-04

---

## Tier Definitions

### Bronze Tier: Foundation (8-12 hours)
**Goal:** Read-only monitoring with intelligent classification and replies writing with summaries
**Deliverable:** Working email monitoring system that creates action items

### Silver Tier: Functional Assistant (20-30 hours)
**Goal:** Add action capabilities with human approval
**Deliverable:** Can draft and send emails with HITL workflow

### Gold Tier: Autonomous Employee (40+ hours)
**Goal:** Multi-domain integration with autonomous workflows
**Deliverable:** Full business automation with accounting integration

---

## Component Breakdown

### 🟢 Bronze Tier Components

#### Core Infrastructure
- ✅ **Obsidian Vault Structure**
  - Dashboard.md
  - Company_Handbook.md
  - Folder structure: /Inbox, /Needs_Action, /Done

- ✅ **Gmail Watcher** (`watchers/gmail_watcher.py`)
  - Poll Gmail API every 10 seconds
  - Extract email metadata (from, subject, snippet, labels, attachments)
  - Create .md files in /Inbox
  - Track processed IDs to avoid duplicates
  - Basic error handling

- ✅ **Claude Code Skills**
  - `.claude/skills/email-classifier/` - Classify emails by priority/category
  - `.claude/skills/email-processor/` - Process emails and extract information
  - `.claude/skills/email-reply-writer/` - Email replies wirting by analyzing the email that came
  - `.claude/skills/summary-creation/` - Summary Writing for emails and other actions
  - `.claude/skills/dashboard-updater/` - Update Dashboard with statistics

- ✅ **Configuration System**
  - `.env` file for credentials
  - Company_Handbook.md for processing guidelines

#### Bronze+ Practical Additions
- ✅ **Smart Classification**
  - Priority levels: URGENT, HIGH, MEDIUM, LOW
  - Sender categorization: VIP, Business, Personal, Automated
  - Keyword-based urgency detection

- ✅ **Dashboard Statistics**
  - Emails processed today/this week
  - Breakdown by priority level
  - Breakdown by sender category
  - Recent activity timeline

- ✅ **Action Item Extraction**
  - Identify questions that need answers
  - Extract deadlines and dates
  - Flag attachments for review
  - Detect requests and tasks

#### Documentation (Bronze)
- ✅ Setup guide
- ✅ Usage guide
- ✅ Architecture overview
- ✅ Troubleshooting guide

---

### 🟡 Silver Tier Components

#### Action Layer
- ⏳ **Email MCP Server** (Node.js)
  - Send emails via Gmail API
  - Handle attachments
  - Support CC/BCC
  - Delivery confirmation

- ⏳ **Human-in-the-Loop Workflow**
  - /Pending_Approval folder
  - /Approved folder
  - /Rejected folder
  - Approval file format with metadata

- ⏳ **Orchestrator** (`orchestrator.py`)
  - Monitor approval folders
  - Trigger MCP actions when approved
  - Handle approval timeouts
  - Audit logging for all actions

#### Additional Watchers
- ⏳ **WhatsApp Watcher** (Playwright-based)
  - Monitor WhatsApp Web
  - Keyword detection
  - Create action files

- ⏳ **LinkedIn Watcher**
  - Monitor messages and notifications
  - Auto-post capability (with approval)

#### Enhanced Skills
- ⏳ **Email Drafter Skill**
  - Generate reply drafts
  - Match sender's tone
  - Include context from thread

- ⏳ **Plan Creator Skill**
  - Create Plan.md files
  - Multi-step task breakdown
  - Dependency tracking

#### Scheduling
- ⏳ **Cron/Task Scheduler Integration**
  - Daily briefing generation
  - Weekly summaries
  - Periodic health checks

---

### 🟠 Gold Tier Components

#### Multi-Domain Integration
- ⏳ **Odoo Accounting Integration**
  - Self-hosted Odoo Community
  - MCP server for Odoo JSON-RPC API
  - Invoice tracking
  - Payment logging

- ⏳ **Social Media Integration**
  - Facebook posting and monitoring
  - Instagram posting and monitoring
  - Twitter/X posting and monitoring

- ⏳ **Finance Watcher**
  - Bank API integration
  - Transaction monitoring
  - Expense categorization

#### Autonomous Workflows
- ⏳ **Ralph Wiggum Loop**
  - Stop hook implementation
  - Multi-step task completion
  - Automatic iteration until done

- ⏳ **Weekly Business Audit**
  - Revenue tracking
  - Bottleneck identification
  - CEO briefing generation

- ⏳ **Error Recovery**
  - Graceful degradation
  - Automatic retry logic
  - Fallback mechanisms

#### Process Management
- ⏳ **Watchdog** (`watchdog.py`)
  - Monitor all processes
  - Auto-restart on failure
  - Health check reporting
  - Alert on critical failures

#### Advanced Features
- ⏳ **Comprehensive Audit Logging**
  - All actions logged with metadata
  - Approval trail
  - Performance metrics

- ⏳ **Multiple MCP Servers**
  - Email MCP
  - Browser MCP (for payments)
  - Calendar MCP
  - Slack/Teams MCP

---

### 💎 Platinum Tier Components

#### Cloud Deployment
- ⏳ **Always-On Cloud VM**
  - 24/7 operation
  - Health monitoring
  - Automatic backups

- ⏳ **Cloud + Local Coordination**
  - Vault sync (Git or Syncthing)
  - Work-zone specialization
  - Claim-by-move rule
  - Security boundaries

#### Production Features
- ⏳ **Odoo Cloud Deployment**
  - HTTPS setup
  - Backup automation
  - MCP integration

- ⏳ **Agent-to-Agent Communication**
  - Direct A2A messages
  - Vault as audit record
  - Delegation workflows

---

## Current Project Status

### ✅ Completed
- Obsidian vault created
- Basic folder structure exists
- Python environment set up
- Discovery session documented

### 🚧 In Progress
- Documentation structure
- Architecture decisions
- Component design

### ⏳ Not Started
- Gmail Watcher implementation
- Claude Code Skills
- Testing infrastructure

---

## Scope Boundaries

### ❌ NOT in Bronze Tier
- Email sending (Silver)
- MCP servers (Silver)
- Orchestrator.py (Silver)
- Watchdog.py (Gold)
- WhatsApp monitoring (Silver)
- Social media integration (Gold)
- Accounting integration (Gold)
- Ralph Wiggum loop (Gold)
- Cloud deployment (Platinum)

### ✅ Bronze Tier Scope
- Gmail monitoring only
- Read-only operations
- Classification and summarization and replies writing
- Dashboard updates
- Action item extraction
- Local file operations only
- Automated Claude Code invocation via watcher

---

## Decision Rationale

### Why No Email Sending in Bronze?
- Hackathon guide explicitly lists "MCP server for external action (e.g., sending emails)" under Silver Tier
- Bronze is about establishing the foundation: perception and reasoning
- Action layer (sending) comes in Silver with proper HITL safeguards

### Why No Orchestrator in Bronze?
- Bronze requirement: "One working Watcher script"
- Watcher can directly invoke Claude Code via subprocess
- Orchestrator adds complexity without value for single watcher
- Silver tier needs orchestrator for approval workflow management

### Why No Watchdog in Bronze?
- Watchdog is mentioned in Gold tier section of guide
- Bronze can use manual process management or PM2
- Custom watchdog is overkill for single watcher script
- Focus Bronze effort on core functionality

---

## Upgrade Path

### Bronze → Silver
**Add:**
- Email MCP server
- HITL approval workflow
- Orchestrator for approval management
- Additional watchers (WhatsApp, LinkedIn)
- Email drafting capability

**Keep:**
- All Bronze components
- Gmail watcher
- Classification system
- Dashboard

### Silver → Gold
**Add:**
- Odoo integration
- Social media integration
- Ralph Wiggum loop
- Watchdog process manager
- Weekly business audit
- Multiple MCP servers

**Keep:**
- All Silver components
- All Bronze components

### Gold → Platinum
**Add:**
- Cloud deployment
- 24/7 operation
- Cloud + Local coordination
- A2A communication

**Keep:**
- All previous components

---

## Notes

- Each tier builds on the previous
- No tier removes functionality from lower tiers
- Bronze is intentionally minimal to establish foundation
- Quality over features in each tier
- Document everything for future tiers

---

**Maintained By:** Project Team
**Review Frequency:** After each tier completion
