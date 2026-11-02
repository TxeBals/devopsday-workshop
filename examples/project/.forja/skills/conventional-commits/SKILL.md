---
name: conventional-commits
description: How to write commit messages in this repository. Load it before running git commit.
---
# Conventional Commits in this repo

Format: `<type>(<scope>): <summary in the imperative, lowercase, no trailing period>`

Types: feat, fix, refactor, test, docs, chore. Scope = module (`amounts`, `dates`, `invoice`).

Steps:
1. `git status` and `git diff` to see what changes.
2. One commit per logical change. Never mix a refactor and a fix.
3. Optional body: the why, not the what. Reference the issue: `Refs #12`.

Example: `fix(amounts): round to cents half-up using Decimal`
