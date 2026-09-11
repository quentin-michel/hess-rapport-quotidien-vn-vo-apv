# Cadrage — VO (Véhicules d'Occasion)

Voir [`CADRAGE.md`](CADRAGE.md) pour le cadrage transverse (objectif général,
architecture, destinataires, décisions communes aux 3 services, méthode `gws`).

**Statut (2026-09-10) : les 8 blocs sont construits, filtrés et validés (données
réelles, Renault Mulhouse) de bout en bout.** Reste : recette complète sur les 9
concessions pilote, envoi réel de test.

## 1. Spécification cible : `Spec_Mail_IA_ChefVentesVO_v3.docx`

Document de référence fourni par Quentin le 2026-09-08. Objectif : un mail par
concession au chef des ventes VO, résumant les points significatifs (leads,
offres, stock, ventes) avec un commentaire IA de synthèse (voir principe du
commentaire dans `CADRAGE.md` §3).

**Pilote : Plaque Renault**, 9 concessions —
`REN_SAVERNE, REN_SELESTAT, REN_STLOUIS, REN_STRASBOURG, REN_WISSEMBOURG,
RENNIS_BELFORT_MONT, RENNIS_COLMAR, RENNIS_HAGUENAU, RENNIS_MULHOUSE` — c'est le
périmètre de **test** avant diffusion à l'ensemble du groupe. Mails envoyés
uniquement aux 2 adresses de test (Quentin, Corentin) pendant cette phase.

Détail complet des champs/tables/filtres par bloc du spec original, non
reproduit ici in extenso — s'y référer directement en cas de doute sur l'intention
métier d'origine (ce document-ci fait foi sur ce qui a été **effectivement
construit**, qui a parfois évolué par rapport au spec initial — cf. §3-10).

## 2. Fichiers et méthode d'extraction

Extraction via **`gws`** (voir `CADRAGE.md` pour le setup) — lecture de plages
précises, fiable, sans troncature silencieuse. Contrainte réelle : un résultat
de plusieurs Mo reste trop gros pour le contexte de Claude, d'où le principe
"Sheet agrège/borne, Claude lit un résultat déjà petit" appliqué à chaque bloc.

L'architecture finale n'a **pas suivi à la lettre** le plan initial "8 fichiers
séparés" — une fois `gws` validé, certains blocs ont été regroupés dans le
fichier source principal quand ils partagent les mêmes imports BigQuery :

| Bloc | Fichier | Onglet(s) final(aux) |
|---|---|---|
| 1 — Leads | `14TWu4moVg6lSOT5KLjnTCumeZcx-3M9Xg2vqpt4-ka4` | `BLOC 1 Leads` |
| 2 — Offres/Reprises | `1C1jMlaD8M1TearS98aiC_J3t6lieq7sp2GdMq_fKDzI` | `BLOC 2 Offre` |
| 3 — Anomalies Achat | `1PdjQzWi0Gbn1KhkaUvC6wPbdyiBIovI_TeB_YhyAraU` | `BLOC 3 Ano Achat` |
| 4 — Qualité Stock | `1NhHCqRM54yWcMomE1Qd0tKGG9KWRV8tvewq9hhCIPfM` | `BLOC 4 Stock_P1` (synthèse) + `BLOC 4 Stock_P2` (détail top-5) |
| 5 — Couverture | `1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU` (fichier principal `Rapport quotidien VO`) | `BLOC 5 Couverture_VO` |
| 6 — Excès Stock | idem (fichier principal) | `BLOC 6 Excès_Stock` |
| 7 — Santé Plaque | idem (fichier principal) | `BLOC 7 Santé_Plaque` |
| 8 — Anomalies Ventes | `110ih-4TOZL8qJD4CHz9avQoHXCN70wU5Pdmcmga1fwI` | `BLOC 8 Ano_Vente` |

Les Blocs 5/6/7 partagent les mêmes sources brutes (`Vente VO 90j SF`,
`Stock VO SF` + extraits joints `Extrait_Ventes_VO`/`Extrait_Stock_VO`) dans le
fichier principal — regroupés car reconstruire les mêmes imports BigQuery dans
3 fichiers séparés aurait été redondant. Chaque onglet `BLOC N` reste petit
(agrégats), donc lisible sans risque malgré le fichier principal volumineux.

