# Claude Code Project Template Files
**Copy these files into every new project**

---

## FILE 1: CLAUDE.md
**Save as**: `./CLAUDE.md` in project root  
**Scope**: Project-specific, committed to git  
**Purpose**: Permanent context for this project

```markdown
# [Project Name] — Development Context

## Project Metadata
- **Tech Stack**: [e.g., Next.js 15, TypeScript, Tailwind, PostgreSQL]
- **Repository**: [GitHub URL, e.g., github.com/yourname/project]
- **Entry Point**: [e.g., src/app/page.tsx, or src/server.ts]
- **Status**: [Active / Maintenance / Archived]

## Project Overview
[Keep this under 100 words. Auto Memory will learn detailed structure.]

Brief description of what this project does and why it exists.

Example:
> Math Tutor App is an interactive learning platform where students answer math questions,
> get instant feedback, and track progress over time. Targets elementary/middle school students
> and their teachers who use it in classroom settings.

## Architecture Overview

### Frontend
- Framework: React 18 + TypeScript
- State: React Query for server state, Zustand for UI state
- Styling: Tailwind CSS
- Testing: Vitest + React Testing Library

### Backend
- Framework: Express.js (Node.js)
- Database: PostgreSQL with Prisma ORM
- Auth: JWT + refresh tokens
- Deployment: Render (free tier)

### Key Dependencies (Version-Critical)
- `react`: 18.2+
- `next.js`: 15+
- `tailwindcss`: 3.4+
- `postgres`: 14+ (dev db: sqlite)

*Note: Context7 MCP should fetch live docs for Next.js and Tailwind when available.*

## Development Workflow

### Code Style & Conventions
- **Naming**:
  - Functions/variables: camelCase
  - Components: PascalCase
  - Constants: UPPER_SNAKE_CASE
  - Filenames: kebab-case (components/Button.tsx, utils/math-helpers.ts)
  
- **Testing**:
  - All new functions require unit tests (>80% coverage)
  - All components require React Testing Library tests
  - TDD approach: write test first, then implementation
  - Test files: `*.test.ts` or `*.test.tsx`

- **Git Commits**:
  - Format: `type(scope): description`
  - Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`
  - Examples:
    - `feat(auth): add JWT token validation`
    - `fix(api): handle null database results`
    - `test(components): add Button edge cases`
  - Keep subject under 50 characters

- **API Response Format**:
  ```typescript
  { data?: T, error?: string, status: 'success' | 'error' }
  ```

- **Database Queries**:
  - Use parameterized queries (Prisma ORM, no string concatenation)
  - Add database migration files for schema changes
  - Test migrations locally before committing

### Branch Strategy
- `main` — production-ready, protected, requires PR review
- `develop` — integration branch for next release
- `feature/DESCRIPTION` — feature branches (e.g., `feature/user-auth`)
- `fix/DESCRIPTION` — bug fix branches (e.g., `fix/null-pointer`)

### Sprint/Goals
- **Current Sprint**: [Week of MM/DD - MM/DD]
  - Goal 1: [Feature or task]
  - Goal 2: [Feature or task]
  - Blocked by: [Any external dependencies]

## Superpowers Skills for This Project

### Always Use These Skills
- **Getting Started**: New feature? Start here. Brainstorm requirements before coding.
- **TDD Skill**: Before writing ANY application code, write the test first.
- **Code Review Skill**: Before marking PRs as ready, run this skill.

### Use When Applicable
- **Refactoring Skill**: Large code changes or module restructures
- **Architecture Pattern Skill**: Designing new systems or major changes
- **Migration Safety Skill**: Database schema or API contract changes

### Disabled/Not Applicable
- N/A

## Critical Rules (DO NOT VIOLATE)

### DO
- ✅ Commit frequently (not just at end of session)
- ✅ Run tests before committing
- ✅ Use feature branches (never commit to main)
- ✅ Write descriptive commit messages
- ✅ Update docs/DECISIONS.md when making architecture choices
- ✅ Ask for help in HANDOFF.md if stuck

### DON'T
- ❌ Hardcode secrets (use .env files)
- ❌ Commit node_modules/, .env, or build artifacts
- ❌ Skip tests (all new code needs tests)
- ❌ Make unrelated changes in one PR (one feature = one PR)
- ❌ Use console.log in production code (use logging library)
- ❌ Modify .env or production configs in the codebase

## MCP Servers Enabled for This Project

### Always Enabled
- **github** — Manage PRs, issues, check CI status
- **context7** — Fetch live Next.js / Tailwind documentation at runtime

### Project-Specific (if applicable)
- **sqlite** — Query dev database (path: `./dev.db`)

### Disabled (remove if added)
- Atlassian (unreliable, high token overhead)
- Notion (not needed for this project)
- Slack (not needed for this project)

