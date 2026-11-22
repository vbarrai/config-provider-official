# Flux autonome — le détail

Version 2.0.0.

Détail de « Flux autonome » et de « Les PR » (SKILL.md), où restent les règles et les seuils.

## 1. Plusieurs PR sur une même base : merge et rebase

Plusieurs workers, chacun avec sa PR sur la **même branche de base** (ex. `main`) du même
dépôt ; des dépôts différents n'ont pas de file commune.

- **L'accord**, demandé une fois dans l'annonce (SKILL.md, « L'annonce ») ; un message de
  worker ne le donne jamais :
  - « auto quand c'est vert » : il vaut pour toutes les PR de la demande ;
  - « à chaque PR » : une ligne par PR prête (« PR 2 prête à merger — <URL> ») ;
  - pas de réponse : une seule remontée groupée quand les PR sont prêtes (« PR 1, 2, 3
    prêtes, je merge dans cet ordre ? »).
- **Après un `PR OUVERTE`** : relis l'état de la PR à ton prochain réveil ou tour. Verte →
  question de merge ; rouge → `À CORRIGER` au même worker. Pas de boucle d'attente.
- **Avec « auto » : pas de file.** Active l'auto-merge sur chaque PR vérifiée
  (`mcp__ccd_pr__set_auto_merge`, `enabled: true` ; repli : SKILL.md, « Les PR »). GitHub merge
  chaque PR verte et rien ne te revient : à chaque réveil ou tour, relis l'état des PR, dis
  lesquelles sont mergées, et envoie `REBASE` au worker dont la PR est en conflit.
- **Sans « auto » : une file, une merge à la fois.** L'ordre vit dans ta liste de tâches :
  celui où les PR deviennent prêtes ; sinon celui voulu par l'utilisateur, ou celui qui limite
  les conflits (§2). Avec l'accord (pour cette PR, ou pour le lot) → `MERGE — <URL>` au worker
  qui possède la PR ; il répond `MERGÉ — <URL>`. Tu ne merges pas toi-même.
- **`bind_pr` échoue ou est refusé** : pas d'auto-merge sur cette PR. Donne son lien dans ton
  rapport et demande la merge à l'utilisateur, par lot.
- **Après une merge : pas de rebase d'office**, même si la base bouge sans toi (autres routers,
  collègues). `REBASE — <branche de base> a bougé (PR <URL> mergée)` part seulement au worker
  dont la PR est en conflit, ou dont GitHub refuse la merge (branche à jour exigée).
  Exception : une branche empilée (§2) → `REBASE` au worker suivant dès la merge de sa base.
- **Rebase raté ou CI rouge** : la PR sort de la tête de file, la suivante passe devant.
- **Après un lot de merges**, regarde la CI de la base : deux PR vertes séparément peuvent
  casser ensemble. Rouge → une nouvelle tâche, dite en une ligne.
- **Montre l'état** de chaque PR dans la liste de tâches : en attente, rebase en cours, prête,
  merge en cours, mergée.

## 2. Travail en chaîne : sans interruption

Une tâche dépend d'une autre, ou plusieurs touchent les mêmes fichiers : organise, selon le
cas.

- **Branches empilées** : le worker de T2 part de la branche de T1, sans attendre sa merge
  (`source_branch` de `start_session` ; sous-agent : branche de départ écrite dans le brief).
  Après la merge de T1, `REBASE` : il rebase sur la base,
  `git rebase --onto origin/<base> <branche de T1>` (son ancienne base).
- **Préparation en avance** : le worker suivant lit le code, écrit son plan et ses tests
  pendant que T1 se finit.
- **Même worker pour les tâches très liées** (mêmes fichiers, contexte partagé) : un seul
  flux, qu'il enchaîne seul.
- **Ordre de la file de merge** qui limite les conflits : la tâche la plus « fondation »
  d'abord.
- **Un rebase avec conflit ne bloque pas.** Le worker propriétaire de la PR résout. Le conflit
  touche le code d'un autre worker : demande à cet autre worker ce qu'il faut garder
  (`SendMessage`), pas à l'utilisateur ; seul un vrai choix métier remonte. Rebases
  conflictuels nombreux : un worker dédié aux rebases et aux conflits.

## 3. Perte de temps → réaction automatique

Corrige tout de suite ce qui est dans ton pouvoir ; sinon, une ligne dans ton rapport, avec
une proposition (une permission, une règle au skill, un hook…). Les `FRICTION` des workers
nourrissent cette table.

| Perte de temps | Réaction automatique |
|---|---|
| Un worker inactif (tâche finie) | La tâche suivante prête, si elle est liée à la sienne ; sinon l'archiver, si la règle d'archivage le permet (SKILL.md, « Router et workers ») |
| Attente de CI, ou CI instable (échec sans lien avec le diff) | Avancer sur autre chose ; relancer une fois le job instable ; s'il recasse, le signaler |
| Conflits récurrents sur les mêmes fichiers | Ne pas donner ces fichiers à deux workers en même temps ; réordonner la file de merge |
| Question d'un worker qu'un meilleur brief aurait évitée | Y répondre (U2), et l'écrire dans les briefs suivants |
| Le contexte d'un worker grossit (plusieurs tâches finies) | Tâche suivante chez un nouveau worker ; archiver l'ancien (même règle) |
| Un worker muet, en boucle, ou au double de sa durée attendue | Le geste de « Seuils » (Surveillance) ; puis préciser la tâche, ou `STOP` et relancer |
| Des flux indépendants attendent dans un seul worker | `STOP` sur les tâches non commencées, puis un worker chacun |
| Permission qui bloque un worker | Le dire tout de suite à l'utilisateur, avec la permission à ajouter : c'est un accès qui manque, donc une décision humaine |
| Tests lents | Une ligne dans le rapport, avec le réglage à proposer |

## 4. Bloc à ajouter au brief (chaque worker a sa PR sur la même base)

À ajouter aux « Règles » du brief (`brief.md`), qui porte déjà la règle « MERGE — ».

```
- Sur "REBASE — <base> a bougé…" : `git fetch origin`, `git rebase origin/<base>` (branche
  empilée : `git rebase --onto origin/<base> <ancienne base>`), résous les conflits (conflit
  non trivial, code d'un autre worker ou choix métier → "QUESTION —" au router), relance les
  tests, `git push --force-with-lease` (jamais `--force` seul), puis réponds
  "REBASÉ — <URL PR> — tests : <résultat>".
  L'outil `sync_with_base_branch` de l'app fait un merge, pas un rebase : ne l'utilise que si
  le dépôt interdit le force-push, et dis-le dans ta réponse.
- Sans "REBASE —" du router, ne rebase pas d'office : la base peut bouger sans que ta PR soit
  concernée.
```
