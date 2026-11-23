# The team (swarm) — steps 0 to 7

Read when a criterion in "Moving to a team" (SKILL.md) is met. Thresholds, U1, U2, blocking
rule and fallback: SKILL.md; they also apply to the team.

## Step 0 — Choose the mode and check its prerequisites (always, first)

- **Sub-agents mode** (default): it needs *agent teams* (named agents): do the
  "Check before launching" of `team-mode.md`.
- **Sessions mode**: only if the user asked for sessions in their own words (SKILL.md,
  "The task cycle", step 2, "When" row). `mcp__ccd_session__start_session` missing (after
  `ToolSearch`) or refused: sub-agents mode (SKILL.md fallback).
- **Fast mode** (`Workflow` tool): only if the user asks for it. Load the `workflow-authoring`
  skill before writing any script.

State the chosen mode in one line.

## Step 1 — Framing (you alone, no agent)

In 6 lines at most:

1. **The problem**, with its scope (files, repos, sources, period…).
2. **The end criterion**: how do we know it is finished and right?
3. **The constraints**: what must not be touched, the available access, the deadlines.
4. **The goal** (always): one sentence that says what the work is for, 2 to 3 example topics
   that fulfill it (the user's when they give some), and what is not one. It filters
   everything else: it goes at the top of `plan.md` and of each brief.

Take an **inline look** if the split depends on it: you need to know the items to share out.
No 3-read cap, but in-depth research goes to a sub-agent.

A missing piece of information changes the split: **one** precise question. Otherwise, move on.

## Step 2 — Classification and relevance test

Put the problem in **one** family (or a sequence, e.g. diagnosis then code):

| Family | Signal |
|---|---|
| Research / analysis | Broad question, multiple sources, need for a sourced synthesis |
| Audit / review | A fixed object (code, PR, data model) to examine from several angles |
| Diagnosis / debug | A symptom, an unknown cause, several plausible hypotheses |
| Code implementation | Build or change code in several pieces |

Is the goal **open** or **closed**?

- **open**: the deliverable is a collection that can grow (question doc, FAQ, test cases,
  audit points). Add the `topologies.md` §5 pattern (topic finders);
- **closed**: a single expected answer (a bug, a decision). No finders, unless a list of
  topics to find (hypotheses, angles) really helps.

**Relevance test.** Drop the team, and say in one line that workers per stream are enough, if:

- the problem fits in a handful of tool calls;
- the sub-tasks cannot be separated (each step depends on the previous one, or several code
  pieces change the same files);
- the expected gain does not justify a cost of 5 to 15× a session.

## Step 3 — Designing the plan

Open `topologies.md` at the family's section and build the plan:

- **Tasks**: self-contained units, written as **What** and **Eval** (SKILL.md, "The task
  cycle", step 1): you accept or send back the result against that Eval. For code, each
  task's files (a file belongs to a single task only).
- **Roles**: the workers, and the specialized roles whose need the plan writes down
  (`topologies.md` §6).
- **Model and effort per role**: the `model` / `effort` row in SKILL.md (cycle step 2):
  `effort: 'low'` for mechanical steps, higher than the session only for hard judges and
  checkers.
- **Dependencies**: which tasks wait for which others. Hierarchy is done in waves, never by
  agents that create others.
- **Redundancy**: for each task, 1 or K copies, each with a **different angle** (instruction,
  objective, search method, model): K identical copies have correlated errors.
- **Checking**: who checks what, and how (sources, reproduction, tests, refutation).
- **Topic finders** (open goal): 1 to 2, and a **topic budget** (maximum number of accepted
  topics): the number of agents does not bound it.
- **Writers**: possible, not required. The deliverable is a long text with a single style
  (doc, minutes, report) and there are 3 executors or more: 1 writer for 2 to 3 executors,
  who then hand in raw material (`MATERIAL` schema) and do not write. Otherwise, each
  executor writes its part.
- **Synthesis**: always an agent, never you (with writers: the lead writer `writer-1`),
  following the merge rule (step 6). Short deliverable: a sub-agent is enough.
- **Deliverable**: a single format, set now (markdown report, branch + diff, comparison table,
  answer in the chat), the one that best serves the end criterion.

**Count the agents**: all of them (sessions, sub-agents or `agent()` calls), all waves
combined, roles, redundant copies, watchdog and synthesis included; you do not count. That
total is what the approval threshold in "Thresholds" compares. A number depends on the results
(e.g. one checker per finding): give a range and take its upper bound.

## Step 4 — Show the plan, then launch or wait

Present the plan in this format:

```
Goal: <one sentence> — examples: <2 to 3 topics> — not a topic: <…>
Family: <family> — pattern: <pattern> (+ open goal, if open)
Mode: sub-agents (in this session) | sessions (linked native sessions) | fast (Workflow)
Communication: <who writes to whom, and for what>
Roles: router (me) — <n> workers — <merger, checker, tester, reproducer, watchdog: those kept, with each one's need> | no specialized role
Deliverable: <format>
Waves:
  1. <name> — <n> agents — <what they do> (redundancy: <rule>)
  2. ...
Checking: <n> agents — <method>
Topic finders: <n> agents — <each one's angle> | none — <reason>
Topic budget: <N> topics at most (also stop after 2 "nothing new", or on your stop)
Writers: <n> agents — <format of a sheet / of the minutes> | none — <reason>
Synthesis: 1 agent
Total: <N> agents (upper bound) — estimated cost ≈ <N×1 to N×1.5>× a normal session
Out of scope: <what will not be covered>
```

Launch or wait: apply "Thresholds" (SKILL.md).

- **You propose the team yourself**: "Shall I launch?".
- **The Total exceeds the approval threshold**: ask for it with `AskUserQuestion`, naming **the
  exact number of agents**, what the extra agents bring, and a **lighter variant** under that
  threshold.
- Never launch more agents than the approved number; if more are needed along the way, stop
  and ask again. The plan changes: recompute the total and reapply the rule.

## Step 5 — Execution

Sub-agents mode: `team-mode.md`. Sessions mode: `team-mode.md`, then `sessions-mode.md`.
Fast mode, below: the agents do not talk to each other during the work (open goal:
`topologies.md` §5).

1. Start from the skeleton in `workflow-templates.md` (API reminders at the top) and adapt it
   to the plan shown. Outputs go through the schemas in `schemas.md`: they are the
   **communication contract** between agents.
2. **One workflow per wave** when a wave depends on the previous one's content (e.g.
   diagnosis: investigation → you read → cross-refutation): read the results and adjust the
   next wave, within the plan's total. Plan fixed in advance: a single workflow.
3. Large artifacts (logs, big diffs, excerpts) go **outside the repo**, in the session's
   scratchpad (sub-folder `swarm-<slug>/`): an agent in a worktree does not see a folder
   created in the main checkout. Pass the run identifier and the paths via `args`.
4. An agent returns `null` (failure or abandon): do not improvise its result. Flag the gap in
   the synthesis, or relaunch that single agent if the plan's total allows.

## Step 6 — Checking and merging

Merge rule, applied by the synthesis agent and checked by you:

- **Agreement** between independent sources or copies: finding kept, high confidence.
- **Disagreement**: both positions are laid out with their evidence. Never decided silently,
  and only if evidence (test, reproduction, primary source) settles it.
- **Isolated** unchecked finding: kept, marked "unconfirmed".
- **Finding refuted** by the check: dropped, mentioned in an appendix.
- **Gaps**: what was not covered (failed agent, unreachable source, sampling) is listed. No
  silent truncation.

Before delivering, reread the synthesis against the raw outputs (with writers: a few sheets
against their `material/<id>.json`): that is where information gets lost the most.

## Step 7 — Delivery

In the format set at step 3, with at the top:

- the answer to the end criterion (yes / no / partly, and why);
- the main findings, with their confidence level;
- the unresolved disagreements and the gaps;
- open goal: the number of topics proposed, accepted, processed, and the reason for stopping
  (budget, nothing new, user's stop);
- the real cost (number of agents launched) and the exchange folder
  (`~/.claude/swarm-runs/<slug>/`) or, in fast mode, the workflow's `journal.jsonl`.

For code: the integration branch (`swarm-<slug>-integration`), the test results (commands and
output), and the remaining work branches. Do not merge into the main branch and push nothing
without explicit approval.
