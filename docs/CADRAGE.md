# Cadrage global — Rapport quotidien VN / VO / APV

**Statut : BROUILLON — à relire et valider à deux avant tout développement.**
Dernière mise à jour : 2026-09-25.

Ce document couvre le cadrage **transverse** aux 3 services. Le détail propre à
chaque service vit dans son propre fichier, pour permettre à plusieurs personnes
de l'éditer en parallèle sans se marcher dessus :

- [`CADRAGE_VN.md`](CADRAGE_VN.md) — Véhicules Neufs
- [`CADRAGE_VO.md`](CADRAGE_VO.md) — Véhicules d'Occasion
- [`CADRAGE_APV.md`](CADRAGE_APV.md) — Après-Vente

## 1. Objectif

Chaque matin, envoyer aux responsables de service **VN**, **VO** et **APV** de chaque
concession un e-mail contenant :

- les chiffres de la veille (**stock**, **ventes**, **achats**) pour leur service ;
- une **détection d'anomalies** sur ces chiffres ;
- un **commentaire généré par IA** résumant la situation.

Cible à terme : diffusion sur **4 niveaux** (service → concession → plaque → siège),
soit environ **400 destinataires**. La V1 se limite au **niveau service**.

## 2. Contexte technique

Le calcul repose sur deux couches :

- **BigQuery** (`hess-data`, projet EU) : source de vérité brute (stocks, ventes,
  facturation atelier, etc.), déjà utilisée par les autres reportings HESS.
- **Google Sheets** : couche de calcul/formules qui transforme la donnée brute en
  chiffres "prêts à publier" (stock veille, ventes veille, achats veille) et,
  selon le service, un marqueur d'anomalie déjà qualifié.

Le rapport quotidien ne recalcule donc pas les KPI depuis zéro : il **lit les
résultats déjà calculés dans les Sheets**. Le détail de ce qui est prêt ou non par
service est dans les fichiers `CADRAGE_VN/VO/APV.md`.

### Sources de données (4 Google Sheets)

| Sheet | État | Détail |
|---|---|---|
| **Référentiel Concession** (`1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY`) | Existe, onglets `Concessions_Plaques`, `Mapping_Sources`, `Mapping_Import` + table Destinataires | Voir §4 ci-dessous |
| **Rapport quotidien APV** (`1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw`) | Existe | Voir `CADRAGE_APV.md` |
| **Rapport quotidien VO** (`1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU`) | Existe | Voir `CADRAGE_VO.md` |
| **Rapport quotidien VN** | Introuvable — à créer | Voir `CADRAGE_VN.md` |

~~Point de vigilance : un projet Apps Script vide nommé "Rapport Quotidien CG"
traîne dans le même dossier Drive, sans contenu.~~ **Supprimé (2026-09-08).**

## 3. Décisions transverses (2026-09-08)

- **Périmètre V1 : niveau service uniquement** (VN/VO/APV par concession). Les
  niveaux concession/plaque/siège et les ~400 destinataires viendront dans une
  itération ultérieure.
