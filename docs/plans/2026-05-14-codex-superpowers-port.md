# Codex CLI Superpowers Port — Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port 8 Superpowers workflow skills + global AGENTS.md to Codex CLI so sessions have the same discipline as Claude Code.

**Architecture:** Skill files live in `codex/skills/` in this repo. `install.sh` copies them to `~/.codex/skills/` and writes `~/.codex/AGENTS.md`. Skills are lazy-loaded — AGENTS.md instructs Codex to `cat` a skill file when the trigger condition is met. No `@`-includes at startup.

**Tech Stack:** Bash (install.sh), Markdown (skill files), Python unittest (tests)

---

## File Map

| Action | Path |
|---|---|
| Create | `codex/AGENTS.md` |
| Create | `codex/skills/brainstorming/SKILL.md` |
| Create | `codex/skills/systematic-debugging/SKILL.md` |
| Create | `codex/skills/test-driven-development/SKILL.md` |
| Create | `codex/skills/verification-before-completion/SKILL.md` |
| Create | `codex/skills/finishing-a-development-branch/SKILL.md` |
| Create | `codex/skills/requesting-code-review/SKILL.md` |
| Create | `codex/skills/receiving-code-review/SKILL.md` |
| Create | `codex/skills/writing-plans/SKILL.md` |
| Modify | `install.sh` (add section 8) |
| Modify | `tests/test_configure.py` (add TestCodexSkills) |

---

## Task 1: Write codex/AGENTS.md

**Files:**
- Create: `codex/AGENTS.md`

- [ ] **Step 1: Create the file with this exact content**

```markdown
# Global Codex Configuration
**Scope**: All projects on this machine

## Tool Mapping

Skill files use Claude Code tool names. In Codex, use these equivalents:

| Skill references | Codex equivalent |
|---|---|
| `Read` (file reading) | `cat <file>` or read directly |
| `Write` (file creation) | write file directly |
| `Edit` (file editing) | edit file directly |
| `Bash` (run commands) | run shell commands (you already do this) |
| `TodoWrite` (task tracking) | maintain checklist at `/tmp/codex-tasks.md` |
| `Skill` tool (invoke a skill) | `cat ~/.codex/skills/<name>/SKILL.md` and follow it |
| `Task` subagent dispatch | not supported — skip those steps in skills |
| `WebSearch` | web search if available |

## Workflow Standards

**Before any new feature or non-trivial change:**
Read and follow `~/.codex/skills/brainstorming/SKILL.md`

**Before writing application code:**
Read and follow `~/.codex/skills/test-driven-development/SKILL.md`

**When hitting a bug for more than 10 minutes:**
Read and follow `~/.codex/skills/systematic-debugging/SKILL.md`

**Before claiming work is done or making a commit:**
Read and follow `~/.codex/skills/verification-before-completion/SKILL.md`

**When implementation is complete:**
Read and follow `~/.codex/skills/finishing-a-development-branch/SKILL.md`

**When receiving code review feedback:**
Read and follow `~/.codex/skills/receiving-code-review/SKILL.md`

**After completing a major feature, before merging:**
Read and follow `~/.codex/skills/requesting-code-review/SKILL.md`

## Code Quality Rules

- Statements coverage: 80% minimum
- Branches coverage: 75% minimum
- Functions coverage: 80% minimum
- Lines coverage: 80% minimum
- No `console.log` in production code (use a logger)
- No hardcoded secrets or tokens
- No dead imports
- All tests pass locally before committing
- Parameterized queries only (no string concatenation in SQL)
- Descriptive variable names over clever abbreviations
- Functions do one thing

## Session Discipline

1. **One task per session** — don't reuse sessions for unrelated work
2. **Commit frequently** — every logical change is a git checkpoint
3. **HANDOFF.md bridges sessions** — 100 lines of structured context beats 500k tokens of history
4. **DECISIONS.md tracks architecture** — always commit this; never commit HANDOFF.md
```

- [ ] **Step 2: Commit**

```bash
git add codex/AGENTS.md
git commit -m "feat: add codex/AGENTS.md global config"
```

---

## Task 2: Port brainstorming skill

**Files:**
- Create: `codex/skills/brainstorming/SKILL.md`

