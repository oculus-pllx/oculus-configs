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

**After approving a design spec (to create the implementation plan):**
Read and follow `~/.gemini/skills/writing-plans/SKILL.md`

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
