# Carte des données APV — où trouver quoi

**Statut : vivant, à tenir à jour à chaque fois qu'un onglet est renommé ou déplacé.**
Réécrite le 2026-10-06 à partir des en-têtes réels des Sheets (relecture complète, date
de référence 05/10/2026).

Ce document répond à une seule question : **pour générer les mails (APV, Directeur,
Plaque), où va-t-on chercher chaque donnée APV ?** Il donne l'accès direct *classeur →
onglet → colonne*. Le *pourquoi* des règles et leur historique sont dans
`CADRAGE_APV.md` ; les règles de composition dans `rapport/regles/apv.md`.

**Règle de lecture** : le rapport lit chaque onglet **par nom d'en-tête**, jamais par
lettre. Les lettres ci-dessous sont un repère au 2026-10-06 : les colonnes bougent
(réagencement du 02/10, insertions des 05 et 06/10). **Toujours vérifier l'en-tête réel
avant d'écrire dans une colonne.**

## 1. Classeurs

| Classeur | ID | Rôle |
|---|---|---|
| `Rapport quotidien APV` | `1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw` | Classeur principal : KPI par concession et par plaque, listes de détail |
| `Anomalies forfaits` | `1T_BKjedX0yH7ENq4Z_88OWlGnBUu6RSez5ohLb0YscU` | Forfaits à marge estimée < 10 % |
| `Prix/Remises forcés` | `1ZZ2Y1EtbonrgOeJ0Zf81XngcZCiifCvtAP2dHczl7GY` | Remises et prix forcés Atelier + Magasin |
| `Référentiel Concession` | `1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY` | Classeur de Quentin, source de vérité : concessions, plaques, noms, mapping brut |

## 2. Onglets lus par le rapport (`rapport/config.py`)

| Source (config) | Classeur › onglet | 1 ligne = | Clé de filtre | Détail |
|---|---|---|---|---|
| `apv_analyse_globale` | APV › `Analyse Globale` | 1 concession | B = code concession, A = code plaque | §3 |
| `apv_encours_prioritaires` | APV › `Encours prioritaires` | 1 OR (top 5 par concession) | A | §4.1 |
| `apv_pieces_a_perte` | APV › `Analyse pièces client J-1` | 1 pièce vendue à perte hier | U, V | §4.2 |
| `apv_efficience_ci` | APV › `Efficience OR CI trop élevé` | 1 OR | A, G | §4.3 |
| `apv_remises_elevees` | APV › `Taux remise MO/PR interne élevé` | 1 OR | A, K | §4.4 |
| `apv_malfacons_j1` | APV › `Malfaçons J-1` | 1 OR × fiche × document | Q, R | §4.5 |
| `apv_plaque` | APV › `Plaque APV` | 1 plaque | A | §6 |
| `apv_forfaits_marge_faible` | Anomalies forfaits › `Extrait J-1 - Marges<10%` | 1 forfait | V, W | §7 |
| `apv_remises_forcees` | Prix/Remises forcés › `Prix/Remises forcés` | 1 ligne forcée | V | §8 |

Le rapport ne garde que les lignes contenant un code du périmètre (code concession pour
les mails de concession ; code plaque + codes de ses concessions pour le mail Plaque).

## 3. `Analyse Globale` — 1 ligne par concession

Structure : **B1** = date de référence (`=MAX('Détail facturation atelier journalière'!M:M)`,
A1 = libellé) ; ligne 1 à partir de C = bandeaux de blocs ; ligne 2 = en-têtes ;
ligne 3 et suivantes = une concession (67 au 05/10). A = code plaque (via
`Concession-plaques`), B = code concession canonique (liste unique tirée de
`Historique CA par atelier`).

### 3.1 Colonnes (72, de A à BT)

