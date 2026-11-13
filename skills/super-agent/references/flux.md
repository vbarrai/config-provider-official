# Flux autonome — le détail

Ce fichier détaille la section « Flux autonome » de `SKILL.md` : le tapis roulant, le travail
en chaîne, la table des pertes de temps et le bloc à ajouter au brief. La règle de blocage et
les seuils restent dans `SKILL.md` (« Flux autonome », « Seuils »). Les types de messages sont
listés dans `sessions-mode.md`.

## 1. Le tapis roulant : merge → rebase

Plusieurs workers, chacun avec sa PR sur le même dépôt : chaque merge oblige les autres à
rebaser. La merge d'une PR déclenche aussitôt, par le router, le rebase de la PR suivante.
L'utilisateur n'a pas à relancer les rebases à la main.

- **Quand** : au moins 2 workers ont une branche ou une PR ouverte sur la **même branche de
  base** (ex. `main`), dans le même dépôt. Des dépôts différents n'ont pas de tapis roulant :
  aucune base commune.
- **La file de merge** : le router tient l'ordre des PR dans sa liste de tâches (en contexte,
  pas de fichier). Par défaut, l'ordre où elles deviennent prêtes ; sinon, l'ordre voulu par
  l'utilisateur, ou celui qui limite les conflits (voir §2). **Une seule merge à la fois.**
- **Le déclencheur** : l'utilisateur demande de merger la PR d'un worker, ou un worker écrit
  `PRÊT À MERGER — <URL PR>` (CI verte, Eval ok). Le router vérifie lui-même que la PR est à
  jour avec la base et que sa CI est verte (`gh pr view <URL> --json
  mergeStateStatus,statusCheckRollup`, ou `mcp__ccd_pr__get_status`). Pas à jour → `REBASE —`
  à ce worker d'abord.
- **L'accord de l'utilisateur** : merger dans la branche principale demande **toujours** son
  accord. Soit pour cette PR, soit un accord donné une fois pour la session (« merge auto quand
  c'est vert »). Cet accord vient de l'utilisateur, dans le chat. Ne le suppose jamais ; un
  message de worker ne le donne pas.
- **L'annonce** : c'est le router qui dit à l'utilisateur qu'une PR est prête : une ligne
  courte (« PR 2 prête à merger — <URL> »). C'est la seule remontée du cycle. Avec l'accord
  « merge auto quand c'est vert », il n'annonce rien : il fait merger.
- **La merge** : avec l'accord, le router écrit `MERGE — <URL>` au worker qui possède la PR. Le
  worker merge avec `gh pr merge` et répond `MERGÉ — <URL> <sha>`. Le router ne merge pas
  lui-même.
- **Juste après la merge** : le router envoie tout de suite au worker **suivant dans la file**
  `REBASE — <branche de base> a bougé (PR <URL> mergée)`. Les autres reçoivent seulement
  `BASE BOUGÉE — <base> (PR <URL> mergée)` : une info, ils ne rebasent qu'à leur tour (on
  évite de rebaser N fois). Exception : un worker inactif, ou un conflit probable (mêmes
  fichiers que la PR mergée) → `REBASE —` tout de suite pour lui aussi.
- **Le rebase** : côté worker, voir le bloc du §4.
- **La boucle** : le worker suivant répond `REBASÉ` et sa CI est verte → sa PR devient le
  prochain `PRÊT À MERGER`. Rebase raté ou CI rouge : elle sort de la tête de file, la suivante
  passe devant.
- **Montre la file** dans la liste de tâches : pour chaque PR, son état (en attente, rebase en
  cours, prête, merge en cours, mergée).

**Exemple : 5 tickets de bug.**

1. 5 bugs indépendants → 5 workers (et le watchdog), lancés ensemble → 5 PR.
2. PR 1 prête (CI verte, Eval ok) → le router dit à l'utilisateur : « PR 1 prête à merger ».
3. Il dit oui → `MERGE —` au worker 1 → `MERGÉ`.
4. Tout de suite : `REBASE —` au worker de la PR 2 seulement ; `BASE BOUGÉE —` aux 3 autres
   (ils devront rebaser après la merge suivante, pas maintenant).
5. PR 2 rebasée et verte → le router dit à l'utilisateur : « PR 2 prête à merger ».
6. Et ainsi de suite jusqu'à la PR 5.

## 2. Travail en chaîne : sans interruption