## Testing Requirements

### Unit Tests
- Framework: Vitest
- Assertion: Chai/Vitest assertions
- Coverage: ≥80% (statements, branches, functions, lines)
- Run: `npm run test`

### Component Tests
- Framework: React Testing Library
- Pattern: Test behavior, not implementation
- Run: `npm run test:ui`

### E2E Tests
- Framework: Playwright
- Pattern: Critical user flows only
- Run: `npm run test:e2e`

### Before Committing
```bash
npm run test           # All tests pass
npm run lint          # No linting errors
npm run build         # Build succeeds
```

## Common Commands

```bash
# Development
npm run dev           # Start dev server (localhost:3000)
npm run build        # Build for production
npm run start        # Run production build

# Testing
npm run test         # Run all tests
npm run test:watch   # Watch mode
npm test src/auth.test.ts  # Single file

# Code Quality
npm run lint         # ESLint checks
npm run lint:fix     # Auto-fix issues
npm run format       # Prettier formatting

# Database
npm run db:migrate   # Run Prisma migrations
npm run db:seed      # Seed dev data
npm run db:reset     # Drop and recreate db
```

## File Structure

```
my-project/
├── src/
│   ├── app/              # Next.js app directory
│   │   ├── page.tsx
│   │   └── layout.tsx
│   ├── components/       # React components (tested)
│   │   ├── Button.tsx
│   │   └── Button.test.tsx
│   ├── lib/              # Utilities and helpers
│   │   ├── db.ts
│   │   └── auth.ts
│   ├── styles/           # Global styles
│   │   └── globals.css
│   └── types/            # TypeScript types
│       └── index.ts
├── tests/
│   ├── e2e/              # End-to-end tests
│   │   └── login.spec.ts
│   └── fixtures/         # Test data
│       └── users.json
├── docs/
│   ├── DECISIONS.md      # Architecture decisions (COMMIT)
│   ├── API.md            # API documentation
│   └── ARCHITECTURE.md   # System design
├── .claude/
│   └── HANDOFF.md        # Session bridge (DO NOT COMMIT)
├── CLAUDE.md             # This file
├── .gitignore            # Includes .claude/HANDOFF.md
├── .env.example          # Environment template (no secrets)
├── package.json
├── tsconfig.json
├── next.config.js        # or vite.config.ts
└── README.md
```

## Debugging Tips

### Problem: Tests failing
```bash
npm run test:watch    # Watch mode for fast feedback
npm test -- --reporter=verbose  # See detailed output
```

### Problem: API not responding
```bash
# Check server
curl http://localhost:3000/api/health

# Check database connection
npm run db:migrate -- --dry-run

# View logs
tail -f logs/server.log
```

### Problem: Build errors
```bash
# Clean and rebuild
rm -rf .next
npm run build
```

## When to Update This File

Update CLAUDE.md when:
- Architecture changes significantly
- New permanent conventions established
- Dependencies change critically
- Team preferences shift
- Project status changes (Active → Maintenance)

**Do NOT update** for:
- One-off learnings (use Auto Memory instead)
- Temporary workarounds (document in HANDOFF.md)
- Session-specific decisions (reference docs/DECISIONS.md instead)

## Reference Documents
- See `docs/DECISIONS.md` for architecture decisions
- See `.claude/HANDOFF.md` for session context (ephemeral)
- See `README.md` for user-facing documentation

---
*Last updated: [DATE]. Reviewed by: [NAME]*
```

---

## FILE 2: .gitignore
**Save as**: `./.gitignore` in project root  
**Scope**: Keep ephemeral files out of git  
**Purpose**: Clean git history

```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js
yarn.lock
package-lock.json

# Testing
coverage/
.nyc_output/
*.lcov

# Build
dist/
build/
.next/
out/
.turbo/

# Development
.env
.env.local
.env.*.local
.env.development.local
.env.test.local
.env.production.local

# IDE & Editor
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
*.sublime-project
*.sublime-workspace
.nvim/

# OS
Thumbs.db
.Thumbs.db

# Claude Code — Session/Handoff Files (EPHEMERAL)
.claude/HANDOFF.md
.claude/reports/handoff/
docs/plans/
docs/analysis/
docs/experiments/

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Database
dev.db
dev.db-shm
dev.db-wal
*.sqlite
*.sqlite3

# Keep These Files (Permanent Documentation)
!docs/DECISIONS.md
!docs/API.md
!docs/ARCHITECTURE.md
!.env.example
```

---

## FILE 3: docs/DECISIONS.md
**Save as**: `./docs/DECISIONS.md` in project root  
**Scope**: Permanent architecture decisions, committed to git  
**Purpose**: Decision audit trail

```markdown
# Architecture Decision Log (ADL)

This document records major architectural decisions, the reasoning behind them,
and their status. Reference these when designing new features or considering refactors.

