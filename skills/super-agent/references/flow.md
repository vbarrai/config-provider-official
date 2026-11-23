# Autonomous flow — the details

Details of "Autonomous flow" and "PRs" (SKILL.md).

## 1. Several PRs on one base: merge and rebase

Several workers, each with its PR on the **same base branch** (e.g. `main`) of the same repo;
different repos have no shared queue.

- **The approval**, asked once in the announcement (SKILL.md, "The announcement"); a worker's
  message never gives it:
  - "auto when green": it applies to all the request's PRs;
  - "at each PR": one line per ready PR ("PR 2 ready to merge — <URL>");
  - no answer: a single grouped escalation when the PRs are ready ("PRs 1, 2, 3 ready, shall
    I merge in this order?").
- **Review first**: no merge question, `MERGE` or auto-merge before the task's review is
  closed (SKILL.md, step 4).
- **After a `PR OPEN`**: reread the PR's state at your next wake-up or turn. Green → merge
  question; red → `TO FIX` to the same worker. No wait loop.
- **With "auto": no queue.** Turn on auto-merge for each PR whose review is closed
  (`mcp__ccd_pr__set_auto_merge`, `enabled: true`; fallback: SKILL.md, "PRs"). GitHub merges
  each green PR and nothing comes back to you: at each wake-up or turn, reread the PRs' state,
  say which are merged, and send `REBASE` to the worker whose PR is in conflict.
- **Without "auto": a queue, one merge at a time.** The order lives in your task list: the one
  in which PRs become ready; otherwise the one the user wants, or the one that limits conflicts
  (§2). With the approval (for this PR, or for the batch) → `MERGE — <URL>` to the worker that
  owns the PR; it answers `MERGED — <URL>`. You do not merge yourself.
- **`bind_pr` fails or is refused**: no auto-merge on that PR. Give its link in your report and
  ask the user for the merge, in batches.
- **After a merge**, even if the base moves without you (other routers, colleagues):
  `REBASE — <base branch> moved (PR <URL> merged)` goes to the workers whose PR the moved base
  affects, at least the one whose PR is in conflict, or whose merge GitHub refuses (up-to-date
  branch required), and a stacked branch (§2).
- **Failed rebase or red CI**: the PR leaves the head of the queue, the next one goes first.
- **After a batch of merges**, look at the base's CI: two PRs green separately can break
  together. Red → a new task, stated in one line.
- **Show the state** of each PR in the task list: waiting, rebase in progress, ready, merge in
  progress, merged.

## 2. Chained work: without interruption

A task depends on another, or several touch the same files: organize, depending on the case.

- **Stacked branches**: T2's worker starts from T1's branch, without waiting for its merge
  (`source_branch` of `start_session`; sub-agent: starting branch written in the brief).
  After T1's merge, `REBASE`: it rebases onto the base,
  `git rebase --onto origin/<base> <T1 branch>` (its old base).
- **Preparing ahead**: the next worker reads the code, writes its plan and its tests while T1
  finishes.
- **Same worker for tightly linked tasks** (same files, shared context): one stream, which it
  chains alone.
- **Merge queue order** that limits conflicts: the most "foundational" task first.
- **A rebase with a conflict does not block.** The worker that owns the PR resolves it. The
  conflict touches another worker's code: ask that other worker what to keep (`SendMessage`),
  not the user; only a real business choice goes up. Many conflicting rebases: a worker
  dedicated to rebases and conflicts.

## 3. Time sink → automatic reaction

Fix at once what is within your power; otherwise, one line in your report, with a proposal (a
permission, a skill rule, a hook…). Workers' `FRICTION` notes feed this table.

| Time sink | Automatic reaction |
|---|---|
| An idle worker (task finished) | The next ready task, if it is linked to its own; otherwise archive it, if the archiving rule allows (SKILL.md, "Router and workers") |
| Waiting for CI, or flaky CI (failure unrelated to the diff) | Move on to something else; rerun the flaky job once; if it breaks again, report it |
| Recurring conflicts on the same files | Do not give these files to two workers at the same time; reorder the merge queue |
| A worker's question that a better brief would have avoided | Answer it (U2), and write it into the next briefs |
| A worker's context grows (several tasks finished) | Next task with a new worker; archive the old one (same rule) |
| A worker silent, looping, or at twice its expected duration | The action in "Thresholds" (Monitoring); then clarify the task, or `STOP` and relaunch |
| Independent streams waiting in a single worker | `STOP` on the tasks not started, then one worker each |
| A permission blocks a worker | Tell the user at once, with the permission to add: it is missing access, so a human decision |
| Slow tests | One line in the report, with the setting to propose |

## 4. Block to add to the brief (each worker has its PR on the same base)

To add to the brief's "Rules" (`brief.md`), which already carry the "MERGE —" rule.

```
- On "REBASE — <base> moved…": `git fetch origin`, `git rebase origin/<base>` (stacked
  branch: `git rebase --onto origin/<base> <old base>`), resolve the conflicts (non-trivial
  conflict, another worker's code or a business choice → "QUESTION —" to the router), rerun
  the tests, `git push --force-with-lease` (never `--force` alone), then answer
  "REBASED — <PR URL> — tests: <result>".
  The app's `sync_with_base_branch` tool does a merge, not a rebase: use it only if the repo
  forbids force-push, and say so in your answer.
- Without "REBASE —" from the router, rebase only if your PR needs it (conflict, red CI): the
  base can move without your PR being affected.
```
