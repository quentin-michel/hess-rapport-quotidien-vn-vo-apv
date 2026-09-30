# Brouillon mail IT — Prérequis techniques pipeline GitHub Actions (2026-09-29)

Contexte : décision d'architecture du 2026-09-29 (`CADRAGE.md` §3) —
l'orchestrateur du rapport quotidien VN/VO/APV sera un workflow GitHub
Actions déclenché par cron, pas une tâche planifiée Claude Code. Deux
prérequis techniques bloquent le passage en production (`CADRAGE.md` §9,
points 1 et 1bis), nécessitant l'IT/l'admin Google Workspace — pas
exécutables par Claude ni par Quentin/Corentin seuls.

**Statut (2026-09-30)** : le point 2 est réglé sans ce mail — la boîte
`rapport-quotidien@hessautomobile.com` existe, l'IT lui a accordé le rôle
IAM sur le projet GCP `controlegestion`, et un envoi de test via l'API
Gmail (token OAuth de la boîte, scope `gmail.send`) a réussi. Reste le
point 1 (compte de service / délégation domaine) si on choisit cette voie
plutôt qu'un token OAuth stocké en secret GitHub pour le cron — le mail
ci-dessous n'est à envoyer que dans ce cas, en retirant le point 2.

---

**Objet : Automatisation rapport quotidien VN/VO/APV — 2 prérequis techniques**

Bonjour,

Dans le cadre du projet de rapport quotidien automatisé (VN/VO/APV), on passe à la phase d'automatisation via un workflow GitHub Actions déclenché chaque matin. Deux prérequis techniques nécessitent votre aide :

**1. Compte de service Google avec délégation de domaine**
Le workflow doit pouvoir lire des Google Sheets (scope `spreadsheets.readonly` uniquement, aucune écriture) sans dépendre d'une session utilisateur active. Il nous faut :
- Un compte de service Google Cloud (projet GCP `controlegestion`, déjà utilisé pour l'outil `gws` de lecture des Sheets)
- La délégation de domaine (domain-wide delegation) activée pour ce compte de service, scope `https://www.googleapis.com/auth/spreadsheets.readonly`
- Le fichier de clé JSON du compte de service, à nous transmettre de façon sécurisée pour le stocker en secret chiffré GitHub

**2. Boîte Gmail HESS dédiée pour l'envoi des rapports**
Les mails quotidiens (VN/VO/APV par concession, synthèses direction/plaque) doivent partir d'une adresse HESS dédiée, pas d'un compte personnel. Il nous faut :
- La boîte Gmail **`rapport-quotidien@hessautomobile.com`** créée (adresse actée le 2026-09-30)
- Des identifiants API (OAuth ou compte de service avec délégation) permettant l'envoi automatisé (scope `gmail.send`), utilisables depuis GitHub Actions

Ces deux éléments bloquent le passage en production de l'automatisation. Disponibles pour en discuter si besoin.

Merci,
Quentin