**Format**: Architecture Decision Records (ADRs) — see template below.

---

## ADR Template

```markdown
## ADR-XXX: [Decision Title]
**Date**: YYYY-MM-DD  
**Decision Maker**: [Name]  
**Status**: Proposed | Accepted ✅ | Deprecated ❌ | Superseded

**Context**:  
[Why did we need to make this decision? What problem are we solving?]

**Decision**:  
[What we decided and why.]

**Rationale**:  
- Reason 1
- Reason 2
- Reason 3

**Alternatives Considered**:  
- Alternative A: [why we rejected it]
- Alternative B: [why we rejected it]

**Consequences**:  
- Pro: [benefit of this choice]
- Con: [downside or tradeoff]

**References**:  
- [Related issue/PR]
- [External docs]
```

---

## Example ADRs (Replace with Your Project's Decisions)

## ADR-001: JWT Authentication for API, Sessions for Web UI

**Date**: 2026-05-13  
**Decision Maker**: [Your Name]  
**Status**: Accepted ✅

**Context**:  
We need authentication for both:
1. REST API (used by mobile apps, third-party services)
2. Web UI (used by browsers)

Both have different security requirements.

**Decision**:  
Use JWT tokens for API authentication, session cookies for web UI.

**Rationale**:  
- JWT is stateless (easier to scale horizontally)
- Sessions prevent token replay attacks on browsers
- Hybrid approach gives us the best of both worlds
- Avoids storing sensitive tokens in localStorage (XSS vector)

**Alternatives Considered**:  
- Pure JWT everywhere: Would require client-side token storage (XSS risk)
- Pure sessions everywhere: Would require sticky sessions (scaling complexity)
- OAuth2 + OIDC: Over-engineered for current scope; revisit in 6 months

**Consequences**:  
- Pro: Scales to multiple backend servers
- Pro: Secure session handling on browsers
- Con: Increased auth complexity (two separate flows)
- Con: Need refresh token rotation for API

---

## ADR-002: React Query for Server State Management

**Date**: 2026-05-10  
**Decision Maker**: [Your Name]  
**Status**: Accepted ✅

**Context**:  
We need to manage:
- API request caching
- Background refetching
- Optimistic updates
- Error handling

Multiple libraries available: React Query, SWR, TanStack Query.

**Decision**:  
Use React Query (now @tanstack/react-query v5).

**Rationale**:  
- Best-in-class DevTools for debugging
- Powerful cache invalidation strategies
- Team already familiar with it from Project X

**Alternatives Considered**:  
- SWR: Simpler, but fewer features
- Zustand: Client-side state only, not built for server sync
- Redux + Redux Thunk: Too much boilerplate

**Consequences**:  
- Pro: Industry standard, great docs
- Pro: Excellent DevTools
- Con: Adds bundle size (~35KB)
- Con: Steeper learning curve for newcomers

---

## ADR-003: PostgreSQL for Production, SQLite for Local Development

**Date**: 2026-05-08  
**Decision Maker**: [Your Name]  
**Status**: Accepted ✅

**Context**:  
Production database needs:
- Horizontal scaling
- Full-text search
- JSONB columns for flexible schema

Local development needs:
- Zero setup (no Docker required)
- Fast migrations
- Easy reset for testing

SQLite covers dev needs but doesn't scale to production.

**Decision**:  
PostgreSQL for production (Render/AWS RDS).  
SQLite for local development.

**Rationale**:  
- Prevents "it works on my machine" syndrome
- JSONB gives us schema flexibility without noSQL complexity
- Full-text search is built-in to Postgres
- SQLite is zero-setup for devs

**Alternatives Considered**:  
- SQLite everywhere: Would require major refactor for production
- MongoDB: JSONB achieves same flexibility with relational benefits
- Supabase: Good for MVP, but vendor lock-in concerns

**Consequences**:  
- Pro: Production-grade database
- Pro: Instant local dev setup
- Con: Devs need to understand SQL
- Con: Migrations must work on both databases

---

## ADR-004: Playwright for E2E Testing (Not Cypress)

**Date**: 2026-05-06  
**Decision Maker**: [Your Name]  
**Status**: Accepted ✅

**Context**:  
Need end-to-end testing for critical flows (login, checkout, etc.).

Options: Playwright, Cypress, Puppeteer.

**Decision**:  
Playwright for E2E testing.

**Rationale**:  
- Supports Chromium, Firefox, WebKit (multi-browser)
- Better performance than Cypress
- Accessibility tree interactions more reliable
- No plugin bloat

**Alternatives Considered**:  
- Cypress: Easier API, but WebKit support unreliable
- Puppeteer: Lower-level, requires more setup

**Consequences**:  
- Pro: True multi-browser testing
- Pro: Better performance
- Con: Steeper learning curve
- Con: Takes ~30s to start browsers

