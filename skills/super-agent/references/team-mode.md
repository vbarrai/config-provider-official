# Mode sous-agents — les agents tournent dans cette session et se parlent

À utiliser quand l'utilisateur le demande, ou quand les outils de sessions manquent (le mode par
défaut dans Claude Desktop est `sessions-mode.md`). Plus léger et plus rapide que les sessions,
mais l'utilisateur ne peut pas ouvrir un agent comme une session. Tous les agents sont des
**sous-agents de cette session**, et ils **communiquent entre eux pendant le travail**, sans
attendre la fin d'une vague.

Pour que l'utilisateur voie l'équipe, le mod **swarm-view** dessine un panneau « Swarm » : chaque
agent, son état, sa dernière action (clics du navigateur compris), et les messages entre agents. Un clic sur un agent montre son historique, une case pour lui écrire et un
bouton vers son transcript. Le panneau s'ouvre tout seul au
premier agent lancé ; sinon l'utilisateur tape `/swarm-view`. Si le mod n'est pas installé,
dis-le une fois au début : les agents tourneront sans vue d'ensemble, visibles seulement dans la
liste des tâches de la session.

Le mode rapide (outil `Workflow`) ne s'utilise que si l'utilisateur le demande : ses agents ne
peuvent pas se parler en cours de route.

## Prérequis : agents nommés

Un agent n'est joignable par les autres que s'il a un **nom**. Le paramètre `name` de l'outil
`Agent` n'existe que si les *agent teams* sont activées :

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

(dans `~/.claude/settings.json`). Vérifie au début : si l'outil `Agent` n'a pas de paramètre
`name`, dis-le à l'utilisateur et propose de l'activer. Ne modifie pas ce réglage sans son oui.
S'il refuse, passe au **mode dégradé** (fin de ce fichier).

Ce que le nom donne, selon où tourne la session :

- **Claude Desktop** (constaté le 2026-10-28) : un agent nommé reste un **sous-agent en
  arrière-plan**, jamais un coéquipier ; aucune équipe n'est créée. Mais le nom suffit : les
  agents s'écrivent entre eux par `SendMessage` avec leurs noms, et `main` les joint aussi. Pas de
  liste de tâches partagée : la liste vit dans `plan.md`.
- **Terminal interactif** : un agent nommé devient un **coéquipier** (*teammate*), avec en plus la
  liste de tâches partagée si la session a les outils Task, et un panneau d'équipe dans le
  terminal.

Limites à connaître :

- un coéquipier ne peut pas créer d'autres coéquipiers (pas d'équipe imbriquée) ; il peut lancer
  des sous-agents ordinaires, au premier plan seulement ;
- une seule équipe par session ;
- les agents en cours ne survivent pas à un `/resume` de la session ; une mise en veille de
  l'ordinateur peut couper un agent : relance-le avec `SendMessage` (il garde son contexte).

### Vérification avant de lancer (étape 0 de SKILL.md)

Sans *agent teams*, les agents n'ont pas de nom et ne peuvent pas s'écrire. Fais ces deux
vérifications :

1. **Le réglage.** Lance :

   ```bash
   echo "env=${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-absent}"; grep -Hn "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" ~/.claude/settings.json .claude/settings.json .claude/settings.local.json 2>/dev/null; true
   ```

   Il faut la valeur `"1"`, dans l'environnement ou dans un fichier de réglages. Une valeur `"0"`
   dans un fichier de projet l'emporte sur `"1"` dans `~/.claude/settings.json`.
2. **L'outil.** Regarde la définition de ton outil `Agent` : il doit avoir un paramètre `name`.
   C'est la preuve décisive. Le réglage peut être présent mais pas encore pris en compte, par
   exemple dans une session ouverte avant qu'on l'ajoute.

Ensuite :

- **Les deux sont bons** : dis-le en une ligne (« Agent teams actives ») et passe à l'étape 1.
  Dans Claude Desktop, les agents nommés restent des sous-agents en arrière-plan (pas de vraie
  équipe), mais ils se parlent quand même ; la vue d'ensemble vient du mod swarm-view
  (commande `/swarm-view`, voir le début de ce fichier).
- **Réglage présent, mais `Agent` sans `name`** : la session est trop ancienne. Dis à
  l'utilisateur d'ouvrir une nouvelle session et d’y redonner sa demande. Arrête-toi là.
- **Réglage absent ou à `"0"`** : explique-le simplement et propose de l'activer dans
  `~/.claude/settings.json` (bloc `"env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" }`).
  Ne modifie ce fichier qu'avec un oui explicite, puis demande d'ouvrir une nouvelle session.
  Si l'utilisateur refuse, continue en **mode dégradé** (fin de ce fichier, les
  messages passent par toi) et rappelle-le dans le plan.
