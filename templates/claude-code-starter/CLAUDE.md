# [Project Name] — Development Context

## Project Metadata
- **Tech Stack**: [e.g., Next.js 15, TypeScript, Tailwind, PostgreSQL]
- **Repository**: [GitHub URL]
- **Entry Point**: [e.g., src/app/page.tsx or src/server.ts]
- **Status**: Active

## Project Overview
[Keep this under 100 words. Auto Memory will learn structural details over sessions.]

## Architecture Overview

### Frontend
- Framework: [e.g., React 18 + TypeScript]
- State: [e.g., React Query + Zustand]
- Styling: [e.g., Tailwind CSS]
- Testing: [e.g., Vitest + React Testing Library]

### Backend
- Framework: [e.g., Express.js]
- Database: [e.g., PostgreSQL + Prisma]
- Auth: [e.g., JWT + refresh tokens]

### Version-Critical Dependencies
- [package]: [version]+ — Context7 should fetch live docs for this

## Development Workflow

### Naming Conventions
- Functions/variables: camelCase
- Components: PascalCase
- Constants: UPPER_SNAKE_CASE
- Files: kebab-case

### Git Commits
Format: `type(scope): description`
Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`
Max 50 chars in subject line.

### Branch Strategy
- `main` — protected, PR required
- `feature/DESCRIPTION` — new features
- `fix/DESCRIPTION` — bug fixes

## Superpowers Skills for This Project

### Always use
- **Brainstorming**: Before any new feature — requirements before code
- **TDD**: Write test first, then implementation
- **Code Review**: Before shipping a slice of work

### Workflow default
- **Commit and push straight to `main`; no PRs.** Pushing is part of finishing. If *this* project uses PRs instead, change this line to `Workflow: uses PRs`.

### Use when applicable
- **Refactoring**: Large module changes
- **Architecture Pattern**: Designing new systems
- **Frontend Design**: UI/component design decisions

## Critical Rules

### DO
- Commit frequently (every logical change, not just end of session)
- Run tests before committing
- Update docs/DECISIONS.md on architecture choices
- Use feature branches — never commit directly to main

### DON'T
- Hardcode secrets (use .env)
- Commit node_modules/, .env, or build artifacts
- Skip tests for new code
- Mix unrelated changes in one PR

## MCP Servers for This Project

- **github** — PR and issue workflow (always)
- **context7** — Live docs for fast-moving frameworks (enable when needed)
- [project-specific MCP if applicable]

## Testing Requirements
- Unit: [framework] — ≥80% coverage
- Component: [framework]
- E2E: [framework] — critical paths only
- Run before committing: `[your test command]`

## Common Commands
```bash
# Dev
[dev command]

# Test
[test command]

# Build
[build command]
```

## When to Update This File
- Architecture changes significantly
- New permanent conventions established
- Critical dependency versions change
- Project status changes

**Don't update for**: session learnings (auto memory), temporary workarounds (HANDOFF.md)

## References
- `docs/DECISIONS.md` — architecture decisions
- `.claude/HANDOFF.md` — session context (ephemeral, not committed)
- `README.md` — user documentation

---
*Last updated: [DATE]*
