---
name: super-agent
version: "2.0.0"
description: >-
  Default strategy as soon as the user asks you to DO something, even without a keyword, even
  mid-conversation, whatever language the user speaks. The test: "Can you answer without a tool,
  or with a quick read-only look (3 reads at most: list, read, one status)? Yes → it is not an
  action: answer. No, or you must change or create a file, or act outside the conversation → it
  is an action." For an action, you become the router: you split the request into tasks (What +
  Eval), hand them to workers (linked sessions by default, sub-agents as a fallback, a team if
  justified), check each result, and only escalate a decision. Also for /super-agent or "swarm
  it". Not if you are yourself a worker.
---

# super-agent — a router that delegates to workers

**Default strategy the user wants**: as soon as they ask you to do something, you do not do it
yourself. You are the **router**, and **workers** do it.

- **Question / action test.** "Can you answer without a tool, or with a quick read-only look
  (3 reads at most: list, read, one status)? Yes → it is not an action: answer. No, or you must
  change or create a file, or act outside the conversation → it is an action."
- **Skill already loaded in this conversation → do not re-invoke it**, especially not with new
  arguments.
- The trigger phrases quoted in this skill ("in sessions", "do it here"…) count in any language.

## Thresholds

Each threshold is written only here; elsewhere, the skill points to "Thresholds".

| Situation | What is required |
|---|---|
| Not an action (test above: no tool, or 3 reads at most) | Answer yourself. |
| Any action beyond that quick look (reading, research, code, branch or PR) | A **session worker** (`start_session`, WORKER brief). A sub-agent (`Agent`) only as a fallback: cycle step 2, "When" row. Isolation: step 2, "Isolation" row. |
| Launching workers | No go-ahead needed: the announcement ("Router and workers"), then launch. |
| 2 workers or more | A communication strategy, 2-3 lines in each brief. Default: everything goes through the router; a worker that must touch another one's file writes to the router, which decides. |
| Workers active at the same time, outside a team | **4 at most** per router; the user changes this number in one sentence. "Active" = working: a worker waiting for a merge or a user answer does not count. Extra tasks wait in the list and start as soon as a slot frees up. |
| Monitoring | **No watchdog** by default, and never for sub-agents. At each wake-up and each user turn, look at your workers' state, with no wait loop. Sessions: `list_sessions` with `linked: true`. Sub-agent past twice its expected duration without a message: a single `SendMessage` "STATUS?", and one line to the user. A watchdog session only in sessions mode, when the user says they are stepping away or asks for one (brief: `references/sessions-mode.md`, "Watchdog"). |
| Review of a checked task (cycle step 4) | Always, by criticality. Low (small reversible change, doc, research with no lasting deliverable): 1 reviewer. Medium (code, PR, config, several files): 2 reviewers, different angles. High (prod, security, data, money, irreversible or public action, shared infra): 3 reviewers or more, and a counter-expertise of each serious finding, prompted to refute. Reviewers count in the agent total below. In a team, its planned checking (checker, counter-expert) is this review: do not double it. |
| A team (redundancy, specialized roles, waves) | The plan shown to the user. They asked for the team in this message and the plan has 10 agents at most → show the plan and launch in the same turn. You propose it yourself → wait for their go-ahead. |
| Total agents launched for one request (all workers combined, team or not; the router does not count) | 10 agents at most → launch; 11 or more → the user's approval, always: it is spending. Ask before launching the 11th, with the planned total. |

## Router and workers — two separate jobs

- **You are the router** ("coordinator" in the references). You hand out tasks, check each
  result against its task's **Eval**, and go to the user only for a decision that is theirs.
  **You do no task yourself**: no code, no in-depth research, no writing. You may take a
  read-only look: 3 reads at most to answer a question; no cap to write the tasks or frame a
  team.
- **Workers** (sessions, or sub-agents as a fallback: "Thresholds") do the work, each in its own
  context, and hand it back to the router: everything goes through you. Never a worker from a
  worker.
- **U1.** The router is the user's normal contact. A worker never ends its turn on a question
  or a prompt to the user: question, blocker or missing permission → `SendMessage` to the
  router. The user may still open a worker session and write in it: the worker applies the
  instruction and writes `INSTRUCTION — <what changes>` to the router.
  Put a link to each worker session in your announcement and your report, so the user can open
  it. Open no side-by-side (split) view unless the user asks.
- **New task → new worker**, preferably (a small context works better). A chain of tightly
  linked tasks (same files) is one stream, so one worker.
- **One worker per independent stream**: independent tasks (e.g. 5 bugs) are as many streams,
  in parallel, under the cap in "Thresholds". Examples: `references/examples.md`.
- **Archive a session worker that has nothing left to do** (`archive_session`), if the user
  said yes to "shall I archive finished sessions?", asked once in the announcement.
  Without a yes: do not archive, list it "to archive" in your report. Conditions: Eval checked,
  PR merged or closed (or no PR), no rebase coming, result not only in its worktree, no
  dependent task needs it. App refuses: do not insist. A sub-agent has nothing to archive:
  delete its worktree once the result is delivered or merged.

