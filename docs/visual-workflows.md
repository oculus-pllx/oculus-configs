# Claude Code Visual Workflow Guide
**Diagrams and flow charts for visual learners**

---

## 1. SETUP WORKFLOW (What You Do Once)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRESH WORKSTATION SETUP                      │
│                     (Takes ~30 minutes)                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: Install Claude Code
┌──────────────────────┐
│  brew install        │
│  claude-code         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  claude --version    │
│  ✅ Verified         │
└──────────┬───────────┘
           │
Step 2: Global Configuration
           ▼
┌──────────────────────────────────┐
│  ~/.claude/CLAUDE.md             │
│  ~/.claude/settings.json         │
│  ~/.claude/rules/ (optional)     │
└──────────┬──────────────────────┘
           │
Step 3: Install Plugins
           ▼
┌──────────────────────────────────┐
│  /plugin install superpowers     │
│  /plugin install claude-mem      │
│  /plugin install frontend-design │
└──────────┬──────────────────────┘
           │
Step 4: Configure MCP Servers
           ▼
┌──────────────────────────────────┐
│  github MCP (for PRs/issues)     │
│  context7 MCP (for live docs)    │
└──────────┬──────────────────────┘
           │
Step 5: Create Project Template
           ▼
┌──────────────────────────────────┐
│  ~/Templates/claude-code-starter │
│  ├── CLAUDE.md                   │
│  ├── .gitignore                  │
│  └── docs/DECISIONS.md           │
└──────────┬──────────────────────┘
           │
           ▼
      ✅ DONE
   Ready for projects!
```

---

## 2. NEW PROJECT WORKFLOW (What You Do Per Project)

```
┌──────────────────────────────────────────────────┐
│         STARTING A NEW PROJECT                   │
│          (Takes ~2 minutes)                      │
└──────────┬───────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│  cp -r ~/Templates/starter/    │
│  ~/Projects/my-new-project     │
└────────────┬───────────────────┘
             │
             ▼
┌────────────────────────────────┐
│  Customize CLAUDE.md:          │
│  • [Project Name]              │
│  • [Tech Stack]                │
│  • Architecture details        │
└────────────┬───────────────────┘
             │
             ▼
┌────────────────────────────────┐
│  git init                      │
│  git add .                     │
│  git commit -m "chore: init"   │
└────────────┬───────────────────┘
             │
             ▼
      ✅ READY
   Start your first session!
```

---

## 3. SESSION WORKFLOW (What You Do During Work)

```
┌──────────────────────────────────────────────────────────────────────┐
│                     SINGLE SESSION WORKFLOW                          │
│                    (Covers ~1-2 hours of work)                      │
└──────────────────────────────────────────────────────────────────────┘

START SESSION
┌────────────────────────────────┐
│  cd ~/Projects/my-project      │
│  claude                        │
│                                │
│  IF FIRST TIME:                │
│  /init                         │
│                                │
│  IF RESUMING:                  │
│  /clear                        │
│  [paste HANDOFF.md prompt]     │
└────────────┬───────────────────┘
             │
UNDERSTAND CONTEXT
             ▼
┌────────────────────────────────┐
│  /memory                       │
│  ✅ See what Claude learned    │
└────────────┬───────────────────┘
             │
WORK (Repeat this cycle)
             ▼
┌──────────────────────────────────────┐
│  Plan mode:                          │
│  "Show me your plan first"           │
│  ✅ Claude shows plan                │
│  ✅ You approve or iterate           │
└────────────┬───────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Execute:                            │
│  Claude codes + tests                │
│  ✅ Changes made                     │
└────────────┬───────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Commit:                             │
│  claude "commit the changes"         │
│  ✅ Git checkpoint created           │
└────────────┬───────────────────────┘
             │
CHECK CONTEXT HEALTH
             ▼
        ┌─────────────────┐
        │   /usage        │
        │   Check tokens  │
        └────┬─────┬──────┘
             │     │
        <70% │     │ >70%
             │     │
             │     ▼
             │  ┌────────────────────┐
             │  │ Context Getting    │
             │  │ Heavy. Choose:     │
             │  │                    │
             │  │ A) Subagent for    │
             │  │    heavy task      │
             │  │                    │
             │  │ B) /compact to     │
             │  │    compress        │
             │  │                    │
             │  │ C) /clear for      │
             │  │    fresh start     │
             │  └────────────────────┘
             │
             ▼
      ┌──────────────────┐
      │ Continue working │◄─────────┐
      │ or wrap up?      │          │
      └────┬─────┬───────┘          │
           │     │                   │
      More│     │ Done               │
           │     │                   │
           ▼     ▼                   │
          [Loop] ┌──────────────────────────┐
                 │  END SESSION             │
                 │  Create HANDOFF.md       │
                 │  /handover  (auto)       │
                 │  OR                      │
                 │  claude "update HANDOFF" │
                 └──────────────────────────┘
                          │
                          ▼
                 ┌──────────────────────────┐
                 │  Final commit            │
                 │  git add .               │
                 │  git commit -m "work"    │
                 │  git push origin         │
                 └──────────────────────────┘
                          │
                          ▼
                   ✅ SESSION COMPLETE
                  Ready for next session!