## 3. Bloc 1 — Leads

**Champs** : `Code_concession, Date_reference, Leads_recus_J1, Leads_recus_7j,
Leads_non_traites_J1, Leads_non_traites_7j`.

**Construction** : requête BigQuery sur `v_sf_lead` (`TECH_ConcessionName__c`,
`Type_de_demande__c = 'Lead VO'`, non-traité = `Status IN ('Nouveau','1- Nouveau')`)
→ onglet source `Leads_SF` → jointure `Mapping` → consolidation par
`Code_concession` (`QUERY`/`GROUP BY`, somme des lignes brutes partageant un même
code — plusieurs marques/sites peuvent pointer vers la même concession).

**Point de vigilance** : une ligne à `Code_concession` vide subsiste (regroupe
les entrées sans mapping, dont un total parasite "Groupe Hess") — non filtrée
par la formule (`WHERE G <> ' '` insuffisant), mais **ignorée systématiquement
par Claude à la lecture**. Pas bloquant.

**Validé (2026-09-09)** — Renault Mulhouse : 29 reçus J-1 (163/7j), 0 non
traités J-1 (9/7j).

## 4. Bloc 2 — Offres VO / Reprises

**Champs** : `Code_concession, Date_reference, Commandes_VOP_acceptees_J1/_7j,
Offres_refusees_J1/_7j, Reprises_acceptees_J1/_7j`.

**Construction** : `v_sf_quote` — `TECH_Concession__c` (⚠ pas
`TECH_ConcessionName__c`, propre à `v_sf_lead`), `Nom_du_type_d_enregistrement__c`
(⚠ pas `Type__c`) pour distinguer Offre VO / Offre de reprise, `Status`
(standard, ⚠ pas `Statut__c`) pour Acceptée/Refusée. Même pattern extraction →
Mapping → consolidation que le Bloc 1.

**Limite acceptée** : pas de filtre "hors véhicule de démonstration" (nom de
champ non identifié) ni "hors buy-back" sur les reprises (spec initial le
signalait déjà comme non résolu).

**Validé (2026-09-09)** — Renault Mulhouse : 3 commandes VOP J-1 (27/7j), 1
offre refusée J-1 (19/7j), 1 reprise acceptée J-1 (10/7j).

## 5. Bloc 3 — Anomalies Achat/Reprise

**Champs finaux** : `Code_concession, Numero_achat, Immatriculation, Date_achat,
Note_criticite, Type_anomalie`.

**Construction** : requête BigQuery complète (dédup + grille de notation +
composition texte), **entièrement en SQL**, pas de formule Sheet pour le score :

```sql
WITH achat_dedup AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY Vehicule_Achete__c ORDER BY Date_d_achat__c DESC) AS rn
  FROM `hess-data.salesforce_source_views.v_sf_achat`
  WHERE Type__c = 'VO'
),
base AS (
  SELECT ... FROM achat_dedup
  WHERE rn = 1 AND Offre_de_reprise_acceptee__c = TRUE AND Prix_de_revient__c > 1
    AND Date_d_achat__c BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()
),
-- scores par critère (écart date/km/prix/aides, paliers 0-10, cf. spec)
-- filtre TVA : écart aides entre 18-22% de l'aide de référence ignoré
-- note_criticite = LEAST(10, MAX(scores) + (nb critères ≥2 - 1))
SELECT ... WHERE note_criticite >= 4
ORDER BY note_criticite DESC, date_achat DESC
```

**Corrections de données appliquées** (contrairement au spec initial qui les
listait comme limites acceptées) :
- **Dédup vente↔offre appliquée** (`ROW_NUMBER PARTITION BY Vehicule_Achete__c`)
  — corrige le bug de +23,5% de doublons identifié dans le spec.
- Filtre TVA sur écart aides géré nativement dans la requête.

