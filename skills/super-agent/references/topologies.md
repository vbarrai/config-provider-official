# Catalogue des topologies

Version 2.0.0.

Combine les patrons en séquence si le problème l'exige (ex. diagnostic → code) : les agents de
toutes les séquences comptent dans le total. Les nombres d'agents valent pour un problème
moyen.

## 1. Recherche / analyse — « carte puis fusion »

1. **Exploration** (3 à 6 agents) : une sous-question par agent ; disjointes, elles couvrent
   ensemble la question. Chaque agent rend des `FINDING` sourcés.
2. **Vérification** (1 à 3 agents) : sur les constats qui portent la conclusion, un
   vérificateur relit la source primaire et rend un `VERDICT`.
3. **Synthèse** (1 agent) : règle de fusion de `equipe.md`, étape 6.

**Redondance** : par diversité de méthode, pas par duplication. Sous-question critique : deux
agents aux angles différents (ex. sources académiques vs retours terrain). Option « critique
de complétude » : un agent final cherche ce qui manque (source non lue, angle non exploré) ;
ce qu'il trouve devient une vague de plus si le total du plan le permet.

**Vérification** : une affirmation est confirmée si sa source primaire la soutient vraiment.
Écarte celles dont la seule source est une reprise d'une autre.

**Livrable par défaut** : rapport markdown sourcé, ou tableau de comparaison.

**Piège** : des sous-questions qui se recouvrent donnent des doublons qui ressemblent à une
confirmation indépendante. Dédoublonne avant de compter les accords.

## 2. Audit / revue — « angles multiples puis contre-expertise »

