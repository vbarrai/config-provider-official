# Exemples de sujets macro

Version 2.0.0 — la même que `SKILL.md`. Sinon, dis-le en une ligne et applique `SKILL.md` seul.

Chaque exemple suit le même gabarit : le sujet, les tâches, la forme choisie (un worker par
flux indépendant, ou une équipe ; voir « Router et workers » dans `SKILL.md`), la stratégie de
communication, la raison du choix et ce qui remonterait à l'humain. Les seuils (échelle de
taille, plafond de workers, surveillance, feu vert, accord) sont ceux de « Seuils » dans
`SKILL.md`. Par défaut, un worker est un sous-agent ; c'est une session seulement si
l'utilisateur en demande avec ses mots (« en sessions », « en parallèle »…). Toute merge dans
la branche principale demande l'accord de l'utilisateur.

---

## 1. Une micro-tâche

- **Sujet macro** : « Corrige la typo dans le titre du README. »
- **Tâches** : T1, une seule, sans branche ni PR demandée.
- **Forme** : 1 flux → 1 sous-agent (outil `Agent`), brief WORKER, modèle moins cher, `effort`
  bas. Pas de session, pas de worktree à archiver.
- **Communication** : le sous-agent rend son rapport, avec la commande et sa sortie (`git diff`).
- **Pourquoi** : une tâche de 2 minutes ne vaut ni une session ni une annonce longue. Le router
  reste libre pour la suite.
- **Remonte à l'humain** : rien. Le router rejoue une commande (`git diff --stat`) et le dit.

## 2. Corriger 5 tickets de bug indépendants

- **Sujet macro** : « Corrige les 5 bugs de la colonne À faire du sprint, une PR par bug. »
- **Tâches** : T1 à T5, un bug chacune, dans des fichiers différents.
- **Forme** : 5 flux → 5 tâches, 4 workers à la fois (plafond de « Seuils »), le 5e dès qu'un
  worker se libère. Des sous-agents en worktree → 5 PR. Pas de watchdog.
- **Communication** : tout passe par le router. Chaque worker → router : un seul message,
  `PRÊT À MERGER`. `REBASE` seulement à un worker dont la PR est en conflit ou refusée par
  GitHub. `QUESTION` pour une décision humaine ; les `FRICTION` vont dans le rapport de fin.
- **Pourquoi** : les bugs sont indépendants, donc en parallèle ils vont bien plus vite. Le
  plafond garde le nombre de workers lisible quand plusieurs routers tournent.