**Fenêtre** : 7 jours glissants (pas J-1 — volume trop faible au quotidien par
concession, confirmé par le spec).

**Onglet final** `BLOC 3 Ano Achat` = extraction réduite (`Code_concession,
Numero_achat, Immatriculation, Date_achat, Note_criticite, Type_anomalie`) via
`QUERY` sur l'onglet source, filtrée `Code_concession <> ' '`.

**Validé (2026-09-10)** — 71 dossiers pour tout le groupe, lecture complète
sans coupure. Renault Mulhouse : 5 dossiers (notes 10, 7, 6, 5, 5), dont
`FN-627-YH` (note 7) et `GR-492-LK` (note 5) — cohérents avec l'exemple du spec
original.

## 6. Bloc 4 — Qualité du stock

**Volet 1 — Synthèse par concession** (`BLOC 4 Stock_P1`) : `Code_concession,
Stock_ST, Stock_CL, Stock_IM, Portefeuille_livraison, Sans_prix_nb,
Sans_destination_nb, Sans_photo_nb, Jamais_publie_nb, CL_en_retard_nb`.
Formules `COUNTIFS` sur `Extrait_Stock_VO` (source : `v_sf_vehicule_stock`,
`TypeVNVO__c='VO' AND NOT is_vd__c`).

**Volet 2 — Détail plafonné** (`BLOC 4 Stock_P2`) : top 5 véhicules les plus
anciens par catégorie et par concession — **fait en formules Sheet natives**
(`COUNTIFS` en astuce de classement : rang = nombre de véhicules de même
concession/catégorie avec la valeur de tri strictement supérieure, +1),
**pas de requête BigQuery supplémentaire**. **5 catégories** (une 5ᵉ ajoutée le
2026-09-11), 5 tableaux côte à côte : Sans prix (colonnes A-E), Sans
destination (G-K), Sans photo (M-Q), Jamais publié (S-W), **CL en retard
(Y-AC, ajoutée sur demande — triée par jours de retard décroissant, i.e.
`date_livraison_souhaitee` croissante = la plus ancienne échéance dépassée en
premier)**.

**Pourquoi ce découpage en 2 volets** : le listing brut (`Extrait_Stock_VO`)
fait ~6230-20000 lignes selon le fichier — bien trop pour être lu par Claude
d'un coup (2-3 Mo). D'où la nécessité de borner à la source : agrégats (Volet
1, ~90 lignes) + top-5 (Volet 2, quelques centaines de lignes max).

**Point observé** : "Sans photo" et "Jamais publié" sont fortement corrélés
(confirmé sur données réelles — parfois les 5 mêmes véhicules dans les 2
listes pour une concession) — comme anticipé par le spec original.

**Validé (2026-09-10)** — Renault Mulhouse : Stock ST 204/CL 78/IM 15,
Portefeuille livraison 78, Sans prix 3 (dont `FN-627-YH` et `GK-964-EX`), Sans
destination 10, Sans photo 24 / Jamais publié 26 (listes quasi-identiques).

**Validé (2026-09-11)** — CL en retard, Renault Mulhouse, 5 véhicules
(4 à 37 jours de retard), dont `GS-767-VC` (Master FG) déjà cité dans
l'exemple du spec original.

## 7. Bloc 5 — Rotation-Couverture

**Champs** : `Code_concession, Stock_ST, Ventes_VOP_moy_mensuelle,
Couverture_mois, Ventes_30j, Ventes_31_60j, Tendance_ventes_pct,
Delai_median_livraison_j`.

**Logique** : `Couverture` = nombre de **mois** de stock au rythme de vente
actuel, mais le rythme mensuel est lui-même lissé sur **90 jours ÷ 3** (pas un
simple dernier mois) pour réduire le bruit d'un mois atypique.

**Source** : requête BigQuery réutilisée pour les Blocs 5/6/7 (`Vente VO 90j SF`
dans le fichier principal — nom historique "30j" corrigé en "90j", la fenêtre
réelle est bien 90 jours). Dédup vente↔offre déjà appliquée dans cette requête.

