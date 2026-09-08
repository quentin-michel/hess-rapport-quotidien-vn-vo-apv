# Cadrage — Rapport quotidien VN / VO / APV

**Statut : BROUILLON — à relire et valider à deux avant tout développement.**
Dernière mise à jour : 2026-09-08.

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
  chiffres "prêts à publier" (stock veille, ventes veille, achats veille).

Le rapport quotidien ne doit donc pas recalculer les KPI depuis zéro : il **lit les
résultats déjà calculés dans les Sheets** (ou, si plus simple/robuste, requête
directement les mêmes tables BigQuery — à trancher, voir §6).

### Sources de données (4 Google Sheets)

| Sheet | État constaté (2026-09-08) | Rôle |
|---|---|---|
| **Référentiel Concession** | Existe (`1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY`), onglets `Concessions_Plaques`, `Mapping_Sources`, `Mapping_Import` | Référentiel concession ↔ plaque ↔ codes source BigQuery. **Doit accueillir un nouvel onglet `Destinataires`** (voir §4). |
| **Rapport quotidien APV** | Existe (`1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw`) | **Couche "prêt à publier" déjà en place** : un tableau récapitulatif quotidien avec `Nb OR clôturés J-1`, `CA MO net HT J-1`, `CA moyenne mobile 4 sem.`, `Écart % CA`, **`Alerte écart CA`**, `CA PR interne/externe Net HT J-1`, `Écart % CA PR Externe`, **`Alerte écart CA PR Externe`**, `Productivité J-1`, `Écart % Productivité`, **`Alerte productivité basse`**, `Efficience J-1`. Valeurs observées : `ALERTE`, `ALERTE PRODUCTIVITE BASSE`. **L'orchestrateur peut lire ce tableau tel quel.** |
| **Rapport quotidien VO** | Existe (`1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU`) | **Couche "prêt à publier" absente** (vérifié 2026-09-08, 11 tableaux inspectés) : pas de valeurs J-1, pas de colonne anomalie sur données calculées — seulement des flags qualitatifs isolés (`Marge négative`, `Analyse santé` type SAIN/CORRECT, `Action recommandée`) répartis sur des tableaux différents (qualité stock, couverture, transferts, santé stock). **Cette couche reste à construire côté Sheet avant que l'orchestrateur puisse lire quoi que ce soit d'exploitable pour VO** — bloquant pour le V1 sur ce service. |
| **Rapport quotidien VN** | **Introuvable sur le Drive — à créer** | Décision prise (2026-09-08) : il faut le créer, sur le modèle de VO/APV. Reste une action à planifier (qui, quand, avec quelles sources BigQuery pour le VN) — pas encore fait. |

~~Point de vigilance : un projet Apps Script vide nommé "Rapport Quotidien CG"
traîne dans le même dossier Drive, sans contenu.~~ **Supprimé (2026-09-08).**

## 3. Décisions déjà prises (2026-09-08)

- **Périmètre V1 : niveau service uniquement** (VN/VO/APV par concession). Les
  niveaux concession/plaque/siège et les ~400 destinataires viendront dans une
  itération ultérieure.