| Col. | Bandeau | Contenu |
|---|---|---|
| C-K | ATELIER - CA MO J-1 | C Nb OR clôturés J-1 · D CA MO net HT J-1 · E moy. mobile 4 sem. (médiane des 28 j) · F écart % · G **Alerte écart CA** · H-J % CA MO CLIENT / GARANTIE / CESSION J-1 · **K Malfaçons J-1** (€) |
| L-S | ATELIER - CA MO MTD | L CA MO MTD · M-O % CLIENT / GARANTIE / CESSION MTD · P Objectif MO mensuel · Q % réalisation (L/P, plein mois) · **R Malfaçons MTD** (€) · **S % Malfaçons MTD** (R/L) |
| T-AE | ATELIER - CA & Marge PR Interne J-1 | T CA PR interne J-1 · U moy. mobile · V écart % · **W Alerte écart CA PR interne** · X-Z % CLIENT / GARANTIE / CESSION J-1 · AA coût · AB marge · AC taux marge · AD marge attendue (mix) · AE écart vs mix (affiché en % = points) |
| AF-AK | ATELIER - CA & Marge PR Interne MTD | AF CA PR interne MTD · AG-AI % CLIENT / GARANTIE / CESSION MTD · AJ Objectif PR interne mensuel · AK % réalisation |
| AL-AS | ATELIER - Prod/Efficience | AL Productivité J-1 · AM moy. mobile · AN écart % · AO **Alerte productivité basse** · AP Efficience J-1 · AQ moy. mobile · **AR Efficience cessions internes J-1** · AS Efficience cessions internes MTD |
| AT-BD | ATELIER - Encours | AT Nb OR en cours · AU Valeur encours MO+PR · AV-AX vieux encours 90-180 j / 180-365 j / +365 j (nb) · AY-BA idem (valeur) · BB Dépréciation · BC Encours en j de CA · BD **Alerte encours** |
| BE-BN | MAGASIN | BE CA PR externe J-1 · BF moy. mobile · **BG écart %** · **BH Alerte écart CA PR externe** · BI coût · BJ marge · BK taux marge J-1 · BL CA PR externe MTD · BM Objectif PR externe mensuel · BN % réalisation |
| BO-BQ | *(Magasin)* | BO Nb pièces magasin vendues J-1 · **BP Valeur pièces magasin à perte J-1** · BQ % pièces magasin vendues à perte J-1 |
| BR-BT | *(données Atelier sous le bandeau Magasin)* | BR Nb pièces atelier client vendues J-1 (hors forfaits) · **BS Valeur pièces atelier à perte J-1 (hors forfait)** · BT % vendues à perte |

En gras : signaux du barème météo et colonnes malfaçons (voir §3.2 et §3.3).

### 3.2 Sources et formules clés

| Colonnes | Source | Règle |
|---|---|---|
| C-J, L-O, T-AD, AF-AI | `Historique CA par atelier` (B date, N code) | J-1 = date B1 ; MTD = du 1er du mois à B1 ; moyennes mobiles = **médiane** des 28 jours précédant B1 |
| P, AJ, BM | `Objectif APV` (J code, B année, C mois ; D MO, F PR interne, G PR externe) | objectif du mois de B1, sans prorata |
| AD | X-Z × `Référentiel métier` B18-B20 (marges de référence CLIENT 34,6 %, GARANTIE 5,7 %, CESSION 7 %) | marge attendue au mix du jour |
| AL-AS | `Historique efficience/prod` (B date, H code ; C temps facturé total, D temps passé rappelé total, E temps facturé cession interne, F temps passé cession interne, G temps passé total) | productivité = C/G ; efficience = C/D ; efficience cessions internes = E/F (AR jour B1, AS mois) |
| AT-BD | `Encours à date` (V code, I ancienneté, M valeur MO+PR, T dépréciation) ; BC ÷ CA moyen 6 mois de `Historique CA mensuel ateliers` | seuils `Référentiel métier` B15-B17 (20 / 30 / 40 j) |
| BE-BN | `Historique CA par Magasin` (B date, E code ; C CA, D coût) | même logique J-1 / MTD / médiane 28 j |
| K, R, S | `Malfaçons du mois` (P montant total, Q code, B date) | formules : `docs/sheets-formulas/malfacons.txt` |
| G, W, BH | F, V, BG < `Référentiel métier` B8 (−30 %) | « ALERTE » ; G : `=IF(F3<…$B$8;"ALERTE";"")`, W et BH : `=IF(V3="";"";IF(V3<…$B$8;"ALERTE";""))` |
| BO, BQ | `Détail facturation magasin journaliere` (T code, C date, S est à perte) | BQ = Σ S ÷ BO |
| BP | `Analyse pièces client J-1` (Q marge €, U code, A canal = « Magasin ») | `=SUMIFS(…!$Q:$Q;…!$U:$U;$B3;…!$A:$A;"Magasin")` |
| BR, BS, BT | `Détail facturation atelier journalière` | critères communs : AK = code, O = « Pièce », AH = « CLIENT », U = 0, N ≠ « FACTURE INTRA GROUPE ATELIER », AI ≠ « Intra-groupe sauf Primocar », AI ≠ « Inter sites » ; BR + X > 0 ; BS = SUMIFS(AA) − SUMIFS(Y) avec AR = 1 ; BT = COUNTIFS(… AR = 1) ÷ BR |