**Canal de vente** — piège rencontré : le filtre `Canal_de_vente__c IN
('Particuliers', 'Flottes / Sociétés')` (⚠ **espaces autour du `/`**, valeur
réelle confirmée par Quentin) doit être répété à l'identique dans **toutes**
les formules `COUNTIFS` qui filtrent par canal (Blocs 5, 6, 7) — une première
version sans les espaces a fait sous-compter silencieusement les ventes
Flottes/Sociétés pendant un temps (corrigé le 2026-09-10, vérifié : les
volumes ont légèrement augmenté après correctif, cohérent).

**Limite connue** : `Delai_median_livraison_j` vide pour les concessions BMW
Motorrad (`BMWM_*`) — pas de bon de commande sur Salesforce pour cette marque,
pas un bug.

**Validé (2026-09-10, après correctif canal)** — Renault Mulhouse : Stock ST
206, ventes moy. mensuelle 91, couverture 2,3 mois, tendance -21% (30j vs 30j
précédents), délai médian 16j.

**Extension Plaque (2026-09-11)** : colonnes ajoutées pour comparer chaque
concession à la moyenne de sa Plaque — `Code_Plaque, Stock_ST_Plaque,
Ventes_VOP_moy_mensuelle_Plaque, Couverture_mois_Plaque,
Delai_median_livraison_j_Plaque, Ventes_30j_Plaque, Ventes_31_60j_Plaque,
Tendance_ventes_pct_Plaque` — mêmes formules que la version concession,
reclées sur `Code_Plaque` au lieu de `Code_concession`. ⚠️ **Bug rencontré puis
corrigé** : la première version utilisait un `VLOOKUP($A2, Extrait_Stock_VO!$X:$Y, 2, FALSE)`
pour récupérer `Code_Plaque` depuis la concession, qui renvoyait des résultats
décalés/faux (ex. `BMW_BESANCON` associé à `PLQ_BMW_MOTO` au lieu de
`PLQ_BMW`) — corrigé par Quentin avec `RECHERCHEX` (XLOOKUP) à la place.
**Toujours vérifier une jointure Plaque avant utilisation**, ce type d'erreur
ne saute pas aux yeux sans comparer au Référentiel.

**Validé (2026-09-11)** — Renault Mulhouse vs Plaque Renault : ventes moy.
91 vs 492, couverture 2,3 vs 2,1 mois, **tendance -21% vs +2%** (Mulhouse
sous-performe nettement le réseau), délai 16j vs 15j.

## 8. Bloc 6 — Excès de stock

**Champs** : `Code_concession, Famille, Energie, Stock, Ventes_moy (90j/3),
Exces, Ancien_nb`. Granularité **(concession × famille × énergie)**, pas juste
concession.

**Construction** : `QUERY` `GROUP BY` multi-colonnes sur `Extrait_Stock_VO`
pour `Stock` ; `COUNTIFS` sur `Extrait_Ventes_VO` pour `Ventes_moy` ; `Exces` =
`MAX(Stock - ROUND(Ventes_moy), 0)`.

