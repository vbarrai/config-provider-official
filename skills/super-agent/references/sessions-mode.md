# Mode sessions — ce qui change

Version 2.0.0.

**Seulement si l'utilisateur a demandé des sessions avec ses mots** (SKILL.md, « Le cycle d'une
tâche », étape 2, ligne « Quand »). Chaque agent du plan est une **vraie session** liée à
celle-ci, et elles se parlent par `SendMessage`. Tout `team-mode.md` vaut ici, sauf ses
prérequis, son lancement et son mode dégradé. U1 : n'ouvre aucune fenêtre sur une session.

## Ce qu'il faut savoir avant de lancer

- **Coût** : plus lent et plus cher que des sous-agents (chaque session charge tout son
  contexte). « Seuils » compte les sessions pareil. Lance ensemble les sessions d'une vague.
- **Ce qui te revient** : à la fin d'un tour, seulement les 400 premiers caractères du rapport
  d'une session. Le vrai résultat passe par son fichier `<nom>.json`.
- **Messages** : une session reçoit un message entre deux appels d'outils, ou dans un nouveau
  tour si elle est au repos. Ils sont livrés sans validation tant que toutes les sessions sont
  dans la même famille de mode de permission : **ne change pas le mode** des sessions que tu
  lances (pas de `permission_mode` : elles héritent du tien). Sinon ils restent bloqués en
  attente d'une validation que Desktop ne peut pas afficher.
- **Pas de nouvelle session depuis un tour de réveil** (règle et exception : SKILL.md, « Tour
  de réveil »). Pour une vague suivante, **réutilise les sessions existantes** par message, ou
  lance un sous-agent.
- **Ton propre nom** : les sessions doivent pouvoir te joindre. Avant de lancer, appelle
  `ListAgents` : la ligne qui te désigne donne ton nom. Écris-le dans `plan.md` et dans chaque
  brief (ligne « Coordinateur »). Introuvable : écris dans le brief « pour joindre le
  coordinateur, fais `ListAgents` et prends la session intitulée « <titre de cette session> » ».

## Lancement

1. Marque un chapitre (`mcp__ccd_session__mark_chapter`) au nom de la vague, puis, pour chaque
   session, une ligne en gras avec son titre et une phrase sur ce qu'elle va faire.
