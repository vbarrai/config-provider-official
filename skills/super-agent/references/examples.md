# Examples of macro topics

Rules and thresholds: `SKILL.md`.

| Topic | Shape | Goes up to the human |
|---|---|---|
| 1. A typo in the README title | 1 session, cheaper model, low `effort`, `use_worktree: false`: it writes in the user's folder. | Nothing: the router replays one command (`git diff --stat`) and says so. |
| 2. 5 independent bugs, one PR per bug | 5 streams, launched up to the cap in "Thresholds": sessions in worktrees, 5 PRs, no watchdog. Merges: `flow.md` §1. | The merge question, once; a product choice (`QUESTION`). |
| 3. A chained field: DB migration → API → UI | A simple field over 3 layers: a single worker, a single PR. Each layer is a real project: 3 chained workers (`flow.md` §2), the contract (field name and type) in all 3 briefs. | The merge approval; deploying the migration to production. |
| 4. A rename that touches the same files everywhere | One stream: 1 worker goes through models, services and tests. An ambiguous name with no stakes: it picks and notes it (U2). | The merge; a rename visible to clients (public API): product choice. |
| 5. The same change in 8 repos | 8 streams, up to the cap in "Thresholds", a common template (steps, commands, Eval) in each brief, cheaper model. Each worker in its repo (sub-agent: repo path in the brief; session: `cwd`). A common pitfall found by a worker goes into the next briefs, and to running workers via `SendMessage`. | The merge approval; a repo that cannot follow without a behavior change. |
| 6. A security audit "as a team", before a prod release | The team is requested: plan shown and launched in the same turn. Audit pattern (`topologies.md` §2), sessions mode: 3 reviewers, 1 checker (counter-expert), 1 synthesis agent, so 5 agents. | Whether to block the prod release. |
| 7. A production incident with an unknown cause | The router proposes the team: it waits for the go-ahead. Diagnosis pattern (`topologies.md` §3), sessions mode: 3 investigators, 1 reproducer (written need: confirm the cause), 1 synthesis session (short deliverable), so 5 agents. | The go-ahead; any action in production. |
| 8. A report comparing 4 tools | No team if each part fits on one page and no finding needs cross-checking: 4 sessions that each write their part. Otherwise, research pattern (`topologies.md` §1): 4 explorers, 1 checker, 1 synthesis agent that writes the report, so 6 agents. Writers only if the report is long and must have a single style. | The final choice of tool (business decision). |