### 3.3 Pièces à perte : un seul périmètre partout (décision du 2026-10-06)

Vente **CLIENT externe**, **hors pièces de forfait**, **hors intragroupe** (Atelier :
imputation `FACTURE INTRA GROUPE ATELIER`, catégories `Intra-groupe sauf Primocar`,
`Inter sites` ; Magasin : `Cessions internes - interservices`, `Intra-Groupe Renault`,
`Inter sites`, `Intra-groupe sauf Primocar`, `Export`), hors avoirs, quantité > 0, prix de
vente net < PAMP. La liste du mail (`Analyse pièces client J-1`), les colonnes BP-BT, la
météo et `Plaque APV!G` comptent **les mêmes pièces**. Les paliers du barème en € portent
sur le **total du jour**. Vérifié le 2026-10-06 (B1 = 05/10) : 34 lignes Atelier + 11
Magasin = 45 = somme de `Plaque APV!G` ; BP-BT identiques à un recalcul indépendant pour
les 67 concessions.

### 3.4 Contrôles et constats du 2026-10-06

- 0 cellule en erreur sur les 67 lignes. Cohérences vérifiées : Q = L/P, AK = AF/AJ,
  BN = BL/BM, F = D/E − 1, V = T/U − 1, AN = AL/AM − 1, AB = T − AA, AC = AB/T,
  AE = AC − AD, BJ = BE − BI, BK = BJ/BE, BG = BE/BF − 1.
- Alertes d'écart de CA fréquentes un lundi (05/10 : 23/67 MO, 25/67 PR interne, 31/67
  PR externe) — à surveiller.
- Valeurs aberrantes BMW_COLMAR (efficience cessions internes MTD 2 880 %, écart marge vs
  mix +417 %) : très peu d'heures pointées ou de CA.
- FIAT_MULHOUSE : mix MO/PR ≠ 100 % (lignes sources à `Affectation` = `0` / `NC` / `1`).

## 4. Listes de détail (niveau concession)

### 4.1 `Encours prioritaires` — top 5 par concession
A Code concession · B N° OR · C Immatriculation · D Ancienneté (j) · E Montant MO encours ·
F Montant PR encours · G Valeur totale OR · H Dépréciation · I Score. **Plafonné à 5 par
concession** (OR > 30 j, tri par score) : jamais présenté comme exhaustif. Source :
`Encours à date`.

### 4.2 `Analyse pièces client J-1` — pièces vendues à perte hier ⚠️
22 colonnes : A Canal (Atelier / Magasin) · B Concession (nom, via `Concession-plaques`) ·
C N° OR (n° de document côté Magasin) · D Date · E Référence · F Désignation ·
G Réceptionnaire / Nom_Magasinier ⚠️ · H Canal de vente · I Catégorie client ·
J Nom du client ⚠️ · K Quantité · L CA brut · M Montant remise · N Remise % · O CA net ·
P PAMP · Q Marge € · R Marge % · S Remise forcée · T Prix forcé · U Code concession ·
V Plaque. Formule unique en A2 : `docs/sheets-formulas/analyse_pieces_j1.txt` (périmètre
§3.3, tri par Marge € croissante). Vide sous l'en-tête un jour sans perte.