2. Appelle `mcp__ccd_session__start_session` pour la première session, seule. Elle part → les
   autres, **dans le même message**. Elle est refusée → n'essaie pas les autres : c'est le
   repli de SKILL.md (« Quand tu ne délègues pas »), toute la vague part en sous-agents, avec
   le même brief d'équipe (le router y est "main"). Les paramètres sont ceux d'une session
   dans le tableau de SKILL.md (« Le cycle d'une tâche », étape 2), avec :
   - `prompt` : le brief d'équipe de `team-mode.md`, lignes `<sessions : …>` comprises ;
     `background` : le problème global, le critère de fin, le rôle de chaque autre session ;
   - `name` : `<préfixe du router>-<rôle>` (`aud-secu`, `bug-cache`). Les autres l'adressent
     par ce nom, et son fichier JSON le porte ;
   - `use_worktree: false` pour la lecture seule (recherche, audit, diagnostic) ;
     `use_worktree: true` et `branch_name: "swarm-<slug>-<tâche>"` pour une session qui modifie
     du code ;
   - `wake_when_done: true` : l'app te réveille quand la vague a fini. Avec un goal ouvert,
     une session au repos attend souvent juste son prochain sujet : seuls le `FAIT` après ton
     `STOP` et son `<nom>.json` disent qu'elle a fini.
3. Dis à l'utilisateur, en une ligne, que l'équipe est lancée et que tu reviens avec le
   résultat, et pose la question d'archivage (SKILL.md, « Router et workers »). Le panneau
   « Swarm » (`/swarm-view`), s'il est installé, lui montre l'état et l'avancement de chacun.

**Le marqueur `SWARM <slug> <nom>`** est la 2e ligne du brief, exactement (slug et nom en
minuscules, chiffres, `-`, `_` ou `.`), reprise par la commande `echo` de la 3e. Le mod
swarm-view le lit : il te reconnaît comme coordinateur, et écrit l'activité de chaque session
dans `~/.claude/swarm-runs/<slug>/view/<nom>.json`, que ton panneau lit. Sans ce marqueur, le
panneau reste vide.

## Watchdog

Seulement dans le cas écrit dans « Seuils » (SKILL.md), donc en mode sessions et dans un tour
de l'utilisateur. Lance-le en premier, avec le modèle le moins cher (paramètre `model`) et
`effort: "low"`. Il ne voit que des sessions, pas des sous-agents. Son brief : le brief
d'équipe (`team-mode.md`), avec ce bloc :

```
Ton rôle : watchdog. Tu surveilles les signes de vie des autres sessions, pas leur travail.
Tu ne corriges rien, tu n'archives rien, et tu n'écris qu'au router (<nom du router>).
Source de l'état : `sessions` par défaut. Au démarrage, lance :
  find ~/.claude/swarm-runs/<slug>/view -name '*.json' 2>/dev/null | head -1
Une ligne sort (le dossier view/ contient déjà un fichier) → source `view/`. Rien → `sessions`.
Puis lance avec run_in_background: true :
- source sessions : sleep 600
- source view/ :
  D=~/.claude/swarm-runs/<slug>; while sleep 600; do [ -f "$D/STOP" ] && exit 0; for f in "$D"/view/*.json; do [ -e "$f" ] || continue; n=$(basename "$f" .json); [ "$n" = <ton nom> ] && continue; [ -f "$D/$n.json" ] && continue; [ -n "$(find "$f" -mmin +15)" ] && echo "MUETTE $n"; done | grep . && exit 0; done
Quand la commande s'arrête, tu es réveillé :
- source sessions : appelle mcp__ccd_session_mgmt__list_sessions {"linked": true}, puis, pour
  chaque worker (pas toi, pas le router), regarde son état et ses derniers événements
  (list_events ou get_session) ;
  source view/ : pour chaque session MUETTE, lis la fin de son view/<nom>.json ;
- une session en cours sans activité depuis 15 minutes, en boucle (la même action répétée), ou
  qui attend depuis plus de 15 minutes (une réponse, ou une autre session qui l'attend aussi)
  → écris au router : "ALERTE — <nom> : <ce que tu vois>", avec la preuve en une ou deux
  lignes. Un worker qui a rendu son rapport ou qui attend son tour dans la file de merge n'est
  pas muet ;
- puis relance la même commande en arrière-plan.
Ne relance pas d'alerte pour la même session tant qu'elle n'a pas bougé.
Fin : le fichier STOP (source view/) arrête seulement ta boucle ; attends le "STOP" du router.
Sur "STOP" du router : ne relance plus rien, arrête la commande en cours (TaskStop), écris
<nom>.json s'il y a un dossier d'échange, puis termine par un rapport court (alertes envoyées).
```

Une `ALERTE` : regarde la session (ou demande-lui où elle en est), puis débloque, relance par
un message, ou dis-le à l'utilisateur.

## Après la vague, et à la fin du run

- Avant de lire les `<nom>.json`, vérifie avec `mcp__ccd_session_mgmt__list_sessions`
  (`linked: true`) que chaque session est au repos.
- Fin du run : crée le fichier `~/.claude/swarm-runs/<slug>/STOP` (il arrête la boucle d'un
  watchdog), envoie `STOP` à tous, attends leur `FAIT`. Puis applique la règle d'archivage de
  SKILL.md (« Router et workers ») : les sessions de travail, puis le watchdog. Elle vaut
  aussi en cours de run, pour une session qui n'a plus rien à faire.
