#!/usr/bin/env python3
"""UserPromptSubmit hook: rappelle d'utiliser le skill super-agent à chaque message.

Ne dit rien pour les briefs de worker (commençant par WORKER ou SWARM),
pour éviter qu'un worker se prenne pour un router.
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

prompt = (data.get("prompt") or "").lstrip()
if prompt.upper().startswith(("WORKER", "SWARM")):
    sys.exit(0)

reminder = (
    "Rappel (hook super-agent) : si ce message demande de FAIRE quelque chose "
    "(coder, corriger, chercher, analyser, rédiger, ouvrir une PR...), invoque le skill "
    "`super-agent` avant toute autre action. Exceptions : simple question, explication "
    "ou conversation ; tu es toi-même un worker (lancé par une autre session) ; "
    "l'utilisateur dit « fais-le ici » ou « sans worker »."
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": reminder,
    }
}, ensure_ascii=False))