### 4.3 `Efficience OR CI trop élevé` — OR en cession interne > 105 %
**Deux tableaux côte à côte** : A-G pour l'affichage (A Code concession, B N° OR,
C Réceptionnaire ⚠️, D Temps facturé, E Temps passé, F Efficience en %, **G Plaque**) et
J-O en décimal (J Code, K N° OR, L Mécanicien ⚠️, M Temps facturé, N Temps passé rappelé,
O Efficience). Le rapport utilise A-G. Seuil : `Référentiel métier` (105 %).

### 4.4 `Taux remise MO/PR interne élevé` — remise MO > 15 % ou PR interne > 20 % ⚠️
A Code concession · B N° OR · C Nom client ⚠️ · D Réceptionnaire ⚠️ · E CA brut MO ·
F Remise MO · G Taux remise MO · H CA brut PR · I Remise PR · J Taux remise PR · **K Plaque**.
Seuils : `Référentiel métier`. Voir §9 (taux aberrants quand le CA brut vaut 0).

### 4.5 `Malfaçons du mois` et `Malfaçons J-1` ⚠️
`Malfaçons du mois` = extrait du connecteur BigQuery `Malfaçons` (requête
`docs/sql/malfacons_gestes_commerciaux.sql`, du 1er du mois de J-1 à J-1) : A Concession ·
B Date_document · C Activite (Mécanique / Carrosserie) · D Fiche_imputee ·
E Libelle_detail_intervention · F Categorie_OR · G Receptionnaire ⚠️ · H Nom_client ⚠️
(propriétaire) · I Immatriculation · J Type_document (Facture / Avoir) · K Numero_OR_DMS ·
L Numero_document · M Montant_MO · N Montant_PR · O Montant_autres · P Montant_total ·
**Q Code concession** (formule, tirée jusqu'à la ligne 2000).
`Malfaçons J-1` = mêmes colonnes A-Q filtrées sur la date B1 d'`Analyse Globale`, triées
par montant décroissant, + **R Plaque**. Définition (10 fiches de cession interne) :
`CADRAGE_APV.md` §15. Montants nets HT, avoirs déduits.

## 5. Onglets intermédiaires (extraits des connecteurs BigQuery)

| Onglet (GRID) | Connecteur (DATA_SOURCE) | Colonnes utiles | Remarques |
|---|---|---|---|
| `Détail facturation atelier journalière` | `Facturation détaillée Atelier` | reflet de `facturation_detaillee_or` J-1 : E Receptionnaire, L/M n° OR, N Libelle_type_imputation, O Libelle_type_operation, U Est_ligne_forfait, W Prix unitaire, X Quantite_facturation, Y PAMP_facturation (total de ligne), AA Prix_vente_net, AB/AC remise, AD Facture_avoirisee, AF/AG forçage, AH Affectation, AI Categorie_client, AJ Nom_client ⚠️, **AK Code concession**, AR **Est pièce à perte** | M = date (donne B1). AR : `=SI($AK2="";"";SI($O2="Pièce";SI(ET($X2>0;$AD2<>1;$AA2<$Y2);1;0);""))`. Quelques lignes sources arrivent décalées (§9) |
| `Détail facturation magasin journaliere` | `Magasin` (`docs/sql/magasin_detail_journalier.sql`) | B Concession, C Date_document, D Numero_document, E Avoir, F Categorie_client, G Nom_Magasinier ⚠️, H Nom_client ⚠️, I Reference, J Libelle_piece, K Qte_servie, L Prix_unitaire_net, M Prix_brut_ligne, N Remise_ligne, O Prix_net_ligne, P PAMP, Q Prix_force, R Remise_forcee, **S Est à perte**, **T Code concession** | S corrigée le 2026-10-06 (elle comparait PAMP < prix forcé depuis le décalage du 25/09) : `=IF($T2="";"";IF(AND($K2>0;$E2<>1;$O2<$P2;$F2<>"Cessions internes - interservices";$F2<>"Intra-Groupe Renault";$F2<>"Inter sites";$F2<>"Intra-groupe sauf Primocar";$F2<>"Export");1;0))` |
| `Historique CA par atelier` | `Historique CA Atelier` | A Concession, B Date, C CA MO, D CA PR interne, E Coût PR interne, F Nb OR clôturés, G-I CA MO CLIENT / GARANTIE / CESSION, J CA PR interne CLIENT, K coût PR interne CLIENT, L-M CA PR interne GARANTIE / CESSION, N Code concession | aucun filtre `Est_ferme` sur le CA depuis le 30/09 (`CADRAGE_APV.md` §14) |
| `Historique CA mensuel ateliers` | `Historique CA mensuel par atelier` | A Concession, B Mois, C CA MO, D CA PR interne, E-K mix par canal, L Code concession, M Plaque | base de l'encours en jours de CA |
| `Historique efficience/prod` | `Historique Efficience + Productivité` | A Concession, B Date, C Temps_facture_total, D Rappel_temps_passe_total, E Temps_facture_cession_interne, F Rappel_temps_passe_cession_interne, G Temps_passe_total, H Code concession, I Plaque | le « / » du nom d'onglet doit être encodé dans une URL d'API |
| `Encours à date` | `Encours` (Salesforce, OR non clôturés) | B Concession, C Numero_OR_DMS, D Immatriculation, I Anciennete_jours, J Receptionnaire, L-P montants, T Depreciation_OR, V Code concession, W Score, X > 30 j, Y Plaque | |
| `Historique CA par Magasin` | `Historique CA Magasin` | A Concession, B Date, C CA_PR_Externe_Net_HT, D Cout_PR_Externe, E Code concession | intersite exclu ; intragroupe et cessions au service commercial **inclus** (vérifié 02/10) ; requête pas dans le dépôt |
| `Objectif APV` | `Obj APV` | A Concession, B Année, C Mois, D MO, E PR interne client, F PR interne, G PR externe, H Magasin, I Plaque, J Code concession | |
| `Malfaçons du mois` | `Malfaçons` | §4.5 | |
| `Temps facturés par jour`, `Temps passés par jour` | `Temps facturés journaliers`, `Temps passés journaliers` | — | non lus par `Analyse Globale` |

Actualisation : tous les connecteurs du classeur sont rafraîchis ensemble chaque jour à
10 h (heure de Paris), après la remontée des sources dans BigQuery.

`Référentiel métier` : seuils (B2-B4 vieux encours 90/180/365 j, B5 et B12 efficience
cession interne 105 %, B8 écart CA −30 %, B11 productivité 80 %, B13-B14 remises 15 % /
20 %, B15-B17 encours 20/30/40 j, B18-B20 marges PR interne de référence par canal).

## 6. Niveau Plaque — `Plaque APV`

1 ligne par plaque ; B1 = `='Analyse Globale'!$B$1`. **11 plaques au 06/10** :
`PLQ_PRIMOCAR` et `PLQ_VEODROME` n'y figurent pas (pas d'activité APV remontée).