Source: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/brainstorming/SKILL.md`

Adaptations from source:
- Remove Visual Companion section entirely (browser tool unavailable in Codex)
- Change `docs/superpowers/specs/` → `docs/specs/`
- Change "Invoke writing-plans skill" → "Read and follow `~/.codex/skills/writing-plans/SKILL.md`"
- Remove "Use elements-of-style:writing-clearly-and-concisely skill if available"

- [ ] **Step 1: Create the directory and file**

```bash
mkdir -p codex/skills/brainstorming
```

Write `codex/skills/brainstorming/SKILL.md` with this content:

````markdown
---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
---

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design and get user approval.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Checklist

You MUST track each of these items and complete them in order:

1. **Explore project context** — check files, docs, recent commits
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — with trade-offs and your recommendation
4. **Present design** — in sections scaled to their complexity, get user approval after each section
5. **Write design doc** — save to `docs/specs/YYYY-MM-DD-<topic>-design.md` and commit
6. **Spec self-review** — quick inline check for placeholders, contradictions, ambiguity, scope
7. **User reviews written spec** — ask user to review the spec file before proceeding
8. **Transition to implementation** — read and follow `~/.codex/skills/writing-plans/SKILL.md`

## The Process

**Understanding the idea:**

- Check out the current project state first (files, docs, recent commits)
- Before asking detailed questions, assess scope: if the request describes multiple independent subsystems, flag this immediately. Help the user decompose into sub-projects first.
- For appropriately-scoped projects, ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**

- Once you believe you understand what you're building, present the design
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

**Design for isolation and clarity:**

- Break the system into smaller units that each have one clear purpose
- For each unit: what does it do, how do you use it, what does it depend on?
- Smaller, well-bounded units are easier to reason about and test independently

**Working in existing codebases:**

- Explore the current structure before proposing changes. Follow existing patterns.
- Include targeted improvements where existing code has problems that affect the work
- Don't propose unrelated refactoring

## After the Design

**Documentation:**

- Write the validated design (spec) to `docs/specs/YYYY-MM-DD-<topic>-design.md`
- Commit the design document to git

**Spec Self-Review:**
After writing the spec document, look at it with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other?
3. **Scope check:** Is this focused enough for a single implementation plan?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? Pick one and make it explicit.

Fix any issues inline before asking the user to review.

**User Review Gate:**
Ask the user to review the written spec before proceeding:

> "Spec written and committed to `<path>`. Please review it and let me know if you want any changes before I write the implementation plan."

Wait for the user's response. Only proceed once the user approves.

**Implementation:**

Read and follow `~/.codex/skills/writing-plans/SKILL.md` to create the implementation plan.

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design, get approval before moving on
````

- [ ] **Step 2: Commit**

```bash
git add codex/skills/brainstorming/SKILL.md
git commit -m "feat: add codex brainstorming skill"
```

---

## Task 3: Port systematic-debugging skill

**Files:**
- Create: `codex/skills/systematic-debugging/SKILL.md`

Source: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/systematic-debugging/SKILL.md`

Adaptations:
- Replace `superpowers:test-driven-development` references → `` `~/.codex/skills/test-driven-development/SKILL.md` ``
- Replace `superpowers:verification-before-completion` references → `` `~/.codex/skills/verification-before-completion/SKILL.md` ``
- Remove `See root-cause-tracing.md in this directory` — file doesn't exist in Codex skills

- [ ] **Step 1: Create directory and file**

```bash
mkdir -p codex/skills/systematic-debugging
```

Copy source file then apply these three edits:

**Edit 1** — Replace skill reference in Phase 4:
```
old: Use the `superpowers:test-driven-development` skill for writing proper failing tests
new: Read and follow `~/.codex/skills/test-driven-development/SKILL.md` for writing proper failing tests
```

**Edit 2** — Replace skill reference in Supporting Techniques section:
```
old: - **superpowers:test-driven-development** - For creating failing test case (Phase 4, Step 1)
     - **superpowers:verification-before-completion** - Verify fix worked before claiming success
new: - **`~/.codex/skills/test-driven-development/SKILL.md`** - For creating failing test case (Phase 4, Step 1)
     - **`~/.codex/skills/verification-before-completion/SKILL.md`** - Verify fix worked before claiming success
```

**Edit 3** — Remove unavailable reference in Phase 1 step 5:
```
old:    See `root-cause-tracing.md` in this directory for the complete backward tracing technique.
new:    (remove this line)
```

- [ ] **Step 2: Commit**

```bash
git add codex/skills/systematic-debugging/SKILL.md
git commit -m "feat: add codex systematic-debugging skill"
```

---

## Task 4: Port test-driven-development skill

**Files:**
- Create: `codex/skills/test-driven-development/SKILL.md`

Source: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/test-driven-development/SKILL.md`

Adaptations:
- Remove `@testing-anti-patterns.md` reference at bottom (file doesn't exist in Codex skills)

- [ ] **Step 1: Create directory and file**

```bash
mkdir -p codex/skills/test-driven-development
```

Copy source file then apply this edit:

**Edit** — Remove testing anti-patterns reference block near the bottom:
```
old: ## Testing Anti-Patterns

