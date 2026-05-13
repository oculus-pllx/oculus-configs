# Global Claude Code Configuration
**Scope**: All projects on this machine

## Active Plugins

### Superpowers (superpowers@claude-plugins-official) — ENABLED
- Use brainstorming skill before any new feature work
- Use TDD skill before writing application code
- Use code review skill before marking PRs ready
- Skills live in: `~/.claude/plugins/cache/claude-plugins-official/superpowers/`

### Frontend Design (frontend-design@claude-plugins-official) — ENABLED
- Use for any UI/UX work, component design, or visual layout decisions

### Skill Creator (skill-creator@claude-plugins-official) — ENABLED
- Use to build custom project-specific skills when a pattern repeats

## Token Discipline (HIGH PRIORITY)

1. **One task per session** — don't reuse sessions for unrelated work
2. **Check context at /usage** — compact or clear when approaching 70%
3. **Use /compact selectively**: `/compact focus on [active feature]` — lossy but preserves momentum
4. **Use subagents** for heavy or parallel work (10+ files, code analysis)
5. **Keep MCP servers minimal** — max 3–4 per session; each costs 100–500 tokens/turn
6. **Fresh sessions beat long sessions** — context rot sets in after 200–300k tokens on long tasks

## Workflow Standards

1. **Plan before execute** — Shift+Tab for plan mode on any non-trivial task
2. **Commit frequently** — every logical change is a git checkpoint, not just end of session
3. **HANDOFF.md bridges sessions** — 100 lines of structured context beats 500k tokens of history
4. **DECISIONS.md tracks architecture** — always commit this; never commit HANDOFF.md

## Session End Checklist

- [ ] All work committed with descriptive message
- [ ] `.claude/HANDOFF.md` updated with next steps and resumption prompt
- [ ] Push to remote if checkpoint is meaningful

@~/.claude/rules/code-quality.md
@~/.claude/rules/plugin-usage.md
