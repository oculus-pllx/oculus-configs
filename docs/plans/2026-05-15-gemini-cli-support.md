# Gemini CLI Support + Template Completions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Gemini CLI skill support (parallel to codex/), add mcp.json to the starter template, and clean up the stale HANDOFF.md gap note about apply_update.

**Architecture:** gemini/ mirrors codex/ exactly — GEMINI.md holds Gemini tool mapping + lazy skill-load triggers, gemini/skills/ holds 8 SKILL.md files copied from codex with path references updated. A new install.sh section 9 deploys these to ~/.gemini/. The mcp.json addition to templates/claude-code-starter/ requires no configure.py changes since install.sh section 4 copies the whole directory.

**Tech Stack:** bash, Python 3 (tests only), existing unittest framework

---

## File Map

| Action | Path |
|--------|------|
| Create | `templates/claude-code-starter/mcp.json` |
| Create | `gemini/GEMINI.md` |
| Create | `gemini/skills/brainstorming/SKILL.md` |
| Create | `gemini/skills/systematic-debugging/SKILL.md` |
| Create | `gemini/skills/test-driven-development/SKILL.md` |
| Create | `gemini/skills/requesting-code-review/SKILL.md` |
| Create | `gemini/skills/receiving-code-review/SKILL.md` |
| Create | `gemini/skills/writing-plans/SKILL.md` |
| Create | `gemini/skills/verification-before-completion/SKILL.md` |
| Create | `gemini/skills/finishing-a-development-branch/SKILL.md` |
| Modify | `install.sh` — add section 9 after section 8 |
| Modify | `tests/test_configure.py` — add TestStarterTemplate + TestGeminiSkills |
| Modify | `HANDOFF.md` — mark apply_update gap as resolved |

---

## Task 1: Starter Template — mcp.json

**Files:**
- Create: `templates/claude-code-starter/mcp.json`
- Modify: `tests/test_configure.py` (add `TestStarterTemplate` class after line 475)

- [ ] **Step 1: Write the failing tests**

Insert this class after the `TestCodexSkills` block (after line 475, before `class TestBrowseDir`):

```python
class TestStarterTemplate(unittest.TestCase):
    def setUp(self):
        self.starter_dir = Path(__file__).parent.parent / "templates" / "claude-code-starter"

    def test_mcp_json_exists(self):
        self.assertTrue(
            (self.starter_dir / "mcp.json").exists(),
            "templates/claude-code-starter/mcp.json missing"
        )

    def test_mcp_json_valid(self):
        p = self.starter_dir / "mcp.json"
        data = json.loads(p.read_text())
        self.assertIn("mcpServers", data)
        self.assertIn("github", data["mcpServers"])
        self.assertIn("context7", data["mcpServers"])
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_configure.py::TestStarterTemplate -v
```

Expected: 2 FAILED — `mcp.json` does not exist yet.

- [ ] **Step 3: Create the file**

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "REPLACE_WITH_YOUR_TOKEN"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

Save as `templates/claude-code-starter/mcp.json`.

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_configure.py::TestStarterTemplate -v
```

Expected: 2 PASSED.

- [ ] **Step 5: Commit**

```bash
git add templates/claude-code-starter/mcp.json tests/test_configure.py
git commit -m "feat: add mcp.json to claude-code-starter template"
```

---

## Task 2: gemini/GEMINI.md

**Files:**
- Create: `gemini/GEMINI.md`
- Modify: `tests/test_configure.py` (add `TestGeminiSkills` class)

- [ ] **Step 1: Write the failing tests**

Insert this class directly after `TestStarterTemplate` (before `class TestBrowseDir`):

```python
class TestGeminiSkills(unittest.TestCase):
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
        self.gemini_dir = Path(__file__).parent.parent / "gemini"

    def test_gemini_md_exists(self):
        self.assertTrue(
            (self.gemini_dir / "GEMINI.md").exists(),
            "gemini/GEMINI.md missing"
        )

    def test_gemini_md_has_tool_mapping(self):
        content = (self.gemini_dir / "GEMINI.md").read_text()
        self.assertIn("read_file", content)
        self.assertIn("run_shell_command", content)
        self.assertIn("activate_skill", content)

    def test_gemini_md_has_skill_triggers(self):
        content = (self.gemini_dir / "GEMINI.md").read_text()
        for skill in self.SKILLS:
            with self.subTest(skill=skill):
                self.assertIn(skill, content, f"GEMINI.md missing trigger for {skill}")

    def test_all_skill_dirs_exist(self):
        for skill in self.SKILLS:
            with self.subTest(skill=skill):
                path = self.gemini_dir / "skills" / skill / "SKILL.md"
                self.assertTrue(path.exists(), f"gemini/skills/{skill}/SKILL.md missing")

    def test_all_skills_have_valid_frontmatter(self):
        for skill in self.SKILLS:
            with self.subTest(skill=skill):
                path = self.gemini_dir / "skills" / skill / "SKILL.md"
                content = path.read_text()
                self.assertTrue(content.startswith("---"), f"{skill}: missing frontmatter opening ---")
                end = content.index("---", 3)
                fm = content[3:end]
                self.assertIn("name:", fm, f"{skill}: frontmatter missing 'name' field")
                self.assertIn("description:", fm, f"{skill}: frontmatter missing 'description' field")

    def test_install_sh_has_gemini_section(self):
        install = Path(__file__).parent.parent / "install.sh"
        content = install.read_text()
        self.assertIn("~/.gemini/GEMINI.md", content)
        self.assertIn("~/.gemini/skills", content)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_configure.py::TestGeminiSkills -v