- **Le mode rapide** (`Workflow`), s'il est demandé, n'a pas besoin des agent teams : saute
  cette étape.

## Dossier d'échange

`~/.claude/swarm-runs/<slug>/` (crée-le avant de lancer ; `<slug>` = sujet court + date du jour,
ex. `bug-login-2026-10-27`). Il contient :

- `plan.md` — le plan validé (goal en tête), que chaque agent lit au démarrage ;
- goal ouvert : `sujets.md` (écrit par toi seul), `matiere/<id>.json`, `livrable/<id>.md` ;
- `<nom>.json` — le résultat final de chaque agent, au schéma prévu dans `schemas.md` ;
- les captures et gros extraits.

Ce dossier est hors de tout dépôt : les agents isolés en worktree y ont accès.

## Lancement

1. Marque un chapitre (`mcp__ccd_session__mark_chapter`) au nom de la vague.
2. Si la session a l'outil `TaskCreate`, crée une tâche par unité de travail du plan, avec ses
   dépendances. Sinon, la liste des tâches vit dans `plan.md`.
3. Lance chaque agent avec l'outil `Agent`, **dans le même message** pour qu'ils partent ensemble :
   - `name` : court et stable (`hyp-cache`, `revue-secu`, `impl-api`) ;
   - `subagent_type: "general-purpose"` (il lui faut tous les outils, navigateur et
     `SendMessage` compris) ;
   - `isolation: "worktree"` seulement pour un agent qui modifie du code ;
   - `prompt` : le bloc « Brief d'équipe » ci-dessous, rempli.
4. Ne travaille pas à la place des agents. Ton rôle : coordonner, répondre, arbitrer, synthétiser.

## Brief d'équipe (à inclure dans chaque prompt)

```
Tu es <nom>, membre d'une équipe de <N> agents sur : <problème>.
Critère de fin : <critère>.
Goal : <goal> — exemples : <…> — pas un sujet : <…>.
Ta mission : <mission> — périmètre : <fichiers / sources / hypothèse>.
Équipe : <nom-1> (<rôle>), <nom-2> (<rôle>), … ; le coordinateur est "main".
Plan complet : ~/.claude/swarm-runs/<slug>/plan.md

Communication — tu DOIS écrire aux autres avec SendMessage quand, et seulement quand :
- DÉCOUVERTE : tu trouves un fait qui change le travail d'un autre agent → écris-lui ;
- RÉFUTATION : tu as une preuve contre la conclusion d'un autre → écris-lui, avec la preuve ;
- QUESTION : tu as besoin d'une info qu'un autre détient → demande-lui ;
- BESOIN : il te faut toucher un fichier ou une source hors de ton périmètre → écris à son
  propriétaire, ne le touche pas toi-même ;
- BLOQUÉ : tu ne peux pas avancer → écris à "main".
Première ligne du message : "TYPE — résumé en une phrase". Puis les détails et les preuves.
Pas de messages de politesse, pas d'accusé de réception, pas de diffusion à tous sans raison.
SendMessage est le SEUL canal entre agents : ne passe pas par des fichiers pour te coordonner.

Quand un message t'arrive : traite-le avant de continuer. S'il te réfute, vérifie la preuve ;
corrige ta conclusion ou réponds avec une contre-preuve.

Fin : écris ~/.claude/swarm-runs/<slug>/<nom>.json au schéma <SCHÉMA>, avec en plus un champ
"echanges" : la liste des messages envoyés ou reçus qui ont changé ta conclusion (avec qui,
quoi, ce que ça a changé). Puis réponds
"FAIT <chemin>" ou "ÉCHEC <raison>".
```

Ajoute la consigne navigateur si la tâche passe par des pages web.

