---
name: collaborai-review
description: Review a pull request like a careful human reviewer — read the diff, leave specific inline comments where something is wrong or unclear, and approve only when it's genuinely sound. Use whenever the user asks to "review this PR", "look over PR #123", "do a code review", "check this PR and approve if it's good", "leave review comments", or hands you a PR number or URL to evaluate. Works on any GitHub repo via the `gh` CLI.
---

# Review a pull request

The job: act as a thoughtful reviewer on a GitHub PR — understand what it's trying to do, find the problems that actually matter, say so where they live in the code, and give a verdict (approve, or request changes) that you'd stand behind. The value of a review comes from judgment, not volume: a reviewer who nitpicks formatting while missing a logic bug is worse than useless, and one who rubber-stamps everything teaches the author nothing.

This skill *posts* a real review to GitHub — comments and an approve/request-changes verdict are visible to the author and the team. That's outward-facing, so the final stage confirms with the user before anything is posted.

## 0. Identify the PR and pull its context

Get the PR reference from the user (a number like `#123`, a URL, or "the current branch's PR"). Then gather what you need to review it well — don't review a diff in a vacuum:

```bash
gh pr view <ref> --json number,title,body,author,baseRefName,headRefName,state,isDraft,reviewDecision
gh pr diff <ref>
gh pr view <ref> --comments        # existing discussion, so you don't repeat points
gh pr checks <ref>                  # CI status — failing checks are a real finding
```

Read the PR's description to learn the *intent*. A diff tells you what changed; the description (and linked issue) tells you what it was supposed to do. Reviewing without intent is how you flag deliberate decisions as bugs.

If the PR is a draft, point that out — the author may not want a formal verdict yet; ask whether they still want a review.

## 1. Understand before you judge

Read the diff in full before forming opinions. For anything non-trivial, open the surrounding files (not just the diff hunks) so you understand the code the change touches — a line can look fine in isolation and be wrong in context. Build a mental model of: what problem this solves, how it solves it, and what could go wrong.

## 2. Find what actually matters

Look for issues in roughly this priority — spend your attention where the cost of a miss is highest:

1. **Correctness** — logic errors, off-by-ones, wrong conditionals, unhandled error/null cases, race conditions, broken edge cases. These are why review exists.
2. **Security & data safety** — injection, missing authz checks, leaked secrets, unsafe deserialization, destructive operations without guards.
3. **Tests** — does new behavior have coverage? Do existing tests still make sense? A correctness-critical change with no test is a finding.
4. **API / contract changes** — breaking changes, backward-incompatible signatures, changes that ripple beyond the diff.
5. **Clarity & maintainability** — genuinely confusing code, misleading names, dead code. Raise these sparingly and only when they'd slow a future reader.

Deliberately *don't* flag: pure style/formatting a linter owns, personal preference rewrites, or speculative "you could also" ideas that aren't problems. Every low-value comment dilutes the ones that matter and wears down the author.

For each finding, decide its weight honestly: **blocking** (must fix before merge), **non-blocking suggestion** (worth doing, author's call), or **question** (you're not sure — ask rather than assert). Mislabeling a nitpick as blocking erodes trust in your reviews.

## 3. Draft the review

Assemble two things:

- **Inline comments** — anchored to the specific file + line, each explaining *what's wrong and why*, and ideally what to do instead. Concrete beats vague: "this throws if `items` is empty — guard with a length check or default" is useful; "handle edge cases" is not.
- **A summary** — a few sentences: what the PR does, your overall read, and the headline issues if any. This is what the author reads first.

Then pick the verdict, and be honest about it:

- **Approve** — only when you'd be comfortable with this merging as-is. Minor non-blocking suggestions are compatible with approval; unresolved blocking issues are not.
- **Request changes** — when there's at least one blocking issue. Make the path to approval clear so the author knows exactly what unblocks it.
- **Comment (no verdict)** — when you have feedback but the call isn't yours to make, or you're genuinely unsure.

If you found nothing wrong, say so plainly and approve — manufacturing concerns to look diligent is its own failure.

## 4. Confirm, then post

Show the user the full review before posting — the summary, every inline comment, and the intended verdict — because a posted review notifies the author and an approval is a real sign-off. Let them adjust or veto. This is the gate; everything before it was read-only.

On confirmation, post with `gh`:

```bash
# Inline comments + verdict in one review. Build the body, then:
gh pr review <ref> --approve --body "<summary>"
# or
gh pr review <ref> --request-changes --body "<summary>"
# or
gh pr review <ref> --comment --body "<summary>"
```

For line-anchored inline comments, `gh pr review` alone can't attach them to specific lines — use the GitHub API for a review with a `comments` array (each with `path`, `line`, `body`) so feedback lands on the exact code:

```bash
gh api repos/{owner}/{repo}/pulls/<number>/reviews -X POST \
  -f event=REQUEST_CHANGES -f body="<summary>" \
  -F 'comments[][path]=src/foo.ts' -F 'comments[][line]=42' -F 'comments[][body]=...'
```

If wiring up per-line comments via the API is impractical for a given case, fall back to putting the specific findings (with `path:line` references) in the review body — clarity of feedback matters more than the delivery mechanism.

Report back the review URL `gh` returns.

## Guardrails

- Don't approve your own PRs silently to move things along, and don't approve a PR with failing CI without flagging the failures — a green verdict over red checks is misleading.
- Never post a review without the user's confirmation in stage 4; a review is a notification and a verdict you can't quietly retract.
- If you can't actually assess the change (missing context, unfamiliar domain, diff too large to reason about), say so and scope your review to what you *can* judge rather than bluffing a verdict.
- Be candid but never hostile. Critique the code, explain the reasoning, assume the author is competent and acting in good faith.
