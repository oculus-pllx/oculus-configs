# Claude Code Quick Reference Card (2026)
**Print this. Tape it to your monitor.**

---

## 📦 ONE-TIME SETUP (30 min)

```bash
# 1. Install
brew install anthropic/claude-code/claude-code  # macOS
# or Windows/Linux — follow docs.claude.com

# 2. Initialize
claude
/init

# 3. Create global config
cat > ~/.claude/CLAUDE.md << 'EOF'
# [paste from main setup guide, Part 2.1]
EOF

# 4. Install plugins
/plugin install superpowers@claude-plugins-official
/plugin install claude-mem
/plugin install frontend-design@claude-plugins-official

# 5. Configure MCP (GitHub + Context7)
# Edit ~/.claude/claude_desktop_config.json
# Add GitHub token: https://github.com/settings/tokens

# 6. Create project template
cp -r ~/Templates/claude-code-starter ~/Projects/my-first-app

# DONE ✅
```

---

## 🚀 START NEW PROJECT (2 min)

```bash
cp -r ~/Templates/claude-code-starter ~/Projects/my-new-project
cd ~/Projects/my-new-project

# Customize CLAUDE.md (2 fields minimum)
# - [Project Name]
# - [Tech Stack]

# Initialize git
rm -rf .git
git init
git add .
git commit -m "chore: initial project"
```

---

## 🔄 SESSION WORKFLOW

### START SESSION
```bash
cd ~/Projects/my-project
claude

# NEW project:
claude "Read CLAUDE.md. First task: [description]. Plan first."

# RESUME project:
/clear
# [Paste resumption prompt from HANDOFF.md]
```

### DURING SESSION
| Action | Command | When |
|--------|---------|------|
| Check tokens | `/usage` | Mid-work |
| See memory | `/memory` | Session start |
| Go to plan mode | `/plan` or Shift+Tab | Before coding |
| Compress | `/compact focus on X` | 70%+ context |
| Commit | `claude "commit..."` | After feature |

### END SESSION
```bash
# Option 1: Auto-handoff (if using plugin)
/handover

# Option 2: Manual
claude "Update .claude/HANDOFF.md with accomplishments, next steps"

# Then:
git add .
git commit -m "session: [summary]"
git push origin
```

---

## 📋 HANDOFF.md STRUCTURE (80-150 lines)

```markdown
# Project Handoff — [Project]
**Session**: [Date] → Next

## What Was Done
- Feature 1: [accomplishment]
- Feature 2: [accomplishment]

## Next Steps (Priority)
1. **Task 1**: [description + acceptance criteria]
2. **Task 2**: [description + acceptance criteria]
3. **Task 3**: [description + acceptance criteria]

## Files to Focus On
- `src/auth.ts` — [what needs work]
- `src/tests/auth.test.ts` — [what needs work]

## How to Resume
/clear
I'm resuming [Project]. Read .claude/HANDOFF.md for context.
Current task: [Task 1]
Plan first, show me plan, then proceed.
```

---

## 💾 GIT COMMIT CONVENTION

```bash
# Format: type(scope): description

feat(auth): add JWT validation           ✅ GOOD
fix(database): fix null reference error  ✅ GOOD
test(api): add 10 edge case tests        ✅ GOOD
refactor(ui): extract button component   ✅ GOOD

Added authentication system              ❌ BAD
bugfix                                   ❌ BAD
updated code                             ❌ BAD
```

**Types**: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`

---

## 🎯 TOKEN MANAGEMENT

**Budget by Task**:
| Task | Tokens | Duration |
|------|--------|----------|
| Small feature | 200k | 1 hour |
| Medium feature | 400-600k | 1-2 hours |
| Large refactor | 800k | 2-3 hours |
| Context rot risk | 200-300k | START NEW SESSION |

**When to spawn subagent**:
```bash
"Spin off subagent to [heavy task].
Return only: summary, list of files changed, no raw code."
```

**When to /clear**:
- Unrelated task
- Context rot visible (forgetting earlier decisions)
- >200k tokens on long-running feature

---

## 📁 FILE CHECKLIST

**Every project needs** ✅:
- [ ] `CLAUDE.md` — project-specific config
- [ ] `docs/DECISIONS.md` — architecture log
- [ ] `.gitignore` — includes `.claude/HANDOFF.md`
- [ ] Initial commit with `/init` or manual setup

**Global setup** ✅ (one time):
- [ ] `~/.claude/CLAUDE.md` — your rules
- [ ] `~/.claude/settings.json` — preferences
- [ ] Superpowers + Claude-Mem plugins installed
- [ ] GitHub + Context7 MCP configured

---

## 🛠️ TROUBLESHOOTING

| Problem | Fix |
|---------|-----|
| Claude won't start | `brew uninstall claude-code && brew install anthropic/claude-code/claude-code` |
| MCP not connecting | Restart Claude (fully quit), check `~/.claude/claude_desktop_config.json` syntax |
| HANDOFF.md pushed to git | `git rm --cached .claude/HANDOFF.md && git commit -m "remove handoff from tracking"` |
| Context getting bloated | Use subagent for analysis, `/compact` mid-task, or `/clear` for new session |
| Auto memory not working | Check `/memory` → should show learnings. Toggle `autoMemoryEnabled` in settings.json |

---

## 📊 EXPECTED BENEFITS

✅ **60-70% token savings** (HANDOFF.md vs. conversation history)  
✅ **Fast context switches** (resume in <1 minute)  
✅ **Clean audit trail** (git commits + DECISIONS.md)  
✅ **Autonomous shipping** (tested, documented, PR-ready)  

---

## 🔗 REFERENCE LINKS

| Resource | Link |
|----------|------|
| Full Setup Guide | `Claude-Code-Setup-Guide.md` |
| Claude Docs | https://docs.claude.com |
| Superpowers | https://github.com/obra/superpowers |
| MCP Servers | https://nimbalyst.com/blog/best-claude-code-mcp-servers |
| Token Optimization | https://www.mindstudio.ai/blog/claude-code-mcp-server-token-overhead |

---

## 💡 PRO TIPS

1. **Invest in CLAUDE.md writing** — 30 min writing = hours saved per project
2. **Commit frequently** — not just at end of session
3. **Use /plan before /execute** — cheap planning saves expensive execution
4. **Keep HANDOFF.md under 150 lines** — should scan in <5 minutes
5. **Fresh sessions > long sessions** — reset context regularly, don't push 1M token limit
6. **Read architecture decisions log** — speeds up onboarding to old projects
7. **Superpowers lifecycle is golden** — brainstorm → plan → implement → review → commit. Don't skip steps.

---

**Last Updated**: May 2026  
**Version**: 1.0  
**Share freely** — MIT License