- **Remonte à l'humain** : la question de merge, une fois, dans l'annonce (« à chaque PR, ou
  auto quand c'est vert ? ») ; un bug dont la correction demande un choix produit.

## 3. Une feature en chaîne : migration DB → API → UI

- **Sujet macro** : « Ajoute la date d'expiration des campagnes, de la base jusqu'à l'écran. »
- **Tâches** : T1 migration DB ; T2 API (dépend de T1) ; T3 UI (dépend de T2).
- **Forme** : une chaîne longue, organisée sans interruption : 3 workers. Pas de watchdog.
- **Communication** : le router fixe le contrat (nom et type du champ) dans les 3 briefs.
  Branches empilées : le worker T2 part de la branche de T1 sans attendre sa merge
  (`source_branch`, ou la branche de départ écrite dans le brief) ; le worker T3 prépare en
  avance (lecture du code, plan, tests sur le contrat), puis part de la branche de T2. Ordre de
  merge : T1, puis T2, puis T3. Après chaque merge, le suivant rebase
  (`git rebase --onto origin/<base> <ancienne base>`). Un conflit dans le code d'un autre worker
  → le router demande à cet autre worker quoi garder.
- **Pourquoi** : la chaîne est longue et les couches sont dans des fichiers différents.
  L'empilement et la préparation en avance évitent que T2 et T3 attendent sans rien faire.
- **Remonte à l'humain** : l'accord de merge (une fois, dans l'annonce) ; le déploiement de la
  migration en production.

## 4. Un gros renommage qui touche les mêmes fichiers partout

- **Sujet macro** : « Renomme `Advertiser` en `Brand` dans tout le backend. »
- **Tâches** : T1 modèles, T2 services, T3 tests — mais tous touchent les mêmes fichiers.
- **Forme** : un seul flux (chaîne très liée) → 1 worker, qui enchaîne T1, T2 et T3 seul.
- **Communication** : worker → router : `PRÊT À MERGER`, `QUESTION` si un renommage est un
  choix produit. Un nom ambigu sans enjeu : il choisit et le note (U2).
- **Pourquoi** : plusieurs workers sur les mêmes fichiers garantissent des conflits. C'est une
  petite chaîne très liée : un seul contexte va plus vite.
- **Remonte à l'humain** : la merge de la PR ; un renommage visible des clients (API publique),
  qui est un choix produit.

## 5. Le même changement dans 8 dépôts

- **Sujet macro** : « Passe les 8 microservices à Node 22 et mets à jour leur CI. »
- **Tâches** : T1 à T8, un dépôt chacune.
- **Forme** : 8 flux → 8 tâches, 4 workers à la fois (plafond de « Seuils »). Chaque worker
  travaille dans son dépôt (`cwd` pour une session). Tâche écrite d'avance : modèle moins cher.
- **Communication** : le router écrit un gabarit commun (étapes, commandes, Eval) dans chaque
  brief. Workers → router : `PRÊT À MERGER`. Un worker qui trouve un piège commun (ex. une
  dépendance native qui casse) le signale au router, qui le met dans les briefs suivants et
  l'envoie aux workers en cours par `SendMessage`. Pas de file de merge commune : chaque dépôt a
  sa propre base.
- **Pourquoi** : 8 dépôts indépendants, un même gabarit. La diffusion des pièges évite que
  8 workers tombent dans le même trou.
- **Remonte à l'humain** : l'accord de merge (une fois, dans l'annonce) ; un service qui ne
  peut pas passer à Node 22 sans changement de comportement.

## 6. Un audit de sécurité avant une mise en production

- **Sujet macro** : « Audite en équipe la sécurité du service de paiement avant la mise en prod. »
- **Tâches** : T1 authentification et droits ; T2 injection et entrées ; T3 secrets et
  dépendances ; T4 vérification des constats graves ; T5 synthèse.
- **Forme** : équipe, patron audit (`topologies.md` §2), mode sous-agents — 3 relecteurs (un
  angle chacun) + 1 checker (contre-expert) + 1 agent de synthèse. Total : 5 agents.
  L'utilisateur a demandé l'équipe : le plan est montré et lancé dans le même tour.
- **Communication** : chaque relecteur envoie ses constats graves au checker dès qu'il les
  trouve ; le checker répond par une réfutation ou une confirmation, preuve à l'appui. La
  synthèse applique la règle de fusion (`equipe.md`, étape 6) ; le router la contrôle.
- **Pourquoi** : un audit gagne à la redondance d'angles, et un faux positif coûte cher. La
  vérification croisée filtre ce qui n'est pas prouvé.
- **Remonte à l'humain** : la décision de bloquer ou non la mise en prod.

## 7. Un incident en production à cause inconnue

- **Sujet macro** : « Les visites en magasin ont chuté de 40 % depuis mardi, trouve pourquoi. »
- **Tâches** : T1 à T3, une hypothèse chacune (collecte, pipeline de données, calcul) ; T4
  reproduire et confirmer la cause.
- **Forme** : équipe, patron diagnostic (`topologies.md` §3), mode sous-agents — 3 enquêteurs +
  1 reproducer (le besoin est écrit : confirmer la cause). Total : 4 agents. Le router propose
  l'équipe lui-même : il attend le feu vert. Livrable de moins d'une page : le router l'écrit.
- **Communication** : débat permanent : chaque enquêteur envoie ses preuves contre les
  hypothèses des autres à leurs enquêteurs. Tout le monde → reproducer : `BUG` ; reproducer →
  router : `CORRIGÉ` (ou un rapport).
- **Pourquoi** : la cause est inconnue ; plusieurs hypothèses en parallèle, réfutées entre
  elles, évitent de s'enfermer dans la première idée.
- **Remonte à l'humain** : le feu vert du plan ; toute action en production (relance d'un job,
  correction de données, déploiement d'un correctif).

## 8. Un rapport comparatif

- **Sujet macro** : « Compare 4 outils d'orchestration de données pour remplacer Airflow. »
- **Tâches** : T1 à T4, un outil chacune ; T5 vérification des points clés ; T6 rédaction du
  rapport.
- **Forme** : sans équipe si le rapport est court : 4 flux → 4 sous-agents qui rédigent chacun
  leur part. En équipe, patron recherche (`topologies.md` §1) : 4 explorateurs + 1 vérificateur
  + 1 agent de synthèse qui écrit le rapport. Total : 6 agents. Des rédacteurs en plus seulement
  si le rapport est long et doit avoir un seul style.
- **Communication** : les explorateurs envoient leurs découvertes aux autres explorateurs quand
  elles les touchent. Le vérificateur reçoit les constats clés et renvoie des réfutations.
  L'agent de synthèse pose ses `QUESTION` aux explorateurs.
- **Pourquoi** : 4 sources indépendantes, puis un texte au style unique, écrit par un seul
  agent.
- **Remonte à l'humain** : le feu vert du plan si le router propose l'équipe ; le choix final
  de l'outil, qui est un arbitrage métier.