```

Expected: multiple FAILED — `gemini/GEMINI.md` does not exist yet.

- [ ] **Step 3: Create gemini/GEMINI.md**

```markdown
# Global Gemini CLI Configuration
**Scope**: All projects on this machine

## Tool Mapping

Skill files use Claude Code tool names. In Gemini CLI, use these equivalents:

| Skill references | Gemini CLI equivalent |
|---|---|
| `Read` (file reading) | `read_file` |
| `Write` (file creation) | `write_file` |
| `Edit` (file editing) | `replace` |
| `Bash` (run commands) | `run_shell_command` |
| `TodoWrite` (task tracking) | `write_todos` |
| `Skill` tool (invoke a skill) | `activate_skill` |
| `Task` subagent dispatch | `@generalist` with filled prompt template |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |

## Workflow Standards

**Before any new feature or non-trivial change:**
Read and follow `~/.gemini/skills/brainstorming/SKILL.md`

**Before writing application code:**
Read and follow `~/.gemini/skills/test-driven-development/SKILL.md`

**When hitting a bug for more than 10 minutes:**
Read and follow `~/.gemini/skills/systematic-debugging/SKILL.md`

**Before claiming work is done or making a commit:**
Read and follow `~/.gemini/skills/verification-before-completion/SKILL.md`

**When implementation is complete:**
Read and follow `~/.gemini/skills/finishing-a-development-branch/SKILL.md`

**When receiving code review feedback:**
Read and follow `~/.gemini/skills/receiving-code-review/SKILL.md`

**After completing a major feature, before merging:**
Read and follow `~/.gemini/skills/requesting-code-review/SKILL.md`

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

Also delete `gemini/.gitkeep` since `GEMINI.md` now anchors the directory:

```bash
rm gemini/.gitkeep
```

- [ ] **Step 4: Run GEMINI.md tests to verify they pass**

```bash
python -m pytest tests/test_configure.py::TestGeminiSkills::test_gemini_md_exists tests/test_configure.py::TestGeminiSkills::test_gemini_md_has_tool_mapping tests/test_configure.py::TestGeminiSkills::test_gemini_md_has_skill_triggers -v
```

Expected: 3 PASSED. The skill dir tests still fail — that's expected, they come next.

- [ ] **Step 5: Commit**

```bash
git add gemini/GEMINI.md gemini/.gitkeep tests/test_configure.py
git commit -m "feat: add gemini/GEMINI.md with tool mapping and skill triggers"
```

---

## Task 3: gemini/skills/* — All 8 Skill Files

**Files:**
- Create: `gemini/skills/brainstorming/SKILL.md`
- Create: `gemini/skills/systematic-debugging/SKILL.md`
- Create: `gemini/skills/test-driven-development/SKILL.md`
- Create: `gemini/skills/requesting-code-review/SKILL.md`
- Create: `gemini/skills/receiving-code-review/SKILL.md`
- Create: `gemini/skills/writing-plans/SKILL.md`
- Create: `gemini/skills/verification-before-completion/SKILL.md`
- Create: `gemini/skills/finishing-a-development-branch/SKILL.md`

- [ ] **Step 1: Copy all skill files and update path references**

```bash
mkdir -p gemini/skills
for skill in brainstorming systematic-debugging test-driven-development \
             requesting-code-review receiving-code-review writing-plans \
             verification-before-completion finishing-a-development-branch; do
  mkdir -p "gemini/skills/$skill"
  sed 's|~/.codex/skills/|~/.gemini/skills/|g' \
    "codex/skills/$skill/SKILL.md" > "gemini/skills/$skill/SKILL.md"
done
```

