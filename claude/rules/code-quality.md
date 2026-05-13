# Code Quality Rules

## Test Coverage Thresholds
- Statements: 80%
- Branches: 75%
- Functions: 80%
- Lines: 80%

## Pre-Commit Checks
- No `console.log` in production code (use a logger)
- No hardcoded secrets or tokens
- No dead imports
- All tests pass locally before committing

## Code Style
- Parameterized queries only (no string concatenation in SQL)
- Descriptive variable names over clever abbreviations
- Functions do one thing