1. **Revue par angle** (3 à 5 agents) : un angle par agent (ex. correction, sécurité,
   performance, cohérence avec l'existant, couverture de tests). Objet volumineux : croise
   angle × partition, en surveillant le total. Chaque agent rend des `FINDING` avec une
   localisation précise (`fichier:ligne`).
2. **Dédoublonnage** (code, pas d'agent) : même localisation + même défaut = un seul constat.
3. **Contre-expertise** (1 agent par constat grave, borne haute à prévoir) : un vérificateur
   chargé de **réfuter**, avec un angle distinct de celui qui a trouvé (ex. « est-ce que le
   contexte appelant l'empêche ? »). Constat retenu s'il n'est pas réfuté. Les constats
   mineurs passent sans contre-expertise, marqués « non confirmé ».
4. **Synthèse** (1 agent) : classement par gravité.

**Livrable par défaut** : rapport de constats classés, avec localisation et scénario d'échec.

**Piège** : un vérificateur prompté pour confirmer confirme. Prompte toujours pour réfuter,
avec « réfuté par défaut si incertain ».

## 3. Diagnostic / debug — « hypothèses concurrentes »

0. **Repérage** (toi, en lecture seule : `equipe.md`, étape 1) : le symptôme, les logs, la
   chronologie, le périmètre. Liste 3 à 5 hypothèses réellement distinctes.
1. **Enquête** (1 agent par hypothèse) : il cherche des preuves **pour et contre** son
   hypothèse, et une expérience qui la départagerait. Rend un `HYPOTHESIS`.
2. **Réfutation croisée** (1 agent par hypothèse encore debout) : chacun reçoit toutes les
   conclusions de la vague 1 et tente de réfuter une hypothèse **autre que la sienne
   d'origine**. C'est une barrière : en mode rapide, un second workflow, après avoir lu les
   résultats de la vague 1.
3. **Synthèse** (1 agent) : hypothèse survivante, preuves, expérience de confirmation proposée.

**Redondance** : le désaccord organisé. Des hypothèses qui se ressemblent rendent le patron
inutile : reformule-les avant de lancer.

**Vérification** : la reproduction ou une preuve directe (log, trace, requête), jamais le
vote. Une hypothèse confirmée par 3 agents sans preuve reste « non confirmée ».

**Livrable par défaut** : réponse dans le chat ou court rapport : cause, preuves, correctif
proposé. Si le correctif est du code : il tient en un worker → un sous-agent, sans second
plan ; sinon, enchaîne sur le patron 4 (nouveau plan, montré à l'utilisateur : `equipe.md`,
étape 4).

**Piège** : en production, aucun agent n'agit (redémarrage, écriture, purge). Lecture seule.

## 4. Implémentation de code — « contrats, parallèle, intégration »

Pour du code découpable en morceaux aux fichiers disjoints.

1. **Contrats** (1 agent, sans isolation, lecture seule) : il fixe les interfaces entre
   morceaux (signatures, types, formats d'échange), découpe en tâches et donne à chacune une
   liste de fichiers **disjointe**. Rend un `CONTRACT_PLAN`. Fichier partagé incontournable ou
   couplage fort → `separable: false` et **le swarm s'arrête** : `STOP` aux rôles déjà lancés,
   et propose un seul worker (sous-agent) qui enchaîne les tâches. Sinon, montre ce découpage
   à l'utilisateur et continue sans attendre, sauf si le lancement attend encore son feu vert
   (`equipe.md`, étape 4).
2. **Implémentation** (1 worker par tâche, `isolation: 'worktree'`) : il ne modifie que ses
   fichiers, écrit ou adapte ses tests, les exécute, **committe** sur sa branche
   `swarm-<slug>-<tâche>` et rend un `CHANGESET` (branche, commit, fichiers touchés, tests
   lancés et résultat). Besoin d'un fichier hors de sa liste : il s'arrête et le signale dans
   `blocked_on`, sans le modifier. Un **tester** (§6) peut tester pour lui dans le navigateur.
3. **Intégration** : le **merger** (§6), en worktree lui aussi, pour ne jamais déplacer le
   HEAD ni toucher le checkout de l'utilisateur. Rend un `INTEGRATION`.
4. **Vérification** : le **checker** (§6) teste le résultat mergé contre l'Eval de chaque
   tâche ; si le diff est gros, 1 relecteur le relit contre les contrats (patron 2 réduit).
5. **Rapport** : pas de texte à synthétiser ; tu rapportes l'état (branche, tests, revue,
   restes).

**Une PR par worker** (avec l'accord de l'utilisateur) → file de merge (`flux.md` §1), sans
merger. « Les PR » de SKILL.md s'applique ; ajoute au brief la règle « PR » de `brief.md`
(sous-agent ou session) : la ligne `PRÊT À MERGER — <URL>` passe avant `FAIT`.

**Redondance** : rare. Pour une pièce petite et critique (algorithme délicat) : deux
implémentations aux approches différentes, départagées par les tests et une revue.

**Vérification** : les tests passent sur la branche d'intégration. Une revue d'agent ne
remplace jamais un test qui échoue.

**Livrable par défaut** : branche d'intégration + diff + sortie des tests. Pas de merge dans
la branche principale ni dans le checkout de l'utilisateur, pas de push, pas de PR sans accord
explicite.

**Pièges**

- Un worktree sans changement est supprimé : un agent qui n'a rien committé ne laisse rien à
  intégrer ; son `CHANGESET` doit le dire.
- Les agents isolés ne voient pas les fichiers non commités du checkout principal : committe,
  ou passe dans le prompt ce dont ils ont besoin.
- Une dépendance entre tâches (B utilise le module de A) se gère par le contrat (interface
  fixée en vague 1), pas en faisant attendre B. Si B a vraiment besoin du code de A : deux
  vagues, ou une seule tâche.

## 5. Goal ouvert — « apporteurs, exécutants, rédacteurs »

Pour un goal ouvert (`equipe.md`, étapes 1 et 2), ex. une doc « qu'est-ce qui se passe quand
je fais X ? ». Ce patron **s'ajoute** à la famille retenue, dont la redondance et la
vérification portent sur la **matière**, avant la rédaction. Goal fermé : le plan s'en passe,
et le dit : `Apporteurs : aucun — <raison>`.

Chaque rôle a son bloc pour le brief d'équipe (`team-mode.md`, « Brief d'équipe »), dont
cette fin remplace la partie « Fin » :

```
Fin : tu ne finis PAS après un sujet. Après chaque sujet, attends le suivant.
Tu finis seulement quand le coordinateur t'envoie "STOP" : alors écris
~/.claude/swarm-runs/<slug>/<nom>.json (sujets traités, chemins, points ouverts, "echanges"),
puis termine par une seule ligne : "FAIT <chemin>" ou "ÉCHEC <raison>".
```

**Apporteurs de sujets** (1 à 2, un angle chacun : ex. l'un lit le code, l'autre les tickets,
Slack et la doc existante).

```
Ton rôle : apporteur de sujets. Angle : <code | tickets et Slack | doc existante | …>.
Tu cherches d'autres sujets du même type que les exemples du goal. Tu ne traites aucun sujet.
Envoie au coordinateur des lots de 5 sujets au plus, message "SUJETS — <n> sujets", au schéma
SUJET (sujet, pourquoi il remplit le goal, où tu l'as vu). Avant chaque lot, filtre avec le goal
et retire les doublons de ~/.claude/swarm-runs/<slug>/sujets.md (que tu lis, sans l'écrire).
Attends la réponse du coordinateur avant le lot suivant. Si tu ne trouves plus rien :
"RIEN DE NOUVEAU". Avancement : sujets acceptés / budget (<N>).
```

**Exécutants** (le gros de l'équipe).

```
Ton rôle : exécutant. Le coordinateur t'envoie un sujet à la fois (message "SUJET — <id>").
Pour chaque sujet : <méthode de la famille : tracer dans le code, reproduire, sourcer…>.
Tu ne rédiges pas : pas de compte rendu, pas de prose. Écris la matière brute dans
~/.claude/swarm-runs/<slug>/matiere/<id>.json au schéma MATIERE (faits, preuves, commandes,
points ouverts, confiance). Puis envoie "MATIÈRE — <id> <chemin>" à <rédacteur>, et
"LIBRE — <id>" au coordinateur. Réponds aux QUESTION du rédacteur.
Avancement : sujets finis / sujets reçus.
```

**Rédacteurs** (possibles, pas obligatoires : `equipe.md`, étape 3).

```
Ton rôle : rédacteur, pour <exécutant-1>, <exécutant-2>. Format d'une fiche : <format fixé>.
Pour chaque "MATIÈRE — <id>" reçu : lis la matière et écris la fiche dans
~/.claude/swarm-runs/<slug>/livrable/<id>.md. N'invente rien : un trou ou un doute → QUESTION à
l'exécutant qui a fourni la matière. Puis "RÉDIGÉ — <id>" au coordinateur.
[redac-1 seulement] Tu es rédacteur en chef : au début, écris le style commun dans
livrable/STYLE.md ; après le STOP, assemble le livrable final dans livrable/INDEX.md.
Avancement : fiches rédigées / matières reçues.
```

**Toi, le coordinateur** : tu es le **seul** à écrire `sujets.md` (id stable `s-01`, `s-02`…,
qui sert à dédoublonner, pas le texte ; statut : proposé, accepté, refusé + raison, en cours
<nom>, matière prête, rédigé). À chaque
`SUJETS`, accepte ou refuse chaque sujet selon le goal (hors goal, même intéressant : refusé,
avec la raison), donne-lui un id, réponds à l'apporteur, et donne chaque sujet accepté à un
exécutant libre (`SUJET`). Tu tiens le budget de sujets.

- Tous les rôles démarrent **dans la vague 1**. Les sujets circulent par messages vers les
  agents qui tournent déjà ; jamais « un agent par sujet ».
- Arrêt quand le **budget de sujets** est atteint, ou après deux `RIEN DE NOUVEAU`, ou sur
  stop de l'utilisateur : `STOP` à chacun. Apporteurs et exécutants écrivent leur `<nom>.json`
  et finissent ; les rédacteurs finissent leurs fiches en cours, `redac-1` assemble le
  livrable, puis ils finissent. `FAIT` n'arrive qu'après un `STOP`.
- Le mode rapide (`Workflow`) ne fait pas de boucle ouverte : trois phases fermées
  (apporteurs jusqu'au budget, puis exécutants, puis rédacteurs).

## 6. Rôles spécialisés — merger, checker, tester, reproducer, watchdog

**Un rôle se prend sur un besoin écrit dans le plan**, pas sur un seuil automatique, et compte
dans le total d'agents. Tu ne fais aucun de ces métiers.

| Rôle | Le besoin qui le justifie | Rend |
|---|---|---|
| **Merger** (l'« intégrateur » du §4) | Les branches doivent être testées ensemble avant toute PR. | `INTEGRATION` |
| **Checker** (aux §1 et §2 : le « vérificateur » ou « contre-expert ») | Un résultat à accepter que tu ne peux pas vérifier toi-même en rejouant 1 à 3 commandes. | `VERDICT` par tâche |
| **Tester** (au fil de l'eau, avant le merge) | Une interface ou des parcours à cliquer que les workers ne peuvent pas tester eux-mêmes. | `VERDICT` |
| **Reproducer** | Un bug à reproduire, ou un run long sur une app qu'on peut lancer en local. À lancer quand le besoin apparaît (sous-agent), pas d'avance. | `HYPOTHESIS` (cause et preuve) et, s'il corrige, `CHANGESET` |
| **Watchdog** | Le seul cas écrit dans « Seuils » (SKILL.md). Brief : `sessions-mode.md`, « Watchdog ». | des `ALERTE` |

Les workers, eux, rendent le schéma de la famille (`FINDING`, `HYPOTHESIS`, `CHANGESET`,
`MATIERE`).

Lance ces rôles dans la même vague que les workers : ils attendent leur premier message.
Exception : le reproducer, lancé quand un bug arrive. Checker et tester cherchent ce qui ne
marche pas, pas à confirmer : une vérification non rejouée est « non vérifiée », jamais « OK ».
Leurs blocs, pour le brief d'équipe :

**Merger**

```
Ton rôle : merger. Tu travailles dans ton propre worktree. Quand le router t'écrit
"À INTÉGRER — <branches>", crée (ou reprends) la branche swarm-<slug>-integration depuis <branche de
départ>, merge chaque branche par son nom complet refs/heads/…, une par une. Conflit trivial :
résous-le. Conflit de fond : n'invente rien, écris au worker concerné et au router.
Puis lance les tests et le lint : <commandes>. Ne pousse rien, ne merge pas dans la branche
principale. Écris le résultat au schéma INTEGRATION, puis "INTÉGRÉ — <résumé>" au router.
Tu ne finis pas après un merge : attends le suivant, jusqu'au STOP.
```

**Checker**

```
Ton rôle : checker. Quand le router t'écrit "À VÉRIFIER — <tâches>", prends la branche
d'intégration, lance l'app (<commande>), et rejoue chaque vérification de l'Eval de chaque
tâche (dans ~/.claude/swarm-runs/<slug>/plan.md), pour de vrai, dans le navigateur si besoin.
Ton but est de trouver ce qui ne marche pas. Une vérification que tu n'as pas pu rejouer est
"non vérifiée", jamais OK. Capture d'écran pour chaque vérification, dans le dossier d'échange.
Rends un VERDICT par tâche, puis "VÉRIFIÉ — <n> OK, <n> KO, <n> non vérifiées" au router.
Attends la vérification suivante, jusqu'au STOP.
```

**Tester**

```
Ton rôle : tester, pour <worker-1>, <worker-2>, <worker-3>. Quand un worker t'écrit
"À TESTER — <tâche> <branche>", lance l'app sur sa branche (dans ton worktree), teste les
parcours et les cas limites de l'Eval de sa tâche dans le navigateur. Réponds au worker :
"VÉRIFIÉ — <tâche> OK" ou "À CORRIGER — <tâche> : <ce qui casse, comment le rejouer>".
Tu ne corriges pas le code toi-même.
```

**Reproducer**

```
Ton rôle : reproducer. Quand quelqu'un t'écrit "BUG — <symptôme>", rejoue les étapes jusqu'à
voir le bug (navigateur, commandes, tests). Trouve la cause, avec une preuve.
- Correctif petit et sûr : fais-le sur ta branche swarm-fix-<bug>, ajoute un test qui échouait
  avant, committe, puis "CORRIGÉ — <bug> <branche>" au router (le merger l'intégrera).
- Sinon : "BUG — <bug> : cause, preuve, correctif proposé" au router.
Ne touche jamais aux branches des workers. Bug impossible à reproduire : dis-le.
Attends le bug suivant, jusqu'au STOP.
```

**Ordre en fin de tâche (code, avec merger)** : worker « tout est commité » → merger →
checker. Un échec du checker repart **au worker de la tâche** (`À CORRIGER — <tâche>`), avec
la vérification qui échoue, puis repasse par le merger et le checker. Le correctif du
reproducer est une branche à lui, que le merger intègre comme les autres (ou une PR à lui).