```

---

## 4. MULTI-SESSION PROJECT FLOW

```
┌────────────────────────────────────────────────────────────────────┐
│              MULTI-SESSION PROJECT (Days/Weeks)                   │
│     Using HANDOFF.md to bridge sessions and save tokens           │
└────────────────────────────────────────────────────────────────────┘


SESSION 1 (Day 1)
┌──────────────────────────┐
│ Start: Feature A         │
│ • Brainstorm spec        │
│ • Implement              │
│ • Test                   │
│ • Commit work            │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ /handover                │
│ Creates .claude/HANDOFF.md
│ • What was done         │
│ • Current state         │
│ • Next steps            │
│ • Resumption prompt     │
└──────────┬───────────────┘
           │
    [TIME PASSES]
    [Next day/hour]
           │
           ▼
SESSION 2 (Day 2)
┌──────────────────────────┐
│ /clear                   │
│ Paste resumption prompt  │
│ Claude reads HANDOFF.md  │
│ (100 lines = ~2k tokens) │
│                          │
│ vs without HANDOFF:      │
│ (full history = 500k!)   │
│                          │
│ SAVES: 400k+ tokens! 🎉 │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Continue Feature A or    │
│ Start Feature B          │
│ (Context is fresh)       │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ /handover               │
│ Update HANDOFF.md       │
└──────────┬───────────────┘
           │
    [Repeat as needed]
           │
    (After many sessions)
           ▼
┌──────────────────────────┐
│ PROJECT COMPLETE        │
│ All work in git         │
│ All decisions logged    │
│ Clear handoff trail     │
└──────────────────────────┘

📊 TOKEN SAVINGS:
───────────────
Naive approach (1 long session):
  Tokens: 1M+ (context rot, degradation)
  Quality: ↓ (model forgets decisions)

With HANDOFF.md (multiple sessions):
  Tokens: 300-400k (fresh context each time)
  Quality: ↑ (clean context, fast decisions)

SAVINGS: 60-70% tokens + higher quality!
```

---

## 5. CONTEXT MANAGEMENT DECISION TREE

```
┌──────────────────────────────────────────────────────┐
│  You're mid-session. How's your context health?     │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
    Check /usage
    
    ┌────────────────────────────────┐
    │  Context Usage?                │
    └────┬────────────┬────────────┬──┘
         │            │            │
    <40% │ 40-70%     │ 70-80%     │ >80%
         │            │            │
         ▼            ▼            ▼
    ┌────────┐  ┌─────────┐  ┌──────────┐
    │ CLEAR  │  │ MONITOR │  │ DECIDE   │
    │        │  │         │  │          │
    │ You're │  │ Keep    │  │ HEAVY    │
    │ fine   │  │ working │  │ CONTEXT  │
    │        │  │ but     │  │ INCOMING │
    │ Keep   │  │ watch   │  │          │
    │ going  │  │ for 70% │  │ Choose:  │
    └────────┘  │ threshold
               │
               └──┬──────┬───────────┐
                  │      │           │
                  A      B           C
                  │      │           │
    ┌─────────────▼──┐  │  ┌─────────▼──────┐
    │ SUBAGENT       │  │  │ /clear + New   │
    │ (Best)         │  │  │ HANDOFF        │
    │                │  │  │ (Clean Slate)  │
    │ Heavy task?    │  │  │                │
    │ Parallel work? │  │  │ Unrelated task?│
    │                │  │  │ Context rot    │
    │ Spin off:      │  │  │ visible?       │
    │ "Subagent to   │  │  │                │
    │  [task]"       │  │  │ YES → /clear   │
    └────────────────┘  │  └────────────────┘
                        │
                        ▼
                    ┌──────────────┐
                    │ /compact     │
                    │ (Lossy)      │
                    │              │
                    │ Mid-feature? │
                    │ Momentum     │
                    │ important?   │
                    │              │
                    │ /compact     │
                    │ focus on X   │
                    └──────────────┘
