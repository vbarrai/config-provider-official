# Exemples de sujets macro

Chaque exemple suit le même gabarit : le sujet, les tâches, la forme choisie (un worker par
flux indépendant, ou une équipe (c) ; voir « Router et workers » dans `SKILL.md`), la stratégie
de communication, la raison du choix et ce qui remonterait à l'humain. Les seuils (feu vert,
watchdog, accord au-delà d'un certain nombre d'agents) sont ceux de « Seuils » dans `SKILL.md`.
Toute merge dans la branche principale demande l'accord de l'utilisateur ; le rebase, lui, se
fait sans demander.

---

## 1. Corriger 5 tickets de bug indépendants

- **Sujet macro** : « Corrige les 5 bugs de la colonne À faire du sprint. »
- **Tâches** : T1 à T5, un bug chacune, dans des fichiers différents.
- **Forme / team** : 5 flux → 5 workers, un par bug → 5 PR, et le watchdog (lancé en
  premier). Total : 6 agents, sans feu vert.
- **Communication** : tout passe par le router. Chaque worker → router : `PR`, puis
  `PRÊT À MERGER`. Tapis roulant : après chaque merge, `REBASE` au worker de la PR suivante
  seulement, `BASE BOUGÉE` aux autres. Watchdog → router : `ALERTE`. Workers → router :
  `QUESTION`, `FRICTION`.
- **Pourquoi** : les bugs sont indépendants, donc en parallèle ils vont 5 fois plus vite. Le
  tapis roulant évite de rebaser 4 PR après chaque merge.
- **Remonte à l'humain** : « PR n prête à merger » (une ligne par PR), sauf accord « merge auto
  quand c'est vert » ; un bug dont la correction demande un choix produit.

## 2. Une feature en chaîne : migration DB → API → UI

- **Sujet macro** : « Ajoute la date d'expiration des campagnes, de la base jusqu'à l'écran. »
- **Tâches** : T1 migration DB ; T2 API (dépend de T1) ; T3 UI (dépend de T2).
- **Forme / team** : une chaîne longue, organisée sans interruption : 3 workers + le
  watchdog. Total : 4 agents, sans feu vert.
- **Communication** : le router fixe le contrat (nom et type du champ) dans les 3 briefs.
  Branches empilées : le worker T2 part de la branche de T1 sans attendre sa merge ; le
  worker T3 prépare en avance (lecture du code, plan, tests sur le contrat), puis part de la
  branche de T2. Ordre de merge : T1, puis T2, puis T3. Après chaque merge, `REBASE` au
  suivant (`git rebase --onto origin/<base> <ancienne base>`). Un conflit dans le code d'un
  autre worker → le router demande à cet autre worker quoi garder.
- **Pourquoi** : la chaîne est longue et les couches sont dans des fichiers différents.
  L'empilement et la préparation en avance évitent que T2 et T3 attendent sans rien faire.
- **Remonte à l'humain** : chaque merge ; le déploiement de la migration en production.

## 3. Un gros renommage qui touche les mêmes fichiers partout

- **Sujet macro** : « Renomme `Advertiser` en `Brand` dans tout le backend. »
- **Tâches** : T1 modèles, T2 services, T3 tests — mais tous touchent les mêmes fichiers.
- **Forme / team** : un seul flux (chaîne très liée) → 1 worker, qui enchaîne T1, T2 et T3
  seul. Total : 1 agent.
- **Communication** : worker → router : `PR`, `QUESTION` si un nom est ambigu, `FRICTION`.
  Pas de tapis roulant (une seule PR).
- **Pourquoi** : plusieurs workers sur les mêmes fichiers garantissent des conflits. C'est une
  petite chaîne très liée : un seul contexte va plus vite.
- **Remonte à l'humain** : la merge de la PR ; un renommage visible des clients (API publique),
  qui est un choix produit.

## 4. Le même changement dans 8 dépôts

