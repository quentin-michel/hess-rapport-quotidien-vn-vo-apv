# Cadrage global — Rapport quotidien VN / VO / APV

**Statut : BROUILLON — à relire et valider à deux avant tout développement.**
Dernière mise à jour : 2026-09-08.

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

## 6. Questions ouvertes transverses

1. **Création de la boîte Gmail HESS dédiée** — qui la crée (IT ?), quel nom
   d'adresse, et comment la connecter à la session qui porte la tâche planifiée ?
2. **Correction à prévoir (non bloquante V1)** : les lignes `Code_Concession = "*"`
   dans le Référentiel devront passer de `Niveau de diffusion = Concession` à
   `Siège` quand le multi-niveaux sera construit — voir §4.

Les questions ouvertes spécifiques à un service sont dans son fichier dédié.

## 7. Prochaines étapes

Le développement priorise **VO** — voir `CADRAGE_VO.md` pour le détail. APV et VN
suivront une fois VO validé en pilote.