```

---

## 6. PLUGIN + MCP DECISION TREE

```
┌────────────────────────────────────────────────────┐
│  Which plugins/MCPs should I enable for this      │
│  project?                                          │
└────────────┬───────────────────────────────────────┘
             │
             ▼
     ┌───────────────────┐
     │ What's my project?│
     └───┬───────┬───┬───┘
         │       │   │
    Node │React  │   │Python
         │       │   │
         ▼       ▼   ▼
    ┌─────────────────────────┐
    │ ALWAYS Enable:          │
    │ • superpowers (plugin)  │
    │ • claude-mem (plugin)   │
    │ • github (MCP)          │
    └─────┬───────────────────┘
          │
          ▼
    ┌─────────────────────────┐
    │ Usually Enable:         │
    │ • context7 (MCP)        │
    │   (React/Next/Tailwind) │
    │                         │
    │ • frontend-design       │
    │   (plugin, if UI work)  │
    └─────┬───────────────────┘
          │
          ▼
    ┌─────────────────────────────┐
    │ Project-Specific (pick 1):  │
    │ • sqlite (database)         │
    │ • postgresql (database)     │
    │ • playwright (e2e testing)  │
    │                             │
    │ Add ONLY if you use it      │
    │ regularly. Avoid others.    │
    └─────┬───────────────────────┘
          │
          ▼
    ┌─────────────────────────┐
    │ DON'T Enable:           │
    │ • Atlassian (unreliable)│
    │ • Too many MCPs (>5)    │
    │ • Unused services       │
    └─────────────────────────┘

⚠️ TOKEN COST WARNING:
──────────────────────
Each MCP server = 100-500 tokens per turn
  • 1-2 servers: 200-1k tokens (fine)
  • 3-4 servers: 400-2k tokens (monitor)
  • 5+ servers: 1k-5k tokens (expensive)

If >4 servers: Use MCP Tool Search (lazy loading)
or consider MCP Gateway (Bifrost) for enterprise
```

---

## 7. COMMIT MESSAGE TYPES FLOWCHART

```
┌─────────────────────────────────────┐
│  You made changes. Commit now.      │
│  What type of change is it?         │
└──────────┬────────────────────────┬─┘
           │                        │
      New Feature               Bug Fix
      │                        │
      ▼                        ▼
    ┌──────┐               ┌──────┐
    │ feat │               │ fix  │
    └──────┘               └──────┘
    
    Examples:               Examples:
    • Add JWT auth         • Fix null ref
    • New component        • Handle edge case
    • New endpoint         • Memory leak fix
    
Other changes:
├─ Test changes       → type: test
│  • New test file
│  • Test coverage
│
├─ Code refactor      → type: refactor
│  • Extract function
│  • Rename variables
│
├─ Documentation      → type: docs
│  • Update README
│  • API docs
│
└─ Build/config       → type: chore
   • Update deps
   • Config changes

FORMAT: type(scope): description
────────────────────────────────

✅ GOOD:
  feat(auth): add JWT validation
  fix(database): handle null values
  test(api): add 5 edge cases
  refactor(ui): extract Button component

❌ BAD:
  added stuff
  bugfix
  updated code
  random changes
```

---

## 8. HANDOFF.md CONTENT CHECKLIST

```
At END of session, update HANDOFF.md with:

┌─────────────────────────────────────────────┐
│ HANDOFF.MD CONTENT CHECKLIST                │
├─────────────────────────────────────────────┤
│                                             │
│ [✓] What Was Done This Session              │
│     • List 3-5 items accomplished           │
│     • Include commit messages if helpful    │
│                                             │
│ [✓] Current Code State                      │
│     • Branch name (e.g., feature/auth)     │
│     • Last commit hash                      │
│     • Uncommitted file changes              │
│                                             │
│ [✓] Architecture Decisions Made              │
│     • Any major choices this session?       │
│     • Reference docs/DECISIONS.md           │
│                                             │
│ [✓] What Worked / What Didn't                │
│     • Lessons for next session              │
│     • Tools that helped                     │
│     • Dead ends to avoid                    │
│                                             │
│ [✓] Known Issues                             │
│     • Bugs found but not fixed              │
│     • Workarounds if applicable             │
│     • Impact on next session                │
│                                             │
│ [✓] Next Steps (Priority Order)              │
│     • 3 items maximum                       │
│     • Include acceptance criteria           │
│     • Specific, actionable                  │
│                                             │
│ [✓] Files to Focus On                       │
│     • 5-10 key files                        │
│     • Why each needs attention              │
│                                             │
│ [✓] How to Resume (Copy-Paste)               │
│     • Exact prompt for next session         │
│     • Constraints/limitations               │
│     • Starting point                        │
│                                             │
└─────────────────────────────────────────────┘

