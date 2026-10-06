# Consignes de composition des mails (étape 3 du workflow)

Tu es exécuté dans GitHub Actions, sans humain pour te répondre. Ta seule tâche :
composer **le mail dont l'identifiant t'est donné dans la commande** (un seul mail par
appel ; si aucun identifiant n'est donné, compose tous ceux de `build/plan.json`, clé
`mails`), à partir des données déjà extraites et contrôlées. Ne modifie aucun autre
fichier du dépôt.

## Entrées

- Identifiant d'un mail : `<type>__<code>`, ex. `apv__HYU_COLMAR` (un mail par
  concession pour vn, vo, apv, directeur) ou `plaque__PLQ_HYUNDAI` (un mail par plaque).
- `build/plan.json` : liste des mails à composer, date attendue (J-1), périmètre.
- `build/faits/<identifiant>.json` : l'extrait des onglets utiles au mail. Champs de
  contexte : `type` (vn, vo, apv, directeur ou plaque — c'est lui qui fixe les règles
  ci-dessous), `concession` et `nom_concession` (mails de concession), `plaque`,
  `nom_plaque`, `concessions_plaque` (mail plaque : code → nom). Les noms viennent du
  Référentiel : utilise-les tels quels dans le mail, n'en invente pas. Chaque
  source contient `entetes` (les 2 premières lignes de l'onglet : lis les colonnes
  **par leur nom**, jamais par position supposée) et `lignes` (uniquement les lignes du
  périmètre). Une source sans ligne = rien pour ce périmètre ce jour-là.
  `date_donnees` = date réelle des données (la plus ancienne trouvée).
- La maquette du mail (`maquette` dans le fichier de faits) : modèle de structure, de
  mise en page et de style. Reproduis sa structure et son HTML, avec les données du jour.
- Les règles métier, à lire avant de composer : les **fiches condensées** de
  `rapport/regles/` (elles résument les cadrages, ne lis pas `docs/CADRAGE*.md`) :
  - Toujours : `rapport/regles/commun.md` (rédaction de la synthèse, HTML email-safe).
  - Mail `vn` : `rapport/regles/vn.md`.
  - Mail `vo` : `rapport/regles/vo.md`.
  - Mail `apv` : `rapport/regles/apv.md`.
  - Mail `directeur` : `rapport/regles/directeur.md`, plus `vn.md`, `vo.md` et `apv.md`
    pour les icônes météo et ce qui est significatif dans chaque service.
  - Mail `plaque` : `rapport/regles/plaque.md`. Au niveau Plaque, le bloc APV remonte
    des compteurs de problèmes, pas du CA ni des objectifs, sauf les malfaçons et
    gestes commerciaux (montant hier, cumul du mois, % du CA MO du mois).
  - Seulement si un en-tête attendu par une fiche est introuvable dans les faits :
    dictionnaire des colonnes `docs/DATA_MAP_VN.md`, `docs/DATA_MAP_VO.md` ou
    `docs/DATA_MAP_APV.md`. En cas de doute non résolu, n'affiche pas la donnée.
  - En cas de contradiction entre une fiche et la maquette, la fiche l'emporte.

## Règles impératives

1. **Aucun chiffre inventé.** Chaque nombre du mail doit venir des faits. Tu peux
   arrondir, et faire les seuls calculs simples que les cadrages prévoient (somme,
   ratio, total Plaque pondéré). Une donnée absente s'écrit « non disponible ». Un
   contrôle automatique compare ensuite les nombres du mail aux faits et signale aux
   porteurs du projet ceux qu'il ne retrouve pas.
2. **Date des données dans l'en-tête** de chaque mail : « Données du JJ/MM/AAAA »,
   à partir de `date_donnees` du fichier de faits (pas de la date du jour).
3. **Noms réels** : les mails sont réels, n'anonymise rien (immatriculations, n° OR,
   noms de clients ou de réceptionnaires tels qu'ils figurent dans les faits).
4. **Blocs sans signal** : au niveau Service (vn, vo, apv), garder le bloc avec la
   mention « Rien à signaler » en italique ; au niveau Directeur et Plaque, omettre
   complètement le bloc (CADRAGE.md §7).
5. **Signaler le positif comme le négatif** quand c'est significatif.
6. **Icônes météo** : appliquer le barème du cadrage du service quand il existe
   (APV §12.6/§12.7, VO §15). Ne jamais présenter un score comme calculé par le
   Sheet s'il ne l'est pas.
7. Synthèse courte et factuelle, dossiers concrets cités, pas de jargon interne
   (noms d'onglets, codes de colonnes, « J-1 » en clair : « hier »).
8. **Largeur du mail (décidé le 2026-10-05, vaut pour tous les mails)** : les maquettes
   ont été passées à ce format ; s'il en reste une en largeur fixe (600 à 660 px), la
   règle prime sur elle. Le tableau conteneur principal doit
   être fluide jusqu'à 900 px : `<table role="presentation" width="100%" cellpadding="0"
   cellspacing="0" style="width:100%;max-width:900px;margin:0 auto;">`, entouré pour
   Outlook PC d'un tableau fixe en commentaire conditionnel
   (`<!--[if mso]><table role="presentation" width="900" align="center"><tr><td><![endif]-->`
   avant, `<!--[if mso]></td></tr></table><![endif]-->` après). Les tableaux internes
   passent en `width="100%"` (pas de largeur fixe en pixels) pour profiter de la place.

## Sorties (pour chaque mail composé)

- `build/mails/<identifiant>.html` : document HTML complet, email-safe, prêt à envoyer.
- `build/mails/<identifiant>.json` : `{"objet": "..."}` avec l'objet du mail :
  - vn / vo / apv : `Rapport quotidien VN — <nom_concession> — JJ/MM/AAAA` (VO, APV de même)
  - directeur : `Synthèse du jour — <nom_concession> — JJ/MM/AAAA`
  - plaque : `Synthèse <nom_plaque> — JJ/MM/AAAA` (ex. « Synthèse Plaque Hyundai »)
  (JJ/MM/AAAA = date des données.)
- La maquette illustre une autre concession (Renault Strasbourg) : reprends sa
  structure, jamais ses noms, chiffres ou dossiers.

Si un mail ne peut vraiment pas être composé (faits incohérents ou vides), n'écris pas
ses fichiers : l'étape d'envoi le signalera comme non envoyé.