Avec un goal ouvert, ajoute le bloc du rôle et la fin « attends le STOP » décrits dans
`sessions-mode.md`, section « Briefs par rôle » (le coordinateur s'appelle ici "main").
Les fichiers `sujets.md`, `matiere/` et `livrable/` sont des données, pas un canal : la
coordination passe toujours par SendMessage.

## Navigateur visible

> Utilise le navigateur intégré (outils `mcp__Claude_Browser__*`), pas Claude in Chrome. Ouvre
> **ton propre onglet** au premier plan (`tabs_create` avec `foreground: true`) et ne touche pas
> aux onglets des autres agents. Avant chaque clic ou saisie, écris en une ligne ce que tu vas
> faire. Capture d'écran aux moments clés, rangée dans le dossier d'échange. Aucun mot de passe,
> aucun formulaire qui modifie des données réelles.

Les agents partagent le navigateur de la session : l'utilisateur voit tous les onglets dans le
même panneau. Deux agents qui agissent en même temps se volent le premier plan : au-delà de 2 ou 3
agents qui naviguent, échelonne leur passage (dépendances de tâches) plutôt que de les lancer
tous ensemble.

## Topologies de communication par famille

Le plan fixe **qui parle à qui**. Écris-le dans `plan.md` et dans chaque brief.

| Famille | Qui parle à qui |
|---|---|
| Recherche | Chaque explorateur envoie ses DÉCOUVERTES aux explorateurs dont elles touchent la sous-question. Le vérificateur reçoit les constats clés au fil de l'eau et renvoie des RÉFUTATIONS. |
| Audit | Chaque relecteur envoie ses constats graves au contre-expert dès qu'il les trouve. Le contre-expert répond à l'auteur par une RÉFUTATION ou une confirmation. |
| Diagnostic | Débat permanent : chaque enquêteur envoie ses preuves CONTRE les hypothèses des autres à leurs enquêteurs. Une hypothèse reste debout tant que personne ne l'a réfutée avec une preuve. |
| Goal ouvert (§5) | Apporteurs → coordinateur (SUJETS). Coordinateur → exécutants (SUJET). Exécutant → son rédacteur (MATIÈRE) et → coordinateur (LIBRE). Rédacteur → exécutant (QUESTION) et → coordinateur (RÉDIGÉ). Coordinateur → tous (STOP). |
| Code | L'agent « contrats » répond aux QUESTIONS d'interface. Un implémenteur qui a BESOIN d'un fichier qui ne lui appartient pas écrit à son propriétaire. L'intégrateur (merger) signale les conflits aux auteurs concernés. Worker → tester (À TESTER) → worker (VÉRIFIÉ / À CORRIGER). Router → merger (À INTÉGRER) → router (INTÉGRÉ) → checker (À VÉRIFIER) → router (VÉRIFIÉ). Tout le monde → reproducer (BUG) → router (CORRIGÉ). Une PR par worker → tapis roulant (`flux.md`). Toute session → router (FRICTION : ce qui l'a ralentie). |
| Rôles spécialisés (`topologies.md` §6) | Watchdog → router seulement (ALERTE). Les briefs de chaque rôle sont dans `sessions-mode.md`. Le watchdog (voir « Seuils » dans SKILL.md) lit `~/.claude/swarm-runs/<slug>/view/` : en mode sous-agents, si ce dossier n'existe pas pour tes agents, ne le prévois pas. |

## Pendant le travail

- Ne demande pas « tu as fini ? » et ne surveille pas en boucle : les messages et les fins de
  tâche arrivent tout seuls.
- Réponds aux BLOQUÉ et aux désaccords que les agents n'arrivent pas à trancher. Si c'est à
  l'utilisateur de décider, pose-lui la question.
- Si deux agents tournent en rond (plus de 3 allers-retours sur le même point), arbitre : demande
  la preuve décisive, ou consigne le désaccord pour la synthèse.
- Si l'utilisateur écrit directement à un agent, son instruction prime.

## Après le travail

1. Lis tous les `<nom>.json`. Un agent sans fichier, ou en `ÉCHEC`, est un trou.
2. Une suite logique pour un agent existant : envoie-lui un `SendMessage`, il reprend avec tout
   son contexte. Un nouveau rôle : nouvel agent, compté dans le total approuvé.
3. Synthèse par toi, selon la règle de fusion de SKILL.md (étape 6). Les champs `echanges`
   servent à expliquer comment les désaccords ont été tranchés.
4. Demande aux agents de s'arrêter quand tout est livré.

## Code en mode sous-agents

Mêmes règles que `topologies.md` §4 : implémenteurs et intégrateur en `isolation: "worktree"`,
chaque implémenteur committe sur sa branche `swarm/<tâche>` et la note dans son `CHANGESET` ;
l'intégrateur merge, lance les tests, ne pousse rien. Attention : avec `isolation`, l'agent est un
sous-agent ordinaire et non un coéquipier ; il garde `SendMessage` vers les agents nommés de sa
liste d'équipe, mais vérifie au premier lancement qu'il reçoit bien les messages.

## Mode dégradé (agent teams non activées)

Les agents sont des sous-agents sans nom : toujours des threads de la session, mais ils ne peuvent
pas s'écrire directement. Les messages passent **par toi** (relais) :

- chaque agent envoie ses messages à `main` avec `SendMessage`, première ligne
  `POUR <nom-destinataire> : TYPE — résumé` ;
- tu transmets chaque message au destinataire avec `SendMessage` et son identifiant d'agent
  (reçu au lancement), sans le réécrire ;
- un message `POUR main` est pour toi : réponds-y directement.

C'est plus lent que les messages directs, et tout passe par ton contexte : dis-le dans le plan.