| Col. | Donnée | Calcul | Source |
|---|---|---|---|
| A | Plaque | `UNIQUE` des plaques | `Concession-plaques` |
| B | Efficience J-1 | `IFERROR(Σ temps facturé ÷ Σ temps passé rappelé;"")` par plaque et date | `Historique efficience/prod` (I) |
| C | Productivité J-1 | `IFERROR(Σ temps facturé ÷ Σ temps passé total;"")` — vide si aucun temps passé total (PLQ_BMW_MOTO le 05/10) | idem |
| D | Valeur encours MO+PR | Σ par plaque | `Encours à date` (Y, M) |
| E | Encours +90 j (nb) | `COUNTIFS(ancienneté ≥ 90)` | `Encours à date` (Y, I) |
| F | Encours en j de CA | valeur ÷ (CA MO + CA PR interne des 6 mois ÷ 180), pondéré | `Historique CA mensuel ateliers` (M) |
| G | Pièces client en marge négative | `COUNTIFS('Analyse pièces client J-1'!$V:$V;$A3)` (Atelier + Magasin) | §4.2 |
| H | Forfaits marge < 10 % | `VLOOKUP` + `IMPORTRANGE` du résumé agrégé | `Anomalies forfaits › Plaque - Forfaits marge faible` |
| I | Remise élevée (OR) | `COUNTIFS` par plaque | `Taux remise MO/PR interne élevé` (K) |
| J | Efficience CI élevée (OR) | `COUNTIFS` par plaque | `Efficience OR CI trop élevé` (G) |
| K | Malfaçons J-1 | `SUMIFS('Analyse Globale'!K)` par code plaque (A) | `Analyse Globale` |
| L | Malfaçons MTD | `SUMIFS('Analyse Globale'!R)` | idem |
| M | % Malfaçons MTD | L ÷ Σ `'Analyse Globale'!L` (CA MO MTD) — pondéré | idem |