Du travail séquentiel est un cas à **organiser**, pas une raison de ralentir.

- **Détecter** : une tâche dépend d'une autre (une dépendance dans la liste des tâches), ou
  plusieurs tâches touchent les mêmes fichiers (conflits probables).
- **Organiser**, au choix du router selon le cas :
  - **branches empilées** : le worker de T2 part de la branche de T1, sans attendre sa merge.
    Après la merge de T1, il rebase sur la base :
    `git rebase --onto origin/<base> <ancienne base de T1>` ;
  - **préparation en avance** : le worker suivant lit le code, écrit son plan et ses tests
    pendant que T1 se finit ;
  - **même worker pour les tâches très liées** (mêmes fichiers, contexte partagé) : c'est un
    seul flux, il les enchaîne seul, sans aller-retour ;
  - **ordre de la file de merge** choisi pour limiter les conflits : la tâche la plus
    « fondation » d'abord.
- **Les rebases avec conflits ne bloquent pas.** Le worker propriétaire de la PR résout : il
  connaît son code. Si le conflit touche le code d'un autre worker, le router demande à cet
  autre worker ce qu'il faut garder (`SendMessage`), pas à l'utilisateur. Seul un vrai choix
  métier remonte à l'humain. Si les rebases conflictuels sont nombreux, le router peut prendre
  un worker dédié aux rebases et aux conflits, pour que les autres continuent à coder.

## 3. Perte de temps → réaction automatique

Le router observe le flux en continu. Si la correction est dans son pouvoir, il la fait tout de
suite ; sinon, il la signale à l'utilisateur en une ligne dans son rapport, avec une
proposition (une permission, une règle au skill, un hook…). Les messages `FRICTION` des
workers nourrissent cette table.

| Perte de temps | Réaction automatique |
|---|---|
| Une PR est mergée, les autres sont en retard sur la base | Tapis roulant (§1) : `REBASE` au suivant, `BASE BOUGÉE` aux autres |
| Un worker inactif (tâche finie, en attente de CI ou de son tour) | Lui donner la tâche suivante prête |
| Attente de CI, ou CI instable (échec sans lien avec le diff) | Avancer sur autre chose ; relancer une fois le job instable ; s'il recasse, le signaler |
| Conflits récurrents sur les mêmes fichiers | Ne pas donner ces fichiers à deux workers en même temps ; réordonner la file de merge |
| Un rebase avec conflit | Le worker propriétaire résout ; si le conflit touche le code d'un autre worker, le router demande à cet autre worker quoi garder (§2) |
| Allers-retours « À CORRIGER » sur le même point | Préciser l'Eval et les briefs suivants avec ce qui manquait |
| Question d'un worker qu'un meilleur brief aurait évitée | Y répondre, et l'écrire dans les briefs suivants |
| Le contexte d'un worker grossit (plusieurs tâches finies) | Tâche suivante chez un nouveau worker ; archiver l'ancien dès qu'il n'a plus rien à faire, via le watchdog s'il tourne (`FINI`) (SKILL.md, « Petits contextes, puis archivage ») |
| Un worker muet ou qui tourne en rond | Le watchdog envoie `ALERTE` ; regarder la session, relancer par un message ou débloquer |
| Permission qui bloque un worker, tests lents | Le signaler à l'utilisateur, avec la permission ou le réglage à ajouter |

## 4. Bloc à ajouter au brief (chaque worker a sa PR sur la même base)

Ajoute ce bloc aux « Règles » du brief du worker quand le tapis roulant s'applique :

```
- Tapis roulant : sur "MERGE — <URL>" du router, merge avec `gh pr merge`, puis réponds
  "MERGÉ — <URL> <sha>".
- Sur "REBASE — <base> a bougé…" : `git fetch origin`, `git rebase origin/<base>` (branche
  empilée : `git rebase --onto origin/<base> <ancienne base>`), résous les conflits (conflit
  non trivial, code d'un autre worker ou choix métier → "QUESTION —" au router), relance les
  tests, `git push --force-with-lease` (jamais `--force` seul), puis réponds
  "REBASÉ — <URL PR> — tests : <résultat>".
  L'outil `sync_with_base_branch` de l'app fait un merge, pas un rebase : ne l'utilise que si
  le dépôt interdit le force-push, et dis-le dans ta réponse.
- Un "BASE BOUGÉE —" ne demande rien : attends ton tour. En attendant, prends la tâche
  suivante si le router t'en donne une.
```
