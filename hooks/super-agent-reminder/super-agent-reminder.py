#!/usr/bin/env python3
"""SessionStart hook: au début de chaque session, rappelle d'utiliser le skill super-agent.

Claude Code (SessionStart) : sort {"hookSpecificOutput": {"hookEventName": "SessionStart",
"additionalContext": ...}}.
Cursor (sessionStart) : sort {"additional_context": ...}.

Au démarrage, il n'y a pas de prompt : le hook ne peut pas savoir si la session est un
worker. C'est le texte du rappel qui donne l'exception « tu es toi-même un worker ».
Le hook ne plante jamais : stdin absent, vide ou invalide → format Claude Code.
"""
import json
import sys

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
    "Rappel (hook super-agent) : pendant cette session, dès qu'un message demande de FAIRE "
    "quelque chose (coder, corriger, chercher, analyser, rédiger, ouvrir une PR...), invoque "
    "le skill `super-agent` avant toute autre action. Exceptions : simple question, "
    "explication ou conversation ; tu es toi-même un worker (lancé par une autre session) ; "
    "l'utilisateur dit « fais-le ici » ou « sans worker »."
)

if data.get("hook_event_name") == "sessionStart":
    # Cursor
    out = {"additional_context": reminder}
else:
    # Claude Code (et défaut)
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": reminder,
        }
    }
print(json.dumps(out, ensure_ascii=False))
