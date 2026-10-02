# Carte des données VO — où trouver quoi

**Statut : vivant, à tenir à jour à chaque fois qu'un onglet est renommé/déplacé.**
Dernière mise à jour : 2026-10-02.

Ce document répond à une seule question : **pour générer le mail VO (niveau Service), où
va-t-on chercher chaque donnée ?** Il complète `CADRAGE_VO.md` (qui documente le *pourquoi*
et l'historique des corrections) en donnant un accès direct *classeur → onglet → colonne*
sans avoir à refouiller. Même principe que `DATA_MAP_APV.md`.

**Piège permanent** : 6 fichiers Sheets séparés, chacun avec son propre connecteur BigQuery
actualisé indépendamment (voir §6) — toujours vérifier l'en-tête réel avant d'écrire dans une
colonne, ne jamais supposer.

## 1. Classeurs

| Classeur | ID | Rôle |
|---|---|---|
| Bloc 1 — Leads | `14TWu4moVg6lSOT5KLjnTCumeZcx-3M9Xg2vqpt4-ka4` | Leads VO reçus/non traités |
| Bloc 2 — Offres/Reprises + Bloc 9 — Commandes & Facturations vs Objectifs | `1C1jMlaD8M1TearS98aiC_J3t6lieq7sp2GdMq_fKDzI` | Même fichier, 2 chaînes d'onglets distinctes |
| Bloc 3 — Anomalies Achat/Reprise | `1PdjQzWi0Gbn1KhkaUvC6wPbdyiBIovI_TeB_YhyAraU` | Dossiers d'achat/reprise à risque (score 0-10) |
| Bloc 4 — Qualité du stock | `1NhHCqRM54yWcMomE1Qd0tKGG9KWRV8tvewq9hhCIPfM` | Sans prix/destination/photo, jamais publié, CL en retard |
| `Rapport quotidien VO` (fichier principal) — Blocs 5/6/7 | `1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU` | Couverture, Excès de stock, Santé Plaque — sources brutes partagées |
| Bloc 8 — Anomalies Ventes | `110ih-4TOZL8qJD4CHz9avQoHXCN70wU5Pdmcmga1fwI` | Marge négative/élevée, détention longue, écart FRE |
| `Référentiel Concession` | `1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY` | Classeur de Quentin, source de vérité transverse (concessions, plaques, mapping brut) |

## 2. Niveau Service — par bloc

### Bloc 1 — Leads
Tabs : requête BigQuery (`v_sf_lead`) → `Leads_SF` → jointure `Mapping` → `BLOC 1 Leads`
(final, consolidé par `Code_concession` via `QUERY`/`GROUP BY`).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Leads reçus/non traités (1 ligne/concession) | `BLOC 1 Leads` | `Code_concession, Date_reference, Leads_recus_J1, Leads_recus_7j, Leads_non_traites_J1, Leads_non_traites_7j` | Une ligne `Code_concession` vide subsiste (regroupe "Groupe Hess" + non-mappés) — **ignorer systématiquement à la lecture**, pas filtrée par la formule |

### Bloc 2 — Offres VO / Reprises
Tabs : requête BigQuery (`v_sf_quote`) → `Mapping` → `BLOC 2 Offre` (final).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Offres/reprises (1 ligne/concession) | `BLOC 2 Offre` | `Code_concession, Date_reference, Commandes_VOP_acceptees_J1/_7j, Offres_refusees_J1/_7j, Reprises_acceptees_J1/_7j` | Champs source ⚠️ : `TECH_Concession__c` (pas `TECH_ConcessionName__c`), `Nom_du_type_d_enregistrement__c` (pas `Type__c`), `Status` standard (pas `Statut__c`). Pas de filtre hors véhicule démo/buy-back (limite acceptée) |

### Bloc 9 — Commandes & Facturations vs Objectifs
Même fichier que le Bloc 2. Tabs : `Com/Fact/Obj` (Connected Sheet BigQuery) →
`Extrait_Com_Fact_Obj` → `BLOC 2_1 Com_Fact_Obj` (final).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Jours ouvrés du mois (constantes, **différenciées par flux**) | `Extrait_Com_Fact_Obj` | `$J:$J`/`$K:$K`/`$L:$L`, récupérées par `XLOOKUP("Commandes"/"Facturations"; A:A; J:J)` | ⚠️ **Différent du VN** : Commandes = calendrier lundi-samedi, Facturations = lundi-vendredi → **pas de référence fixe unique**, toujours passer par le `XLOOKUP` sur le nom du flux |
| Commandes/Facturations vs objectifs (1 ligne par concession, pas de détail marque) | `BLOC 2_1 Com_Fact_Obj` | J-1, 7j, moy. hebdo 4 sem., MTD, MTD N-1, Objectif mois, Manque à date, Taux atteinte %, Projection fin de mois, Reste à faire/jour ouvré, Tendance | Grain Plaque × Concession, colonne flux fixée à `"VO"`. **Pas de ligne TOTAL GROUPE** (seulement totaux Plaque). Concessions Bâle + BMW Motorrad exclues |

### Bloc 3 — Anomalies Achat/Reprise
Entièrement en SQL (dédup + score), onglet source → `BLOC 3 Ano Achat` (final, `QUERY` filtrée
`Code_concession <> ' '`).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Dossiers d'achat/reprise à risque | `BLOC 3 Ano Achat` | `Code_concession, Numero_achat, Immatriculation, Date_achat, Note_criticite, Type_anomalie` | Fenêtre **7 jours glissants** (volume J-1 seul jugé trop faible). Dédup déjà appliquée (`ROW_NUMBER PARTITION BY Vehicule_Achete__c`). Seuil de remontée : `note_criticite >= 4` |

### Bloc 4 — Qualité du stock
Source : `Extrait_Stock_VO` (`v_sf_vehicule_stock`, `TypeVNVO__c='VO' AND NOT is_vd__c`).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Synthèse par concession | `BLOC 4 Stock_P1` | `Code_concession, Stock_ST, Stock_CL, Stock_IM, Portefeuille_livraison, Sans_prix_nb, Sans_destination_nb, Sans_photo_nb, Jamais_publie_nb, CL_en_retard_nb` | `COUNTIFS` sur `Extrait_Stock_VO` |
| Top-5 détail par catégorie et concession | `BLOC 4 Stock_P2` | 5 tableaux côte à côte : Sans prix (A-E), Sans destination (G-K), Sans photo (M-Q), Jamais publié (S-W), **CL en retard (Y-AC)** — triée par jours de retard décroissant | Formules Sheet natives (`COUNTIFS` en astuce de rang), pas de requête BigQuery supplémentaire. "Sans photo" et "Jamais publié" fortement corrélés en pratique |

### Blocs 5/6/7 — Couverture, Excès de stock, Santé Plaque
Fichier principal `Rapport quotidien VO`. Sources brutes partagées : `Vente VO 90j SF`
(malgré le nom historique "30j"), `Stock VO SF` → `Extrait_Ventes_VO` / `Extrait_Stock_VO`.

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Rotation-Couverture (1 ligne/concession) | `BLOC 5 Couverture_VO` | `Code_concession, Stock_ST, Ventes_VOP_moy_mensuelle, Couverture_mois, Ventes_30j, Ventes_31_60j, Tendance_ventes_pct, Delai_median_livraison_j` + extension Plaque : `Code_Plaque, Stock_ST_Plaque, Ventes_VOP_moy_mensuelle_Plaque, Couverture_mois_Plaque, Delai_median_livraison_j_Plaque, Ventes_30j_Plaque, Ventes_31_60j_Plaque, Tendance_ventes_pct_Plaque` | ⚠️ Filtre canal **obligatoire et identique partout** (Blocs 5/6/7) : `Canal_de_vente__c IN ('Particuliers', 'Flottes / Sociétés')` — espaces autour du `/` significatifs. `Delai_median_livraison_j` vide pour BMW Motorrad (normal, pas de bon de commande Salesforce) |
| Excès de stock (1 ligne/concession × famille × énergie) | `BLOC 6 Excès_Stock` | `Code_concession, Famille, Energie, Stock, Ventes_moy (90j/3), Exces, Ancien_nb` | Pas de colonne de rang — **Claude filtre/trie à la lecture** (table ~300 Ko, lisible d'un coup). `Exces = MAX(Stock - ROUND(Ventes_moy), 0)` |
| Santé Plaque (1 ligne/Plaque × famille × énergie) | `BLOC 7 Santé_Plaque` | Même construction que Bloc 6 + `Age_moyen, Age_median, Couverture_brute` (intermédiaire), `Analyse_santé, Action_recommandée` (formules MAP/LAMBDA, seuils fournis par Quentin) | **Exclu du mail Service V1** — réservé au futur mail Directeur de plaque. Piège : `JOINDRE` n'existe pas en FR, utiliser `TEXTJOIN` (nom anglais + `;` séparateur) |

### Bloc 8 — Anomalies Ventes
Tabs : `Ventes_1j_SF` (Connected Sheet BigQuery) → `Extrait_Ventes_1j_SF` → `Bloc 8 Ano_Vente`
(final, renommé 2026-09-15).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Anomalies de vente du jour | `Bloc 8 Ano_Vente` | `Code_concession, Immatriculation, Marque, Modele, Marge_vehicule, Duree_detention_j, Date_vente, Type_anomalie` | Fenêtre **~J-1** (`date_vente >= J-1`, resserrée le 2026-09-15 depuis 7j glissants). Seuils : Marge négative <-1000€, Marge élevée >4000€, Détention longue >180j, Écart FRE significatif >500€ (et `frais_estimes` non vide), Facturation Marchand non autorisée hors `PRIMO_*` — tous hors canal Primocar sauf le dernier |

## 3. Transco concession/plaque

Chaque classeur a son propre onglet `Mapping` local, alimenté par import depuis
`Référentiel Concession > Mapping_Sources`, puis consolidation par `Code_concession`
(`QUERY`/`GROUP BY` — plusieurs marques/sites peuvent pointer vers le même code).

**Piège rencontré (Bloc 5, extension Plaque)** : la première version utilisait un
`VLOOKUP($A2, Extrait_Stock_VO!$X:$Y, 2, FALSE)` pour récupérer `Code_Plaque` depuis la
concession, qui renvoyait des résultats décalés/faux (ex. `BMW_BESANCON` associé à
`PLQ_BMW_MOTO` au lieu de `PLQ_BMW`) — corrigé avec `RECHERCHEX` (XLOOKUP). **Toujours
vérifier une jointure Plaque contre le Référentiel avant utilisation**, ce type d'erreur ne
saute pas aux yeux.

## 4. Niveau Plaque

Deux emplacements : les colonnes d'extension Plaque directement dans `BLOC 5 Couverture_VO`
(comparaison concession vs Plaque), et l'onglet séparé `BLOC 7 Santé_Plaque` (diagnostic
réseau). **Les deux sont exclus du mail Service V1** — réservés à un futur mail Directeur de
plaque (même principe de périmètre que VN §4).

## 5. Données personnelles

Aucune colonne nominative (nom client, vendeur, réceptionnaire) identifiée dans les onglets
finaux documentés ci-dessus — les blocs VO sont tous des agrégats ou des listes orientées
véhicule (immatriculation, marque, modèle), pas des listes nominatives contrairement à
l'APV. À revérifier si un nouveau bloc ajoute un champ nominatif.

## 6. Pièges génériques rencontrés ce chantier (à ne pas refaire)

1. **Filtre canal à espaces significatifs** (`'Flottes / Sociétés'`) — doit être recopié à
   l'identique dans toutes les formules `COUNTIFS` qui filtrent par canal (Blocs 5/6/7),
   sinon sous-comptage silencieux (déjà arrivé, corrigé 2026-09-10).
2. **`VLOOKUP` pour une jointure Plaque peut renvoyer un résultat décalé sans erreur visible**
   — préférer `RECHERCHEX`/XLOOKUP, toujours vérifier contre le Référentiel (§3).
3. **`JOINDRE` n'existe pas en français** dans ce Sheet — utiliser `TEXTJOIN`.
4. **Règle de tri/troncature inversée le 2026-09-25** : montant/note décroissant en premier,
   date décroissante en cas d'égalité (Blocs 3 et 8) — remplace l'ancienne règle
   date-d'abord. Gérée par Claude à la composition du mail, pas par une colonne Sheet.
5. **Ligne `Code_concession` vide non filtrée** (Bloc 1, "Groupe Hess" + non-mappés) — à
   ignorer systématiquement à la lecture, la formule source ne le fait pas.
6. **6 fichiers Sheets actualisés indépendamment, sans synchronisation** — risque de
   composer un mail avec des blocs de jours différents. Auto-refresh 6h-7h en cours de mise
   en place (Quentin) ; une vérification de fraîcheur avant envoi reste à construire (voir
   `CADRAGE_VO.md` §16-17).
