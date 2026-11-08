# Global Claude Code Configuration
**Scope**: All projects on this machine

## Remote Jobs and Usage Budget (HIGH PRIORITY)

- Treat hourly and weekly AI usage as a limited resource. Waiting for a remote
  job must not consume repeated model turns or repeatedly reload conversation
  context.
- Start long builds, CI, deployments, transfers, and scans once; record the job
  ID, host, commit, log/artifact location, and next action in a concise handoff.
- Prefer completion events, callbacks, or a detached non-AI watcher that records
  the final result. Use notifications only through an already authorized channel.
- Do not run minute-by-minute status checks, sleep/poll/model-turn loops, or
  repeated "still running" updates. An unchanged running state needs no analysis.
- If completion events are unavailable, leave the job running unattended and
  report its ID and how to resume once. Do not claim you will monitor it after
  ending the turn. Check again when the user requests it or a completion/failure
  signal arrives. Explicit monitoring requests permit a detached watcher, not
  repeated model-driven polling.
- Inspect only the final status and relevant failure output on completion.
  Investigate earlier only when concrete evidence requires intervention.
- Reuse verified results for the same commit and artifact. Repeat a check only
  after a relevant change, a failure, or a specific unresolved concern; do not
  rerun broad gates for documentation-only changes unless required by the
  existing pipeline. Let automatically triggered CI finish unattended.
- Read unchanged instructions, logs, and files once per task where possible.
  Search narrowly, batch independent reads, and preserve a short durable handoff
  instead of repeatedly reconstructing the full task context.
- Send updates for meaningful transitions, findings, blockers, and completion.
  Do not keep an otherwise idle AI turn alive solely to narrate a remote job.


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
`/etc/ccc/registry/access-map.md`. It is the single registry of every credential
on this workstation: what it can do, where it lives (PRISM vault, `/etc/ccc/secrets/`, `~/.config`),
and which projects depend on it. It holds locations only. **Never print, log, or commit a secret
value**; read tokens into a variable in a subshell and report only status, names, or hashes. Update
the registry when a credential is created, moved, or rotated. Other projects point to it rather than
keeping their own copy.

## Parallax EQEmu Knowledge and Tooling

For any Parallax EQEmu project, begin at
`/srv/ccc/projects/parallax-emu-coordinator` and follow its project map. The canonical
EQEmu Tome, operational knowledge, and LightRAG loaders live in
`/srv/ccc/projects/parallax-eqemu`; do not copy their implementations into sibling
repositories. Load the approved operational chapter with
`python3 deploy/sysmap.py rag-load-operations` from that repository. This adds only
the allowlisted operational source and does not clear the public system map.

@~/.claude/rules/code-quality.md
@~/.claude/rules/plugin-usage.md
@~/.claude/rules/ui-baseline.md
