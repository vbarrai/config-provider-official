## PR descriptions: section order

Every pull request body you write or update (whatever the skill or method, and even when the
PR template or the skill's default body orders things differently) uses this order:

1. `What Does It Do?`: always first, as a plain `## What Does It Do?` heading, **not** in a
   collapsible block, so it is the first thing a reader sees.
2. `Context`: collapsible.
3. `Prompt`: collapsible (see "include my prompts" below).
4. `Agent proof of test`: collapsible (see "include proof of testing" below).
5. `Human test plan`: collapsible. This is the template's or skill's `Test Plan` section,
   renamed; keep its checklist content.

Any other section from the PR template goes after these, collapsible. Rename sections exactly
as above (`Test Plan` → `Human test plan`, `Proof of testing` → `Agent proof of test`).

## PR descriptions: one-sentence summary first

In every pull request body you write or update (whatever the skill or method), the very first
line under `## What Does It Do?` is one simple sentence that sums up the whole PR: the problem
and the solution (e.g. "Les stats de campagne étaient fausses à cause d'un fuseau horaire mal
géré ; on les calcule maintenant en UTC."). Plain words, no jargon, no bullet. Details come
after it.

## PR descriptions: collapsible sections

For readability, every section of a pull request body is collapsible, **except
`What Does It Do?`**, which stays a plain heading at the top. This applies to `Context`,
`Prompt`, `Agent proof of test`, `Human test plan`, the PR template's other sections, the
skill's default sections, and any other.

- Each collapsible section is a `<details>` block whose `<summary>` holds the section title in
  bold. Never use a `## Heading` for these sections.
- Keep a blank line after `</summary>` and before `</details>`, or GitHub will not render the
  Markdown inside (lists, code blocks, images).
- Sections are collapsed by default (no `open` attribute).
- Besides `What Does It Do?`, only two things stay outside the blocks: the Linear link line,
  if any, and the final attribution line (`🤖 Generated with …`), which are single lines, not
  sections.

Shape of a section:

````markdown
<details>
<summary><b>Agent proof of test</b></summary>

`GET /api/campaigns/123/stats` → `200`

```json
{ "impressions": 48210, "clicks": 312, "ctr": 0.0065 }
```

</details>
````

## PR descriptions: include my prompts

Whenever you open or update a pull request through the `branch-commit-pr` or
`branch-commit-pr-ticket` skills (any variant: unprefixed, `tech:`, `fast-`, …), put a
collapsible `Prompt` section in the PR body, right after `Context` (see "section order"
above):

- A single short prompt: quote it verbatim as a blockquote (`> ...`).
- Several prompts, or long ones: give a concise chronological summary as bullets
  (one bullet per request, keeping my wording and intent, dropping the noise).
- Never include secrets, tokens, credentials or personal data; redact them.
- Leave out the skill invocation itself (e.g. `/branch-commit-pr`); only what I asked for.

Every section other than `What Does It Do?` is collapsible, as described above.

## PR descriptions: include proof of testing

Every pull request you open or update (whatever the skill or method) must prove that the
changes work, in a collapsible `Agent proof of test` section of the PR body, right after
`Prompt` (see "section order" above):

- Prove it **end to end**, on the real thing. Running the automated test suite or the
  linter is not proof: it adds little value. Mention them in one line at most, never as the
  main evidence.
- Exercise the change for real (run the app, call the API, run the query, run the script on
  real or realistic data) and show what actually came out.
- Actually run what you show before opening the PR; never claim a test you did not run.
- UI or visual changes: attach screenshots (before/after when relevant) of the real app.
  Upload them with gh's native flag: `gh pr create/edit/comment --attach './shot.png#Alt
  text'` (repeatable; gh ≥ 2.99). Never commit screenshots to the repo, never use
  third-party image hosts or cookie-based upload extensions.
- Logic, scripts, APIs, data: paste real copies of the data: the API request and its actual
  response, the SQL query and its actual result rows, the script's actual output, trimmed to
  what matters.
- If something could not be tested, say so explicitly and explain why, instead of
  omitting it.
- Redact secrets, tokens, credentials and personal data from screenshots and outputs.
