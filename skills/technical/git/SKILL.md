---
name: git
description: Use Git safely and write Conventional Commits.
version: 0.1.0
platforms: [linux, macos, windows]
---

# Git

Use when preparing commits or performing Git operations in a repository.

## Conventional Commits

- Every commit message must follow `type(scope): description`, with an optional scope.
- Use `feat` for a new feature, `fix` for a bug fix, and `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, or `chore` when they describe the change more accurately.
- Write a concise, imperative description in English. Describe the change, not the activity of making a commit.
- Mark breaking changes with `!` before the colon or a `BREAKING CHANGE: ` footer explaining the incompatible change and required migration.
- Keep each commit focused on one coherent change. Split unrelated changes rather than hiding them behind a broad message.

Examples of commit messages:

```text
feat(auth): add password reset
fix(parser): handle empty input
docs: clarify installation steps
feat(api)!: require authentication for exports
```

## Basic Practices

- Inspect the current branch, working tree, and relevant diff before changing Git state. Preserve unrelated work and existing staged changes.
- Stage only files or hunks belonging to the intended commit. Review the complete staged diff before committing; never include secrets, credentials, or unrelated generated files.
- Run relevant checks before committing. Report failed or skipped checks rather than claiming validation succeeded.
- Do not commit or push unless explicitly requested. Before pushing, verify the remote and destination branch; never assume a remote name.
- Do not discard local changes, delete branches, rewrite published history, or force-push without explicit authorization for that action. Prefer reversible operations; when an authorized force-push is necessary, use `--force-with-lease` instead of `--force`.
- When resolving conflicts, understand both sides and preserve the intended behavior. If the correct resolution is unclear, ask rather than choosing a side blindly.
- After an operation, verify the resulting status and report what changed, any commit created, and whether anything was pushed.