SIZE TARGET: 80-150 lines
READING TIME: <5 minutes

If longer → you're documenting too much
If shorter → missing context next session needs
```

---

## 9. TOKEN BUDGET BY TASK TYPE

```
┌──────────────────────────────────────────────────────┐
│  TOKEN BUDGET GUIDE (Plan your task size)           │
└──────────────────────────────────────────────────────┘

QUICK FIXES
┌──────────────────────────┐
│ Budget: 100-200k tokens  │
│ Duration: <1 hour        │
│ Example:                 │
│ • Fix typos              │
│ • Minor bugfix           │
│ • Update config          │
│ Strategy:                │
│ → Single session         │
│ → One MCP server (GitHub)│
└──────────────────────────┘

SMALL FEATURE
┌──────────────────────────┐
│ Budget: 200-400k tokens  │
│ Duration: 1-2 hours      │
│ Example:                 │
│ • Add UI component       │
│ • Implement API endpoint │
│ • Refactor 1 module      │
│ Strategy:                │
│ → Single session, fresh  │
│ → 2 MCP servers max      │
└──────────────────────────┘

MEDIUM FEATURE
┌──────────────────────────┐
│ Budget: 400-600k tokens  │
│ Duration: 2-3 hours      │
│ Example:                 │
│ • User auth flow         │
│ • Payment integration    │
│ • Database migration     │
│ Strategy:                │
│ → 1-2 sessions           │
│ → Use HANDOFF.md bridge  │
│ → Subagent for tests     │
└──────────────────────────┘

LARGE REFACTOR
┌──────────────────────────┐
│ Budget: 600-900k tokens  │
│ Duration: 3-5 hours      │
│ Example:                 │
│ • Rewrite auth system    │
│ • Full feature (UI+API)  │
│ • Major architecture     │
│ Strategy:                │
│ → 2-3 sessions, fresh    │
│ → /clear between         │
│ → HANDOFF.md essential   │
│ → Subagent for heavy    │
│   parts                  │
└──────────────────────────┘

⚠️ DON'T EXCEED:
→ 800-900k tokens in single session
→ Start fresh session at that point
→ Context rot visible after 200k

💰 COST AT $6/1M tokens:
200k tokens  = $1.20
400k tokens  = $2.40
800k tokens  = $4.80
```

---

## 10. TROUBLESHOOTING DECISION TREE

```
┌──────────────────────────────────────┐
│  Something's broken. What's wrong?   │
└──────────┬──────────────────────────┘
           │
      ┌────┴────┬─────────┬──────────┬─────────┐
      │         │         │          │         │
   Claude   MCP       Plugin    File         Git
   won't    won't    missing    error       error
   start    connect            issue
      │        │        │         │         │
      ▼        ▼        ▼         ▼         ▼
   ┌─────┐ ┌──────┐ ┌───────┐ ┌──────┐ ┌──────┐
   │     │ │      │ │       │ │      │ │      │
   │ 1a  │ │ 2a   │ │ 3a    │ │ 4a   │ │ 5a   │
   │     │ │      │ │       │ │      │ │      │
   └─────┘ └──────┘ └───────┘ └──────┘ └──────┘

1a. Claude Won't Start
    └→ Fully uninstall + reinstall
    └→ Check: claude --version
    └→ Run: claude doctor

2a. MCP Won't Connect
    └→ Check: ~/.claude/claude_desktop_config.json
    └→ Validate JSON syntax (use jq)
    └→ Fully quit Claude Code, relaunch
    └→ Check GitHub token not expired

3a. Plugin Missing
    └→ /plugin install [name]@[source]
    └→ Check: /plugin list
    └→ Fully quit and restart

4a. File/Folder Issues
    └→ Check .gitignore syntax
    └→ Verify paths exist
    └→ Check permissions
    └→ Reference Setup Guide Part 9

5a. Git Issues
    └→ Check: git status
    └→ Verify: git config user.name
    └→ See: Setup Guide Part 6.3 (Commits)

Still stuck?
    └→ Check Quick Reference (Troubleshooting section)
    └→ Search Setup Guide (Ctrl+F)
    └→ Reference official docs link
    └→ Ask Claude in fresh session
```

---

## 11. PROJECT TEMPLATE STRUCTURE AT A GLANCE

```
┌──────────────────────────────────────────────────┐
│  NEW PROJECT DIRECTORY STRUCTURE                │
│  (Copy from ~/Templates/claude-code-starter)    │
└──────────────────────────────────────────────────┘