Principe : au niveau Plaque et Directeur, le bloc APV remonte des **compteurs de
problèmes**, pas de CA ni d'objectifs — **sauf les malfaçons** (montant et % du CA MO,
décision du 2026-10-06). Totaux Plaque toujours **pondérés** (somme des numérateurs ÷
somme des dénominateurs), jamais une moyenne des %. Les remises forcées n'ont pas de
total Plaque (classeur pas branché, §8).

## 7. Classeur `Anomalies forfaits`

| Onglet | Rôle | Colonnes |
|---|---|---|
| `Data source Forfait marges` (connecteur) → `Extrait J-1 - Marges<10%` | Forfaits facturés hier à marge estimée < 10 % (requête `docs/sql/marge_forfaits_j1_extract.sql`) | A Date_reference · B Concession · D Numero_OR_DMS · E Nom_client ⚠️ · H Receptionnaire ⚠️ · J Libelle_forfait · M Detail_pieces · N Prix_forfait_HT · O Taux_remise_forfait_pct · P Cout_PR · Q Heures_MO · R Taux horaire estimé · S Coût MO estimé · T Marge_estimee · U Taux_marge_estime_pct · **V Code concession** · **W Plaque** |
| `Plaque - Forfaits marge faible` | Résumé par plaque, seul onglet réimporté dans `Plaque APV` | A Code_Plaque · B Nb forfaits < 10 % |
| `Historique`, `Destinataires marge faible` | Historisation et diffusion dédiée du mail forfaits (`CADRAGE_APV.md` §9.1) | — |
| `Forfaits pièces suspectes` → `Forfaits suspects` | Détection n° 3, **en pause** : pas dans le mail | — |
| `Mapping`, `Concession-plaques` | Transco locale | — |

## 8. Classeur `Prix/Remises forcés` — pas encore branché au niveau Plaque