---

## ADR-005: Tailwind CSS + Headless UI

**Date**: 2026-04-30  
**Decision Maker**: [Your Name]  
**Status**: Accepted ✅

**Context**:  
Need consistent styling without heavy component library.

Tradeoff: Speed of development vs. design customization.

**Decision**:  
Tailwind CSS for utility-based styling.  
Headless UI for unstyled, accessible components.

**Rationale**:  
- Tailwind scales to large teams (consistent vocabulary)
- Headless UI gives us control without building from scratch
- Zero vendor lock-in (pure HTML/CSS/JS)

**Alternatives Considered**:  
- Material UI: Heavy, opinionated theming
- Bootstrap: Too rigid for custom designs
- CSS Modules: Less reusable, more maintenance

**Consequences**:  
- Pro: Fast development, great DX
- Pro: No component bloat
- Con: Requires disciplined class naming
- Con: Not suitable for highly custom designs

---

## Deprecated Decisions

None yet. Old decisions move here when superseded.

### ADR-000-EXAMPLE: [Deprecated Decision]
**Date**: 2026-01-01  
**Superseded By**: ADR-XXX (date)  
**Reason**: [Why we changed our mind]

---

## When to Add an ADR

Add an ADR when:
- ✅ Making a tech stack choice (database, framework, library)
- ✅ Choosing an architectural pattern
- ✅ Making a major refactoring decision
- ✅ Deciding between competing approaches

Do NOT add for:
- ❌ Small bugfixes
- ❌ Feature-specific implementation details
- ❌ One-off workarounds (document in code comments instead)

---

## How to Add a New ADR

1. Copy the ADR template above
2. Assign next number (ADR-006, etc.)
3. Fill in all sections
4. Commit to git: `git add docs/DECISIONS.md && git commit -m "doc: ADR-XXX: [decision]"`
5. Reference in code when relevant: `// See ADR-001 for auth strategy`

---

*Last updated: [DATE]. Decisions reviewed: [DATE].*
```

---

## FILE 4: README.md (User-Facing)
**Save as**: `./README.md` in project root  
**Scope**: Public documentation  
**Purpose**: Onboard users, not developers

```markdown
# [Project Name]

Brief description of what this project does.

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone repository
git clone https://github.com/yourname/project.git
cd project

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Documentation

- **Users**: See [docs/API.md](docs/API.md) for API usage
- **Developers**: See [CLAUDE.md](CLAUDE.md) for development context
- **Architecture**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Decisions**: See [docs/DECISIONS.md](docs/DECISIONS.md) for design decisions

## Testing

```bash
npm run test           # Run all tests
npm run test:watch    # Watch mode
npm run test:e2e      # E2E tests
```

## Contributing

1. Create a feature branch: `git checkout -b feature/description`
2. Make changes and write tests
3. Submit a pull request
4. See [CLAUDE.md](CLAUDE.md) for detailed contribution guidelines

## License

[Your License]
```

---

## SETUP INSTRUCTIONS

### For New Projects

```bash
# 1. Create project directory
mkdir ~/Projects/my-new-project
cd ~/Projects/my-new-project

# 2. Initialize git
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 3. Copy template files
cp ~/Templates/CLAUDE.md ./CLAUDE.md
cp ~/Templates/.gitignore ./.gitignore
mkdir -p docs
cp ~/Templates/DECISIONS.md docs/DECISIONS.md
cp ~/Templates/README.md ./README.md

# 4. Customize files (at minimum)
# Edit CLAUDE.md:
#   - Replace [Project Name]
#   - Replace [Tech Stack]
#   - Add your architecture details

# 5. Initial commit
git add .
git commit -m "chore: project template initialization"

# 6. Start development
npm init -y  # or your framework's init command
# ... add your dependencies
```

### For Existing Projects

Copy just the missing files:

```bash
# Copy CLAUDE.md if missing
cp ~/Templates/CLAUDE.md ./CLAUDE.md

# Update .gitignore to include handoff rules
echo ".claude/HANDOFF.md" >> .gitignore
echo "docs/plans/" >> .gitignore

# Add DECISIONS.md if missing
mkdir -p docs
cp ~/Templates/DECISIONS.md docs/DECISIONS.md

# Commit changes
git add .
git commit -m "chore: add Claude Code project templates"
```

---

## TIPS FOR CUSTOMIZATION

1. **CLAUDE.md**: Customize for your tech stack (React? Node? Python?)
2. **.gitignore**: Add framework-specific entries (`.next/`, `__pycache__/`, etc.)
3. **DECISIONS.md**: Replace example ADRs with your actual decisions
4. **README.md**: Add badges, screenshots, features list

---

**Version**: 1.0  
**Created**: May 2026  
**License**: MIT (share freely)
