#!/usr/bin/env python3
"""super-agent-reminder hook: reminds the agent to use the super-agent skill.

Wired to SessionStart (see hooks.json): one reminder per session.

Claude Code: outputs {"hookSpecificOutput": {"hookEventName": <event received>,
"additionalContext": ...}}. The event name is read from the input (`hook_event_name`),
not hard-coded: wired to UserPromptSubmit, the script outputs valid JSON, but the reminder
then goes out with every message, WORKER briefs included (no filter). Missing or unknown
name -> "SessionStart".
Cursor (sessionStart): outputs {"additional_context": ...}.

At startup there is no prompt: the hook cannot know whether the session is a worker. The
reminder text gives the "you are yourself a worker" exception.
The question / action test is copied word for word from SKILL.md: change them together.
The hook never crashes: missing, empty or invalid stdin -> Claude Code format.
"""
import json
import sys

# Claude Code events whose output accepts `additionalContext`.
CLAUDE_CODE_EVENTS = ("SessionStart", "UserPromptSubmit")

data = {}
try:
    if not sys.stdin.isatty():
        raw = sys.stdin.read()
        if raw.strip():
            data = json.loads(raw)
except Exception:
    data = {}
if not isinstance(data, dict):
    data = {}

reminder = (
    "Reminder (super-agent hook): at each user message, run this test. "
    "\"Can you answer without a tool, or with a quick read-only look (3 reads at most: list, "
    "read, one status)? Yes → it is not an action: answer. No, or you must change or "
    "create a file, or act outside the conversation → it is an action.\" "
    "For an action, invoke the `super-agent` skill before any other action. "
    "Skill already loaded in this conversation → do not re-invoke it. "
    "Exceptions: you are yourself a worker (your brief starts with `WORKER` or `REVIEWER`, or another "
    "agent or another session launched you); the user says \"do it here\", \"yourself\" "
    "or \"without a worker\", in any language."
)

event = data.get("hook_event_name")
if event == "sessionStart":
    # Cursor
    out = {"additional_context": reminder}
else:
    # Claude Code (and default)
    out = {
        "hookSpecificOutput": {
            "hookEventName": event if event in CLAUDE_CODE_EVENTS else "SessionStart",
            "additionalContext": reminder,
        }
    }
# Pure ASCII output (\uXXXX escapes): the hook does not crash if the output is not UTF-8.
print(json.dumps(out))