**Top 3 par concession (excès ≥ 3)** : pas de colonne de rang dédiée — **Claude
filtre/trie lui-même à la lecture** (table déjà petite, ~300 Ko pour tout le
groupe, largement lisible d'un coup).

**Validé (2026-09-10)** — Renault Mulhouse, top 3 : Clio Hybride essence
(stock 23, ventes 5, excès **18**), Master FG Diesel (stock 15, ventes 4, excès
**11**), Mégane Électrique / Sandero GPL ex æquo (excès 7). **Cohérence
frappante avec l'exemple du spec original**, qui citait déjà "Clio Hybride
essence" en excès n°1 pour cette même concession (jour différent).

## 9. Bloc 7 — Contexte réseau (Santé Plaque)

Même construction que le Bloc 6, mais **au niveau Plaque** (`Code_Plaque` au
lieu de `Code_concession`), avec en plus `Age_moyen` (AVG), `Age_median`
(formule `MEDIAN(ARRAYFORMULA(IF(...)))`).

**Diagnostic Santé et Action recommandée** (colonnes `Analyse_santé` et
`Action_recommandée`) : formules `MAP`/`LAMBDA` fournies par Quentin (grille de
seuils sur `stock/ventes/age_moyen/age_median`, catégories SAIN / CORRECT /
FATIGUÉ / CRITIQUE / NON SIGNIFICATIF, + alerte "PURGER ANCIENNES" combinée si
écart>30 et stock≥5 ; action recommandée croisant santé × couverture brute).
Nécessite une colonne intermédiaire `Couverture_brute` (`Stock/Ventes_moy`, ou
`"Infini"` si `Ventes_moy=0`).

⚠️ Piège rencontré : la fonction `JOINDRE` n'existe pas en français dans ce
Sheet (erreur "fonction inconnue") — utiliser `TEXTJOIN` (nom anglais, avec les
points-virgules français `;` comme séparateurs).

**Validé (2026-09-10)** — Plaque Renault, Clio Hybride essence : Stock 78,
Excès 45, Âge moyen 57j, **Analyse santé = "SAIN + ⚠ PURGER ANCIENNES"**,
Action = MAINTENIR — confirme que l'excès de Mulhouse est un problème
**réseau**, pas isolé à une concession.

**Décision (2026-09-11)** : Bloc 7 est construit et validé, mais **volontairement
exclu du mail niveau Service** (V1). Cette analyse réseau/plaque n'a de sens
qu'au niveau plaque — elle est réservée à un futur **mail directeur de plaque**
(3ᵉ niveau de diffusion, cf. `CADRAGE.md` §1). Le Bloc reste lu et exploité côté
Sheet, simplement pas restitué dans le mail Service actuel.

## 10. Bloc 8 — Anomalies Ventes

**Champs finaux** (`BLOC 8 Ano_Vente`) : `Code_concession, Immatriculation,
Marque, Modele, Marge_vehicule, Duree_detention_j, Type_anomalie`.

**Règles retenues (2026-09-10, après calibrage sur 90 jours)** — différent du
spec initial sur plusieurs points :

| Critère | Seuil | Note |
|---|---|---|
| Marge négative *(renommé, était "Perte significative")* | < -1000€ | hors canal Primocar |
| Marge élevée | > 4000€ | hors canal Primocar |
| Détention longue | > 180j | hors canal Primocar |
| Vente rapide | **supprimé** | jugé peu utile après revue |
| Écart FRE significatif | > 500€ | **ET `frais_estimes` non vide et ≠ 0** (sinon pas d'anomalie — un écart n'a pas de sens sans estimation de référence) |
| Facturation Marchand non autorisée *(nouveau)* | `canal_vente = "Marchand"` ET concession hors `PRIMO_*` | seules les concessions Primocar ont le droit de facturer à un marchand |

**Fenêtre** : 7 jours glissants (élargie temporairement à 90j pour calibrer les
seuils sur un échantillon robuste — cf. §11 — puis rebasculée à 7j).

**Calibrage des seuils** : basé sur la distribution réelle des 90 derniers
jours (percentiles), pas un ajustement à l'estime — voir §11 pour la méthode.
Seuils finalement **gardés identiques aux valeurs d'origine** pour marge/
détention (Quentin a tranché de ne pas resserrer), ajustés seulement pour
Écart FRE (600€→500€ + garde-fou) et suppression de Vente rapide.

**Affichage si plus de 5 anomalies pour une concession/jour** : **pas de score
de gravité** (option envisagée puis écartée) — tri par **date décroissante en
premier, puis note/montant décroissant** en cas d'égalité de date (décidé
2026-09-11, remplace l'idée initiale d'ordre de priorité par catégorie),
top 5 + note "+N autres anomalies". Géré par Claude à la composition du mail,
pas par une colonne Sheet. **Même règle de tri appliquée au Bloc 3** (Anomalies
Achat/Reprise). Pour trier le Bloc 8 par date, `date_vente` doit être ajoutée
à la requête `QUERY` de `BLOC 8 Ano_Vente` (pas encore fait à ce jour).

