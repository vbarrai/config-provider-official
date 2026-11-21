#!/usr/bin/env python3
"""Hook super-agent-reminder : rappelle d'utiliser le skill super-agent.

Branché sur SessionStart (voir hooks.json) : un rappel par session.

Claude Code : sort {"hookSpecificOutput": {"hookEventName": <événement reçu>,
"additionalContext": ...}}. Le nom de l'événement est lu dans l'entrée (`hook_event_name`),
pas écrit en dur : le même script marche s'il est branché sur UserPromptSubmit. Un nom absent
ou inconnu → "SessionStart".
Cursor (sessionStart) : sort {"additional_context": ...}.

Au démarrage, il n'y a pas de prompt : le hook ne peut pas savoir si la session est un
worker. C'est le texte du rappel qui donne l'exception « tu es toi-même un worker ».
Le test question / action est recopié mot pour mot de SKILL.md : modifie-les ensemble.
Le hook ne plante jamais : stdin absent, vide ou invalide → format Claude Code.
"""
import json
import sys

# Événements Claude Code dont la sortie accepte `additionalContext`.
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
    "Rappel (hook super-agent) : à chaque message de l'utilisateur, fais ce test. "
    "« Peux-tu répondre sans outil, avec ce que tu sais déjà et ce qui est déjà dans la "
    "conversation ? Oui → ce n'est pas une action : réponds. Non → c'est une action. » "
    "Pour une action, invoque le skill `super-agent` avant toute autre action. "
    "Skill déjà chargé dans cette conversation → ne le réinvoque pas. "
    "Exceptions : tu es toi-même un worker (ton brief commence par `WORKER`, ou un autre "
    "agent ou une autre session t'a lancé) ; l'utilisateur dit « fais-le ici » ou "
    "« sans worker »."
)

event = data.get("hook_event_name")
if event == "sessionStart":
    # Cursor
    out = {"additional_context": reminder}
else:
    # Claude Code (et défaut)
    out = {
        "hookSpecificOutput": {
            "hookEventName": event if event in CLAUDE_CODE_EVENTS else "SessionStart",
            "additionalContext": reminder,
        }
    }
print(json.dumps(out, ensure_ascii=False))
