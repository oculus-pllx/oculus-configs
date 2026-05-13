# Claude Code Setup & Best Practices Guide (2026)
## Complete Workstation Configuration for Solo Developers

**Version**: 1.0  
**Last Updated**: May 2026  
**Audience**: Solo developers, small teams  
**Scope**: Fresh workstation setup + token-efficient workflows  

---

## Table of Contents
1. [Overview & Philosophy](#overview--philosophy)
2. [Pre-Setup Checklist](#pre-setup-checklist)
3. [Part 1: Install Claude Code](#part-1-install-claude-code)
4. [Part 2: Global Configuration](#part-2-global-configuration)
5. [Part 3: Plugin & MCP Setup](#part-3-plugin--mcp-setup)
6. [Part 4: Project Template Creation](#part-4-project-template-creation)
7. [Part 5: Handoff System](#part-5-handoff-system)
8. [Part 6: Session Workflow](#part-6-session-workflow)
9. [Troubleshooting & FAQ](#troubleshooting--faq)
10. [Quick Reference](#quick-reference)

---

## Overview & Philosophy

Claude Code is not a code generator—it's a **collaborative AI developer** that works best with structured context, clear constraints, and proper session management.

### Key Principles
- **Context is currency**: Manage it ruthlessly. Token costs scale with context bloat.
- **Handoffs over memory**: Use structured handoff documents instead of relying on built-in memory systems.
- **Commits are checkpoints**: Every meaningful change gets committed to git. Sessions are temporary; git is permanent.
- **Superpowers drives behavior**: Plugins guide Claude toward better outcomes. Let them work.
- **Fresh sessions > long sessions**: Reset context regularly. Prevents degradation.

### Expected Results
- **60-70% token savings** on multi-session projects vs. naive approaches
- **Faster onboarding** between sessions (handoff documents are 100 lines, not history)
- **Clear decision trail** (git log + DECISIONS.md = project archaeology)
- **Autonomous shipping** (PR-ready features, tested, documented)

---

## Pre-Setup Checklist

Before starting, verify you have:

- [ ] **macOS 12+, Windows 10+, or Linux**: Claude Code runs on all platforms
- [ ] **Node.js 18+**: `node --version` (needed for some MCP servers)
- [ ] **Git 2.0+**: `git --version` (essential for workstation setup)
- [ ] **Claude Code license**: Claude Pro or Max plan (free tier has limits)
- [ ] **Text editor**: VS Code, Cursor, or terminal editor (your choice)
- [ ] **GitHub account**: Optional but recommended for MCP integration
- [ ] **~30 minutes**: First-time setup
- [ ] **Internet connection**: For downloading tools and docs

**Pro Tip**: If upgrading from Claude Code 2.0.x, uninstall first: `brew uninstall claude-code` (macOS) or Windows Control Panel (Windows).

---

## Part 1: Install Claude Code

### Step 1.1: Install via Package Manager

**macOS (Homebrew)**:
```bash
brew install anthropic/claude-code/claude-code
```

**Windows (Winget)**:
```powershell
winget install Anthropic.ClaudeCode
```

**Linux (APT)**:
```bash
sudo apt-get update
sudo apt-get install claude-code
```

**Verify installation**:
```bash
claude --version
claude doctor
```

Both commands should return version info and system health. If not, reinstall.

### Step 1.2: Initialize Claude Code

```bash
# Start your first session (creates ~/.claude/ directory structure)
claude

# Inside Claude Code, run:
/init

# This bootstraps:
# - ~/.claude/CLAUDE.md (global config)
# - ~/.claude/settings.json (preferences)
# - ~/.claude/projects/ (auto-memory storage)
```

### Step 1.3: Verify Installation

```bash
# Check directory structure
ls -la ~/.claude/

# Expected output:
# .claude/
# ├── CLAUDE.md
# ├── settings.json
# ├── projects/
# └── plugins/
```

If any directories are missing, run `/init` again or manually create them:
```bash
mkdir -p ~/.claude/{plugins,projects,reports}
touch ~/.claude/CLAUDE.md ~/.claude/settings.json
```

---

## Part 2: Global Configuration

### Step 2.1: Create Global CLAUDE.md

This file applies to **all projects**. It's your personal coding constitution.

**Create `~/.claude/CLAUDE.md`**:

```markdown
# Global Claude Code Configuration

## Identity & Scope
- **Role**: Autonomous full-stack contributor, not assistant
- **Scope**: Multi-project, team-aware, production-ready
- **Duration**: Long-running sessions with /compact when approaching context limits

## Plugin & Skills Activation
- **Superpowers**: REQUIRED. Use it for every new project start.
  - Always run brainstorm → plan → implement workflow
  - Use its 14 built-in skills; do NOT reinvent workflows
  - Read skills from ~/.claude/plugins/cache/Superpowers/skills/
- **Claude-Mem**: ACTIVE. Access cross-session memory via the plugin
- **Auto Memory**: ENABLED. Claude writes its own learnings to ~/.claude/projects/{project}/
  - Do NOT duplicate auto-memory entries into CLAUDE.md
  - Check /memory periodically and prune outdated entries

## Token Discipline (HIGH PRIORITY)
1. **One task per session.** Don't reuse sessions for unrelated work.
2. **Use /compact** when session grows beyond 50 messages or 100K tokens
3. **MCP Tools**: Only load 3-5 servers max (see MCP Rules below)
4. **File Reads**: Point to specific files, not entire directories
   - BAD: "review the whole src/ folder"
   - GOOD: "review src/api.ts and src/auth.ts"
5. **Auto Memory Over CLAUDE.md**: If Claude learns something in session, it auto-saves. Don't manually add it unless permanent.

## MCP Rules (Token Savings Critical)
- GitHub MCP: ALWAYS enabled (essential for PR/issue workflow)
- Context7 MCP: ENABLED for fast-moving frameworks (React, Next.js, Tailwind)
- Maximum 4 servers per session; disable unused ones in settings.json
- Each MCP server costs 100-500 tokens per turn (schemas get re-sent)
- Use MCP Tool Search feature (lazy loading) to reduce context by 95%

## Workflow Standards
1. **Planning First**: Run plan mode before implementation
   - Brainstorm specifications with user before coding
   - Show plan for approval before execution
   - This cheap planning saves expensive execution tokens
2. **Superpowers Lifecycle**:
   - Brainstorm → Plan → Implement → Review → Commit
   - Do NOT skip brainstorm; do NOT skip review
3. **Git Worktrees**: Always use `isolation: worktree` for parallel tasks
4. **Subagents for Heavy Lifting**: Delegate code analysis/review to subagents, keep main session light

## Code Style & Conventions
- Format: Prettier/ESLint on save
- Testing: TDD (red → green → refactor)
- Git commits: [type]: description (imperative, <50 chars)
  - Types: feat, fix, test, refactor, chore
- No production secrets in prompts; use env vars or MCP vaults

## Memory Locations
- Session memory: ~/.claude/projects/{project-name-with-hyphens}/
- Auto-learned facts: checked via /memory command
- Skills registry: ~/.claude/plugins/cache/Superpowers/skills/
- Global config: ~/.claude/settings.json and this file

---
*Last reviewed: [today's date]. Update this file whenever you establish a new permanent preference.*
```

**Copy this file**:
```bash
cat > ~/.claude/CLAUDE.md << 'EOF'
[paste content above]
EOF
```

### Step 2.2: Configure settings.json

Edit `~/.claude/settings.json`:

```bash
# Open in your editor
code ~/.claude/settings.json
# or
nano ~/.claude/settings.json
```

**Recommended settings**:

```json
{
  "model": "claude-opus-4-6",
  "autoMemoryEnabled": true,
  "compactOnContextThreshold": 75,
  "permissionMode": "plan",
  "tokens": {
    "warningThreshold": 700000,
    "errorThreshold": 950000
  },
  "attribution": {
    "commit": "Generated with Claude Code\n\nCo-Authored-By: Claude Sonnet <noreply@anthropic.com>",
    "pr": "AI-assisted development with Claude Code"
  },
  "gitDefaults": {
    "workTreeIsolation": true,
    "autoCommit": false
  }
}
```

**Key settings explained**:
- `permissionMode: "plan"`: Claude shows you what it will do before touching files
- `autoMemoryEnabled: true`: Claude learns from each session
- `compactOnContextThreshold`: Automatically offers to compact at 75% context
- `warningThreshold`: Alerts you before hitting context limits

**Verify**:
```bash
cat ~/.claude/settings.json | jq .
```

### Step 2.3: Create Global Rules Directory (Optional but Recommended)

```bash
mkdir -p ~/.claude/rules
```

Create modular rule files:

**`~/.claude/rules/code-quality.md`**:
```markdown
## Test Coverage Thresholds
- Statements: 80%
- Branches: 75%
- Functions: 80%
- Lines: 80%

## Pre-Commit Checks
- No console.log in prod code
- No hardcoded secrets
- No dead imports
- All tests pass
```

**`~/.claude/rules/plugin-usage.md`**:
```markdown
## When to Invoke Superpowers Skills
- **Brainstorm Skill**: Any time starting a new feature
- **TDD Skill**: Before writing ANY application code
- **Code Review Skill**: Before marking PRs as ready
- **Git Skill**: Before committing anything
- **Architecture Pattern Skill**: When refactoring or designing new systems
```

These files auto-load into every Claude Code session (set up in Step 2.2 if using lazy loading).

---

## Part 3: Plugin & MCP Setup

### Step 3.1: Install Core Plugins

**Inside a Claude Code session**:

```bash
claude

# Inside Claude Code:
/plugin install superpowers@claude-plugins-official
/plugin install claude-mem
/plugin install frontend-design@claude-plugins-official
```

**Verify plugins installed**:
```bash
/plugin list
```

Expected output:
```
Installed Plugins:
✓ superpowers (v5.1.0)
✓ claude-mem (latest)
✓ frontend-design (latest)
```

### Step 3.2: Configure MCP Servers (GitHub + Context7)

**Edit `~/.claude/claude_desktop_config.json`** (Claude Desktop) or `.mcp.json` (Claude Code):

```bash
# Find your config file
# macOS: ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json
# Linux: ~/.config/Claude/claude_desktop_config.json

code ~/.claude/claude_desktop_config.json
```

**Add MCP servers**:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {}
    }
  }
}
```

**To get GitHub token**:
1. Go to https://github.com/settings/tokens
2. Generate new fine-grained personal access token
3. Grant permissions: `Contents: read/write`, `Pull requests: read/write`, `Issues: read`
4. Copy token into config

**Verify MCP setup**:
```bash
# Restart Claude Code (fully quit and relaunch)
claude mcp list
```

Expected output:
```
Connected MCP Servers:
✓ github (active)
✓ context7 (active)
```

**Pro Tip**: Start with just GitHub + Context7. Add project-specific MCPs per project, not globally.

---

## Part 4: Project Template Creation

### Step 4.1: Create Project Scaffolding

Every new project needs this structure. Create a reusable template.

**For Node.js/TypeScript projects**:

```bash
# Create template directory
mkdir -p ~/Templates/claude-code-starter/{src,tests,docs,.claude}

# Copy CLAUDE.md template
cat > ~/Templates/claude-code-starter/CLAUDE.md << 'EOF'
# [Project Name] — Development Context

## Project Metadata
- **Tech Stack**: [e.g., Next.js 15, TypeScript, Tailwind, PostgreSQL]
- **Repository**: [GitHub URL]
- **Entry Point**: [e.g., src/app/page.tsx, package.json scripts]

## Architecture
[Keep this under 100 words. Auto Memory will learn structure details.]
- **Frontend**: [Brief: layout, state management, styling]
- **Backend**: [Brief: API framework, auth, database]
- **Key Dependencies**: [Version-critical ones that Context7 MCP should fetch docs for]

## Current Sprint / Goals
- Goal 1: [What we're shipping this week]
- Goal 2: [...]
- **Blocked By**: [Any external dependencies]

## Code Patterns & Conventions
- Naming: camelCase functions, PascalCase components, UPPER_SNAKE_CASE constants
- Testing: Jest + React Testing Library (TDD required)
- API response format: `{ data?, error?, status }`
- Database queries: Use parameterized queries only

## Superpowers Skills for This Project
- **Required**: Getting Started, TDD, Code Review, Architecture Pattern
- **Optional**: Refactoring, Migration Safety (if applicable)

## What NOT to Do
- Do NOT use context-switching between features mid-session
- Do NOT commit directly to main (always PR)
- Do NOT modify .env or production configs

## MCP Servers Enabled
- `github` — PR/issue workflow
- `context7` — Fetch Next.js/Tailwind docs at runtime
- (Disable: Notion, Atlassian, anything unused)

@~/.claude/rules/code-quality.md
@~/.claude/rules/plugin-usage.md
EOF

# Create .gitignore
cat > ~/Templates/claude-code-starter/.gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Handoff files (ephemeral, session-to-session bridges)
.claude/HANDOFF.md
.claude/reports/handoff/
docs/plans/
docs/analysis/

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# Build
dist/
build/
.next/

# Keep permanent docs
!docs/DECISIONS.md
!docs/API.md
!docs/ARCHITECTURE.md
EOF

# Create directories
mkdir -p ~/Templates/claude-code-starter/{src,tests,docs/.claude}

# Initialize git (for template)
cd ~/Templates/claude-code-starter
git init
git add CLAUDE.md .gitignore
git commit -m "chore: initial project template"
```

### Step 4.2: Use Template for New Projects

```bash
# For each new project:
cp -r ~/Templates/claude-code-starter ~/Projects/my-new-project
cd ~/Projects/my-new-project

# Customize CLAUDE.md
# Edit the [Project Name], [Tech Stack], etc.
nano CLAUDE.md

# Initialize git repo (fresh repo, not copied)
rm -rf .git
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
git add .
git commit -m "chore: project initialized"
```

### Step 4.3: Create docs/DECISIONS.md Template

Every project needs this to track architectural decisions.

```bash
cat > ~/Templates/claude-code-starter/docs/DECISIONS.md << 'EOF'
# Architecture Decision Log (ADL)

## ADR Template
Each decision should follow this format:

```
## ADR-XXX: [Decision Title]
**Date**: YYYY-MM-DD  
**Decision**: [What we decided]  
**Reasoning**: 
- Point 1
- Point 2

**Tradeoffs**:
- Pro: X
- Con: Y

**Status**: Proposed | Accepted ✅ | Deprecated ❌
```

---

## Example ADR

## ADR-001: JWT vs Session-Based Auth
**Date**: 2026-05-13  
**Decision**: Use JWT for API, sessions for web UI  
**Reasoning**: 
- JWT is stateless (easier horizontal scaling)
- Sessions prevent token replay attacks on web UI
- Hybrid approach avoids storing tokens in localStorage

**Tradeoffs**:
- Pro: Scales to multiple servers
- Con: Increased complexity in auth flow

**Status**: Accepted ✅
EOF
```

---

## Part 5: Handoff System

### Step 5.1: Create Handoff Template

This is the **session-to-session bridge**. Create globally once, reuse for every project.

```bash
cat > ~/.claude/handoff-template.md << 'EOF'
# Project Handoff — [Project Name]
**Session**: [YYYYMMDD-HHmm] → Next  
**Status**: [In Progress / Ready for Review / Blocked]

## What Was Done This Session
- [Feature/task 1]: [what was accomplished]
- [Feature/task 2]: [what was accomplished]
- [Bug fixes]: [what was fixed]

## Current Code State
- **Branch**: [current branch name]
- **Last Commit**: [commit hash] "[message]"
- **Uncommitted Changes**: [files changed, brief summary]
  - `src/auth.ts`: Added JWT validation
  - `src/tests/auth.test.ts`: Added 5 new test cases

## Architecture Decisions Made
- Decision 1: [Why you chose X over Y]
- Decision 2: [Why you chose X over Y]

## What Worked
- [Approach A was effective because...]
- [Tool X helped because...]

## What Didn't Work
- [Approach B failed because...]
- [We tried X but it caused Y]

## Known Issues
- [ ] Issue 1: [description, impact, workaround]
- [ ] Issue 2: [description, impact, workaround]

## Next Steps (Priority Order)
1. **[Task Title]**: [1-2 sentence description + acceptance criteria]
2. **[Task Title]**: [1-2 sentence description + acceptance criteria]
3. **[Task Title]**: [1-2 sentence description + acceptance criteria]

## Files to Focus On (for next session)
- `src/auth.ts` — incomplete JWT implementation
- `src/tests/auth.test.ts` — needs edge case tests
- `docs/API.md` — needs updating with new endpoints

## Context Notes
- [Any MCP server special setup needed?]
- [Any git branch strategy needed?]
- [Any uncommitted secrets or configs?]
- [Current Auto Memory status: size, what was learned]

## How to Resume (Copy-Paste into Next Session)
```bash
/clear

I'm resuming work on [project name]. Read .claude/HANDOFF.md for full context.

Current task: [Task from "Next Steps"]

Constraints:
- [Any hard constraints from CLAUDE.md]
- [Any architectural rules]
- [Any token/time limits]

Plan first, show me the plan, then proceed.
```
EOF
```

### Step 5.2: Install Handoff Plugin (Automated)

**Optional but recommended**: Install the Claude-Handover plugin to auto-generate HANDOFF.md.

```bash
claude

# Inside Claude Code:
/plugin install handover@danielrosehill/Claude-Handover --scope user
```

Then at end of session:
```bash
/handover
```

This automatically:
- Analyzes git status and recent commits
- Reviews diffs of uncommitted changes
- Checks CLAUDE.md files
- Creates structured HANDOFF.md

### Step 5.3: Add Handoff to Project .gitignore

For **every project**, add to `.gitignore`:

```bash
echo ".claude/HANDOFF.md" >> .gitignore
echo "docs/plans/" >> .gitignore
```

This keeps ephemeral handoff documents out of git while keeping permanent docs committed.

---

## Part 6: Session Workflow

### Step 6.1: Starting a New Session

**First session (new project)**:

```bash
cd ~/Projects/my-new-project
claude

# Inside Claude Code:
/init  # Bootstrap project memory

# Then:
claude "I'm starting a new [Project Name] project. 
Read CLAUDE.md for project context.

Let's start with: [your first task]

Run plan mode first to show me your understanding."
```

**Subsequent sessions (resuming project)**:

```bash
cd ~/Projects/my-new-project
claude

# Inside Claude Code:
/clear

I'm resuming work on [project name]. 
Read .claude/HANDOFF.md for full context.

Current task: [Task from "Next Steps" in HANDOFF.md]

Constraints:
- Token budget: 800k
- Time: 2 hours
- MCP servers: GitHub only (disable unused)

Plan first, show me the plan, then proceed.
```

### Step 6.2: During Session—Token Management

**Monitor context health**:

```bash
# Check token usage
/usage

# Expected output:
# Context: 45%
# Input tokens: ~150k
# Output tokens: ~50k
```

**When context approaches 70-80%**:

**Option A—Subagent for heavy work**:
```bash
"Spin off a subagent to refactor the auth module.
Return: list of files changed, what was refactored, any breaking changes.
Do not return raw code diffs."
```

**Option B—Compact (lossy but momentum-preserving)**:
```bash
/compact focus on the auth feature, drop test debugging output
```

**Option C—Clear + Handoff (best for clean break)**:
```bash
"Before we /clear, update .claude/HANDOFF.md with current progress.
Include next steps and files to focus on.
Then write a resumption prompt I can paste into a new session."

# Then:
/clear

[paste resumption prompt]
```

### Step 6.3: Commits During Session

**Commit frequently** (every logical change):

```bash
# Ask Claude to commit
claude "commit the changes in src/auth.ts with message: feat(auth): add JWT validation"

# Or do it manually
git add src/auth.ts
git commit -m "feat(auth): add JWT validation"
```

**Commit conventions**:
- `feat:` new feature
- `fix:` bug fix
- `test:` test changes
- `refactor:` code restructuring
- `docs:` documentation
- `chore:` build/config

Each commit is a **waypoint**. If you need to bail out, you have clean checkpoints.

### Step 6.4: End of Session

**Create handoff** (3 options):

**Option 1—Automated (if using plugin)**:
```bash
/handover
```

**Option 2—Manual**:
```bash
claude "Update .claude/HANDOFF.md with:
- What we accomplished
- Current branch and uncommitted changes
- Next steps (3 priority items)
- Files to focus on
- Then write a resumption prompt"
```

**Option 3—Use /clear with context capture**:
```bash
claude "Summarize from here"

# Claude writes a message summarizing learnings, then:
/clear

# You get clean slate for next session
```

**Then**:

```bash
# Commit work (if not already done)
git status
git add .
git commit -m "session: [summary of work done]"

# Push to remote (optional, keeps backup)
git push origin main
```

---

## Part 7: Multi-Session Example

### Scenario: Building a Math Tutoring App

**Session 1**:
```bash
cd ~/Projects/math-tutor
claude

/clear

Starting Math Tutor App. Read CLAUDE.md for context.

First task: Implement QuestionGenerator component.

Constraints:
- Use React + TypeScript
- TDD approach
- 90% test coverage required

Plan first.
```

Work until context hits 70%+ or task completes.

**End of Session 1**:
```bash
/handover  # Auto-generates HANDOFF.md

# Then:
git add .
git commit -m "feat(components): implement QuestionGenerator with tests"
git push origin feature/questions
```

**Session 2** (next day):
```bash
cd ~/Projects/math-tutor
claude

/clear

Resuming Math Tutor App. Read .claude/HANDOFF.md for full context.

Current task: Write E2E tests for question flow

Constraints:
- Use Playwright
- Tests run <5 seconds
- 90% coverage on QuestionGenerator

Plan first, show me test plan, then proceed.
```

Claude reads HANDOFF.md (100 lines) instead of conversation history (500k tokens). **Context savings: 60-70%**.

---

## Part 8: Troubleshooting & FAQ

### Q: Claude Code won't start / shows version mismatch

**Solution**:
```bash
# Completely uninstall
brew uninstall claude-code  # macOS
# or Windows: Control Panel → Uninstall

# Reinstall
brew install anthropic/claude-code/claude-code

# Verify
claude --version
claude doctor
```

### Q: MCP servers aren't connecting

**Solution**:
```bash
# Check config file exists
ls -la ~/.claude/claude_desktop_config.json

# Verify JSON syntax
cat ~/.claude/claude_desktop_config.json | jq .

# If error, fix JSON and restart Claude Code
# (fully quit, relaunch)
```

### Q: /init doesn't create CLAUDE.md

**Solution** (manual creation):
```bash
mkdir -p ~/.claude
cat > ~/.claude/CLAUDE.md << 'EOF'
# [Your CLAUDE.md content from Part 2.1]
EOF
```

### Q: How do I know if auto memory is working?

**Solution**:
```bash
# Check auto memory folder
ls -la ~/.claude/projects/

# Inside Claude Code:
/memory

# You'll see:
# 1. Managed Policy Memory (organization-wide)
# 2. Project Memory (./CLAUDE.md)
# 3. User Memory (~/.claude/CLAUDE.md)
# 4. Auto Memory (learnings from this project)
```

### Q: HANDOFF.md is too long / too short

**Solution**:
- **Too long**: Focus on "Next Steps" + "Files to Focus On". Trim context notes.
- **Too short**: Add "What Worked" + "What Didn't Work" sections. These help next session.
- **Target**: 80-150 lines. Should take <5 minutes to read.

### Q: I pushed HANDOFF.md to git by accident

**Solution**:
```bash
# Remove from git (but keep locally)
git rm --cached .claude/HANDOFF.md
git commit -m "chore: remove handoff from git tracking"

# Make sure .gitignore has it
echo ".claude/HANDOFF.md" >> .gitignore
git add .gitignore
git commit -m "chore: add HANDOFF.md to gitignore"
```

### Q: How many projects can I manage with this setup?

**Answer**: Unlimited. Each project has its own CLAUDE.md + HANDOFF.md. Global config scales to any number of projects.

### Q: Should I commit DECISIONS.md?

**Answer**: YES. DECISIONS.md is permanent project documentation. Commit it. HANDOFF.md is ephemeral—don't commit it.

---

## Part 9: Quick Reference

### Command Cheat Sheet

| What | Command | When |
|------|---------|------|
| Check token usage | `/usage` | Mid-session |
| Compress history | `/compact focus on X` | Context >70% |
| Fresh context | `/clear` | End of session |
| View plugins | `/plugin list` | Verify setup |
| Update memory | `/memory` | Session start |
| Summarize | `"Summarize from here"` | Before /clear |
| Handoff (auto) | `/handover` | End of session |
| Plan mode | `/plan` or `Shift+Tab` | Before executing |
| Usage costs | `/cost` | End of session |

### File Structure Reference

```
~/.claude/                           # Global config (macOS/Linux)
├── CLAUDE.md                        # Global rules (all projects)
├── settings.json                    # Claude Code preferences
├── rules/                           # Modular rules (optional)
│   ├── code-quality.md
│   └── plugin-usage.md
├── projects/                        # Auto-memory (project-local)
│   └── {project-name}/
│       └── memory/
└── plugins/                         # Installed plugins

~/Projects/my-project/              # Per-project
├── CLAUDE.md                        # Project-specific config
├── .claude/
│   └── HANDOFF.md                   # Session-to-session bridge (ephemeral)
├── .gitignore                       # (includes .claude/HANDOFF.md)
├── docs/
│   ├── DECISIONS.md                 # Architecture decision log (commit)
│   ├── API.md
│   └── ARCHITECTURE.md
├── src/
├── tests/
└── .git/
```

### Token Budget Reference

| Scenario | Recommended Tokens | When |
|----------|-------------------|------|
| Small feature (1 file) | 200k | <1 hour |
| Medium feature (3-5 files) | 400-600k | 1-2 hours |
| Large refactor (10+ files) | 800k | 2-3 hours |
| Context rot risk | 200-300k | Start new session |

**Rule of thumb**: Start new session when reaching 200-300k used tokens on long tasks. Use subagents for heavy work (analysis, refactoring) to keep main session fresh.

### MCP Server Reference

| Server | Purpose | Token Cost | When to Use |
|--------|---------|-----------|-----------|
| GitHub | PR/issue workflow | 200-400 | Always on |
| Context7 | Live docs (React, Next.js, Tailwind) | 100-300 | Fast-moving frameworks |
| SQLite | Query dev database | 150-250 | Database debugging |
| Filesystem | Read/write outside project | 100-200 | Cross-project file ops |
| Playwright | Browser automation | 500+ | UI testing (expensive) |

**Rule**: Start with GitHub + Context7 only. Add project-specific MCPs per project, not globally.

---

## Part 10: Publishing & Sharing

### Publishing This Guide

**For GitHub**:
```bash
# Create docs/ directory in your repo
mkdir -p docs/guides

# Copy this guide
cp Claude-Code-Setup-Guide.md docs/guides/

# Customize for your team
# - Replace [Your Name] with actual names
# - Add team-specific MCP servers
# - Add team code conventions
# - Update architecture decision examples

git add docs/guides/
git commit -m "docs: add Claude Code setup guide"
git push origin main
```

**For internal wiki** (Notion, Confluence):
1. Copy this guide into your wiki tool
2. Create a "Claude Code" space
3. Pin the setup guide to the top
4. Add per-project decision logs as sub-pages

**For team distribution**:
```bash
# Create PDF
markdown-pdf Claude-Code-Setup-Guide.md -o Claude-Code-Setup-Guide.pdf

# Share via Slack/Teams
# "Here's the setup guide for Claude Code. Takes 30 minutes."
```

### Customizing for Your Team

Add a "Team Customization" section:

```markdown
## Part 11: Team Customization

### Architecture Pattern
Our team prefers:
- Backend: [Your framework] with [Your ORM]
- Frontend: [Your framework] with [Your state management]
- Testing: [Your test framework]
- Deployment: [Your platform]

### Code Conventions
- API responses: `{ data, error, status }`
- Error handling: [Your approach]
- Git branches: `feature/JIRA-XXX-description`
- PR review: [Your rubric]

### MCP Servers for Our Stack
```

---

## Summary

You now have:
- ✅ Claude Code installed and verified
- ✅ Global CLAUDE.md for consistent behavior across projects
- ✅ Plugin + MCP setup (Superpowers, Claude-Mem, GitHub, Context7)
- ✅ Project template for 30-second new project setup
- ✅ Handoff system for multi-session token efficiency
- ✅ Structured session workflow (plan → execute → commit → handoff)
- ✅ Decision log system (DECISIONS.md)

**Next steps**:
1. Create your first project: `cp -r ~/Templates/claude-code-starter ~/Projects/my-first-app`
2. Read global CLAUDE.md once to internalize the principles
3. Start a session and follow Part 6 (Session Workflow)
4. Commit after every logical change
5. Use HANDOFF.md to bridge sessions

**Expected outcome**: 60-70% token savings on multi-session projects, faster context switches, and a permanent audit trail of all decisions.

---

## References

- [Claude Code Official Docs](https://docs.claude.com/en/docs/claude-code/overview)
- [Using Claude Code: Session Management](https://claude.com/blog/using-claude-code-session-management-and-1m-context)
- [MCP Token Optimization](https://www.mindstudio.ai/blog/claude-code-mcp-server-token-overhead)
- [Superpowers Framework](https://github.com/obra/superpowers)
- [Best Practices by Nimbalyst](https://nimbalyst.com/blog/)

---

**Document Version**: 1.0  
**Last Updated**: May 2026  
**Maintainer**: Your Name / Team  
**License**: MIT (feel free to share, modify, distribute)
