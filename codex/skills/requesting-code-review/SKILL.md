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
