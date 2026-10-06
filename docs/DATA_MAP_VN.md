# Carte des données VN — où trouver quoi

**Statut : vivant, à tenir à jour à chaque fois qu'un onglet est renommé/déplacé.**
Dernière mise à jour : 2026-10-05 — **vérifié onglet par onglet sur les Sheets réels** (en-têtes
lus via `gws`, chiffres recalculés depuis les extraits), pas seulement recopié de
`CADRAGE_VN.md`.

Ce document répond à une seule question : **pour générer le mail VN (niveau Service), où
va-t-on chercher chaque donnée ?** Il complète `CADRAGE_VN.md` (qui documente le *pourquoi*
et l'historique) en donnant un accès direct *classeur → onglet → colonne*. Même principe que
`DATA_MAP_APV.md`.

**Piège permanent** : les classeurs sont des Sheets vivants. Onglets renommés, colonnes
déplacées ou réordonnées sont déjà arrivés plusieurs fois (voir §7). **Toujours vérifier
l'en-tête réel avant de lire ou d'écrire dans une colonne.**

## 1. Classeurs

| Classeur (titre réel) | ID | Onglets réels (dans l'ordre) |
|---|---|---|
| `Rapport quotidien VN - Bloc 1` | `1oQzC5CV8Xqb6oTVAmNakcn3pSJD0yqP1eSdE7guHn80` | `Mapping`, `Leads_SF_VN` (connecté), `Extrait Leads_SF_VN` ⚠️, `BLOC 1 Leads VN` |
| `Rapport quotidien VN - Bloc 2` | `14iuxhKZr34StlxCn8IodM9iquoqH9wnc5EhsBYxBUDE` | `Mapping`, `Obj Com/Fact.` (connecté), `Extrait_ComFact`, `BLOC 2` |
| `Rapport quotidien VN - Bloc 3/4/5` | `10cOmCg_e8JKKpaHY0pI6QTPWLehO_VVfVAU6bXAROWE` | `Mapping`, `Mapping Marque Modèle`, `DM_Stock_VN_VD` (connecté), `DM_Vente_VN_VD` (connecté), `Extrait_Stock_VN_VD`, `Extrait_Vente_VN_VD`, `BLOC 3 P1 Stock VN_VD`, `BLOC 3 P2 Stock VN_VD`, `BLOC 4 Couverture VN`, `BLOC 5 TOP 3` |
| `Rapport quotidien VN - BLOC 6` | `16xQnrbCZpPP2sDy4WxJvglRdIVYkwx31wiWC_n0lKcg` | `Mapping`, `DM Vente` (connecté), `Extrait Vente VN VD` ⚠️, `BLOC 6 - Anomalie Vente VN-VD` |
| `Référentiel Concession` | `1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY` | Source de vérité transverse (concessions, plaques, mapping brut) |

⚠️ **Deux noms d'onglets contiennent une espace insécable** (entre `Extrait` et le reste) :
`Extrait Leads_SF_VN` et `Extrait Vente VN VD`. Taper une espace normale dans une plage
(`gws`, formule, script) échoue avec « Unable to parse range ». Passer le caractère
`U+00A0` (ex. en bash : `$'Extrait\xc2\xa0Leads_SF_VN'`). Les onglets `BLOC …`,
`Extrait_ComFact`, `Extrait_Stock_VN_VD`, `Extrait_Vente_VN_VD` ont des noms normaux.

## 2. Règles de lecture communes à tous les onglets

- **Lignes parasites à toujours ignorer** : toute ligne dont le `Code_concession` est vide ou
  vaut `" "`. Elles existent dans presque tous les onglets (voir détail par bloc) et le
  script ne doit jamais les remonter dans un mail.
- **Lignes fantômes** dans `Extrait_Stock_VN_VD` : environ 2 125 lignes sans type
  (`Est_VN_VD_ou_VO` vide), restes de formules. Filtrer sur `VN`/`VD`.
- **Nombres au format français** : virgule décimale (`-23681,1`), pourcentages en texte
  (`-9,39%`), dates `JJ/MM/AAAA`.
- **`Mapping`** : présent en premier onglet de chaque classeur, 3 colonnes
  `Valeur_Source, Code_concession, Code_Plaque` (Blocs 2, 3/4/5, 6) ; le classeur Bloc 1 a une
  colonne de plus en tête (`Source_BigQuery`, valeur `v_sf_leads`).

## 3. Exclusions volontaires (décisions de Quentin, ne pas "corriger")

| Libellé source | Où il apparaît | Statut |
|---|---|---|
| `Stock Plaque Renault` | Stock VN/VD (1 012 véhicules) | Retiré du rattachement concession, compté seulement niveau plaque |
| `Renault Saint-Avold` | Stock VN/VD (237 véhicules) | Exclu volontairement (confirmé 2026-10-05) |
| `Fiat Saint-Etienne` | Stock VN/VD (85 véhicules) | Exclu volontairement (confirmé 2026-10-05) |
| `S-LEASE …` (Bischheim, Metz, Laxou, Illzach, Dijon, Franois, Besançon, Reims, Prix-lès-Mézières) / `SLEASE` | Stock, ventes, Bloc 2, Bloc 6 | Exclu volontairement (confirmé 2026-10-05) |
| Concessions de Bâle | Tous blocs | Hors périmètre |

Conséquence : ces libellés n'ont pas de `Code_concession` dans les extraits — c'est **normal**.

## 4. Niveau Service — par bloc

### Bloc 1 — Leads VN
Classeur `Bloc 1`. Chaîne : `Leads_SF_VN` → `Extrait Leads_SF_VN` → `BLOC 1 Leads VN`.

| Donnée | Onglet | Colonnes (A→…) | Notes |
|---|---|---|---|
| Leads reçus/non traités | `BLOC 1 Leads VN` | A `Code_concession`, B `Date_reference`, C `Leads_recus_J1`, D `Leads_recus_7j`, E `Leads_non_traites_J1`, F `Leads_non_traites_7j` | Date de référence = la veille. **1re ligne = code `" "`** : leads sans concession dès la source (42 reçus J-1, tous non traités le 2026-10-04) — **perdus pour les mails**, à ignorer |
| Extrait (avant consolidation) | `Extrait Leads_SF_VN` | A `Concession` (libellé brut), B…F idem, G `Code_concession` | 1re ligne : `Concession` vide |

### Bloc 2 — Commandes & Facturations VN vs Objectifs
Classeur `Bloc 2`. Chaîne : `Obj Com/Fact.` → `Extrait_ComFact` → `BLOC 2`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Extrait brut | `Extrait_ComFact` | A `flux` (Commandes/Facturations), B `libelle` (concession brute, vide = total marque), C `marque`, D `j1`, E `s7`, F `s4_prec_total`, G `mtd`, H `mtd_n1`, I `obj_mois`, J `jo_ecoules`, K `jo_mois`, L `jo_restants`, M `date_reference`, N `Code_concession`, O `Code_Plaque` | Jours ouvrés identiques pour les 2 flux (calendrier lun-ven) : `$J$2/$K$2/$L$2` |
| Résultat final | `BLOC 2` | 25 colonnes A→Y : A `Plaque`, B `Concession`, C `Marque`, puis **D→N** `Cde – …` et **O→Y** `Fact – …` (J-1, 7 jours, Moy. hebdo 4 sem., Mois à date, Mois à date N-1, Objectif mois, Manque à date, Taux atteinte %, Projection fin de mois, Reste à faire / jour ouvré, Tendance) | Voir types de lignes ci-dessous |

**4 types de lignes dans `BLOC 2`** (à distinguer à la lecture) :
1. **Concession × marque** : `Plaque`, `Concession`, `Marque` renseignés (ex. `PLQ_BMW / BMW_BELFORT / MINI`).
2. **Total concession** : `Marque = TOTAL` (ex. `PLQ_BMW / BMW_BELFORT / TOTAL`).
3. **Total plaque** : `Concession = TOTAL` et `Marque = TOTAL`.
4. **Total marque pour le groupe** : `Plaque` et `Concession` vides, `Marque` renseignée (`ALFA ROMEO`, `FIAT`, `NISSAN`, `OPEL`, `TOYOTA`) + une ligne `TOTAL`.

Plus : pour chaque concession, une ligne à **marque vide**, toute à zéro — à ignorer.
`Taux atteinte %` vide quand l'objectif vaut 0 (normal). Aucune erreur `#REF`/`#N/A` constatée.
BMW Motorrad : `Cde – Mois à date` vient d'un déclaratif mensuel (pas de détail J-1/7j).

**À trancher** : 6 libellés de l'extrait n'ont **aucun code concession** et sont donc absents de
`BLOC 2` — `Nissan Beaune`, `Opel Metz`, `Alfa Romeo Besançon`, `Fiat Haguenau`, `Fiat
Huningue`, `Opel Thionville`. Tous à 0 aujourd'hui (aucune perte visible), mais dès qu'une
de ces concessions aura de l'activité elle disparaîtra silencieusement du mail. Hors
périmètre ou mapping à ajouter ?

### Bloc 3 — Stock VN/VD
Classeur `Bloc 3/4/5`. Chaîne : `DM_Stock_VN_VD` → `Extrait_Stock_VN_VD` → `BLOC 3 P1` / `P2`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Détail stock | `Extrait_Stock_VN_VD` | **A→U** : `Concession`, `Est_VN_VD_ou_VO`, `Statut_de_stock`, `Detail_statut_stock`, `Numero_de_stock`, `CRC_vehicule`, `Serie_VIN`, `Libelle_marque`, `Libelle_modele`, `Date_achat`, `Numero_commande_constructeur`, `Date_commande_constructeur`, `Date_commande_client`, `Date_livraison_a_client`, `Est_contremarque`, `Prix_achat`, `Somme_options_constructeur`, `Somme_options_complementaires`, `Somme_frais`, `Montant_surestimation`, `Somme_aides` ; **V** `Ancienneté depuis l'achat`, **W** `Durée de contremarque`, **X** `Valeur_stock`, **Y** `Code_concession`, **Z** `Code_Plaque`, **AA/AB/AC** voir ci-dessous, **AD** `Marque harmonisée`, **AE** `Modèle harmonisé` | ⚠️ **AA, AB, AC** s'appellent `Stock âgé VN (+6 mois)`, `Stock âgé VD (+6 mois)`, `Contremarqué +90j` mais contiennent des **rangs** (sentinelle `999` pour les non-qualifiants), pas des compteurs |
| Synthèse par concession | `BLOC 3 P1 Stock VN_VD` | A `Code_Concession` (C majuscule), B `Stock VN`, C `Stock VD`, D `Stock âgé VN (+6 mois)`, E `Stock âgé VD (+6 mois)`, F `Contremarqué +90j` | **Recalculé depuis l'extrait : 0 écart sur les 63 concessions.** Contient 2 lignes parasites (code vide / `" "`) |
| Top-5 détail | `BLOC 3 P2 Stock VN_VD` | **3 tableaux côte à côte** : A→F (`Code_concession`, `Numéro Stock`, `VIN`, `marque`, `modele`, `Stock âgé VN`), H→M (idem, `Stock âgé VD`), O→T (idem, `Contremarqué`) | ⚠️ **Pas un vrai top 5** : les ex æquo d'ancienneté dépassent 5 lignes (BMW_MULHOUSE 8, REN_SELESTAT 8 en contremarqué, BMW_LONS/HYU_MULHOUSE 7…). ⚠️ Le groupe sans code concession occupe ~1 018 lignes de bruit en tête — filtrer |

### Bloc 4 — Couverture, Excès de stock
Même classeur. Chaîne : `DM_Vente_VN_VD` → `Extrait_Vente_VN_VD` → `BLOC 4 Couverture VN` → `BLOC 5 TOP 3`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Transco libellés | `Mapping Marque Modèle` | `Marque (source)`, `Libellé modèle (source)`, `Marque harmonisée`, `Modèle harmonisé` | Construite par Quentin |
| Ventes 90 jours | `Extrait_Vente_VN_VD` | A `Concession`, B `Libelle_marque`, C `Libelle_modele`, D `nb_ventes_90j`, E `ventes_moy_mensuelle`, F `Code_concession`, G `Code_Plaque`, H `Marque harmonisée`, I `Modèle harmonisé` | 34 lignes sans code concession, toutes S-LEASE (exclusion volontaire) |
| Couverture / excès | `BLOC 4 Couverture VN` | A `Code_concession`, B `Marque harmonisée`, C `Modèle harmonisé`, D `Stock`, E `Ventes moy`, F `Couveture` (**faute de frappe réelle**), G `Excès de stock`, H `Ancien_nb`, I `Colonne de rang`, J `Code_Plaque de la ligne`, K `Stock Plaque`, L `Ventes moy. Plaque`, M `Couverture Plaque` | **Recalculé : 0 écart sur les 723 lignes.** Dernière ligne parasite (code vide, `#N/A` en J). **J→M = comparaison Plaque, réservée au futur mail Directeur** |
| Podium top 3 excès | `BLOC 5 TOP 3` | A `Code_concession`, B `Marque harmonisée`, C `Modèle harmonisé`, D `Stock`, E `Ventes moy`, F `Excès de stock` | Excès ≥ 12 (P90), 3 lignes max par concession. Commence par des lignes à code vide (dont un « stock » fantôme de 2 125) — ignorer |

**Limites connues du Bloc 4** (à avoir en tête, pas des erreurs de calcul) :
- **92 véhicules en stock sans modèle harmonisé** (`Mapping Marque Modèle` incomplet : Nissan Juke F16B 48, Leaf 26, Interstar 5, Hyundai Ioniq 3 / Inster / Ioniq 5 N, un Range Rover). Ils sont regroupés en **une seule ligne à modèle vide par marque** → couverture et excès de ces modèles faux. Côté ventes : 20 lignes dans le même cas (Juke, Mini Cooper F66, Leaf, Scenic E-Tech…).
- **Les modèles vendus sans stock actuel n'apparaissent pas** (112 couples concession × modèle, ~95 ventes/mois) : la liste est construite à partir du stock. Une rupture sur un modèle qui se vend est invisible.
- **Arrondi à l'affichage** : un excès affiché `12` peut valoir 11,7 et rester sous le seuil (BMW Besançon Série 1 : absent du `TOP 3`).

### Bloc 6 — Anomalies Ventes VN/VD
Classeur `BLOC 6`. Chaîne : `DM Vente` → `Extrait Vente VN VD` → `BLOC 6 - Anomalie Vente VN-VD`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Détail ventes + classification | `Extrait Vente VN VD` | **A→T** : `numero_dossier`, `vin`, `immatriculation`, `Concession`, `marque`, `modele`, `vn_vd`, `Vendeur` ⚠️, `categorie`, `destination`, `energie`, `Date_de_vente`, `date_achat_vehicule`, `ca_brut_vehicule_ht`, `cout_acquisition_ht`, `remise_ht`, `transfert_de_marge_ht`, `aides_au_chassis_ht`, `marge_brute_vehicule_ht`, `marge_dossier_icar_ht` ; **U** `% Marge brute Véhicule`, **V** `Code_concession`, **W** `Code_Plaque`, **X** `Durée de détention`, **Y** `Anomalie VD`, **Z** `Pas a signaler`, **AA** `A signaler`, **AB** `A vérifier` | 447 lignes, fenêtre 5 jours (30/09→03/10). Classification : Y = 36, Z = 16 (« OK - compensé par périphériques »), **AA = 59 (« À corriger … »)**, AB = 5 |
| **Listing final (à lire pour le mail)** | `BLOC 6 - Anomalie Vente VN-VD` | A `numero_dossier`, B `vin`, C `immatriculation`, D `Code_concession`, E `Code_Plaque`, F `marque`, G `modele`, H `vn_vd`, I `destination`, J `marge_brute_vehicule_ht`, K `marge_dossier_icar_ht`, L `Durée de détention`, M `Anomalie VD`, N `A signaler`, O `A vérifier` | 66 dossiers au 2026-10-05, triés pire marge en premier. Ne contient **pas** `Vendeur` |

Formule actuelle du listing (corrigée le 2026-10-05) :
```
=QUERY('Extrait Vente VN VD'!A2:AB; "SELECT A, B, C, V, W, E, F, G, J, S, T, X, Y, AA, AB WHERE Y != '' OR AA != '' OR AB != '' ORDER BY S"; 0)
```
**Correctif optionnel non appliqué** : 13 dossiers S-LEASE (code concession vide) y figurent encore.
Les exclure avec `WHERE V != '' AND (Y != '' OR AA != '' OR AB != '')`.

## 5. Niveau Plaque — réservé à un futur mail Directeur

Colonnes `J→M` de `BLOC 4 Couverture VN` (comparaison Plaque) : décision de périmètre du
2026-09-23, **à retirer du mail Service**. Pas d'onglet Plaque dédié côté VN (contrairement à
`Plaque APV`).

## 6. Données personnelles — jamais dans un mockup non anonymisé

- `Extrait Vente VN VD`, colonne **H `Vendeur`** : nom du vendeur. **Absente du listing final**
  `BLOC 6` (le `SELECT` ne la reprend pas) — ne pas l'y ajouter.

Les autres onglets (Blocs 1 à 5, listing Bloc 6) sont des agrégats ou des listes orientées
véhicule sans nom de personne. Immatriculation/VIN ne sont pas traités comme donnée
personnelle (convention APV/VO).

## 7. Pièges rencontrés (à ne pas refaire)

1. **Formule `QUERY` non mise à jour après un réordonnancement de colonnes** (Bloc 6, corrigé
   le 2026-10-05) : le listing renvoyait le `%` de marge à la place du code concession et
   **aucune des 59 anomalies « À corriger »**, sans aucune erreur visible. Après tout
   déplacement de colonne, relire **toutes** les formules qui référencent l'onglet par lettre.
2. **Espace insécable dans un nom d'onglet** : voir §1.
3. **En-têtes qui ne disent plus ce qu'il y a dedans** : `AA/AB/AC` de `Extrait_Stock_VN_VD`
   (rangs nommés comme des compteurs). Se fier au contenu vérifié, pas au libellé.
4. **`IF(condition; COUNTIFS(...)+1; "")` casse `QUERY` en aval** : utiliser la sentinelle
   numérique `999`. `QUERY` mal devine l'en-tête sur une plage commençant ligne 2 : ajouter `; 0`.
5. **Champ `Est_vehicule_courtoisie` est INT64** : ne pas le comparer à `'0'` entre guillemets.
6. **Libellés marque/modèle différents entre stock et ventes** : toujours passer par
   `Mapping Marque Modèle` ; un modèle absent du mapping fausse silencieusement couverture et
   excès (voir limites du Bloc 4).
7. **`IMPORTRANGE` à autoriser manuellement une première fois** dans l'UI Sheets, sinon les
   `RECHERCHEX` en aval échouent sans erreur visible.
8. **Seuil générique « marge fortement négative » hors BMW (cellule `$Z$1`)** : pointait vers
   un en-tête texte (comparaison toujours vraie). Le classement `À corriger` produit bien 59
   lignes aujourd'hui, mais l'emplacement du vrai seuil reste à confirmer (`CADRAGE_VN.md` §7).
