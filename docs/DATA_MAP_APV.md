# Carte des données APV — où trouver quoi

**Statut : vivant, à tenir à jour à chaque fois qu'un onglet est renommé/déplacé.**
Dernière mise à jour : 2026-10-05 (bloc malfaçons et gestes commerciaux).

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
| KPI CA/objectifs/efficience/productivité/encours + volume Magasin (1 ligne/concession) | `Analyse Globale` | A=Code plaque, B=Code concession canonique, **B1**=date de référence (A1 = libellé ; déplacée de C1 le 2026-10-02), ligne 1 à partir de C = bandeaux de blocs, ligne 2=en-têtes, ligne 3+=data. Détail des 66 colonnes (A→BN) en §2.1 | Toutes les formules SUMIFS/AVERAGEIFS pointent vers les onglets bruts ci-dessous. **Lire par nom d'en-tête, pas par lettre** (colonnes réagencées le 2026-10-02, 3 colonnes malfaçons insérées le 2026-10-05) |
| Top 5 encours les plus anciens par concession | `Encours prioritaires` | Code concession, N° OR, Immatriculation, Ancienneté (j), Montant MO/PR encours, Valeur totale OR, Dépréciation, Score | **Plafonné à 5/concession** — pas une liste exhaustive |
| Ventes à perte pièces (J-1) | `Analyse pièces client J-1` (renommé, ex-"Analyse pièces J-1") | 22 colonnes (mise en page du 2026-10-02) : A=Canal (Atelier/Magasin), **B=Concession (nom)**, C=N° OR (n° de document côté Magasin), D=Date (format Date), G=Réceptionnaire/Nom_Magasinier ⚠️, J=Nom du client ⚠️, Q=Marge € (tri croissant), **U=Code concession**, **V=Plaque** | ⚠️ Données personnelles. Formule unique en A2 : `docs/sheets-formulas/analyse_pieces_j1.txt`. Était en `#VALUE!` jusqu'au 2026-10-02 (cf. §8 pt.6) |
| Ventes à perte pièces Magasin, volume total (J-1) | `Détail facturation magasin journaliere` | Revalidé le 2026-10-02 : B=Concession (brut), C=Date_document, D=Numero_document, E=Avoir, F=Categorie_client, G=Nom_Magasinier ⚠️, H=Nom_client ⚠️, I=Reference, J=Libelle_piece, K=Qte_servie, L=Prix_unitaire_net, M=Prix_brut_ligne, N=Remise_ligne, O=Prix_net_ligne, P=PAMP, Q=Prix_force, R=Remise_forcee, **S**=Est à perte (formule Sheet), **T**=Code concession (formule Sheet, fixe) | ⚠️ Données personnelles. Requête : `docs/sql/magasin_detail_journalier.sql`. Champ `Magasin` retiré le 25/09 → tout a décalé d'1 colonne **sauf** S et T |
| Pièces atelier client vendues / à perte (J-1) | `Détail facturation atelier journalière` | Reflet de `facturation_detaillee_or` : N=Libelle_type_imputation, O=Libelle_type_operation, U=Est_ligne_forfait, X=Quantite_facturation, Y=PAMP_facturation (total de ligne), AA=Prix_vente_net, AD=Facture_avoirisee, AH=Affectation, AI=Categorie_client, AJ=Nom_client ⚠️, AK=Code concession, **AR=Est pièce à perte** | AR corrigée le 2026-10-02 : `=SI($AK2="";"";SI($O2="Pièce";SI(ET($X2>0;$AD2<>1;$AA2<$Y2);1;0);""))` — même règle que `Analyse pièces client J-1` (prix de vente net < PAMP, quantité > 0, hors facture avoirisée). L'ancienne version (`$Z<$Y`, montant facturé) marquait à tort les pièces de forfait (facturées 0 €) et les avoirs : 1 834 lignes « à perte » le 01/10 contre 153 réelles. BJ/BK d'`Analyse Globale` filtrent en plus `Est_ligne_forfait=0`. ⚠️ Quelques lignes sources arrivent **décalées** (ex. un nom de client en colonne Code concession, `Affectation` = `0`/`NC`/`1`) — origine probable de l'écart de mix FIAT_MULHOUSE, non traité |
| CA PR externe (Magasin) J-1 / MTD | `Historique CA par Magasin` (extraction du connecteur `Historique CA Magasin`) | Concession, Date, CA_PR_Externe_Net_HT, Cout_PR_Externe, Code concession | Périmètre vérifié le 2026-10-02 (53/53 concessions à l'euro près) : **intersite exclu** (codes mouvement SIS/EIS = catégorie « Inter sites »), mais **intragroupe et cessions au service commercial inclus**. Requête du connecteur pas encore dans le dépôt |
| OR en cession interne, efficience >105% | `Efficience OR CI trop élevé` | **2 tableaux côte à côte** : A:F (affichage %) et I:N (calcul décimal). A=Code concession, G=Plaque, C=Réceptionnaire ⚠️ | ⚠️ Ne pas confondre les deux tableaux ; Plaque en G, **pas** en O |
| OR à taux de remise MO/PR interne élevé | `Taux remise MO/PR interne élevé` | A=Code concession, K=Plaque, C=Nom client ⚠️, D=Réceptionnaire ⚠️ | ⚠️ Données personnelles |
| Malfaçons et gestes commerciaux du mois (1er du mois de J-1 → J-1) | `Malfaçons du mois` (extrait du connecteur BigQuery, sans onglet d'aperçu) | A=Concession, B=Date_document, C=Activite (Mécanique/Carrosserie), D=Fiche_imputee, E=Libelle_detail_intervention, F=Categorie_OR, G=Receptionnaire ⚠️, H=Nom_client ⚠️ (propriétaire), I=Immatriculation, J=Type_document (Facture/Avoir), K=Numero_OR_DMS, L=Numero_document, M=Montant_MO, N=Montant_PR, O=Montant_autres, P=Montant_total, **Q=Code concession** (formule Sheet, tirée jusqu'à la ligne 2000) | Requête : `docs/sql/malfacons_gestes_commerciaux.sql` (10 fiches de cession interne, définition `CADRAGE_APV.md` §15). Montants nets HT (`Prix_vente_net`, avoirs déduits). 1 ligne = 1 OR × fiche × date × document. Retirer un champ de la requête décale Q (cf. §8 pt.6) |
| Malfaçons et gestes commerciaux du jour (J-1) | `Malfaçons J-1` | Mêmes 17 colonnes A:Q que `Malfaçons du mois` + **R=Plaque**. Formules : `docs/sheets-formulas/malfacons.txt` (A1 en-têtes, A2 `SORT(FILTER(...))` sur la date `Analyse Globale!B1`, tri par montant décroissant ; R2 via `Concession-plaques`) | ⚠️ Données personnelles. Vide sous l'en-tête un jour sans malfaçon |
| Seuils métier (productivité basse, encours surveillance/alerte/critique) | `Référentiel métier` | `$B$11` (productivité), `$B$15/16/17` (encours) | |

### 2.1 `Analyse Globale` — colonnes (réagencées le 2026-10-02, malfaçons ajoutées le 2026-10-05)

Rangées par activité (Atelier puis Magasin), puis par indicateur : chaque
indicateur regroupe J-1, moyenne mobile, écart, alerte, MTD, objectif et mix
par canal. Bandeaux de blocs en ligne 1 (repris tels quels ci-dessous).

| Colonnes | Bandeau ligne 1 | Contenu |
|---|---|---|
| A-B | — | Code plaque, Code concession canonique |
| C-K | ATELIER - CA MO J-1 | C Nb OR clôturés J-1, D CA MO J-1, E moy. mobile 4 sem., F écart %, G **Alerte écart CA**, H-J % CA MO CLIENT/GARANTIE/CESSION J-1, **K Malfaçons J-1** (€) |
| L-S | ATELIER - CA MO MTD | L CA MO MTD, M-O % CA MO CLIENT/GARANTIE/CESSION MTD, P objectif MO mensuel, Q % réalisation, **R Malfaçons MTD** (€), **S % Malfaçons MTD** (= R/L, coût total malfaçons rapporté au seul CA MO) |
| T-AD | ATELIER - CA & Marge PR Interne J-1 | T CA PR interne J-1, U moy. mobile, V écart %, W-Y % CA PR interne CLIENT/GARANTIE/CESSION J-1, Z coût, AA marge, AB taux marge J-1, AC marge attendue (mix), AD écart vs mix |
| AE-AJ | ATELIER - CA & Marge PR Interne MTD | AE CA PR interne MTD, AF-AH % CLIENT/GARANTIE/CESSION MTD, AI objectif PR interne mensuel, AJ % réalisation |
| AK-AQ | ATELIER - Prod/Efficience | AK productivité J-1, AL moy. mobile, AM écart %, AN **Alerte productivité basse**, AO efficience J-1, AP moy. mobile, AQ efficience cessions internes MTD |
| AR-BB | ATELIER - Encours | AR nb OR en cours, AS valeur, AT-AV vieux encours 90-180j/180-365j/+365j (nb), AW-AY idem (valeur), AZ dépréciation, BA encours en j de CA, BB **Alerte encours** |
| BC-BJ | MAGASIN | BC CA PR externe J-1, BD moy. mobile, BE coût, BF marge, BG taux marge J-1, BH CA PR externe MTD, BI objectif, BJ % réalisation |
| BK-BL | *(sous le bandeau MAGASIN)* | BK nb pièces magasin vendues J-1, BL % vendues à perte J-1 |
| BM-BN | *(sous le bandeau MAGASIN, mais données Atelier)* | BM nb pièces atelier client vendues hors forfaits (Quantité>0), BN % vendues à perte (format %) |

Colonnes malfaçons (2026-10-05) : K = `SUMIFS` de `Malfaçons du mois!P` par code
concession (Q) à la date B1 ; R = même somme du 1er du mois à B1 ; S = R/L.
Formules exactes : `docs/sheets-formulas/malfacons.txt`. Vérifié le 2026-10-05 sur
OPELFIAT_DIJON : K = 0 € (dimanche 04/10), R = 2 507,91 € (2 OR du 01/10), S = 57,9 %
(début de mois : ratio très volatil, cf. `CADRAGE_APV.md` §15).

Contrôles de cohérence passés le 2026-10-02 sur les 67 concessions (lettres
actuelles, après l'insertion du 2026-10-05 : Q=L/P, AJ=AE/AI, BJ=BH/BI, F=D/E-1,
V=T/U-1, AM=AK/AL-1, AA=T-Z, AB=AA/T, AD=AB-AC, BF=BC-BE, BG=BF/BC) : 0 incohérence. Seule anomalie de données :
FIAT_MULHOUSE, mix MO/PR ≠ 100 % (lignes à `Affectation` = `0`/`NC`/`1`).

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
| B1 | Date de référence | `='Analyse Globale'!$B$1` (suivi automatique du déplacement C1→B1 du 2026-10-02) | — |
| B | Efficience J-1 | `IFERROR(SUMIFS(Temps_facture)/SUMIFS(Rappel_temps_passe);"")` par Plaque+Date | `Historique efficience/prod` (I=Plaque) |
| C | Productivité J-1 | `IFERROR(SUMIFS(Temps_facture)/SUMIFS(Temps_passe_total);"")` par Plaque+Date — vide plutôt que `#DIV/0!` quand la plaque n'a aucun temps passé total ce jour-là (cas PLQ_BMW_MOTO au 05/10, corrigé le 2026-10-06) | `Historique efficience/prod` (I=Plaque) |
| D | Valeur encours MO+PR | `SUMIFS(Montant_MO_PR_encours)` par Plaque | `Encours à date` (Y=Plaque, M=Montant) |
| E | Encours +90j (nb) | `COUNTIFS(Ancienneté>=90)` par Plaque | `Encours à date` (Y=Plaque, I=Ancienneté) |
| F | Encours en j de CA | Valeur encours ÷ ((somme CA MO 6 mois + somme CA PR interne 6 mois)/180), pondéré réseau | `Historique CA mensuel ateliers` (F=Plaque, C=CA MO, D=CA PR interne) |
| G | Pièces client en marge négative | `=COUNTIFS('Analyse pièces client J-1'!$V:$V;$A3)` (Atelier + Magasin) — affichait 0 partout jusqu'au 2026-10-02, repointé sur V | `Analyse pièces client J-1` (**V**=Plaque) |
| H | Forfaits marge <10% | `RECHERCHEV` + `IMPORTRANGE` vers un résumé agrégé (pas le détail brut) | `Anomalies forfaits > Plaque - Forfaits marge faible` |
| I | OR remise élevée | `COUNTIFS` par Plaque | `Taux remise MO/PR interne élevé` (K=Plaque) |
| J | OR efficience CI élevée | `COUNTIFS` par Plaque | `Efficience OR CI trop élevé` (**G**=Plaque) |
| K | Malfaçons J-1 (€) | `SUMIFS('Analyse Globale'!K)` par Code plaque (A) | `Analyse Globale` (K) |
| L | Malfaçons MTD (€) | `SUMIFS('Analyse Globale'!R)` par Code plaque | `Analyse Globale` (R) |
| M | % Malfaçons MTD | L ÷ `SUMIFS('Analyse Globale'!L)` (CA MO MTD) — pondéré | `Analyse Globale` (R, L) |

**Statut connu au 2026-09-25** : `UNIQUE()` ne remonte que 11 plaques sur 13
(`PLQ_PRIMOCAR` et `PLQ_VEODROME` suspectées manquantes) — à vérifier/corriger.

**Principe de conception (validé avec Corentin le 25/09)** : au niveau Plaque/Directeur,
le bloc APV du mail **ne remonte pas de CA/objectif** — uniquement des compteurs de
problème (voir mémoire `feedback_plaque_mail_apv_signals_not_ca`). **Exception
(2026-10-06)** : malfaçons et gestes commerciaux en montant et en % du CA MO
(colonnes K-M, formules `docs/sheets-formulas/malfacons.txt` §3, en place depuis
le 2026-10-06). Les totaux Plaque
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
  élevé` (Nom client, Réceptionnaire), `Malfaçons du mois` et `Malfaçons J-1`
  (Nom_client, Receptionnaire, Immatriculation)
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
   Même cause pour `Analyse pièces client J-1`, en `#VALUE!` jusqu'au 2026-10-02 :
   la partie Magasin lisait les anciennes lettres, ne trouvait plus aucune ligne,
   et un `FILTER` vide (1 cellule `#N/A`) empilé sous un bloc de 20 colonnes fait
   planter tout le tableau. Corrigé, et chaque bloc est désormais protégé par
   `IFNA(...; ligne vide)`.
7. Comparer des valeurs avant/après ne détecte pas une colonne déjà cassée avant :
   `Plaque APV!G` valait 0 avant et après le 2026-10-02, alors que la liste
   source contenait 139 lignes (corrigé le jour même). Toujours confronter un
   compteur à sa source.
