---
name: collaborai-pr
description: Take the changes already in the working tree, run the project's checks (lint, typecheck, tests, build), fix anything that fails, then move the work onto a fresh branch and open a pull request. Use this whenever the user says they're done with a change and wants to "ship it", "open a PR", "make a PR", "put this up for review", "push this", "create a branch and PR", or otherwise wrap up local work into a reviewable PR — even if they don't name every step. Works in any repo by auto-detecting the check commands.
---

# Ship changes as a PR

The job: turn an already-modified working tree into a green, reviewable pull request. The user has done the coding; you handle the mechanical-but-careful part — proving the change is sound, then packaging it cleanly. The reason this is a skill and not a one-liner is that each step has a failure mode that wrecks the result if rushed: running the wrong checks gives false confidence, a vague branch name and PR body make review slow, and pushing without the user's nod is hard to undo.

Work through the stages in order. Don't skip the verification gate — a PR that fails CI wastes the reviewer's time and yours.

## 0. Confirm there's something to ship

Run `git status --short` and `git diff --stat` (plus `git diff --stat --staged`). If the tree is clean, stop and tell the user there's nothing to ship rather than inventing an empty PR.

Note the current branch. If you're already on a feature branch (not `main`/`master`), the user may want to keep committing there rather than branch again — ask which they prefer. If you're on the default branch, you'll create a new branch in stage 3.

## 1. Detect the project's checks

There's no universal check command, so infer them from what the repo actually uses. Look, in this rough priority order, and run what you find:

- **`package.json` scripts** — run the ones that exist among `lint`, `typecheck` (or `type-check`), `test`, `build`. Use the repo's package manager (presence of `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, else npm).
- **Makefile / Justfile** — targets like `make check`, `make lint`, `make test`.
- **Language-native tooling** when there's no script wrapper: `cargo check && cargo test` (Rust), `go vet ./... && go test ./...` (Go), `ruff check && pytest` or `pre-commit run --all-files` (Python).
- **A CI workflow** (`.github/workflows/*.yml`) is the source of truth for what "green" means — skim it and mirror the same commands locally when nothing else is obvious.

If you genuinely can't find any checks (e.g. a config or docs repo with no test setup), say so plainly and treat validation as "n/a" rather than fabricating a command. Don't invent a `test` script that isn't there.

State which checks you're about to run before running them, so the user can correct you if you've guessed wrong.

## 2. Run checks, and fix what fails

Run the detected checks. If everything passes, go to stage 3.

If something fails, your default is to fix it — that's what the user wants from this skill, not a bug report handed back to them. But fix with judgment:

- Read the actual failure. A lint rule, a type error, and a broken test each call for a different fix.
- Make the **smallest correct** change that addresses the real cause. Don't suppress a lint rule, delete an assertion, or `// @ts-ignore` your way to green — that defeats the entire point of running checks.
- Re-run the checks after fixing. Loop until green, but cap it: after **3 rounds** still failing, stop and bring the user the remaining failure with what you tried and why it's resisting. Some failures (a genuinely flaky test, an environment issue, a design decision) aren't yours to silently paper over.

Any fixes you make become part of the change that ships — they'll be committed alongside the original work in stage 3.

## 3. Create the branch

Read the full diff (`git diff` and any staged diff) so the branch name and PR describe what actually changed, not a guess.

Derive a branch name from the change: `<type>/<short-kebab-summary>`, where type is `feat`, `fix`, `chore`, `docs`, `refactor`, or `test` based on the nature of the diff. Keep the summary 2-4 words. Examples:

- New user-login API endpoint → `feat/add-login-endpoint`
- Fixing an off-by-one in pagination → `fix/pagination-off-by-one`
- Updating the install section of the README → `docs/update-install-steps`

Create and switch to it with `git switch -c <branch>` (this carries your uncommitted changes onto the new branch — they aren't lost).

## 4. Commit

Stage and commit the change with a message that follows the repo's existing convention — check `git log --oneline -10` first and match it. If the repo uses Conventional Commits, follow suit; if it uses plain imperative subjects, do that. A good default subject is imperative and ≤72 chars, with a body only if the change needs explaining.

If your environment specifies a commit trailer (many setups require a `Co-Authored-By:` line attributing the assisting model), append it; otherwise just commit with the message above.

## 5. Confirm, then push and open the PR

Pushing and opening a PR are outward-facing and awkward to walk back, so **show the user the plan and get a yes before you push**: the branch name, the commit subject, and the PR title + a 1-2 sentence body summary. This is the one place to pause — everything before it is local and reversible.

On confirmation:

1. Push with upstream tracking: `git push -u origin <branch>`.
2. Open the PR with `gh pr create`. Write a real title and body — don't leave them empty. The body should be a short, skimmable summary of *what changed and why*, structured as:

```
## What
- bullet points of the concrete changes

## Why
- one or two lines of motivation / context

## Checks
- which checks were run and their result (or "n/a — no checks in this repo")
```

Pass the body via `--body` (use a heredoc or `--body-file` for multi-line). If the repo has a PR template, fill it instead of overriding it.

3. Report the PR URL that `gh` returns so the user can click straight through.

## Guardrails

- **Never** force-push, rewrite shared history, or push directly to `main`/`master`.
- If `git push` fails on auth, surface the error and suggest the user check `gh auth status` rather than retrying blindly.
- Don't commit obvious secrets (`.env` files, key material) even if they're in the working tree — flag them to the user instead.
- If checks can't be made green within the cap, default to opening a **draft** PR (`gh pr create --draft`) only if the user explicitly accepts shipping red; otherwise stop at stage 2.
