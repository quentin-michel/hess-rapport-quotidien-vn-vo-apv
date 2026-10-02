# Carte des données VN — où trouver quoi

**Statut : vivant, à tenir à jour à chaque fois qu'un onglet est renommé/déplacé.**
Dernière mise à jour : 2026-10-02.

Ce document répond à une seule question : **pour générer le mail VN (niveau Service), où
va-t-on chercher chaque donnée ?** Il complète `CADRAGE_VN.md` (qui documente le *pourquoi*
et l'historique des corrections) en donnant un accès direct *classeur → onglet → colonne*
sans avoir à refouiller. Même principe que `DATA_MAP_APV.md`.

**Piège permanent** : les classeurs sont des Sheets vivants. Onglets renommés, colonnes
déplacées ou réordonnées sont déjà arrivés plusieurs fois ce chantier (voir §6). **Toujours
vérifier l'en-tête réel avant d'écrire dans une colonne**, ne jamais supposer.

## 1. Classeurs

| Classeur | ID | Rôle |
|---|---|---|
| Bloc 1 — Leads VN | `1oQzC5CV8Xqb6oTVAmNakcn3pSJD0yqP1eSdE7guHn80` | Leads VN reçus/non traités |
| Bloc 2 — Commandes & Facturations VN vs Objectifs | `14iuxhKZr34StlxCn8IodM9iquoqH9wnc5EhsBYxBUDE` | Pacing commandes/facturations par concession × marque |
| Bloc 3 (Stock VN/VD) + Bloc 4 (Couverture/Excès/Plaque) | `10cOmCg_e8JKKpaHY0pI6QTPWLehO_VVfVAU6bXAROWE` | Même fichier, 2 chaînes d'onglets distinctes (stock, puis ventes+couverture) |
| Bloc 6 — Anomalies Ventes VN/VD | `16xQnrbCZpPP2sDy4WxJvglRdIVYkwx31wiWC_n0lKcg` | Marge négative/suspecte, détention longue VD |
| `Référentiel Concession` | `1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY` | Classeur de Quentin, source de vérité transverse (concessions, plaques, mapping brut) |

## 2. Niveau Service — par bloc

### Bloc 1 — Leads VN
Tabs : `Leads_SF_VN` (Connected Sheet BigQuery) → `Extrait Leads_SF_VN` → `BLOC 1 Leads VN`
(onglet final).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Leads reçus/non traités (1 ligne/concession) | `BLOC 1 Leads VN` | `Code_concession, Date_reference, Leads_recus_J1, Leads_recus_7j, Leads_non_traites_J1, Leads_non_traites_7j` | Structure identique au Bloc 1 VO. Filtre VN géré côté connecteur BigQuery, pas visible via `gws` |

### Bloc 2 — Commandes & Facturations VN vs Objectifs
Tabs : `Mapping` (transco), `Obj Com/Fact.` (Connected Sheet, objectifs) → `Extrait_ComFact`
(extraction réduite) → `BLOC 2` (final).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Jours ouvrés du mois (constantes) | `Extrait_ComFact` | `$J$2`/`$K$2`/`$L$2` = écoulés/total/restants | Référence **fixe** réutilisée telle quelle dans tout `BLOC 2` (contrairement au VO, qui a un calendrier différent par flux, voir `DATA_MAP_VO.md`) |
| Commandes/Facturations vs objectifs (1 ligne par concession × marque + totaux Plaque/marque) | `BLOC 2` | Par flux (Commandes, Facturations) : J-1, 7j, moy. hebdo 4 sem., MTD, MTD N-1, Objectif mois, Manque à date, Taux atteinte %, Projection fin de mois, Reste à faire/jour ouvré, Tendance | **Pas de ligne TOTAL GROUPE** (retirée 2026-09-25). BMW Motorrad : `Nb_commande_d__claratif` (déclaratif mensuel, pas de détail J-1/7j) |
| Transco brute → canonique | `Mapping` | `Valeur_Source → Code_concession/Code_Plaque` | — |

### Bloc 3 — Stock VN/VD
Tabs : `DM_Stock_VN_VD` (Connected Sheet BigQuery) → `Extrait_Stock_VN_VD` (extraction
finale) → `Bloc 3 - P1 Stock VN_VD` / `Bloc 3 - P2 Stock VN_VD`.

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Détail stock + calculs (1 ligne/véhicule) | `Extrait_Stock_VN_VD` | A-U = colonnes de la requête BigQuery dans l'ordre (Concession, Est_VN_VD_ou_VO, Statut_de_stock, Detail_statut_stock, Numero_de_stock, CRC_vehicule, Serie_VIN, Libelle_marque, Libelle_modele, Date_achat, Numero_commande_constructeur, Date_commande_constructeur, Date_commande_client, Date_livraison_a_client, Est_contremarque, Prix_achat, Somme_options_constructeur, Somme_options_complementaires, Somme_frais, Montant_surestimation, Somme_aides) ; **V**=Ancienneté depuis achat, **W**=Durée de contremarque, **X**=Valeur_stock, **Y**=Code_concession, **Z**=Code_Plaque, **AA**=Rang âge VN, **AB**=Rang âge VD, **AC**=Rang contremarqué, **AD/AE**=Marque/Modèle harmonisés (ajoutées pour le Bloc 4, voir ci-dessous) | `Nb_jours_depuis_date_achat` natif de BigQuery est vide à 100% — ne pas l'utiliser, c'est `V` (calcul Sheet) qui sert |
| Synthèse par concession | `Bloc 3 - P1 Stock VN_VD` | Stock VN, Stock VD, Stock âgé VN (+6 mois/180j), Stock âgé VD (+6 mois), Contremarqué +90j | `COUNTIFS` sur `Extrait_Stock_VN_VD` |
| Top-5 détail par concession | `Bloc 3 - P2 Stock VN_VD` | 3 `QUERY` : Stock âgé VN, Stock âgé VD, Contremarqué — colonnes renvoyées : Code_concession, N° de stock, VIN, Marque, Modèle, puis Ancienneté (ou Durée de contremarque) | Basé sur les colonnes de rang (AA/AB/AC), sentinelle `999` pour les non-qualifiants (pas de texte vide, casse `QUERY` sinon) |

### Bloc 4 — Couverture, Excès de stock, Comparaison Plaque
Même fichier que le Bloc 3. Tabs : `Mapping Marque Modèle` (transco libellés), `DM_Vente_VN_VD`
(Connected Sheet) → `Extrait_Vente_VN_VD` → `BLOC 4 Couverture VN` (final).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Transco libellés marque/modèle | `Mapping Marque Modèle` | `Marque (source), Libellé modèle (source), Marque harmonisée, Modèle harmonisé` | Construite par Quentin — 163/344 paires stock/ventes sans correspondance exacte avant harmonisation |
| Ventes 90j agrégées (1 ligne/concession × marque × modèle) | `Extrait_Vente_VN_VD` | A=Concession, B=Libelle_marque, C=Libelle_modele, D=nb_ventes_90j, E=ventes_moy_mensuelle, F=Code_concession, G=Code_Plaque, H=Marque harmonisée, I=Modèle harmonisé | Source `datamart_ventes.entete_du_dossier` + `vehicules` (**pas** `v_sf_vente`, Modele_Vehicule__c trop souvent vide/technique côté Salesforce) |
| Couverture/Excès (1 ligne/concession × marque × modèle harmonisés) | `BLOC 4 Couverture VN` | A=Code_concession, B=Marque harm., C=Modèle harm., D=Stock, E=Ventes moy., F=Couverture, G=Excès de stock, H=Ancien_nb (+6 mois), I=Rang (top 3 excès), J=Code_Plaque, K=Stock Plaque, L=Ventes moy. Plaque, M=Couverture Plaque | Exclut les lignes `Code_concession` vide (39% des lignes brutes, jugé non prioritaire par Quentin). **Colonnes J-M (comparaison Plaque) réservées au futur mail Directeur de plaque — à retirer du mail Service** |

### Bloc 6 — Anomalies Ventes VN/VD
Tabs connectées : `entete_du_dossier`, `vehicules`, `lignes_du_dossier` → `DM Vente` →
`Extrait Vente VN/VD` → `BLOC 6 - Anomalie Vente VN-VD` (final).

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| Détail ventes + marges + classification (1 ligne/dossier) | `Extrait Vente VN/VD` | Colonnes requête (A-T) : numero_dossier, vin, immatriculation, Concession, marque, modele, vn_vd, Vendeur ⚠️, categorie, destination, energie, Date_de_vente, date_achat_vehicule, ca_brut_vehicule_ht, cout_acquisition_ht, remise_ht, transfert_de_marge_ht, aides_au_chassis_ht, marge_brute_vehicule_ht, marge_dossier_icar_ht ; puis Code_concession/Code_Plaque (RECHERCHEX via `Mapping` local), Durée de détention (VD), % Marge brute Véhicule | ⚠️ **Colonnes réordonnées le 2026-09-25** : `% Marge brute Véhicule` déplacée en **U**, ce qui décale `Code_concession/Code_Plaque/Durée de détention/Anomalie VD/Pas a signaler` en **V/W/X/Y/Z**, et place `A signaler` en **AA**, `A vérifier` en **AB**. **Toute lettre de colonne ci-dessus est à revérifier sur le Sheet avant usage** — la formule du listing final (ci-dessous) a été écrite avant ce réordonnancement et référence encore `U/V` comme Code_concession/Code_Plaque |
| Listing final (anomalies du jour) | `BLOC 6 - Anomalie Vente VN-VD` | `QUERY` : numero_dossier, Code_concession/Code_Plaque, marque/modèle, vn_vd, destination, les 2 marges, 3 colonnes d'anomalie (Anomalie VD / À signaler / À vérifier) | Seuil générique BMW hors BMW/MINI actuellement **cassé** (`$Z$1` pointe vers un en-tête texte, pas un nombre — comparaison toujours vraie, voir §6) |

## 3. Transco concession/plaque

Le `Mapping` local de chaque classeur (Bloc 2, Bloc 6) est alimenté par `IMPORTRANGE` depuis
`Référentiel Concession > Mapping_Sources` (même source que VO/APV) ; `Code_Plaque` récupéré
par `RECHERCHEX` (XLOOKUP), pas par `VLOOKUP` (piège VO déjà rencontré, voir
`DATA_MAP_VO.md` §4 — vérifier qu'il ne se reproduit pas ici si une nouvelle formule est
ajoutée).

**Piège spécifique IMPORTRANGE** : la formule doit être saisie puis autorisée manuellement
une première fois dans l'UI Sheets — sinon les `RECHERCHEX` en aval échouent silencieusement
sans erreur visible côté requête.

## 4. Niveau Plaque — réservé à un futur mail Directeur

Les colonnes de comparaison Plaque (Bloc 4, colonnes J-M de `BLOC 4 Couverture VN`) existent
déjà mais sont **réservées au futur mail Directeur de plaque** — décision de périmètre prise
le 2026-09-23, retrait du mail Service pas encore exécuté dans la maquette. Pas d'onglet
Plaque dédié séparé pour VN (contrairement à `Plaque APV` côté APV) : la comparaison vit
directement dans l'onglet concession.

## 5. Données personnelles — jamais dans un mockup non anonymisé

- `Extrait Vente VN/VD` (classeur Bloc 6) : colonne **Vendeur** — nom du vendeur.

Aucune autre colonne nominative identifiée dans les onglets finaux documentés ci-dessus
(Blocs 1-4 sont des agrégats sans nom de personne). Immatriculation/VIN ne sont pas traités
comme donnée personnelle dans ce chantier (convention déjà actée côté APV/VO).

## 6. Pièges génériques rencontrés ce chantier (à ne pas refaire)

1. **Champ `Est_vehicule_courtoisie` est INT64`** — ne jamais le comparer à `'0'` entre
   guillemets (erreur rencontrée et corrigée le 2026-09-17).
2. **`IF(condition; COUNTIFS(...)+1; "")` casse `QUERY` en aval** — remplacer le texte vide
   par la sentinelle numérique `999` pour les lignes non qualifiantes.
3. **`QUERY` peut mal deviner l'en-tête** quand la plage commence à la ligne 2 d'un onglet —
   ajouter `; 0` en 3ᵉ argument force "pas d'en-tête".
4. **Désaccord de libellés marque/modèle entre sources** (stock vs ventes, préfixes/suffixes/
   accents/codes techniques) — toujours passer par une table de transco dédiée
   (`Mapping Marque Modèle`), ne jamais comparer les libellés bruts directement.
5. **Un réordonnancement manuel de colonnes casse silencieusement toute formule qui les
   référence par lettre ailleurs** (Bloc 6, §2 ci-dessus) — même famille de bug que le
   piège §8.1 de `CADRAGE_APV.md` (onglet renommé → référence orpheline), mais ici c'est un
   déplacement de colonnes dans le même onglet. Toujours revérifier l'en-tête réel avant de
   réutiliser une lettre de colonne documentée.
6. **Comparaison nombre/texte toujours vraie côté Sheets** : une formule qui compare une
   valeur à une cellule censée contenir un seuil, mais qui contient en réalité un texte
   (en-tête de colonne mal référencé), ne renvoie jamais `FAUX` — bug actuellement ouvert sur
   le seuil générique du Bloc 6 (`$Z$1`, voir §2).