- **Sujet macro** : « Passe les 8 microservices à Node 22 et mets à jour leur CI. »
- **Tâches** : T1 à T8, un dépôt chacune.
- **Forme / team** : 8 flux → 8 workers, un par dépôt, et le watchdog. Total : 9 agents,
  sans feu vert (sous le seuil d'accord).
- **Communication** : le router écrit un gabarit commun (étapes, commandes, Eval) dans chaque
  brief. Workers → router : `PR`, `PRÊT À MERGER`, `FRICTION`. Un worker qui trouve un piège
  commun (ex. une dépendance native qui casse) le signale au router, qui le diffuse aux autres
  par `SendMessage`. Pas de tapis roulant : chaque dépôt a sa propre base, aucun rebase croisé.
- **Pourquoi** : 8 dépôts indépendants, un même gabarit. La diffusion des pièges évite que
  8 workers tombent dans le même trou.
- **Remonte à l'humain** : la merge de chaque PR (ou un accord « merge auto quand c'est vert ») ;
  un service qui ne peut pas passer à Node 22 sans changement de comportement.

## 5. Un audit de sécurité avant une mise en production

- **Sujet macro** : « Audite la sécurité du service de paiement avant la mise en prod. »
- **Tâches** : T1 authentification et droits ; T2 injection et entrées ; T3 secrets et
  dépendances ; T4 vérification des constats graves.
- **Forme / team** : (c), patron audit (`topologies.md` §2) — 1 watchdog + 3 relecteurs (un
  angle chacun) + 1 checker (contre-expert). Total : 5 agents, après feu vert du plan.
- **Communication** : chaque relecteur envoie ses constats graves au checker dès qu'il les
  trouve ; le checker répond par une réfutation ou une confirmation, preuve à l'appui. Watchdog
  → router : `ALERTE`. Synthèse par le router, avec la règle de fusion (étape 6).
- **Pourquoi** : un audit gagne à la redondance d'angles, et un faux positif coûte cher. La
  vérification croisée filtre ce qui n'est pas prouvé.
- **Remonte à l'humain** : le feu vert du plan ; la décision de bloquer ou non la mise en prod.

## 6. Un incident en production à cause inconnue

- **Sujet macro** : « Les visites en magasin ont chuté de 40 % depuis mardi, trouve pourquoi. »
- **Tâches** : T1 à T3, une hypothèse chacune (collecte, pipeline de données, calcul) ; T4
  reproduire et confirmer la cause.
- **Forme / team** : (c), patron diagnostic (`topologies.md` §3) — 1 watchdog + 3 enquêteurs +
  1 reproducer. Total : 5 agents, après feu vert du plan.
- **Communication** : débat permanent : chaque enquêteur envoie ses preuves contre les
  hypothèses des autres à leurs enquêteurs. Tout le monde → reproducer : `BUG` ; reproducer →
  router : `CORRIGÉ` (ou un rapport). Watchdog → router : `ALERTE`.
- **Pourquoi** : la cause est inconnue ; plusieurs hypothèses en parallèle, réfutées entre
  elles, évitent de s'enfermer dans la première idée.
- **Remonte à l'humain** : le feu vert du plan ; toute action en production (relance d'un job,
  correction de données, déploiement d'un correctif).

## 7. Un rapport comparatif

- **Sujet macro** : « Compare 4 outils d'orchestration de données pour remplacer Airflow. »
- **Tâches** : T1 à T4, un outil chacune ; T5 vérification des points clés ; T6 rédaction du
  rapport.
- **Forme / team** : (c), patron recherche (`topologies.md` §1) — 1 watchdog + 4 explorateurs +
  1 vérificateur + 2 rédacteurs (1 pour 2 explorateurs). Total : 8 agents, après feu vert du
  plan. Variante plus légère sans équipe : 4 flux → 4 workers qui rédigent eux-mêmes, et le watchdog, si le rapport
  est court.
- **Communication** : les explorateurs rendent de la matière brute (`MATIÈRE`) à leur
  rédacteur, et envoient leurs découvertes aux autres explorateurs quand elles les touchent. Le
  vérificateur reçoit les constats clés et renvoie des réfutations. Rédacteur → explorateur :
  `QUESTION` ; rédacteur → router : `RÉDIGÉ`.
- **Pourquoi** : 4 sources indépendantes, puis un texte au style unique. Les rédacteurs
  laissent les explorateurs sur le fond.
- **Remonte à l'humain** : le feu vert du plan ; le choix final de l'outil, qui est un
  arbitrage métier.
