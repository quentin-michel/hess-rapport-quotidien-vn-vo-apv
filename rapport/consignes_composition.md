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
- Les règles métier, à lire avant de composer :
  - Toujours : `docs/CADRAGE.md` §3 (règles de rédaction de la synthèse) et §6 (HTML
    « email-safe » : tableaux et styles en ligne uniquement, pas de flex/grid, pas de
    variables CSS, pas de police web).
  - Mail `vn` : `docs/CADRAGE_VN.md` §6 (maquette mail VN) et les blocs §1-5.
  - Mail `vo` : `docs/CADRAGE_VO.md` §14 (format du mail), §15 (icône météo), blocs §3-11.
  - Mail `apv` : `docs/CADRAGE_APV.md` §12 (formalisation du mail, icônes §12.6/§12.7),
    §14 (règle de l'effet de mix sur la marge PR interne) et §15 (malfaçons et gestes
    commerciaux : bloc du mail et points météo).
  - Mail `directeur` : `docs/CADRAGE.md` §7.
  - Mail `plaque` : `docs/CADRAGE.md` §8. Au niveau Plaque, le bloc APV remonte des
    compteurs de problèmes (encours, pièces à perte, forfaits, remises…), pas du CA ni
    des objectifs. Seule exception, aux niveaux Directeur et Plaque : les malfaçons et
    gestes commerciaux s'affichent en montant (hier, cumul du mois) et en % du CA MO du
    mois (`docs/CADRAGE_APV.md` §15).
  - Dictionnaire des colonnes : `docs/DATA_MAP_VN.md`, `docs/DATA_MAP_VO.md`,
    `docs/DATA_MAP_APV.md`.

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
