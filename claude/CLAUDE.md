# Global Claude Code Configuration
**Scope**: All projects on this machine

## Active Plugins

### Superpowers (superpowers@claude-plugins-official) — ENABLED
- Use brainstorming skill before any new feature work
- Use TDD skill before writing application code
- Use code review skill before shipping a slice of work
- **Default workflow: commit and push straight to `main`; no PRs.** Pushing to origin is part of finishing — don't wait for an explicit "push" directive. Only a project that *uses* PRs should say so in its own `CLAUDE.md` (e.g. `Workflow: uses PRs`); absent that, never offer or open a PR.
- Skills live in: `~/.claude/plugins/cache/claude-plugins-official/superpowers/`

### Frontend Design (frontend-design@claude-plugins-official) — ENABLED
- Use for any UI/UX work, component design, or visual layout decisions
- **No default design system.** `rules/ui-baseline.md` covers accessibility and
  structure only; visual style comes from whatever the project already uses.
- A project that wants Material Design 3, Tailwind, or any other house style
  names it in its own `CLAUDE.md`. Never import one globally.

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

## Credentials and Infrastructure Registry

Before reporting any credential, token, host, or tunnel as missing or unknown, read
`/srv/ccc/projects/Meridian-VPS/docs/access-map.md`. It is the single registry of every credential
on this workstation: what it can do, where it lives (PRISM vault, `/etc/ccc/secrets/`, `~/.config`),
and which projects depend on it. It holds locations only. **Never print, log, or commit a secret
value**; read tokens into a variable in a subshell and report only status, names, or hashes. Update
the registry when a credential is created, moved, or rotated. Other projects point to it rather than
keeping their own copy.

@~/.claude/rules/code-quality.md
@~/.claude/rules/plugin-usage.md
@~/.claude/rules/ui-baseline.md