| Onglet | Rôle | Colonnes |
|---|---|---|
| `Data Prix/Remises forcés` (connecteur) → `Prix/Remises forcés` | Lignes à prix ou remise forcés, Atelier + Magasin | A concession · B numero_or · C numero_facture · **D type** (Atelier / Magasin : le mail APV ne prend que **Magasin**) · E date_doc · F receptionnaire ⚠️ · G reference · H libelle · I type_imputation · J categorie_client · K nom_client ⚠️ · L forfait · M forcage · N quantite · O prix_brut · P prix_vente_net · Q remise_montant · R remise_pct · S pamp · T marge · U taux_marge_pct · **V Code concession** |
| `Contact` | Destinataires par concession | Concession · Fonction (Chef d'atelier / Responsable Magasin) · Nom complet ⚠️ · Email |
| `Mapping concessions`, `Transco_Concessions` | Transco (la seconde, legacy, est à clarifier) | — |

Pour le niveau Plaque : même recette que les forfaits (colonne Plaque, résumé agrégé par
plaque, `IMPORTRANGE` depuis `Plaque APV`). Pas fait.

## 9. Anomalies de données connues

- **`Taux remise MO/PR interne élevé`** : quand le CA brut MO ou PR vaut 0 avec une remise
  non nulle, le taux sort absurde (ex. BMW_BELFORT au 05/10 : −343 399 471 587 000 000 %).
  Ces lignes ne sont pas de vraies remises élevées ; la formule devrait exiger un CA brut > 0.
- **`Efficience OR CI trop élevé`** : des OR à 0,01 h de temps passé donnent des
  efficiences de plusieurs milliers de % (ex. 3 300 % à BMW_COLMAR).
- **`Détail facturation atelier journalière`** : quelques lignes sources arrivent
  décalées (un nom de client en colonne Code concession, `Affectation` = `0` / `NC` / `1`).
- **Isuzu Châlons** (plaque Hyundai) : pas de données VO ni APV propres.

## 10. Données personnelles

Noms réels de clients et de salariés (jamais dans un fichier commité ni une maquette non
anonymisée ; noms réels dans les mails envoyés) :
- `Rapport quotidien APV` : `Analyse pièces client J-1`, `Détail facturation atelier
  journalière`, `Détail facturation magasin journaliere`, `Efficience OR CI trop élevé`,
  `Taux remise MO/PR interne élevé`, `Malfaçons du mois`, `Malfaçons J-1`, `Encours à date`
  (réceptionnaire, mécanicien), `Encours prioritaires` (immatriculations).
- `Anomalies forfaits` : `Extrait J-1 - Marges<10%`.
- `Prix/Remises forcés` : `Prix/Remises forcés`, `Contact`.

Les résumés agrégés (`Plaque APV`, `Plaque - Forfaits marge faible`) ne contiennent que des
compteurs et montants : ce sont eux qu'on réimporte entre classeurs, jamais le détail.

## 11. Pièges rencontrés (à ne pas refaire)

1. **Colonnes décalées par un changement de requête.** Retirer ou ajouter un champ à une
   requête de connecteur décale les colonnes de l'extrait, mais pas les colonnes en
   formule ajoutées à droite. Toute formule qui lit l'extrait par lettre doit alors être
   revue. Arrivé le 25/09 (retrait du champ `Magasin`) : `Analyse Globale` cassée, liste
   des pièces à perte en `#VALUE!` jusqu'au 02/10, et colonne `Est à perte` du détail
   magasin fausse jusqu'au 06/10 (elle comparait PAMP et prix forcé).
2. **Un `IFERROR` peut cacher une panne.** Un onglet renommé casse les formules qui le
   citent ; si l'erreur est avalée par un `IFERROR` avec une valeur de repli, rien ne se
   voit. Préférer un repli visible (`"MAPPING MANQUANT: "&valeur`).
3. **Un compteur se confronte à sa source.** Comparer avant/après ne voit pas une colonne
   déjà cassée : `Plaque APV!G` valait 0 avant et après le 02/10 alors que la liste
   contenait 139 lignes.
4. **Deux mesures d'un même signal doivent partager le même périmètre.** Le 06/10, la
   valeur et le % des pièces à perte se contredisaient (l'un incluait les forfaits,
   l'autre l'intragroupe) : un seul périmètre, §3.3.
5. **Vérifier l'en-tête réel avant d'écrire.** Arrivé plusieurs fois (`Encours à date`
   W/X, `Efficience OR CI trop élevé` G et non O).
6. **`IMPORTRANGE`** : une plage par import ; importer le résultat agrégé, jamais le détail
   (données personnelles).
7. **Nom d'onglet avec « / »** (`Historique efficience/prod`, `Taux remise MO/PR interne
   élevé`, `Prix/Remises forcés`) : à encoder dans une URL d'API ; l'outil de lecture local
   (`gws`) échoue dessus, GitHub Actions passe.
8. **Champs BigQuery `Regroupement_concession(s)_APV`** : ne regroupent rien (valeur =
   concession brute). Toujours passer par `Mapping concession` pour obtenir le code.
