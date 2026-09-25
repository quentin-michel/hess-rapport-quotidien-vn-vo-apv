# Carte des données APV — où trouver quoi

**Statut : vivant, à tenir à jour à chaque fois qu'un onglet est renommé/déplacé.**
Dernière mise à jour : 2026-09-25.

Ce document répond à une seule question : **pour générer le mail APV (niveau Service,
Directeur ou Plaque), où va-t-on chercher chaque donnée ?** Il complète
`CADRAGE_APV.md` (qui documente le *pourquoi* et l'historique des corrections) en
donnant un accès direct *classeur → onglet → colonne* sans avoir à refouiller.

**Piège permanent** : les classeurs sont des Sheets vivants, édités en parallèle par
Corentin/Quentin. Onglets renommés, colonnes déplacées ou tableaux à double mise en
page sont déjà arrivés plusieurs fois ce chantier (voir §5). **Toujours vérifier
l'en-tête réel avant d'écrire dans une colonne**, ne jamais supposer.

## 1. Classeurs

| Classeur | ID | Rôle |
|---|---|---|
| `Rapport quotidien APV` | `1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw` | Classeur principal — KPI par concession et par plaque |
| `Anomalies forfaits` | `1T_BKjedX0yH7ENq4Z_88OWlGnBUu6RSez5ohLb0YscU` | Forfaits à marge faible/négative (détection dédiée) |
| `Prix/Remises forcés` | `1ZZ2Y1EtbonrgOeJ0Zf81XngcZCiifCvtAP2dHczl7GY` | Remises/prix forcés Atelier+Magasin (**bloc pas encore branché au niveau Plaque**) |
| `Référentiel Concession` | `1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY` | Classeur de Quentin, source de vérité transverse (concessions, plaques, mapping brut) |

## 2. Niveau Service (1 concession) — `Rapport quotidien APV`

| Donnée | Onglet | Colonnes clés | Notes |
|---|---|---|---|
| KPI CA/objectifs/efficience/productivité/encours + volume Magasin (1 ligne/concession) | `Analyse Globale` | A=Plaque, B=Code concession canonique, C1=date de référence (ligne 1), ligne 2=en-têtes, ligne 3+=data. **AT**=Nb pièces magasins vendues J-1, **AU**=% pièces vendues à perte J-1 (ajoutés 2026-09-25) | Toutes les formules SUMIFS/AVERAGEIFS pointent vers les onglets bruts ci-dessous |
| Top 5 encours les plus anciens par concession | `Encours prioritaires` | Code concession, N° OR, Immatriculation, Ancienneté (j), Montant MO/PR encours, Valeur totale OR, Dépréciation, Score | **Plafonné à 5/concession** — pas une liste exhaustive |
| Ventes à perte pièces (J-1) | `Analyse pièces client J-1` (renommé, ex-"Analyse pièces J-1") | B=Code Concession, U=Plaque, J=Nom du client ⚠️ | ⚠️ Données personnelles |
| Ventes à perte pièces Magasin, volume total (J-1) | `Détail facturation magasin journaliere` | B=Concession (brut), **C**=Date_document, T=Code concession (fixe, ajouté manuellement — ne bouge pas si la requête source change), **S**=Est à perte (`=IF(P<Q;1;0)`, ajouté 2026-09-25), H=Nom_Magasinier ⚠️, I=Nom_client ⚠️ | ⚠️ Données personnelles. Champ `Magasin` retiré de la requête le 25/09 → tout a décalé d'1 colonne **sauf** `Code concession` (fixe en T) |
| OR en cession interne, efficience >105% | `Efficience OR CI trop élevé` | **2 tableaux côte à côte** : A:F (affichage %) et I:N (calcul décimal). A=Code concession, G=Plaque, C=Réceptionnaire ⚠️ | ⚠️ Ne pas confondre les deux tableaux ; Plaque en G, **pas** en O |
| OR à taux de remise MO/PR interne élevé | `Taux remise MO/PR interne élevé` | A=Code concession, K=Plaque, C=Nom client ⚠️, D=Réceptionnaire ⚠️ | ⚠️ Données personnelles |
| Seuils métier (productivité basse, encours surveillance/alerte/critique) | `Référentiel métier` | `$B$11` (productivité), `$B$15/16/17` (encours) | |

## 3. Transco concession/plaque — `Rapport quotidien APV`

| Onglet | Rôle | Colonnes |
|---|---|---|
| `Mapping concession` | Valeur brute BigQuery → code canonique (entete_or, entete_pieces) | A-D = Source_BigQuery/Champ_Source/Valeur_Source/Code_Concession_Canonique (import filtré depuis `Référentiel Concession > Mapping_Sources`) ; E/F = Code_Plaque/Nom_Plaque ajoutés (non utilisés par `Plaque APV`, redondant avec `Concession-plaques`) |
| `Concession-plaques` | Code canonique → Plaque — **LA** source de vérité Plaque | Import direct de `Référentiel Concession > Concessions_Plaques!A:D` (Code_Concession, Nom_Concession, Code_Plaque, Nom_Plaque) |

**Piège important** : les champs BigQuery `Regroupement_Concession_APV`
(`entete_pieces`) et `Regroupement_concessions_APV` (`entete_or`) **ne font aucun
regroupement multi-marques** — vérifié empiriquement, leur valeur est identique au
champ `Concession` brut. Ne jamais s'y fier pour la transco ; toujours passer par
`Mapping concession`/`Mapping_Sources`.

## 4. Niveau Plaque (réseau) — `Rapport quotidien APV`

Onglet `Plaque APV` — 1 ligne par plaque (13 plaques), généré automatiquement.

| Colonne | Donnée | Formule (résumé) | Source brute |
|---|---|---|---|
| A | Plaque | `=UNIQUE('Concession-plaques'!$C:$C)` | — |
| B1 | Date de référence | `='Analyse Globale'!$C$1` | — |
| B | Efficience J-1 | `SUMIFS(Temps_facture)/SUMIFS(Rappel_temps_passe)` par Plaque+Date | `Historique efficience/prod` (I=Plaque) |
| C | Productivité J-1 | `SUMIFS(Temps_facture)/SUMIFS(Temps_passe_total)` par Plaque+Date | `Historique efficience/prod` (I=Plaque) |
| D | Valeur encours MO+PR | `SUMIFS(Montant_MO_PR_encours)` par Plaque | `Encours à date` (Y=Plaque, M=Montant) |
| E | Encours +90j (nb) | `COUNTIFS(Ancienneté>=90)` par Plaque | `Encours à date` (Y=Plaque, I=Ancienneté) |
| F | Encours en j de CA | Valeur encours ÷ ((somme CA MO 6 mois + somme CA PR interne 6 mois)/180), pondéré réseau | `Historique CA mensuel ateliers` (F=Plaque, C=CA MO, D=CA PR interne) |
| G | Pièces en marge négative | `COUNTIFS` par Plaque | `Analyse pièces client J-1` (U=Plaque) |
| H | Forfaits marge <10% | `RECHERCHEV` + `IMPORTRANGE` vers un résumé agrégé (pas le détail brut) | `Anomalies forfaits > Plaque - Forfaits marge faible` |
| I | OR remise élevée | `COUNTIFS` par Plaque | `Taux remise MO/PR interne élevé` (K=Plaque) |
| J | OR efficience CI élevée | `COUNTIFS` par Plaque | `Efficience OR CI trop élevé` (**G**=Plaque) |

**Statut connu au 2026-09-25** : `UNIQUE()` ne remonte que 11 plaques sur 13
(`PLQ_PRIMOCAR` et `PLQ_VEODROME` suspectées manquantes) — à vérifier/corriger.

**Principe de conception (validé avec Corentin le 25/09)** : au niveau Plaque/Directeur,
le bloc APV du mail **ne remonte pas de CA/objectif** — uniquement des compteurs de
problème (voir mémoire `feedback_plaque_mail_apv_signals_not_ca`). Les totaux Plaque
sont calculés en **agrégation pondérée** (somme des numérateurs/dénominateurs réseau),
jamais en moyenne simple des % par concession.

## 5. Classeur `Anomalies forfaits`

| Onglet | Rôle | Colonnes |
|---|---|---|
| `Mapping` | Même structure que `Mapping concession` (transco brute→canonique) | Source_BigQuery/Champ_Source/Valeur_Source/Code_Concession_Canonique |
| `Extrait J-1 - Marges<10%` | Forfaits à marge <10% du jour | V=Code concession (déjà branché), W=Plaque, E=Nom_client ⚠️, H=Receptionnaire ⚠️ |
| `Concession-plaques` | Import local (même source que dans `Rapport quotidien APV`) | — |
| `Plaque - Forfaits marge faible` | Résumé agrégé par plaque, **seul ce qui est réimporté dans `Plaque APV`** (pas le détail brut avec les noms) | A=Plaque (`UNIQUE`), B=Nb forfaits (`COUNTIFS`) |
| `Forfaits pièces suspectes` (DATA_SOURCE) | Détection n°3 — **en pause depuis 2026-09-23**, non utilisée dans le mail actuel | — |

## 6. Classeur `Prix/Remises forcés` — **pas encore branché au niveau Plaque**

| Onglet | Rôle | Colonnes |
|---|---|---|
| `Mapping concessions` | Transco brute→canonique complet (entete_or, entete_pieces, v_sf_account) | A-D |
| `Prix/Remises forcés` | Extrait Atelier+Magasin du jour | V=Code concession (corrigé le 25/09 — pointait vers un onglet `Mapping` renommé en `Mapping concessions`, fallback `IFERROR` masquait l'erreur), C=Nom client ⚠️, D=Réceptionnaire ⚠️ |
| `Contact` | Destinataires par concession | Concession, Fonction (Chef d'atelier / Responsable Magasin), Nom complet ⚠️, Email |
| `Transco_Concessions` | Mapping legacy différent (nom brut → nom groupé lisible), potentiellement redondant avec `Mapping concessions` — statut à clarifier avec Corentin | |

Pour brancher ce classeur au niveau Plaque : même recette que pour les forfaits
(§4/§5) — ajouter une colonne `Plaque` sur `Prix/Remises forcés` (via import de
`Concession-plaques`), puis un onglet résumé agrégé par plaque, puis
`RECHERCHEV`+`IMPORTRANGE` depuis `Plaque APV`. Pas fait à ce jour.

## 7. Données personnelles — où elles sont, jamais dans un mockup non anonymisé

Colonnes contenant des noms de clients/salariés réels (à toujours anonymiser avant
tout commit git ou brouillon partagé) :

- `Rapport quotidien APV` : `Analyse pièces client J-1` (Nom du client, Réceptionnaire),
  `Détail facturation magasin journaliere` (Nom_client, Nom_Magasinier),
  `Efficience OR CI trop élevé` (Réceptionnaire/Mécanicien), `Taux remise MO/PR interne
  élevé` (Nom client, Réceptionnaire)
- `Anomalies forfaits` : `Extrait J-1 - Marges<10%` (Nom_client, Receptionnaire)
- `Prix/Remises forcés` : `Prix/Remises forcés` (nom_client, receptionnaire),
  `Contact` (Nom complet, Email)

Les onglets résumés agrégés (`Plaque APV`, `Plaque - Forfaits marge faible`) ne
contiennent **aucune** donnée personnelle — uniquement des compteurs — c'est
pourquoi ce sont eux qu'on réimporte entre classeurs, jamais le détail brut.

## 8. Pièges génériques rencontrés ce chantier (à ne pas refaire)

1. Un onglet renommé en cours de route casse silencieusement toute formule qui le
   référence par nom — si l'erreur est avalée par un `IFERROR` avec fallback sur la
   valeur brute, le bug reste invisible. Toujours préférer un fallback visible
   (`"MAPPING MANQUANT: "&valeur`) à un silence.
2. Ne jamais supposer qu'une colonne est vide avant d'y écrire — vérifier l'en-tête
   réel (arrivé 3 fois : `Encours à date` colonnes W/X, `Efficience OR CI trop élevé`
   colonne O au lieu de G).
3. `IMPORTRANGE` ne traverse qu'un seul onglet/plage à la fois — deux structures
   sources différentes (ex. mapping valeur-brute vs mapping plaque) nécessitent deux
   imports séparés, même dans le même classeur.
4. Import inter-classeurs : toujours importer le **résultat agrégé** (compteur par
   plaque), jamais le détail brut, pour éviter de propager des données personnelles
   d'un classeur à l'autre.
5. Une plage type `NomOnglet!A1:D100` contenant un `/` dans le nom d'onglet doit être
   URL-encodée si on y accède via l'API brute (le CLI `gws` ne le fait pas
   automatiquement).
6. Retirer un champ d'une requête `DATA_SOURCE` décale toutes les colonnes de
   l'extrait qui le suivent — **sauf** les colonnes ajoutées manuellement en dehors
   de la requête (ex. `Code concession` sur `Détail facturation magasin
   journaliere`, ancrée en position fixe) : elles restent où elles sont, ce qui
   peut désynchroniser une formule qui référence une autre colonne par sa position
   d'avant le changement (arrivé le 25/09 : `Date_document` glissée de D à C après
   retrait du champ `Magasin`, formule `Analyse Globale` cassée jusqu'à correction).