When adding mocks or test utilities, read @testing-anti-patterns.md to avoid common pitfalls:
- Testing mock behavior instead of real behavior
- Adding test-only methods to production classes
- Mocking without understanding dependencies

new: (remove this section entirely)
```

- [ ] **Step 2: Commit**

```bash
git add codex/skills/test-driven-development/SKILL.md
git commit -m "feat: add codex test-driven-development skill"
```

---

## Task 5: Port verification-before-completion skill

**Files:**
- Create: `codex/skills/verification-before-completion/SKILL.md`

Source: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/verification-before-completion/SKILL.md`

Adaptations: **None.** This skill is pure prose with no tool references. Copy verbatim.

- [ ] **Step 1: Create directory and copy**

```bash
mkdir -p codex/skills/verification-before-completion
cp ~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/verification-before-completion/SKILL.md \
   codex/skills/verification-before-completion/SKILL.md
```

- [ ] **Step 2: Commit**

```bash
git add codex/skills/verification-before-completion/SKILL.md
git commit -m "feat: add codex verification-before-completion skill"
```

---

## Task 6: Port finishing-a-development-branch skill

**Files:**
- Create: `codex/skills/finishing-a-development-branch/SKILL.md`

Source: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/finishing-a-development-branch/SKILL.md`

Adaptations:
- Remove Step 2 worktree detection entirely (Codex doesn't use git worktrees)
- Simplify Step 2 → "Determine base branch" (renumber remaining steps)
- Remove Step 6 "Cleanup Workspace" section (worktree cleanup not applicable)
- Remove worktree column from Quick Reference table
- Remove worktree-related items from Common Mistakes and Red Flags

- [ ] **Step 1: Create directory and file**

```bash
mkdir -p codex/skills/finishing-a-development-branch
```

Write `codex/skills/finishing-a-development-branch/SKILL.md` with this content:

````markdown
---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Determine base branch → Present options → Execute choice.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**If tests fail:**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

Stop. Don't proceed to Step 2.

**If tests pass:** Continue to Step 2.

### Step 2: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
git rev-parse --abbrev-ref HEAD
```

Or ask: "This branch split from main — is that correct?"

### Step 3: Present Options

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Don't add explanation** — keep options concise.

### Step 4: Execute Choice

#### Option 1: Merge Locally

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>

# Only after merge succeeds: delete branch
git branch -d <feature-branch>
```

#### Option 2: Push and Create PR

```bash
git push -u origin <feature-branch>

gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

#### Option 3: Keep As-Is

Report: "Keeping branch <name>."

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>

Type 'discard' to confirm.
```

Wait for exact confirmation. If confirmed:

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

## Quick Reference

| Option | Merge | Push | Delete Branch |
|--------|-------|------|---------------|
| 1. Merge locally | yes | — | yes |
| 2. Create PR | — | yes | — |
| 3. Keep as-is | — | — | — |
| 4. Discard | — | — | yes (force) |

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without typed 'discard' confirmation
- Force-push without explicit request

**Always:**
- Verify tests before offering options
- Present exactly 4 options
- Get typed confirmation for Option 4
````

- [ ] **Step 2: Commit**

```bash
git add codex/skills/finishing-a-development-branch/SKILL.md
git commit -m "feat: add codex finishing-a-development-branch skill"
```

---

## Task 7: Port requesting-code-review skill

**Files:**
- Create: `codex/skills/requesting-code-review/SKILL.md`

Source: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/requesting-code-review/SKILL.md`

Adaptations:
- Replace Task tool subagent dispatch with a structured self-review checklist (Codex has no subagent dispatch)
- Remove template reference (`code-reviewer.md` doesn't exist in Codex skills)

- [ ] **Step 1: Create directory and file**

```bash
mkdir -p codex/skills/requesting-code-review
```

Write `codex/skills/requesting-code-review/SKILL.md` with this content:

````markdown
---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

# Requesting Code Review

Perform a structured self-review before merging to catch issues early.

**Core principle:** Review early, review often.

## When to Review

**Mandatory:**
- After completing a major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective helps)
- Before refactoring (baseline check)
- After fixing a complex bug

## How to Review

**1. Get the diff:**

```bash
BASE_SHA=$(git rev-parse origin/main 2>/dev/null || git rev-parse main)
HEAD_SHA=$(git rev-parse HEAD)
git diff "$BASE_SHA".."$HEAD_SHA"
```