- **Destinataires** : gérés dans le Google Sheet **Référentiel Concession**
  (pas d'annuaire externe) — table déjà existante, voir §4.
- **Collaboration** : le projet vit dans ce dépôt GitHub privé
  (`hess-rapport-quotidien-vn-vo-apv`), partagé entre les deux porteurs du projet.
  Rien n'est construit sans validation commune préalable.
- **Détection d'anomalies** : effectuée **en amont, dans les Google Sheets**
  (formules), pas par l'orchestrateur. L'orchestrateur consomme des chiffres déjà
  qualifiés, il ne recalcule rien. La logique métier reste dans les Sheets,
  pilotable par vous deux sans toucher au code.
- **Limite technique actée** : Claude n'a aucun outil pour éditer un Google Sheet
  existant (cellules, formules, connecteur BigQuery/Connected Sheets) —
  seulement le lire, ou créer un fichier Drive entièrement nouveau. **Toute
  construction dans un Sheet est donc faite par Quentin/Corentin, jamais par
  Claude**, pour tout le projet.
- **Outil de lecture des Sheets : `gws` (Google Workspace CLI) obligatoire,
  toujours** (2026-09-10). Remplace l'ancien outil Drive (conversion du fichier
  entier en texte), qui tronquait silencieusement les gros fichiers multi-
  onglets sans erreur explicite. `gws` lit une plage précise d'un onglet via
  l'API Sheets (`gws sheets +read --spreadsheet ID --range "Onglet!A1:Z100"`,
  ou `gws sheets spreadsheets get --params '{"spreadsheetId":"ID"}'` pour
  lister les onglets) — fiable, pas de troncature silencieuse. Limite réelle :
  un résultat de plusieurs Mo (au-delà d'un ou deux milliers de lignes) reste
  trop volumineux pour être chargé dans le contexte de Claude d'un coup — d'où
  le principe des onglets/fichiers "prêts à publier" déjà réduits (agrégats +
  top N) plutôt que des extraits bruts. Setup : authentification OAuth2 scope
  `spreadsheets.readonly` uniquement (`gws auth login --readonly --services
  sheets`), client OAuth du projet GCP `controlegestion`
  (`C:\Users\quentinmichel\.config\gws\client_secret.json`), compte
  `quentinmichel@hessautomobile.com`. L'API Google Sheets doit être activée sur
  le projet GCP utilisé, et le compte doit avoir le rôle IAM "Service Usage
  Consumer" dessus.
  **Incident (2026-09-18)** : le binaire `gws` original a été perdu suite à un
  crash/réinstallation de l'appli Claude côté Corentin — il vivait dans un
  espace propre à une session de l'appli, pas dans le profil Windows normal
  (seule la config OAuth dans `~/.config/gws` a survécu, elle est hors de
  portée de l'appli). **Recréé le jour même, versionné dans ce dépôt sous
  [`tools/gws`](../tools/gws) cette fois** (voir son `README.md` pour
  l'installation) — précisément pour ne plus dépendre d'un espace qu'une
  réinstallation de l'appli peut effacer. Même syntaxe de commandes que
  ci-dessus, aucun changement d'usage. **À installer aussi côté Quentin**
  (`cd tools/gws && python -m pip install -e .` puis `gws auth login
  --readonly --services sheets`) — l'ancien token de Corentin n'est pas
  réutilisable par un autre compte/machine.
- **Orchestrateur : tâche planifiée Claude Code**, pas GitHub Actions. Choix
  assumé malgré la recommandation inverse (GitHub Actions aurait tourné
  indépendamment de tout compte Claude Code, avec code versionné/review-able à
  deux). Conséquences acceptées :
  - L'automatisation dépend d'un **compte Claude Code qui reste actif** dans la
    durée (celui qui héberge la tâche planifiée) — pas un cron autonome.
  - Le **repo GitHub sert de documentation et de mémoire du projet**, mais
    n'exécute rien lui-même.
  - **Expéditeur des mails : boîte Gmail HESS dédiée**, pas un compte personnel
    — à créer et connecter à la session qui porte la tâche planifiée (action non
    faite à ce jour, voir §6).
  - **Commentaire IA natif** (pas de clé API Anthropic séparée à gérer), format
    **court et factuel (2-3 phrases)**.
  - **Principe de lisibilité et pertinence du mail (validé 2026-09-10, affiné
    2026-09-15 suite au retour du patron sur la V1 : "il faut encore bien
    améliorer le prompt pour que l'email soit facile à lire, pertinent")** —
    ce principe ne se limite pas au commentaire IA : c'est le critère de
    jugement pour **tout le contenu du mail** (quoi inclure, à quel niveau de
    détail). C'est le commentaire qui en dépend le plus directement, parce
    qu'il est généré et non contraint par une formule figée comme le reste du
    mail — d'où les règles ci-dessous, formulées pour lui mais applicables à
    toute décision de contenu. Le commentaire ne doit **pas répéter des
    chiffres déjà visibles** dans les blocs structurés du mail — sa valeur
    ajoutée est la **synthèse croisée entre blocs**, pas un résumé.
    Concrètement :
    1. **Chercher les recoupements** entre blocs (un même véhicule/dossier qui
       apparaît dans plusieurs blocs — ex. noté en anomalie achat ET encore sans
       prix en stock 7 jours plus tard) — c'est le signal le plus utile, souvent
       invisible en lisant les tableaux séparément. **Pas cantonné à l'axe
       achat↔stock** (décidé 2026-09-15) : les Leads (ex. leads non traités
       depuis J-1 — affaire potentiellement perdue) et les Anomalies ventes
       doivent être couverts par le commentaire si c'est le signal le plus
       pertinent du jour pour la concession, pas seulement en cas
       d'illustration achat/stock. Le commentaire suit le signal le plus
       fort du jour, quel que soit le bloc d'où il vient.
    2. **Nommer des priorités concrètes** (immatriculation, dossier) plutôt que
       des constats généraux ("il y a un excès de stock").
    3. **Transformer une tendance en risque prospectif actionnable** ("sans
       action, l'écart va se creuser") plutôt qu'un simple constat statistique.
    4. **Ne jamais citer la note brute d'anomalie** (ex. "noté 4/10", "10/10")
       (décidé 2026-09-11) — c'est un score interne au calcul, pas une
       information utile au lecteur ; décrire le problème concret (l'écart,
       le délai, le manque) à la place.
    5. **Limite stricte de longueur** (décidé 2026-09-15) : **2 phrases
       maximum, ~350 caractères au total** — pas juste "court" comme objectif
       vague. Le format visé "2-3 phrases" avait dérivé en pratique vers 2
       paragraphes denses (test Saverne du 11/09) faute de limite chiffrée.
    6. **Une phrase = un signal** (décidé 2026-09-15) : ne pas chaîner
       plusieurs recoupements différents dans une même phrase au fil de
       virgules/points-virgules. Grouper dans une même phrase plusieurs
       véhicules touchés par le **même** signal reste acceptable (ex. deux
       Clio toutes deux sans prix après signalement achat) ; mélanger deux
       sujets différents (ex. anomalie achat + tendance ventes) ne l'est pas.
    7. **Mener par l'action, pas par le constat** (décidé 2026-09-15) :
       commencer par ce qu'il faut faire ("à publier en priorité : ...")
       plutôt que par une observation neutre ("le problème n'a pas été
       traité en aval").
    8. **Caler la densité sur le volume réel, ne pas remplir** (décidé
       2026-09-15) : si une seule anomalie est vraiment solide (concession à
       faible volume, par exemple), ne pas ajouter un deuxième point plus
       faible juste pour occuper les phrases disponibles — une phrase nette
       vaut mieux que deux dont une bancale. **Ceci ne s'applique pas quand
       deux signaux sont réellement forts** (précisé 2026-09-15) : dans ce
       cas, deux phrases pour deux signaux distincts (un par bloc, cf. règle
       6), dans la limite des 2 phrases de la règle 5 — la règle 8 interdit
       de *forcer* un deuxième point faible, pas d'en garder un deuxième qui
       est légitimement fort.
    9. **Ne jamais utiliser le vocabulaire de classification interne** ("à
       vérifier", "à corriger", "à signaler"...) comme mot du texte, même en
       tête de phrase pour donner le ton (décidé 2026-09-25, suite à un
       "À corriger :" resté dans la Synthèse VN alors que la règle 4
       l'interdit déjà pour les notes chiffrées) — ces libellés servent au
       tri interne dans les Sheets (cf. `CADRAGE_VN.md` §5), jamais à
       l'affichage destinataire. Décrire le fait/l'action directement
       ("le dossier affiche une marge de -2 123€...") plutôt que de
       préfixer par la catégorie qui l'a fait remonter. **Étendu le
       2026-09-25** : la même règle vaut pour le vocabulaire du
       classificateur Tendance (Bloc 2/9 Commandes & Facturations) — ne pas
       écrire "hausse confirmée"/"baisse confirmée"/"sans que l'écart soit
       confirmé" dans le texte, ce sont des états internes du calcul (cf.
       `CADRAGE_VN.md` §2), pas des mots pour le lecteur. Dire le chiffre et
       la comparaison directement ("22 commandes contre un rythme habituel
       de 32 par semaine, léger retrait de 9,5% par rapport à l'an
       dernier") plutôt que le résultat de la classification. Plus
       généralement : **toute phrase de synthèse doit rester compréhensible
       par quelqu'un qui ne connaît pas la mécanique de calcul** — un bon
       test est de se relire en se demandant si un lecteur qui n'a jamais
       vu les Sheets comprendrait la phrase du premier coup.
    Exemple qui a fonctionné (Mulhouse, 2026-09-10) : identifier que
    `FN-627-YH` était toujours sans prix/destination en stock alors qu'il
    avait déjà été signalé à l'achat pour des écarts de prix/km/date, plutôt
    que de relister séparément l'anomalie achat et le chiffre "sans prix"
    déjà visibles ailleurs dans le mail.
    Avant/après sur Renault Saverne (2026-09-15, règles 5-8 appliquées) :
    - *Avant* (2 paragraphes, note citée, 2 signaux dont un faible) : "Deux
      dossiers montrent que le problème identifié à l'achat n'est pas traité
      en aval : `GH-907-MT`... noté 4/10... ; `GL-384-ER`... même note...
      Par ailleurs, l'excès de Sandero essence... s'ajoute à une tendance
      ventes en repli de -24%..."
    - *Après* (1 signal solide, action en tête, ~235 caractères) : "À publier
      en priorité : les Clio `GH-907-MT` et `GL-384-ER`, signalées à l'achat
      pour des écarts de prix/km/délai, sont toujours sans prix de vente 5 à
      7 jours après. Sans correction, ces deux dossiers immobilisent du stock
      déjà vendable." — la tendance ventes du jour (-8% vs -4% Plaque) a été
      volontairement écartée, jugée trop faible pour être un vrai deuxième
      signal (règle 8).
- **Historisation : oui**, dans un Google Sheet dédié (`Historique_Envois` —
  date, concession, service, destinataire, anomalie détectée, statut d'envoi).
- **Cas `Service = VN_VO`** (une personne gère VN et VO pour sa concession) :
  **deux mails séparés**, pas de cas particulier à coder.
- **Priorité de développement (2026-09-08) : VO en premier**, avant APV (qui est
  pourtant déjà prêt côté données) et VN (pas encore créé) — choix assumé du
  porteur du projet. Détail dans `CADRAGE_VO.md`.

## 4. Modèle de données — destinataires (existant, confirmé)

Le Référentiel Concession contient une table avec les colonnes :

| Code_Concession | Service | Nom | Email | Niveau de diffusion |
|---|---|---|---|---|
| `BMW_BELFORT` | `Atelier` | Christophe Maradene | christophemaradene@... | `Service` |
| `BMW_DOLE;BMW_LONS` | `Concession` | Cédric Dufour | cedricdufour@... | `Concession` |
| `PLQ_BMW;PLQ_BMW_MOTO` | `Plaque` | Christophe Grunfelder | christophegrunfelder@... | `Plaque` |
| `*` | `Concession` | Corentin Laas | corentinlaas@... | `Concession` |

Points de structure pour le parsing (pas de rework de format nécessaire) :

- **`Code_Concession` peut contenir plusieurs codes séparés par `;`** (une
  personne peut couvrir plusieurs concessions/plaques). → il faut **exploser**
  cette colonne (une ligne par code) avant de joindre au reste du référentiel.
- **`Code_Concession = "*"`** (Corentin Laas, Quentin Michel) : **ce sont les 2
  adresses de test des porteurs du projet, pas des destinataires réels.**
  Pendant les pilotes (VO : Plaque Renault, voir `CADRAGE_VO.md`), ces 2 adresses
  reçoivent les mails à la place des vrais destinataires. À terme, elles
  recevront la diffusion niveau **siège** — **la colonne `Niveau de diffusion`
  de ces 2 lignes est donc probablement à corriger de `Concession` vers `Siège`**
  quand le multi-niveaux sera construit (pas bloquant pour le V1).
- **Le libellé `Service` utilisé pour l'APV est `Atelier`**, pas `APV`. Pour le
  V1, les valeurs de `Service` à filtrer sont : `VN`, `VO`, `Atelier` (APV), et
  `VN_VO`.
- Les lignes `Niveau de diffusion = Concession` et `Plaque` existent déjà dans la
  donnée mais sont **hors périmètre V1**.

Table de faits quotidienne cible (par concession × service × date), lue depuis
les Sheets (déjà calculée + anomalie déjà qualifiée) :

| Champ | Origine |
|---|---|
| `Date` | J-1 (date du rapport) |
| `Code_Concession`, `Service` | Référentiel |
| `Stock_veille`, `Ventes_veille`, `Achats_veille` | Sheet du service, déjà calculé |
| `Anomalie(s)` | Sheet du service, déjà qualifiée par les formules |

## 5. Architecture générale

```
BigQuery (source brute)
        │
        ▼
Google Sheets (formules : valeurs veille + anomalie déjà qualifiée, par service)
        │
        ▼
Orchestrateur quotidien (matin)
   ├─ 1. LIT les Sheets (valeurs + anomalies déjà calculées, rien à recalculer)
   ├─ 2. GÉNÈRE le commentaire IA à partir de ces valeurs
   └─ 3. ENVOIE un e-mail par (concession × service), aux destinataires du
        Référentiel Concession filtrés sur Niveau de diffusion = Service
        │
        ▼
Responsables de service VN / VO / Atelier (APV)
```

## 6. Contrainte HTML des mails — "email-safe" (2026-09-25)

**Découverte lors du premier envoi de test réel** du projet (Renault
Strasbourg, VN/VO/APV, 2026-09-25) — les 3 maquettes existantes
(`docs/mockup_email_*.html`) utilisent des **variables CSS** (`var(--navy)`,
`var(--gold)`...) et du **flexbox/grid** pour la mise en page. Ces deux
techniques ne sont **pas fiables dans les clients mail** (Gmail en tête,
Outlook desktop encore moins) : elles sont silencieusement ignorées, et le
mail arrive sans aucune mise en forme, en texte brut.

Ce problème n'avait jamais été détecté avant car les maquettes n'avaient été
vues qu'en rendu Artifact/navigateur (qui supporte tout ça sans problème) —
jamais en rendu réel de client mail, puisque c'était le tout premier envoi
réel du projet (aucune des "simulations de mail" précédentes documentées
dans `CADRAGE_VO.md` §13 n'avait été réellement envoyée).

**Règles HTML "email-safe" à appliquer à tout mail réellement envoyé** (les
3 services sont concernés, pas seulement celui qui a servi de test) :
1. **Pas de variables CSS** (`var(--x)`) — toutes les couleurs en valeurs
   littérales (hex), répétées à chaque usage plutôt que centralisées.
2. **Pas de flexbox ni de grid** — mise en page en `<table>` HTML (le seul
   système de layout fiable sur tous les clients mail, Outlook desktop en
   particulier, qui utilise le moteur de rendu Word).
3. **Styles en ligne** (`style="..."` sur chaque élément) plutôt que des
   classes CSS dans un bloc `<style>` — certains clients strippent les
   balises `<style>`.
4. **Pas de police externe** (le `<link>` Google Fonts des maquettes n'est
   pas fiable en email, souvent bloqué) — police système
   (`Arial, Helvetica, sans-serif`).
5. **Icônes météo en emoji Unicode** (&#9728; &#9729; ...) plutôt qu'en SVG
   inline — le SVG n'est pas supporté par de nombreux clients mail.

**Conséquence** : `docs/mockup_email_vn.html` et `docs/mockup_email_vo.html`
ont été **remplacés le 2026-09-25** par leur conversion email-safe (données
réelles Renault Strasbourg — VIN/immatriculations, pas de donnée nominative,
cohérent avec la pratique déjà en place sur ces 2 fichiers). Côté APV,
`docs/mockup_email_apv_v2.html` (structure indépendante de Corentin) est
**conservé tel quel** ; sa conversion email-safe vit dans un fichier séparé,
`docs/mockup_email_apv_v2_safe.html`, avec les **noms de clients et de
salariés anonymisés** (Client A/B/..., Réceptionnaire A/B/..., Mécanicien
A/B) avant commit — seule la donnée nominative est retirée, les
immatriculations/n° OR restent réels. `docs/mockup_email_apv.html` (version
d'origine, Mulhouse) reste également en place, non reconverti pour
l'instant. Ces 3 fichiers email-safe sont désormais **la base à partir de
laquelle continuer** (structure de layout en tableaux, à conserver pour
toute évolution future du contenu).

**Validé (2026-09-25)** : les 3 mails reconvertis (avant anonymisation
côté APV) ont été envoyés réellement (via un compte Gmail connecté à la
session, pas encore la boîte HESS dédiée — voir question ouverte
ci-dessous) à Quentin et Corentin pour Renault Strasbourg, et confirmés
correctement affichés par le destinataire.

## 7. Mail Directeur de concession — niveau 2 de diffusion (2026-09-25)

Premier mail construit pour le niveau **Concession** de la diffusion à 4
niveaux (§1) — au-dessus du niveau Service (V1, seul niveau construit
jusqu'ici), en dessous de Plaque/Siège (pas encore abordés).

**Principe validé (2026-09-25)** : contrairement aux mails Service, le
Directeur de concession ne reçoit pas le détail complet des 3 activités,
mais une synthèse condensée qui ne signale que l'essentiel et le
significatif :
- **Structure fixe : bloc VN → bloc VO → bloc APV**, dans cet ordre.
- **Un bloc entier est omis** si le service correspondant n'a rien de
  significatif à signaler ce jour-là — contrairement au niveau Service (où
  l'absence d'anomalie reste affichée en italique, ex. "Rien à signaler"
  dans `CADRAGE_VO.md` §11), ici c'est un silence complet, pas de bloc du
  tout. **Non testé sur ce mockup** : les 3 services avaient un signal réel
  pour Renault Strasbourg le 23/09 — le comportement d'omission reste à
  valider sur un cas réel où un service n'a rien à signaler.
- **Une Synthèse IA cross-service ouvre le mail**, avant les 3 blocs —
  distincte des Synthèse par service : elle recoupe/priorise entre VN, VO
  et APV, alors que les Synthèse Service ne travaillent qu'à l'intérieur
  d'un seul bloc. Une phrase par service ayant un signal, même ordre
  VN→VO→APV, mêmes règles de rédaction que §3 (factuel, dossiers concrets,
  pas de jargon interne).
- Chaque bloc service reste factuel et cite des dossiers concrets
  (immatriculation/VIN/n° OR), mais **sans tableau détaillé** — condensé en
  un paragraphe de 2 phrases maximum, précédé d'un badge résumant le
  chiffre clé du bloc.
- **Signaler le positif comme le négatif** (décidé 2026-09-25) : ne pas se
  limiter aux points d'alerte — une tendance positive notable (ex.
  facturations VO +17% vs l'an dernier) a sa place dans le bloc au même
  titre qu'un point négatif, dès lors qu'elle est significative.
- Réutilise les icônes météo déjà calculées par chaque service (pas de
  nouveau score recalculé pour ce niveau) — affichées en 3 mini-cartes en
  tête de mail, chacune avec le fait le plus marquant du service en une
  ligne.

Maquette (données réelles Renault Strasbourg, 23/09/2026, email-safe dès
la première version — règles §6 appliquées d'emblée) :
[`docs/mockup_email_directeur.html`](mockup_email_directeur.html).

## 8. Questions ouvertes transverses

1. **Création de la boîte Gmail HESS dédiée** — qui la crée (IT ?), quel nom
   d'adresse, et comment la connecter à la session qui porte la tâche planifiée ?
   Le test du 2026-09-25 (§6) a été envoyé depuis un compte Gmail connecté à
   la session en attendant, pas la boîte dédiée.
2. **Correction à prévoir (non bloquante V1)** : les lignes `Code_Concession = "*"`
   dans le Référentiel devront passer de `Niveau de diffusion = Concession` à
   `Siège` quand le multi-niveaux sera construit — voir §4.
3. ~~Reconversion email-safe des 3 maquettes~~ **fait (2026-09-25)** pour
   VN, VO (fichiers remplacés) et APV (`mockup_email_apv_v2_safe.html`,
   anonymisé) — voir §6.
4. **Test du mail Directeur sur un cas où un service n'a rien à signaler**
   (voir §7) — le mockup Renault Strasbourg a les 3 services actifs, donc
   la logique d'omission de bloc n'a encore jamais été vérifiée en
   pratique.

Les questions ouvertes spécifiques à un service sont dans son fichier dédié.

## 9. Prochaines étapes

Le développement priorise **VO** — voir `CADRAGE_VO.md` pour le détail. APV et VN
suivront une fois VO validé en pilote.

1. Construire la suite du projet (contenu, blocs restants, intégration
   Gmail dédiée) **à partir des 3 maquettes email-safe** (§6) plutôt que
   des anciennes versions à variables CSS/flex/grid.
