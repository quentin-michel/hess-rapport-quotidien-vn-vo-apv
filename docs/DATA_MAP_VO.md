# Carte des données VO — où trouver quoi

**Statut : vivant, à tenir à jour à chaque fois qu'un onglet est renommé/déplacé.**
Dernière mise à jour : 2026-10-05 — **vérifié bloc par bloc sur les Sheets réels** (en-têtes et
formules lus via `gws`, chiffres recalculés depuis les extraits), pas seulement recopié de
`CADRAGE_VO.md`.

Ce document répond à une seule question : **pour générer le mail VO (niveau Service), où
va-t-on chercher chaque donnée ?** Il complète `CADRAGE_VO.md` (le *pourquoi* et l'historique)
en donnant un accès direct *classeur → onglet → colonne*. Même principe que `DATA_MAP_APV.md`
et `DATA_MAP_VN.md`.

**Piège permanent** : 6 classeurs séparés, chacun avec son connecteur BigQuery. Toujours vérifier
l'en-tête réel avant de lire une colonne, ne jamais supposer (voir §8).

## 1. Classeurs

| Classeur (titre réel) | ID | Onglets réels (dans l'ordre) |
|---|---|---|
| `Rapport quotidien VO - Bloc 1` | `14TWu4moVg6lSOT5KLjnTCumeZcx-3M9Xg2vqpt4-ka4` | `Mapping`, `Leads_SF` (connecté), `Extrait Leads_SF`, `BLOC 1 Leads` |
| `Rapport quotidien VO - Bloc 2` | `1C1jMlaD8M1TearS98aiC_J3t6lieq7sp2GdMq_fKDzI` | `Mapping`, `Offre_SF` (connecté), `Extrait_Offre_SF`, `BLOC 2 Offre`, `Com/Fact/Obj` (connecté), `Extrait_Com_Fact_Obj`, `BLOC 2_1 Com_Fact_Obj`, `BDC Ouvert + 15j` (connecté), `Extrait_BDC_Ouvert`, `BLOC 2_2 BDC Ouvert` |
| `Rapport quotidien VO - Bloc 3` | `1PdjQzWi0Gbn1KhkaUvC6wPbdyiBIovI_TeB_YhyAraU` | `Mapping`, `Achat_VO_SF` (connecté), `Extrait_Achat_VO`, `BLOC 3 Ano Achat` |
| `Rapport quotidien VO - Bloc 4` | `1NhHCqRM54yWcMomE1Qd0tKGG9KWRV8tvewq9hhCIPfM` | `Mapping`, `Stock VO SF` (connecté), `Extrait_Stock_VO` (**29 colonnes**), `BLOC 4 Stock_P1`, `BLOC 4 Stock_P2` |
| `Rapport quotidien VO - Bloc 5/6/7` | `1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU` | `Mapping_Import`, `Vente VO 90j SF` (connecté), `Stock VO SF` (connecté), `Extrait_Stock_VO` (**25 colonnes**), `Extrait_Ventes_VO`, `BLOC 5 Couverture_VO`, `BLOC 6 Excès_Stock`, `BLOC 7 Santé_Plaque` |
| `Rapport quotidien VO - Bloc 8` | `110ih-4TOZL8qJD4CHz9avQoHXCN70wU5Pdmcmga1fwI` | `Mapping`, `Ventes_1j_SF` (connecté), `Extrait_Ventes_1j_SF`, `Bloc 8 Ano_Vente` |
| `Référentiel Concession` | `1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY` | Source de vérité transverse (concessions, plaques, mapping brut) |

⚠️ Il existe **deux onglets `Extrait_Stock_VO` différents** (Bloc 4 : 29 colonnes, code concession en X,
rangs en Y→AC ; Bloc 5/6/7 : 25 colonnes, code concession en X, code plaque en Y). Ne jamais les confondre.

## 2. Règles de lecture communes

- **Lignes parasites à toujours ignorer** : toute ligne dont le `Code_concession` est vide ou vaut
  `" "`, et les lignes entièrement vides (les extraits et `BLOC 4/6/7` en contiennent des milliers :
  restes de formules). Ne jamais lire un extrait directement, passer par l'onglet `BLOC …`.
- **Nombres au format français** (virgule décimale), dates `JJ/MM/AAAA`.
- **Onglet `Mapping`** : sa disposition varie selon le classeur — `Source_BigQuery, Valeur_Source,
  Code_concession, Code_Plaque` (Blocs 1 et 2) ; `Valeur_Source, Code_concession, …` (Blocs 4 et 8,
  d'après leurs `XLOOKUP`) ; `Mapping_Import` = `Valeur_Source, Code_Concession, Code_Plaque`
  (Bloc 5/6/7, **C majuscule**). Le Bloc 3 n'a pas été relevé. Toujours lire l'en-tête.
- **Fraîcheur** : tous les connecteurs ont été rafraîchis avec succès le 2026-10-05 entre 04:18 et
  04:40 UTC (06:18-06:40 heure de Paris l'été). Le mail doit partir **après 06:40** (Bloc 2 le dernier).
- **Fenêtres relatives** : les Blocs 4, 5, 6 et 7 calculent à partir de `TODAY()` (jour de la lecture) ;
  le Bloc 2/9 et le Bloc 8 partent de J-1.

## 3. Exclusions volontaires (décisions de Quentin, ne pas "corriger")

| Libellé source | Où il apparaît | Statut |
|---|---|---|
| `Opel Metz`, `Opel Thionville`, `Fiat Haguenau`, `Fiat Huningue`, `Nissan Beaune`, `Alfa Romeo Besançon` | Leads, Bloc 2, Com/Fact | Hors périmètre (confirmé 2026-10-05) |
| `Fiat Saint-Etienne`, `S-LEASE …` | Leads, stock | Exclus volontairement (décision VN du 2026-10-05) |
| `Opel Beaune` | Stock VO (1 véhicule IM) | Exclu volontairement (2026-10-05) |
| `HESS classic`, `Plaque Primocar`, `Plaque Veodrome` | Leads VO | Exclus volontairement (2026-10-05) |
| 3 véhicules CL à concession vide | Stock VO | Exclus volontairement (2026-10-05) |
| `Groupe Hess` | Leads, Com/Fact | Total parasite, jamais une concession |
| Concessions de Bâle, BMW Motorrad | Com/Fact (Bloc 2_1) | Exclues par la requête (alignement Tableau « Quotidienne VOP ») |

Conséquence : ces libellés n'ont pas de `Code_concession` dans les extraits — c'est **normal**.

**Encore à trancher** : `Strasbourg Illkirch` (2 BDC) et `Toyota Meuse` (1 BDC) n'ont pas de code
concession dans `Extrait_BDC_Ouvert` ; et `fiat-500-occasion.com` (1 lead / 7j) dans les leads.

## 4. Niveau Service — par bloc

### Bloc 1 — Leads
Classeur `Bloc 1`. Chaîne : `Leads_SF` → `Extrait Leads_SF` → `BLOC 1 Leads`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Leads reçus/non traités | `BLOC 1 Leads` | A `Code_concession`, B `Date_reference`, C `Leads_recus_J1`, D `Leads_recus_7j`, E `Leads_non_traites_J1`, F `Leads_non_traites_7j` | **Recalculé : 0 écart sur 74 concessions.** 1re ligne = code `" "` (leads sans concession : 27 J-1, dont « Groupe Hess » 1 035 sur 7j) — ignorer |
| Extrait | `Extrait Leads_SF` | A `Concession` (brute), B…F idem, G `Code_concession` | |

### Bloc 2 — Offres VO / Reprises
Classeur `Bloc 2`. Chaîne : `Offre_SF` → `Extrait_Offre_SF` → `BLOC 2 Offre`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Offres/reprises | `BLOC 2 Offre` | A `Code_concession`, B `Date_reference`, C/D `Commandes_VOP_acceptees_J1/_7j`, E/F `Offres_refusees_J1/_7j`, G/H `Reprises_acceptees_J1/_7j` | **Recalculé : 0 écart sur 70 concessions.** ⚠️ Fenêtre sur `DATE(CreatedDate)` (création de l'offre), statut actuel — **pas** la date de confirmation du BDC du Bloc 2_1 : les deux « commandes 7 jours » ne coïncident pas (BMW Belfort : 3 ici, 4 au Bloc 2_1) |

### Bloc 2_1 (ex-Bloc 9) — Commandes & Facturations vs Objectifs
Même classeur. Chaîne : `Com/Fact/Obj` → `Extrait_Com_Fact_Obj` → `BLOC 2_1 Com_Fact_Obj`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Extrait brut | `Extrait_Com_Fact_Obj` | A `flux`, B `libelle`, C `marque` (= `VO`), D `j1`, E `s7`, F `s4_prec_total`, G `mtd`, H `mtd_n1`, I `obj_mois`, J `jo_ecoules`, K `jo_mois`, L `jo_restants`, M `date_reference`, N `Code_concession`, O `Code_Plaque` | ⚠️ **Jours ouvrés différents par flux** : Commandes lundi-samedi (3/27/24 le 2026-10-05), Facturations lundi-vendredi (2/22/20). Toujours lire la ligne du bon flux |
| Résultat final | `BLOC 2_1 Com_Fact_Obj` | 25 colonnes A→Y : A `Plaque`, B `Concession`, C `VO` (constante), **D→N** `Cde – …` et **O→Y** `Fact – …` (J-1, 7 jours, Moy. hebdo 4 sem., Mois à date, Mois à date N-1, Objectif mois, Manque à date, Taux atteinte %, Projection fin de mois, Reste à faire / jour ouvré, Tendance) | **142 formules recalculées : 0 écart.** Types de lignes : concession (C = `VO`), total plaque (B = `TOTAL`, Plaque renseignée), **total global** (`['', 'TOTAL', 'TOTAL']`, **conservé volontairement** pour le niveau siège), plus une ligne vide `['', '', 'VO']` |

### Bloc 2_2 — BDC ouverts depuis plus de 15 jours
Même classeur. Chaîne : `BDC Ouvert + 15j` → `Extrait_BDC_Ouvert` → `BLOC 2_2 BDC Ouvert`.
Détail complet (requête, formules, règles) : `CADRAGE_VO.md` §11.1.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Extrait | `Extrait_BDC_Ouvert` | A `concession_proprietaire`, B `date_confirmation_bdc`, C `proprietaire` ⚠️, D `status`, E `etape_affaire`, F `statut_vehicule`, G `statut_stock`, H `vehicule_selectionne`, I `immatriculation`, J `marque`, K `modele`, L `Code_concession`, M `Code_Plaque`, N `Ancienneté_j` (`TODAY()-B`), O `Rang` | 494 BDC réels + ~505 lignes vides. Critère : offre acceptée, véhicule en cours de livraison (CL), BDC signé il y a **plus de 15 jours** |
| Détail (top 5 par concession) | `BLOC 2_2 BDC Ouvert` A→G | A `Code_concession`, B `immatriculation`, C `marque`, D `modele`, E `proprietaire` ⚠️, F `date_confirmation_bdc`, G `Ancienneté_j` | 281 lignes, plus ancien en premier ; **ex æquo > 5 lignes** (jusqu'à 9). Aucun filtre sur l'étape : 173 BDC à « 3- Offre en cours », 3 clos/perdus |
| Résumé par concession | `BLOC 2_2 BDC Ouvert` I→J | I `Concession` (code), J `Nb BDC VO` | **Total de la concession**, pas seulement les 5 du détail ; vérifié = extrait pour 68 concessions |

### Bloc 3 — Anomalies Achat/Reprise
Classeur `Bloc 3`. Chaîne : `Achat_VO_SF` → `Extrait_Achat_VO` → `BLOC 3 Ano Achat`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Dossiers à risque | `BLOC 3 Ano Achat` | A `Code_concession`, B `Numero_achat`, C `Immatriculation`, D `Date_achat`, E `Note_criticite`, F `Type_anomalie` | **82 dossiers = exactement l'extrait (note ≥ 4)**, 33 concessions, jusqu'à 8 par concession, aucun doublon. Fenêtre 7 jours glissants (28/09→03/10) |
| Extrait (25 col.) | `Extrait_Achat_VO` | `numero_achat`, `concession`, `repreneur` ⚠️, `date_achat`, `date_previsionnelle_entree_offre`, `immatriculation`, `prix_de_revient_ttc`, `prix_de_revient_offre_ttc`, `montant_vehicule_ttc`, `prix_reprise_offre`, `kilometrage_icar`, `kilometrage_offre`, `aide_a_la_reprise_offre`, `transfert_de_marge`, `ecart_prix`, `ecart_km`, `ecart_date`, `ecart_aides`, `score_date`, `score_km`, `score_prix`, `score_aides`, `note_criticite`, `type_anomalie`, `Code_concession` | Le listing final ne contient **pas** `repreneur` |

### Bloc 4 — Qualité du stock
Classeur `Bloc 4`. Chaîne : `Stock VO SF` → `Extrait_Stock_VO` → `BLOC 4 Stock_P1` / `P2`.
Source : stock VO (types ST/CL/IM), hors véhicules de démonstration.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Extrait (29 col.) | `Extrait_Stock_VO` | A `numero_vehicule`, B `concession`, C `statut`, D `destination`, E `marque`, F `famille`, G `modele`, H `energie`, I `kilometrage`, J `prix_vente_ttc`, K `jours_stock`, L `jours_publication`, M `date_achat`, N `date_entree_stock`, O `prix_achat_ttc`, P `prix_achat_ht`, Q `vin`, R `immatriculation`, S `id_icar_short`, T `date_livraison_souhaitee`, U `ventes_moy_mensuelle_meme_modele`, V `nb_photos`, W `Date_Livraison`, **X `Code_concession`**, Y `rang Sans prix`, Z `rang Sans destination`, AA `rang Sans photo`, AB `rang Jamais publié`, AC `rang CL en retard` | ~4 900 lignes vides ; rangs = sentinelle `999` pour les non-qualifiants |
| Synthèse par concession | `BLOC 4 Stock_P1` | A `Code_concession`, B `Stock_ST`, C `Stock_CL`, D `Stock_IM`, E `Portefeuille_livraison`, F `Sans_prix_nb`, G `Sans_destination_nb`, H `Sans_photo_nb`, I `Jamais_publie_nb`, J `CL_en_retard_nb` | **Recalculé : 0 écart sur 74 concessions.** ~62 lignes parasites (code vide) |
| Top détail | `BLOC 4 Stock_P2` | **4 tableaux** côte à côte, chacun `Code_concession, immatriculation, marque, modele, <jours en stock>` : Sans prix A→E, Sans destination G→K, Sans photo M→Q, Jamais publié S→W | ⚠️ La dernière colonne de chaque tableau porte le nom de la catégorie mais contient les **jours en stock**. Ex æquo > 5 lignes (jusqu'à 13) |

Définitions (formules réelles) : `Sans_prix` = ST dont `prix_vente_ttc` vide ; `Sans_destination` =
ST dont `destination` vide ; `Sans_photo` = ST avec `nb_photos` = 0 ; `Jamais_publie` = ST avec
`jours_publication` = -1 ; `Portefeuille_livraison` = CL de destination « Particulier » ;
`CL_en_retard_nb` = CL « Particulier » dont `date_livraison_souhaitee` < `TODAY()`.

**« CL en retard » est retiré complètement du mail** (décidé le 2026-10-06) : le détail n'existe plus
dans `BLOC 4 Stock_P2` et `CL_en_retard_nb` n'est plus affiché. Un nouveau bloc plus fiable sera
ajouté plus tard, après retour du service Data.

### Blocs 5, 6, 7 — Couverture, Excès, Santé Plaque
Classeur `Bloc 5/6/7`. Sources : `Vente VO 90j SF` et `Stock VO SF` (connectés) → `Extrait_Ventes_VO`,
`Extrait_Stock_VO` (25 col.).

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Ventes 90 j (extrait) | `Extrait_Ventes_VO` | A `numero_vente`, B `concession`, C `canal_vente`, D `statut`, E `date_vente`, F `date_livraison`, G `date_achat`, H `duree_detention_jours`, I `marque`, J `famille`, K `modele`, L `energie`, M `kilometrage`, N `date_premiere_mise_en_circulation`, O `vin`, P `immatriculation`, Q `id_vehicule_selectionne`, R `date_confirmation_commande`, S `facture_totale`, T `prix_vehicule_ttc`, U `marge_vente`, V `marge_vehicule`, **W `Code_concession`**, **X `Code_Plaque`**, Y `Date de Vente` | 4 968 ventes (07/07→03/10), toutes `Validée`, canaux Particuliers (4 847) et Flottes / Sociétés (121), toutes rattachées |
| Stock (extrait) | `Extrait_Stock_VO` | A→W identiques à l'extrait du Bloc 4 (jusqu'à `Date_Livraison`), **X `Code_concession`**, **Y `Code_Plaque`** | ⚠️ La colonne V `nb_photos` y est formatée en date (`30/01/1900` au lieu d'un nombre) — sans effet ici, aucun bloc ne l'utilise |
| Couverture (1 ligne/concession) | `BLOC 5 Couverture_VO` | A `Code_concession`, B `Stock_ST`, C `Ventes_VOP_moy_mensuelle`, D `Couverture_mois`, E `Ventes_30j`, F `Ventes_31_60j`, G `Tendance_ventes_pct`, H `Delai_median_livraison_j`, **I `Code Plaque`** (avec espace), J `Stock_ST_Plaque`, K `Ventes_VOP_moy_mensuelle_Plaque`, L `Couverture_mois_Plaque`, M `Delai_median_livraison_j_Plaque`, N `Ventes_30j_Plaque`, O `Ventes_31_60j_Plaque`, P `Tendance_ventes_pct_Plaque` | **Recalculé : 0 écart sur 74 concessions.** ⚠️ `Tendance_ventes_pct` est un **ratio** (`0,49` = +49 %) = (E−F)/F. Délai médian = médiane (date de vente − date de confirmation BDC) sur 90 j. **J→P = comparaison avec la Plaque, affichée dans le mail Service VO** (décidé le 2026-10-06) |
| Excès (1 ligne/concession × famille × énergie) | `BLOC 6 Excès_Stock` | A `Code_concession`, B `Famille`, C `Energie`, D `Stock`, E `Ventes_moy 90j/3`, F `Exces`, G `Ancien_nb` | **Recalculé : 1 écart sur 2 274 lignes** (casse, voir §8). `Ancien_nb` = stock en vente depuis **90 jours ou plus**. `Exces = MAX(Stock − ROUND(Ventes_moy), 0)`. 1 601 lignes vides sur 3 875. Pas de rang : trier/filtrer à la lecture |
| Santé Plaque (1 ligne/Plaque × famille × énergie) | `BLOC 7 Santé_Plaque` | A `Code_Plaque`, B `Famille`, C `Energie`, D `Stock`, E `Age_moyen`, F `Ventes_moy (90j/3)`, G `Exces`, H `Age_median`, I `Analyse_santé`, J `Couverture_brute`, K `Action_recommandée` | **Recalculé : 0 écart sur 1 352 lignes réelles** (sur 2 909). 75 % « NON SIGNIFICATIF ». **Réservé au futur mail Directeur** |

Règles de santé (formule réelle) : NON SIGNIFICATIF si stock < 3 **et** ventes < 3 ; CRITIQUE si âge
médian ≥ 120 ou âge moyen ≥ 180 ; FATIGUÉ si âge médian 90-119, ou 60-89 avec âge moyen > 120 ;
CORRECT si âge médian 60-89, ou < 60 avec âge moyen 90-120 ; sinon SAIN. `+ ⚠ PURGER ANCIENNES` si
excès > 30 et stock ≥ 5. Action selon santé × couverture (stock ÷ ventes, « Infini » si 0 vente) :
SAIN → ACHETER (< 1,5) / MAINTENIR (≤ 3) / BAISSER LES PRIX ou STOCK FRAIS - OK ; CORRECT → ACHETER (< 1) /
MAINTENIR (≤ 3) / BAISSER LES PRIX ; FATIGUÉ → ACHETER + BAISSER ANCIEN (< 1) / BAISSER LES PRIX (≤ 3) /
SOLDER LES ANCIENNES ; CRITIQUE → BAISSER LES PRIX (< 1,5) / SOLDER LES ANCIENNES (≤ 3) / SOLDER URGENT.

### Bloc 8 — Anomalies Ventes
Classeur `Bloc 8`. Chaîne : `Ventes_1j_SF` → `Extrait_Ventes_1j_SF` → `Bloc 8 Ano_Vente`.

| Donnée | Onglet | Colonnes | Notes |
|---|---|---|---|
| Extrait (27 col.) | `Extrait_Ventes_1j_SF` | A→Y : `numero_vente`, `concession`, `canal_vente`, `statut`, `date_vente`, `date_livraison`, `date_achat`, `duree_detention_jours`, `marque`, `famille`, `modele`, `energie`, `kilometrage`, `date_premiere_mise_en_circulation`, `vin`, `immatriculation`, `id_vehicule_selectionne`, `date_confirmation_commande`, `facture_totale`, `prix_vehicule_ttc`, `marge_vente`, `marge_vehicule`, `frais_estimes`, `frais_reels`, `ecart_fre` ; **Z `Code_concession`**, **AA `Type_anomalie`** | Fenêtre = hier + aujourd'hui (`BETWEEN J-1 AND CURRENT_DATE()`, date UTC) |
| Listing final | `Bloc 8 Ano_Vente` | A `Code_concession`, B `Immatriculation`, C `Marque`, D `Modele`, E `Marge_vehicule`, F `Duree_detention_j`, G `Date_vente`, H `Type_anomalie` | `QUERY` sur l'extrait, lignes avec anomalie et code concession |

Règles (formule réelle de `AA`) : « Marge négative » si marge véhicule < −1 000 € ; « Marge élevée » si
> 4 000 € ; « Détention longue » si > 180 j — **ces trois hors canal Primocar** ; « Écart FRE
significatif » si écart > 500 € et frais estimés non vides et ≠ 0 ; « Facturation Marchand non autorisée »
si canal Marchand hors concessions `PRIMO_*`. Plusieurs motifs se cumulent (` + `).

**Vide le lundi, c'est normal** : le 2026-10-05 le listing est vide car la fenêtre couvrait dimanche
(3 ventes un dimanche sur 90 jours). Les ventes du **samedi** (173 sur 90 j) sont couvertes par le mail
du **dimanche** — les mails partent bien le dimanche (confirmé 2026-10-05). Non vérifié sur données
vivantes ce jour-là ; volume attendu (rejeu 90 j) : ~14 anomalies/jour pour tout le groupe en médiane
(max 53).

## 5. Niveau Plaque

`BLOC 7 Santé_Plaque` : exclu du mail Service V1
(décision du 2026-09-11). Pas d'onglet Plaque dédié séparé au-delà de ceux-là.

## 6. Données personnelles — jamais dans un mockup non anonymisé

- `Extrait_BDC_Ouvert` colonne **C `proprietaire`** et `BLOC 2_2 BDC Ouvert` colonne **E `proprietaire`** :
  nom du vendeur, affiché dans le mail (décidé le 2026-10-06).
- `Extrait_Achat_VO` colonne **C `repreneur`** : nom du repreneur. Absent du listing final `BLOC 3`.

Les autres onglets finaux (Blocs 1, 2, 2_1, 3, 4, 5, 6, 7, 8) ne contiennent aucun nom de personne.

## 7. Limites de données connues (pas des erreurs de calcul)

- **Étiquettes famille différentes entre stock et ventes** (Bloc 6) : 379 ventes sur 4 968 (8 %) ont
  une famille absente du stock (`Clio V (BJA) Ph1 NG`, `Nouvelle 208`, `SANDERO (06/2022)` face à `CLIO`…).
  Elles ne sont rattachées à aucune ligne : l'excès de la ligne de stock correspondante est surestimé.
  Pas de table de correspondance (contrairement au VN : `Mapping Marque Modèle`).
- **Casse non harmonisée** : `COUNTIFS` ignore la casse, donc `I20` et `i20` se confondent (seul écart relevé au Bloc 6).
- **Énergies de ventes absentes du stock** : vide (78 ventes) ou `Hybride`.
- **Granularité du Bloc 7** : 75 % des lignes sont trop petites pour être diagnostiquées.

## 8. Pièges rencontrés (à ne pas refaire)

1. **Deux `Extrait_Stock_VO` différents** (29 vs 25 colonnes) — voir §1.
2. **Deux définitions de « commande 7 jours »** : création de l'offre (`BLOC 2 Offre`) vs confirmation
   du BDC (`BLOC 2_1`, `BLOC 2_2`). Préciser laquelle est lue.
3. **Jours ouvrés par flux** au Bloc 2_1 : lundi-samedi (Commandes) ≠ lundi-vendredi (Facturations).
4. **Filtre canal à espaces significatifs** : `'Flottes / Sociétés'` (espaces autour du `/`) à recopier à
   l'identique dans toute formule filtrant par canal (Bloc 5 le fait ; le Bloc 6 ne filtre pas mais sa
   source ne contient déjà que ces deux canaux).
5. **`VLOOKUP` pour une jointure Plaque** peut renvoyer un résultat décalé sans erreur : utiliser
   `XLOOKUP`/`RECHERCHEX` et vérifier contre le Référentiel.
6. **`JOINDRE` n'existe pas en français** : `TEXTJOIN`.
7. **Ex æquo** : les « top 5 » (`BLOC 2_2`, `BLOC 4 Stock_P2`) dépassent 5 lignes ; le plafond « top 5 + N
   autres » se fait à la composition du mail.
8. **Règle de tri inversée le 2026-09-25** : montant/note décroissant d'abord, date ensuite (Blocs 3 et 8).
9. **En-têtes irréguliers** : `Code Plaque` (BLOC 5, avec espace), `Code_Concession` (Mapping_Import),
   dernière colonne de `BLOC 4 Stock_P2` nommée comme la catégorie alors qu'elle contient des jours.
10. **Formules à `TODAY()`** (Blocs 4, 5, 6, 7, `Ancienneté_j` du Bloc 2_2) : résultat dépendant du jour de
    lecture, pas de J-1. Le Bloc 8 utilise `CURRENT_DATE()` en **UTC**.