**2. Work through this checklist for every changed file:**

```
For each file in the diff:

Correctness:
- [ ] Logic is correct and handles edge cases
- [ ] No off-by-one errors or boundary conditions missed
- [ ] Error paths are handled

Tests:
- [ ] New behavior has tests
- [ ] Tests watched fail before implementation (TDD followed)
- [ ] Edge cases are covered

Security:
- [ ] No hardcoded secrets or tokens
- [ ] User input is validated at boundaries
- [ ] No SQL string concatenation

Code Quality:
- [ ] No dead imports or unused variables
- [ ] No console.log in production paths
- [ ] Functions do one thing
- [ ] Variable names are descriptive

Requirements:
- [ ] Re-read the plan or spec
- [ ] Every requirement has an implementation
- [ ] Every implementation has a requirement (no scope creep)
```

**3. Categorize findings:**

```
Critical  — breaks functionality, security issue, data loss risk → fix before proceeding
Important — test missing, error unhandled → fix before merge
Minor     — naming, style, comment quality → note for later
```

**4. Fix Critical and Important issues, then verify:**

```bash
# Run full test suite
<your test command>

# Confirm output
Expected: all tests pass, 0 failures
```

## Integration with Workflows

**After each major task:** Review before moving on — catch issues before they compound.

**Before merge:** Always review. One pass now saves hours of debugging later.

## Red Flags

**Never:**
- Skip review because "it's simple"
- Merge with unfixed Critical issues
- Merge with unfixed Important issues

**If unsure about a finding:**
- Check existing tests for precedent
- Check git log for prior decisions
- Ask your human partner
````

- [ ] **Step 2: Commit**

```bash
git add codex/skills/requesting-code-review/SKILL.md
git commit -m "feat: add codex requesting-code-review skill"
```

---

## Task 8: Port receiving-code-review skill

**Files:**
- Create: `codex/skills/receiving-code-review/SKILL.md`

Source: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/receiving-code-review/SKILL.md`

Adaptations:
- Remove GitHub thread replies section (Codex doesn't post GitHub API replies)

- [ ] **Step 1: Create directory and file**

```bash
mkdir -p codex/skills/receiving-code-review
```

Copy source file then remove this section:

```
old: ## GitHub Thread Replies