- **Destinataires** : gérés dans un nouvel onglet du Google Sheet
  **Référentiel Concession** (pas d'annuaire externe).
- **Collaboration** : le projet vit dans ce dépôt GitHub privé
  (`hess-rapport-quotidien-vn-vo-apv`), partagé entre les deux porteurs du projet.
  Rien n'est construit sans validation commune préalable.
- **Détection d'anomalies** : effectuée **en amont, dans les Google Sheets**
  (formules), pas par l'orchestrateur. L'orchestrateur consomme des chiffres déjà
  qualifiés (valeur + anomalie éventuelle déjà identifiée), il ne recalcule rien.
  → simplifie fortement le pipeline (voir §5) et **ferme la question ouverte sur la
  définition d'anomalie** : la logique métier reste dans les Sheets, pilotable par
  vous deux sans toucher au code.
- **Destinataires : déjà en place**, pas besoin de créer un onglet — voir §4.
- **Orchestrateur : tâche planifiée Claude Code**, pas GitHub Actions (2026-09-08).
  Choix assumé malgré la recommandation inverse (GitHub Actions aurait tourné
  indépendamment de tout compte Claude Code, avec code versionné/review-able à
  deux). Conséquences à accepter, documentées comme risques ci-dessous plutôt que
  comme questions ouvertes :
  - L'automatisation dépend d'un **compte Claude Code qui reste actif** dans la
    durée (celui qui héberge la tâche planifiée) — pas un cron autonome.
  - Le **repo GitHub sert de documentation et de mémoire du projet** (ce cadrage,
    décisions, éventuels scripts/prompts de référence), mais **n'exécute rien
    lui-même** : pas de logs d'exécution centralisés ni de review par PR du
    comportement réel du jour au jour.
  - ~~L'expéditeur des mails sera le compte Gmail connecté à la session Claude
    Code...~~ **Tranché (2026-09-08) : boîte Gmail HESS dédiée**, pas un compte
    personnel — à créer et connecter à la session qui porte la tâche planifiée.
  - Le **commentaire IA est natif** (pas de clé API Anthropic séparée à gérer) —
    ça ferme la partie "quel modèle/API" de la question §6.7.

## 4. Modèle de données — destinataires (déjà existant, confirmé)

Le Référentiel Concession contient déjà une 3ᵉ table avec les colonnes :

| Code_Concession | Service | Nom | Email | Niveau de diffusion |
|---|---|---|---|---|
| `BMW_BELFORT` | `Atelier` | Christophe Maradene | christophemaradene@... | `Service` |
| `BMW_DOLE;BMW_LONS` | `Concession` | Cédric Dufour | cedricdufour@... | `Concession` |
| `PLQ_BMW;PLQ_BMW_MOTO` | `Plaque` | Christophe Grunfelder | christophegrunfelder@... | `Plaque` |
| `*` | `Concession` | Corentin Laas | corentinlaas@... | `Concession` |

Points de structure à noter pour le parsing (pas de rework de format nécessaire,
juste à gérer correctement) :

- **`Code_Concession` peut contenir plusieurs codes séparés par `;`** (une personne
  peut couvrir plusieurs concessions/plaques — ex. `OPEL_BARLEDUC;OPEL_STDIZIER;OPEL_VERDUN;TOY_BARLEDUC;TOY_STDIZIER;TOY_VERDUN`).
  → il faut **exploser** cette colonne (une ligne par code) avant de joindre au reste
  du référentiel.
- **`Code_Concession = "*"`** (Corentin Laas, Quentin Michel) : **ce sont les 2
  adresses de test des porteurs du projet, pas des destinataires réels.**
  Décision (2026-09-08) : remplacer l'étoile par des codes de concessions de test
  choisis par eux, pour recevoir les mails pendant le développement/la recette. À
  terme (itération multi-niveaux), ces 2 adresses recevront la diffusion niveau
  **siège**, pas niveau Concession comme actuellement indiqué — **la colonne
  `Niveau de diffusion` de ces 2 lignes est donc probablement à corriger de
  `Concession` vers `Siège`** dans le Référentiel (à faire quand le multi-niveaux
  sera construit, pas bloquant pour le V1).
- **Le libellé `Service` utilisé pour l'APV est `Atelier`**, pas `APV`. Pour le V1
  (niveau Service), les valeurs de `Service` à filtrer sont : `VN`, `VO`, `Atelier`
  (APV), et `VN_VO` (une personne gérant à la fois VN et VO pour sa concession — le
  mail lui sera-t-il envoyé deux fois, une par service, ou une fois consolidé ? →
  question à trancher, cf. §6).
- Les lignes `Niveau de diffusion = Concession` et `Plaque` existent déjà dans la
  donnée mais sont **hors périmètre V1** (V1 = `Niveau de diffusion = Service`
  uniquement) — elles serviront telles quelles pour l'itération suivante, sans
  retravail de structure.

Table de faits quotidienne (par concession × service × date) — lue depuis les
Sheets (déjà calculée + anomalie déjà qualifiée) :

| Champ | Origine |
|---|---|
| `Date` | J-1 (date du rapport) |
| `Code_Concession`, `Service` | Référentiel |
| `Stock_veille` | Sheet du service, déjà calculé |
| `Ventes_veille` | Sheet du service, déjà calculé |
| `Achats_veille` | Sheet du service, déjà calculé |
| `Anomalie(s)` | Sheet du service, **déjà qualifiée par les formules** — l'orchestrateur la lit telle quelle, ne la recalcule pas |

Reste à localiser précisément, dans Rapport quotidien VO/APV, **où** (quel onglet,
quelle plage) vivent ces valeurs "prêtes à publier" + le marqueur d'anomalie — à
faire une fois l'orchestrateur choisi (§6.1), pour ne pas lire une plage à l'aveugle.

## 5. Architecture (simplifiée — décision du 2026-09-08)

La détection d'anomalie étant déjà faite côté Sheets, l'orchestrateur n'a plus que
3 responsabilités :

```
BigQuery (source brute)
        │
        ▼
Google Sheets (formules : stock/ventes/achats veille + anomalie déjà qualifiée)
        │
        ▼
Orchestrateur quotidien (matin)
   ├─ 1. LIT les Sheets (valeurs + anomalies déjà calculées, rien à recalculer)
   ├─ 2. GÉNÈRE le commentaire IA à partir de ces valeurs
   └─ 3. ENVOIE un e-mail par (concession × service), aux destinataires du
        Référentiel Concession filtrés sur Niveau de diffusion = Service
        │
        ▼
Responsables de service VN / VO / Atelier(APV)
```

Le **moteur** est tranché (§3) : tâche planifiée Claude Code.

## 6. Questions ouvertes (bloquantes avant développement)

~~1. Orchestrateur d'exécution~~ **Tranché (2026-09-08) : tâche planifiée Claude Code — voir §3.**
~~2. Expéditeur de l'e-mail~~ **Tranché (2026-09-08) : boîte Gmail HESS dédiée — voir §3.**
~~3. Lignes `Code_Concession = "*"`~~ **Tranché (2026-09-08) : ce sont les adresses de test des porteurs du projet — voir §4.**
~~4. Cas `Service = VN_VO`~~ **Tranché (2026-09-08) : deux mails séparés (VN et VO), pas de cas particulier à coder.**
~~5. Commentaire IA (ton)~~ **Tranché (2026-09-08) : court et factuel, 2-3 phrases.**
~~6. Historisation~~ **Tranché (2026-09-08) : oui, dans un Google Sheet dédié (`Historique_Envois` — date, concession, service, destinataire, anomalie détectée, statut d'envoi).**

**Nouveau blocage découvert (2026-09-08, exploration des sheets VO/APV) :**
**APV a déjà toute la couche "prêt à publier" + anomalies** (tableau récapitulatif
avec J-1, moyennes mobiles, écarts %, flags `Alerte...` — voir §2). **VO ne l'a
pas** : aucune valeur J-1, aucune colonne anomalie sur données calculées. Ça veut
dire concrètement :
- Le service **APV peut passer en développement dès maintenant** (l'orchestrateur
  a une source fiable à lire).
- Les services **VO et VN sont bloqués** tant que cette couche de calcul (valeurs
  veille + règles d'anomalie, en formules Sheets) n'est pas construite — c'est un
  travail Sheets à part entière, pas du développement de l'orchestrateur.

1. **Construire la couche "prêt à publier" + anomalies dans Rapport quotidien VO**
   (sur le modèle du tableau récapitulatif d'APV) — qui s'en charge, avec quelles
   règles de seuil/moyenne mobile pour le stock/ventes/achats VO ?
2. **Créer Rapport quotidien VN** (décidé le 2026-09-08, pas encore fait) — sur le
   modèle de VO/APV, **avec cette même couche "prêt à publier" + anomalies dès la
   création** plutôt qu'en 2 temps. Sources/mappings BigQuery pour le Neuf à
   déterminer. **Action à exécuter uniquement sur accord explicite.**
3. **Emplacement exact du tableau récapitulatif APV** (onglet, plage précise) — à
   pointer avant de coder la lecture (le nom de l'onglet n'a pas pu être récupéré
   par l'export texte, seuls les en-têtes de colonnes sont connus).
4. **Création de la boîte Gmail HESS dédiée** — qui la crée (IT ?), quel nom
   d'adresse, et comment la connecter à la session qui porte la tâche planifiée ?
5. **Correction à prévoir (non bloquante V1)** : les lignes `Code_Concession = "*"`
   dans le Référentiel devront passer de `Niveau de diffusion = Concession` à
   `Siège` quand le multi-niveaux sera construit — voir §4.

## 7. Prochaines étapes

**Décision (2026-09-08) : le prototype V1 porte sur VO en premier** (pas APV,
malgré sa couche déjà prête — choix assumé du porteur du projet).

**Règle explicite pour cette phase : je ne touche à aucun Google Sheet pour
l'instant.** Quentin construit lui-même la couche "prêt à publier" + anomalies
dans Rapport quotidien VO (formules, structure de l'onglet récapitulatif, sur le
modèle du tableau APV identifié en §2/§6). Je n'édite ni ne crée rien côté Sheets
tant que ce n'est pas explicitement redemandé.

1. Quentin ajoute les formules/la structure dans Rapport quotidien VO.
2. Pendant ce temps, à définir ensemble : sur quoi je travaille en parallèle (ex.
   préparer le squelette de code de l'orchestrateur sans le connecter à rien,
   affiner le prompt du commentaire IA, ou rien tant que le sheet n'est pas prêt).
3. Une fois la couche VO prête et son emplacement (onglet/plage) communiqué : je
   branche la lecture, le commentaire IA et l'envoi pour le service VO uniquement,
   sur les adresses de test (§4), avant toute généralisation.