The `sed` command updates all cross-references in brainstorming and systematic-debugging (the only two skills that reference other skills by path). All other skills have no `~/.codex/` references, so sed is a no-op for them.

- [ ] **Step 2: Verify the substitution is correct**

```bash
grep -r "~/.codex/" gemini/skills/
```

Expected: no output. All references should now be `~/.gemini/`.

```bash
grep -r "~/.gemini/skills/" gemini/skills/
```

Expected: lines from `brainstorming/SKILL.md` and `systematic-debugging/SKILL.md` showing the updated paths.

- [ ] **Step 3: Run the skill tests**

```bash
python -m pytest tests/test_configure.py::TestGeminiSkills -v
```

Expected: all 5 tests PASSED (the `test_install_sh_has_gemini_section` will still fail — that's Task 4).

- [ ] **Step 4: Commit**

```bash
git add gemini/skills/
git commit -m "feat: add gemini/skills/ — 8 Superpowers-equivalent skills for Gemini CLI"
```

---

## Task 4: install.sh — Section 9 (Gemini CLI)

**Files:**
- Modify: `install.sh` — add section 9 after the section 8 `fi` block (after line 154)

- [ ] **Step 1: Add section 9 to install.sh**

Append the following block after the closing `fi` of section 8 (after line 154, before the final `echo` block):

```bash
# ── 9. Gemini CLI setup ──────────────────────────────────────────────────────
if command -v gemini &>/dev/null; then
  GEMINI_DIR="$HOME/.gemini"
  mkdir -p "$GEMINI_DIR/skills"

  if [ -f "$GEMINI_DIR/GEMINI.md" ]; then
    cp "$GEMINI_DIR/GEMINI.md" "$GEMINI_DIR/GEMINI.md.bak"
    echo "[info] ~/.gemini/GEMINI.md backed up to GEMINI.md.bak"
  fi
  cp "$REPO_DIR/gemini/GEMINI.md" "$GEMINI_DIR/GEMINI.md"
  echo "[ok]   ~/.gemini/GEMINI.md"

  cp -r "$REPO_DIR/gemini/skills/"* "$GEMINI_DIR/skills/"
  SKILL_COUNT=$(ls "$REPO_DIR/gemini/skills/" | wc -l | tr -d ' ')
  echo "[ok]   ~/.gemini/skills/ ($SKILL_COUNT skills installed)"
else
  echo "[skip] gemini not found — skipping Gemini CLI setup"
  echo "       Install Gemini CLI then re-run install.sh"
fi
```

- [ ] **Step 2: Run the install.sh test**

```bash
python -m pytest tests/test_configure.py::TestGeminiSkills::test_install_sh_has_gemini_section -v
```

Expected: PASSED.

- [ ] **Step 3: Run all Gemini tests**

```bash
python -m pytest tests/test_configure.py::TestGeminiSkills -v
```

Expected: all 6 tests PASSED.

- [ ] **Step 4: Run the full test suite to confirm no regressions**

```bash
python -m pytest tests/ -v
```

Expected: all 65+ tests PASSED (57 original + 2 starter template + 6 gemini = 65).

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat: install.sh section 9 — Gemini CLI setup"
```

---

## Task 5: Update HANDOFF.md

**Files:**
- Modify: `HANDOFF.md`

- [ ] **Step 1: Update the stale gap note and near-term items**

In `HANDOFF.md`:

1. Remove the "Known gap" paragraph under "Self-Update (Dashboard)":
   ```
   **Known gap**: apply_update copies the binary but doesn't restart systemd — manual `systemctl --user restart oculus-configure` needed after a self-update
   ```
   Replace with:
   ```
   `_restart_service()` is called at the end of `apply_update()` — systemd/launchd restart happens automatically on self-update.
   ```

2. Under "Near-term items", mark completed items and add Gemini CLI:
   - Change `[ ]` to `[x]` for "Gemini CLI support"
   - Change `[ ]` to `[x]` for "Add `.gitignore` and `mcp.json` to `templates/claude-code-starter/`"
   - Change `[ ]` to `[x]` for "Fix `apply_update` to restart systemd service after copying binary"

3. Update "Resumption prompt" to reflect current state.

- [ ] **Step 2: Verify the full test suite still passes**

```bash
python -m pytest tests/ -v 2>&1 | tail -5
```

Expected: something like `65 passed in X.XXs`.

- [ ] **Step 3: Final commit**

```bash
git add HANDOFF.md
git commit -m "docs: update HANDOFF.md — Gemini CLI done, apply_update gap resolved"
```