When replying to inline review comments on GitHub, reply in the comment thread
(`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a
top-level PR comment.

new: (remove this section entirely)
```

- [ ] **Step 2: Commit**

```bash
git add codex/skills/receiving-code-review/SKILL.md
git commit -m "feat: add codex receiving-code-review skill"
```

---

## Task 9: Port writing-plans skill

**Files:**
- Create: `codex/skills/writing-plans/SKILL.md`

Source: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-plans/SKILL.md`

Adaptations:
- Change plan save path: `docs/superpowers/plans/` → `docs/plans/`
- Replace Execution Handoff section: remove subagent option, inline execution only
- Update plan header template: remove subagent reference

- [ ] **Step 1: Create directory and file**

```bash
mkdir -p codex/skills/writing-plans
```

Copy source file then apply these edits:

**Edit 1** — Plan save path:
```
old: **Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
new: **Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`
```

**Edit 2** — Plan header template (remove subagent reference):
```
old: > **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
     (recommended) or superpowers:executing-plans to implement this plan task-by-task.
     Steps use checkbox (`- [ ]`) syntax for tracking.

new: > Implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
```

**Edit 3** — Replace Execution Handoff section entirely:
```
old: ## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (recommended)** ...
**2. Inline Execution** ...
**Which approach?"**

**If Subagent-Driven chosen:**
...

**If Inline Execution chosen:**
...

new: ## Execution Handoff

After saving the plan, say:

**"Plan complete and saved to `docs/plans/<filename>.md`. Ready to implement task-by-task.
Say 'go' to start on Task 1, or review the plan first."**

Then implement each task in order, marking checkboxes as you go.
```

- [ ] **Step 2: Commit**

```bash
git add codex/skills/writing-plans/SKILL.md
git commit -m "feat: add codex writing-plans skill"
```

---

## Task 10: Add Codex section to install.sh

**Files:**
- Modify: `install.sh`

- [ ] **Step 1: Write the failing test**

In `tests/test_configure.py`, add this test class before `class TestHtmlJs`:

```python
class TestCodexSkills(unittest.TestCase):
    SKILLS = [
        "brainstorming",
        "systematic-debugging",
        "test-driven-development",
        "requesting-code-review",
        "receiving-code-review",
        "writing-plans",
        "verification-before-completion",
        "finishing-a-development-branch",
    ]

    def setUp(self):
        self.codex_dir = Path(__file__).parent.parent / "codex"

    def test_agents_md_exists(self):
        self.assertTrue(
            (self.codex_dir / "AGENTS.md").exists(),
            "codex/AGENTS.md missing"
        )

    def test_all_skill_dirs_exist(self):
        for skill in self.SKILLS:
            with self.subTest(skill=skill):
                path = self.codex_dir / "skills" / skill / "SKILL.md"
                self.assertTrue(path.exists(), f"codex/skills/{skill}/SKILL.md missing")

    def test_all_skills_have_valid_frontmatter(self):
        for skill in self.SKILLS:
            with self.subTest(skill=skill):
                path = self.codex_dir / "skills" / skill / "SKILL.md"
                content = path.read_text()
                self.assertTrue(content.startswith("---"), f"{skill}: missing frontmatter opening ---")
                end = content.index("---", 3)
                fm = content[3:end]
                self.assertIn("name:", fm, f"{skill}: frontmatter missing 'name' field")
                self.assertIn("description:", fm, f"{skill}: frontmatter missing 'description' field")

    def test_install_sh_has_codex_section(self):
        install = Path(__file__).parent.parent / "install.sh"
        content = install.read_text()
        self.assertIn("~/.codex/AGENTS.md", content)
        self.assertIn("~/.codex/skills", content)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m unittest tests.test_configure.TestCodexSkills -v
```

Expected: FAIL — skills not yet installed to ~/.codex, and install.sh check fails

- [ ] **Step 3: Add Codex section to install.sh**

Append this block before the final `echo "=== Done ==="` line in `install.sh`:

```bash
# ── 8. Codex CLI setup ──────────────────────────────────────────────────────
if command -v codex &>/dev/null; then
  CODEX_DIR="$HOME/.codex"
  mkdir -p "$CODEX_DIR/skills"

  if [ -f "$CODEX_DIR/AGENTS.md" ]; then
    cp "$CODEX_DIR/AGENTS.md" "$CODEX_DIR/AGENTS.md.bak"
    echo "[info] ~/.codex/AGENTS.md backed up to AGENTS.md.bak"
  fi
  cp "$REPO_DIR/codex/AGENTS.md" "$CODEX_DIR/AGENTS.md"
  echo "[ok]   ~/.codex/AGENTS.md"

  cp -r "$REPO_DIR/codex/skills/"* "$CODEX_DIR/skills/"
  SKILL_COUNT=$(ls "$REPO_DIR/codex/skills/" | wc -l | tr -d ' ')
  echo "[ok]   ~/.codex/skills/ ($SKILL_COUNT skills installed)"
else
  echo "[skip] codex not found — skipping Codex CLI setup"
  echo "       Install Codex then re-run install.sh"
fi
```

- [ ] **Step 4: Run tests**

```bash
python3 -m unittest tests.test_configure.TestCodexSkills -v
```

Expected: All 4 tests pass (AGENTS.md exists, all 8 skill dirs exist, frontmatter valid, install.sh has codex section)

- [ ] **Step 5: Run full test suite to check for regressions**

```bash
python3 -m unittest discover -q
```

Expected: All tests pass, 0 failures

- [ ] **Step 6: Commit**

```bash
git add install.sh tests/test_configure.py
git commit -m "feat: add Codex section to install.sh + TestCodexSkills tests"
```

---

## Task 11: End-to-end verify

- [ ] **Step 1: Dry-run install.sh Codex section**

```bash
bash install.sh 2>&1 | grep -A5 "Codex"
```

Expected output contains:
```
[ok]   ~/.codex/AGENTS.md
[ok]   ~/.codex/skills/ (8 skills installed)
```

- [ ] **Step 2: Verify skills landed in ~/.codex**

```bash
ls ~/.codex/skills/
```

Expected: 8 directories matching the skill names

- [ ] **Step 3: Verify a skill is readable**

```bash
head -5 ~/.codex/skills/brainstorming/SKILL.md
```

Expected:
```
---
name: brainstorming
description: "You MUST use this before any creative work...
---
```

- [ ] **Step 4: Update HANDOFF.md**

Update `HANDOFF.md`:
- Increment test count to reflect new TestCodexSkills tests
- Mark Codex CLI support as done in near-term items
- Update last commit SHA and resumption prompt

- [ ] **Step 5: Final commit**

```bash
git add -f HANDOFF.md 2>/dev/null || true
git commit -m "feat: Codex CLI Superpowers port complete"
```

If HANDOFF.md is gitignored, skip the add — it stays local.