**Piège de jointure** : `frais_estimes`/`frais_reels` proviennent du **même
join `quote_dedup`** déjà utilisé pour `date_confirmation_commande` (offre
acceptée la plus récente par véhicule) — pas un nouveau join, cohérence
garantie.

**Validé (2026-09-10)** — Renault Mulhouse : 8 anomalies (fenêtre 7j), dont
`GR-375-VL` (Master FG, marge -6737€, détention 275j) — **valeurs identiques à
l'exemple du spec original**, excellente cohérence.

## 11. Calibrage des seuils Bloc 8 — méthode

1. Élargissement temporaire de la requête BigQuery à 90 jours (au lieu de 7)
   pour obtenir un échantillon robuste (~8963 ventes vs ~610 sur 7j).
2. Calcul des percentiles réels (marge véhicule, durée détention, écart FRE)
   plutôt que deviner des seuils.
3. Proposition de seuils visant ~3-5% des ventes flaguées par critère (rare =
   vraiment notable), présentée à Quentin avec le détail par concession.
4. **Décision finale de Quentin** : conserver les seuils d'origine pour
   marge/détention (jugés déjà corrects à l'usage), ajuster uniquement Écart
   FRE et supprimer Vente rapide — les percentiles ont servi de base de
   discussion, pas de règle automatique.
5. Requête rebasculée à 7 jours après calibrage.

## 12. Simulation de mail complète — Renault Mulhouse (2026-09-10)

Deux simulations réalisées (texte du mail, pas d'envoi réel) :
- Une première avec les Blocs 1-4 seulement (avant que 5-8 soient construits).
- Une complète avec les 8 blocs, une fois tout construit.

**Commentaire IA — itération importante** : la première version du commentaire
recomposait des chiffres déjà visibles dans les blocs structurés (peu de valeur
ajoutée, relevé par Quentin). Version corrigée : le commentaire doit chercher
les **recoupements entre blocs** (ex. `FN-627-YH` noté 7/10 en anomalie achat
ET encore sans prix/destination 7j plus tard) et transformer les tendances en
risques prospectifs actionnables plutôt que de répéter les chiffres. Principe
documenté dans `CADRAGE.md` §3 (s'applique à tous les services, pas que VO).

## 13. Format du mail — décisions (2026-09-11)

Retours de Quentin sur le mockup (`docs/mockup_email_vo.html`), traités point
par point :

1. **Titre** : suppression de la baseline "Groupe Familial depuis 1946" —
   header réduit au logo seul.
2. **Nom de la concession** : lu depuis le Référentiel Concession, onglet
   `Concessions_Plaques`, colonne B (`Nom_Concession`, libellé d'affichage —
   ex. "Renault/Nissan Mulhouse"), plutôt qu'un `Code_Concession` brut.
   Adresse(s) mail lues dans l'onglet `Destinataires` du même fichier.
3. **KPI (les 4 premiers)** : confirmé qu'ils sont recalculés chaque jour (pas
   des valeurs figées) — pas de changement de structure nécessaire.
4. **Synthèse** : OK tel quel.
5. **Sources** : ne pas afficher les références de fichiers/onglets sources
   dans le mail (info technique sans valeur pour le destinataire).
6. **Anomalies achat/reprise (Bloc 3)** : ne pas afficher la colonne note ;
   trier par **date décroissante en premier, puis note décroissante** en cas
   d'égalité (même règle que Bloc 8, cf. §10).
7. **Qualité du stock (Bloc 4)** : détailler la liste des **CL en retard**
   (pas seulement le total) — voir §5.
8. **Rotation & couverture (Bloc 5)** : ajouter les **moyennes Plaque** en
   comparaison des chiffres concession, calcul fait côté Sheet (pas par
   Claude) — voir extension Plaque au §7. Complété ensuite par une demande de
   **tendance ventes également au niveau Plaque** (même logique que la
   tendance concession, calculée côté Sheet).
9. **Contexte réseau/plaque (Bloc 7)** : ne pas l'inclure dans le mail
   Service — réservé au futur mail directeur de plaque (voir note ajoutée
   au §9).
10. **Anomalies ventes (Bloc 8)** : même règle de tri que le point 6 — date
    décroissante en premier, puis note/montant décroissant.

## 14. Icône météo — score de vigilance (2026-09-11)

Indicateur visuel en haut du mail (à côté du titre), pour donner un état
d'esprit global de la concession en un coup d'œil, sans lire le détail des
blocs. Test initial en 5 icônes (soleil/nuage/pluie/orage/neige) — décision
finale : **4 icônes seulement**, pas de "neige" (remplacée par "pas d'icône"
quand le volume n'est pas significatif, cf. ci-dessous).

**Score par points, cumulé sur 3 critères.** Barème initial validé le
2026-09-10 ("Ça me va, on garde ces seuils"), puis **affiné le 2026-09-11**
sur les critères Anomalies ouvertes et Tendance ventes :

**1. Anomalies ouvertes** (+2 points si le total ci-dessous ≥ 6 — seuil
provisoire, gardé tel quel malgré le changement de mode de comptage,
**à réajuster lors des tests réels** si besoin) — la façon de
compter diffère selon le bloc, car les deux types d'anomalie n'ont pas la même
nature :
- **Achat/reprise (Bloc 3)** : anomalies **encore ouvertes, en cumul, sans
  limite de temps** — ce sont des dossiers correctibles (prix, photo,
  destination manquants...), donc un cumul de dossiers non résolus reflète une
  vraie charge de travail en cours.
- **Vente (Bloc 8)** : anomalies détectées **uniquement sur les ventes de
  J-1** — une marge négative ou une détention longue est un **fait constaté
  sur une vente déjà faite** ("si on perd 10K€ sur un VO, il est possible que
  ce soit vrai" — pas un état à corriger), donc pas de sens à le cumuler
  indéfiniment ; seul le fait nouveau du jour compte pour la météo du jour.

**2. Tendance ventes 30j** — gradué (et non plus tout-ou-rien) :

| Tendance vs période précédente | Points |
|---|---|
| ≥ 0% (stable ou en hausse) | 0 |
| entre 0% et -5% | +1 |
| entre -5% et -10% | +2 |
| < -10% | +3 |

**3. Couverture** : inchangé, +2 si hors zone normale (trop basse ou trop
haute vs seuils Bloc 5).

Le score max passe donc de 6 à 7 (2 + 3 + 2). **Mapping score → icône
inchangé malgré ce nouveau max** (décidé 2026-09-11, "reste sur un orage à
partir de 6") :

| Score | Icône |
|---|---|
| 0-1 | ☀️ Soleil |
| 2-3 | ☁️ Nuage |
| 4-5 | 🌧️ Pluie |
| 6+ | ⛈️ Orage |

**Cas particulier — volume non significatif** (décidé 2026-09-11, "si non
significatif on met rien") : si le volume de ventes mensuel moyen de la
concession est trop faible pour que les tendances/pourcentages soient
fiables (ex. `ventes_moy_mensuelle < 3`), **aucune icône n'est affichée** —
un score basé sur un dénominateur trop petit serait trompeur plutôt
qu'informatif.

Le calcul du score (agrégation des 3 critères + seuil de significativité)
reste à implémenter côté Sheet, comme le reste de la logique métier — pas
par Claude à la volée.

## 15. Prochaines étapes

1. Recette du pilote sur les 9 concessions Renault (pas seulement Mulhouse).
2. Ajouter `date_vente` à la requête `QUERY` de `BLOC 8 Ano_Vente` pour
   permettre le tri date-décroissante (cf. §10).
3. Construire côté Sheet : moyennes/tendance Plaque pour le Bloc 5 (§13 pt.8,
   déjà partiellement fait — voir §7) et le score de vigilance météo (§14).
4. Provisionner la boîte Gmail dédiée (cf. `CADRAGE.md` §6) pour un premier
   envoi de test réel aux 2 adresses pilote.
5. Une fois VO validé : reprendre APV (déjà prêt côté données) et VN (sheet à
   créer) sur le même modèle.
