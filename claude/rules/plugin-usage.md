# Plugin Usage Rules

## Superpowers Skill Triggers
- **Brainstorming**: Any new feature or non-trivial task — invoke BEFORE touching code
- **TDD**: Before writing any application code — write the test first
- **Code Review**: Before shipping a slice of work — run this skill (default workflow pushes to `main`, no PRs; see global CLAUDE.md)
- **Debugging**: When stuck on a bug for more than 10 minutes — use systematic-debugging skill
- **Frontend Design**: Any UI component or layout decision

## When NOT to use plugins
- Trivial fixes (typos, config changes) — don't add overhead
- Exploratory spikes — use plain conversation, not workflows

## Plugin Install Reference (correct commands)
```
# Inside a Claude Code session:
/plugin install superpowers@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
/plugin install claude-mem@thedotmack
/plugin install caveman@caveman
/plugin install andrej-karpathy-skills@karpathy-skills
```

## Enabling/Disabling Plugins
Plugins installed but not enabled still load their skills — enable only what you actively use
to keep session overhead low. Manage via `/plugin enable` and `/plugin disable`.