my-project/
│
├── 📄 CLAUDE.md ........................ Project context
│   └─ Read at session start
│   └─ Customize [Project Name] + [Tech Stack]
│
├── 🔒 .gitignore ....................... Track what NOT to commit
│   ├─ .claude/HANDOFF.md (ephemeral)
│   ├─ docs/plans/ (ephemeral)
│   └─ node_modules/, .env, etc.
│
├── 📋 docs/
│   ├─ DECISIONS.md .................... Architecture log (COMMIT)
│   │  └─ Add ADR-001, ADR-002, etc.
│   │  └─ Reference when designing
│   ├─ API.md .......................... API documentation
│   └─ ARCHITECTURE.md ................. System design
│
├── 📁 src/
│   ├─ app/ or server.ts ............... Your app code
│   ├─ components/ ..................... React/UI components (if applicable)
│   ├─ lib/ ............................ Utilities
│   └─ tests/ .......................... Test files
│
├── 🔐 .claude/
│   └─ HANDOFF.md ...................... Session bridge (DO NOT COMMIT)
│      └─ Auto-generated by /handover
│      └─ Deleted before next session
│
├── 📄 README.md ....................... User documentation
├── 📄 .env.example .................... Environment template
├── 📄 package.json .................... Dependencies
├── 📄 tsconfig.json ................... TypeScript config
└── 📁 .git/ ........................... Version history (git)

REMEMBER:
✅ Commit:     CLAUDE.md, docs/DECISIONS.md, src/, README.md
❌ Don't commit: .claude/HANDOFF.md, .env, node_modules/, .next/
```

---

## 12. QUICK DECISION MATRIX

```
┌────────────────────────────────────────────────────────┐
│  DECISION MATRIX - When to Use What                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│ DO I NEED A NEW SESSION?                             │
│ ────────────────────────────────────────────────────  │
│ Context >300k AND unrelated task        → YES, /clear │
│ Context 70-80% AND same feature         → NO, /compact│
│ Context 70-80% AND parallel work needed → SUBAGENT   │
│ Context fresh AND continuing task       → NO, /continue
│                                                        │
│ SHOULD I COMMIT NOW?                                 │
│ ────────────────────────────────────────────────────  │
│ Feature complete                → YES, one commit     │
│ Mid-feature, logical checkpoint → YES, smaller commit │
│ Just experimenting              → NO, wait for end    │
│ Bug discovered                  → YES, separate commit│
│                                                        │
│ SHOULD I USE A SUBAGENT?                             │
│ ────────────────────────────────────────────────────  │
│ Heavy analysis (10+ files)      → YES               │
│ Parallel independent tasks      → YES               │
│ Light targeted work             → NO                │
│ Need results mid-session        → NO (use /compact) │
│                                                        │
│ SHOULD I UPDATE CLAUDE.MD?                           │
│ ────────────────────────────────────────────────────  │
│ Permanent team convention established → YES          │
│ Architecture changed significantly    → YES          │
│ One-time learning from session       → NO (auto-mem)│
│ Workaround for specific task         → NO (HANDOFF) │
│                                                        │
│ SHOULD I ADD TO DECISIONS.MD?                        │
│ ────────────────────────────────────────────────────  │
│ Major tech choice (database, framework) → YES        │
│ Architectural pattern decision        → YES          │
│ Implementation detail                 → NO (code)    │
│ Bug workaround                        → NO (comments)│
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## VISUAL SUMMARY

**Print or bookmark this page. Reference it during work.**

```
WORKSTATION SETUP: Done once, lasts forever
  Install → Global Config → Plugins → MCP → Templates → ✅

NEW PROJECT: 2 minutes
  Copy Template → Customize → Git Init → ✅

SESSION START: Varies
  New:    /init (first time only)
  Resume: /clear + paste HANDOFF prompt

DURING SESSION: Cycle repeats
  Plan (show me plan first)
    ↓
  Execute (code + test)
    ↓
  Commit (git checkpoint)
    ↓
  Check /usage
    ├─ <70%: Continue
    ├─ 70-80%: Monitor
    └─ >80%: Subagent or /clear

SESSION END: Bridge to next
  /handover → HANDOFF.md created → Final commit → Done

MULTI-SESSION BRIDGE:
  Session 1 → HANDOFF.md (100 lines) ← Session 2
  Saves: 400k+ tokens vs naive approach!
```

---

**These diagrams work best printed or as PDF bookmarks.**

**Share them with your team. They onboard 40% faster with visuals.**

---

Version: 1.0 | May 2026 | MIT License