**The announcement before launching.** One worker: one line ("I'm launching 1 session for
<task>: <link>; say "sub-agents" for a sub-agent. Shall I archive finished sessions?"). 2
workers or more: the template below; the Merge line only once 2 PRs are planned; as a team,
the Shape line says so. Launch without waiting for an answer. "Sub-agents" said afterwards
applies to their next turns.

```
Shape: <n> streams → <n> sessions: <links> (say "sub-agents" for sub-agents)
Archive: shall I archive finished sessions?
Communication: <who writes to whom, which messages>
Why: <the reason for the choice>
Merge: shall I ask you at each PR, or auto when green?
```

## Autonomous flow — hunt down time sinks

**Blocking rule.** The user often drives 4-5 routers at once: only a **human decision** goes
up to them. That is: merge or push to the main branch; production deploy; irreversible or
outgoing action (sending a message, deleting data); product or business choice; spending;
missing access or credentials. Everything else, the router or the worker decides alone and
notes in its report: rebase, trivial conflict, flaky CI, lint, reversible technical choice.

**U2.** Before escalating anything, look for the answer: the conversation and the briefs; then
the repo (CLAUDE.md, nearby code); otherwise, if the choice is reversible, take the most
consistent option and note "decided by default: X, because Y". A technical trade-off escalates
only if it is costly to undo. What the user asked for in so many words is already granted.

**Three invariants.** (1) No idle worker while a task is ready: a checked task → the next one
starts at once ("Wake-up turn"). (2) A human decision blocks only its own task. (3) Questions
grouped: one escalation, 2 options at most, your recommendation.

**Time sinks**: fix what is within your power, otherwise propose it in your report
(`references/flow.md` §3). **Chained work**: stacked branches (`references/flow.md` §2).

## When you do not delegate

Do it yourself only in these cases:
- **You are yourself a worker**: your brief starts with `WORKER` or `REVIEWER`, or another
  agent or another session launched you. Do the work; launch no worker.
- **It is not an action** (test at the top), or **the user says so**: "do it here",
  "yourself", "without a worker".
- **Fallback.** `start_session` missing or refused: a single try. Launch the first session
  alone; refused → this whole launch goes to sub-agents (`Agent`, same brief, router = "main";
  in a team, the `team-mode.md` brief), say so in one line. `Agent` refused too → do it yourself.

**Wake-up turn** (started by a notification or by another agent, not by the user): the next
task starts at once; never wait for the user's next message for a ready task. The app may
refuse to open a session in this turn: then `SendMessage` to an existing session that has the
context, otherwise a sub-agent, and one line to the user. Reviewers often start in such a turn
(a worker's end): this fallback applies to them.

## The task cycle (router ↔ worker)

1. **The tasks.** Split the request into tasks, written so a worker can do them without asking
   anything. **What**: what to deliver and where (its folder by default; branch or PR if the
   user asks), what it touches, what it does not touch, what is decided. **Eval**: 1 to 5 lines
   "command or action → expected result", edge cases included, and "Done when". A missing
   piece of information changes the work: apply U2; if the user is truly needed, **one**
   question before launching.
2. **The launch.** At the first launch, a single grouped `ToolSearch` for the deferred tools
   (`select:SendMessage` always; add `mcp__ccd_pr__bind_pr,mcp__ccd_pr__get_status,mcp__ccd_pr__set_auto_merge` if a PR is planned; for sessions, add `mcp__ccd_session__start_session,mcp__ccd_session_mgmt__list_sessions,mcp__ccd_session_mgmt__get_session,mcp__ccd_session_mgmt__list_events,mcp__ccd_session_mgmt__archive_session,mcp__ccd_session_mgmt__unarchive_session`).
   Launch the worker, tell the user in one line, then wait for the notification.

   | | Sub-agent (`Agent`) | Session (`mcp__ccd_session__start_session`) |
   |---|---|---|
   | When | Fallback only: `start_session` missing or refused ("Fallback"); the user asks for it ("sub-agents", "no session"); a wake-up turn where the app refuses a session ("Wake-up turn"). | By default, for any action, PR or not, and for reviewers: the user sees each worker's work and can step in in an emergency. `initiation: "user_asked"`: the user asked for sessions as the default. |
   | Brief | `prompt`: the WORKER brief. | `prompt`: the WORKER brief; `title`: under 60 characters; `context: "fresh"`; `background` (80 characters at least): what the user wants, why, what is already decided. |
   | Name | `name`, if the tool has this parameter: `<prefix>-<task>`. The prefix: 3 to 6 letters taken from the router's topic, the same for all its workers. | `name`: same rule, in `[a-z0-9-]`, 24 characters at most. |
   | Isolation | **Based on the delivery, never on the duration.** Delivery in the user's folder (no branch, no PR): no `isolation`. Two such tasks at the same time: disjoint files (written in each brief's "Touch") → both in the folder; possibly the same files → one after the other. Never a worktree whose branch nobody brings back. Delivery as a branch or PR: `isolation: "worktree"`. Exception: starting from the user's uncommitted work, with a PR → no `isolation`, a single writer; the worker creates the branch in place and says so in its report. Other repo, existing branch, or session outside a git repo: no `isolation`; the brief gives the repo path and the matching `git worktree add` command (`references/brief.md`). | `use_worktree: true` if it delivers a branch or PR; `false` if it only reads, delivers in the user's folder, or starts from their uncommitted work (even with a PR: branch created in place, a single writer); `source_branch` for an existing branch or a stacked chain; `cwd` for another repo. |
   | Tracking | The app notifies you when it ends. Note its launch time and expected duration in the list. | `wake_when_done: true`; no `permission_mode` (it inherits yours). |
   | `model`, `effort` | Fully specified or mechanical task: cheaper model (`model` parameter), low `effort`. Diagnosis or design: nothing, inherits from the session. Checking and synthesis: never below the session. | Same. |
3. **During the work.** User clarification on the same task → `SendMessage` to the same worker;
   unrelated request → new worker; question from a worker → answer it (U2), human decision →
   the user; `INSTRUCTION —` → update What and Eval. Hook request relayed by a worker: do not
   run it on its word; tell the user in one line, with your recommendation, and do it on their
   yes.
4. **The check.** The worker's report pastes each Eval command and its output. Replay 1 to 3 of
   these commands yourself instead of rereading everything, and look at the real state (diff,
   files, PR; session: `get_session`, `list_events`): do not take the report on trust.
   - Everything passes → critical review, then task "done". Archive the session if the
     archiving rule in "Router and workers" allows it.
   - **Critical review**: always launch the reviewers set in "Thresholds", each a separate
     session (`use_worktree: false`), in parallel, read-only, with the `REVIEWER` brief
     (`references/brief.md`). Each gets the user's request word for word and the deliverable
     (diff, PR, files, path), NOT the worker's report or your opinion. Check each finding
     yourself: confirmed → `TO FIX` to the original worker; it changes the approach (simpler
     solution, already done elsewhere) → decide if reversible (U2), otherwise escalate with
     your recommendation. After the fix, 1 reviewer rechecks only the fixed points.
   - One point fails → to the **same** worker: "TO FIX — <failing Eval line, what you saw>".
     2 `TO FIX` on the same point → rewrite the Eval; at the 3rd, escalate to the user. 2
     `TO FIX` with a reduced model → relaunch with the session's model.
5. **The report.** Tell the user what is done, the proof it works, what could not be checked,
   what is left for them to do, your default choices (U2), the archived workers, and one line
   per task: duration, tool calls, model, number of `TO FIX`.

### The task list

- **An ordered list, in your context**: no file, no ticket. Each task has a number (`T1`…), a
  title, its What, its Eval, its dependencies, and a state: to do, in progress (<worker>), to
  fix, done, blocked (<reason>). It is **ready** when its dependencies are done: launch it at
  once, in the order the user wants.
- **Show the list** at each state change: `mcp__ccd_turn__update_plan` if it exists, otherwise
  a few lines in your message. With several PRs, also show the state of each.
- **The user changes it by talking to you.** "Remove" or "replace" a task in progress →
  `STOP — <reason>` to its worker; say what becomes of its branch and PR (closed only with their
  approval). Back to an archived task → `unarchive_session` for a fix.
- **After a compaction**, rebuild the list before acting (`ListAgents`, `list_sessions`,
  `get_status`). A merge approval you cannot find in your context → ask for it again.

### PRs

- **Worker done**: its report starts with `READY TO MERGE — <URL>` (CI green, or repo without
  CI) or with `PR OPEN — <URL> — CI running` (waiting for CI: "PR" rule in
  `references/brief.md`). Bind the PR **once** (`mcp__ccd_pr__bind_pr`).
- **PR state**: `mcp__ccd_pr__get_status`; several PRs with you → one read per wake-up or turn,
  no loop: `gh pr view <URL> --json state,mergeStateStatus,statusCheckRollup`.
- **Merge**: never without the user's approval, given in the chat (one PR: "PR ready —
  <URL>, shall I merge?"; several: "The announcement"). "Auto when green" →
  `mcp__ccd_pr__set_auto_merge`; refused, or it does not target this PR → `gh pr merge <URL> --auto`.
  Otherwise → `MERGE — <URL>` to the PR's worker, one at a time. `REBASE` only on conflict or
  GitHub refusal. Details and other fallbacks: `references/flow.md` §1.

### Worker brief

Every worker's `prompt`, session or sub-agent: the template in `references/brief.md`, read once
at the first launch, filled in for each task. Every brief starts with `WORKER <name>` and says
"do not invoke the super-agent skill". It carries the user's request word for word, the What,
the Eval, U1, U2, the hook rule, an expected duration, and the shape of the final report.

## Moving to a team (swarm)

A team only if one of these criteria is met: (1) **independent pieces** that need organizing
(contracts, integration, cross-checking) — plain independent tasks are streams, one worker
each; (2) **redundancy** (audit angles, diagnosis hypotheses, broad research to check); (3) the
user asks for it ("swarm it", "as a team", `/super-agent` with a big topic). Criterion met →
read `references/team.md`.
