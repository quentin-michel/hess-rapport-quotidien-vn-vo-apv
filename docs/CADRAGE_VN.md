# Cadrage — VN (Véhicules Neufs)

Voir [`CADRAGE.md`](CADRAGE.md) pour le cadrage transverse (objectif général,
architecture, destinataires, décisions communes aux 3 services).

**Statut (2026-09-24) : blocs 1, 2, 3, 4 et 6 terminés et validés, maquette de
mail entièrement retravaillée sur une concession pilote (météo, KPI, Bloc 2
intégré)** — même méthode que VO (Sheet par bloc, validé sur données réelles
avant de documenter).

**Principe de méthode (rappel 2026-09-16)** : ne pas extrapoler de logique
métier VN par analogie avec le VO sans vérification — un essai de proposition
de blocs VN "plausibles" (carnet de commandes, objectifs constructeur, démo
vieillissante...) a été explicitement rejeté par Quentin ("tu es en train
d'inventer, tout n'est pas disponible"). Chaque champ/table utilisé ci-dessous
a été confirmé par un extrait Sheet réel ou une requête BigQuery exécutée avec
succès, pas supposé par analogie.

## 1. Bloc 1 — Leads VN

**Fichier** : nouveau Sheet dédié, tabs `Leads_SF_VN` (Connected Sheet
BigQuery) → `Extrait Leads_SF_VN` → `BLOC 1 Leads VN`
(`1oQzC5CV8Xqb6oTVAmNakcn3pSJD0yqP1eSdE7guHn80`).

**Structure identique au Bloc 1 VO** : `Code_concession, Date_reference,
Leads_recus_J1, Leads_recus_7j, Leads_non_traites_J1, Leads_non_traites_7j`.
Le filtre VN est géré dans la requête du connecteur BigQuery (côté Sheet, pas
visible via `gws` — voir limite outillage dans `CADRAGE.md`), sur une table
qui a un équivalent VN/VO/reprise (confirmé indirectement : ce Sheet existe et
retourne des valeurs cohérentes, filtrage déjà en place par Quentin/Corentin).

**Validé (2026-09-16)**, données réelles, tout le groupe :
- Renault/Nissan Mulhouse : 33 leads reçus J-1, **14 non traités** — signal
  fort (~40% des leads de la veille pas traités).
- Renault Saverne : 6 reçus J-1, 2 non traités.

## 2. Bloc 2 — Commandes & Facturations VN vs Objectifs

**Statut : terminé et validé (2026-09-24), construit par Quentin.** Remplace
définitivement l'ancienne piste "anomalie aide non respectée" (comparaison
feuille de marge vs vente) — **abandonnée**, elle était bloquée depuis le
2026-09-17 sur un nom de champ manquant côté vente et n'a jamais été
débloquée. Nouvelle direction, plus directement utile au quotidien : suivi
Commandes/Facturations VN vs objectifs budgétaires, par concession × marque.
*(Résumé de l'ancienne piste abandonnée en fin de section, pour mémoire.)*

**Fichier** : même spreadsheet que l'ancien travail Bloc 2
(`14iuxhKZr34StlxCn8IodM9iquoqH9wnc5EhsBYxBUDE`), structure refaite. Tabs :
`Mapping` (transco `Valeur_Source → Code_concession/Code_Plaque`),
`Obj Com/Fact.` (Connected Sheet BigQuery, objectifs), `Extrait_ComFact`
(extraction réduite, une ligne par flux × concession × marque × jour) →
`BLOC 2` (final, grain concession × marque + totaux plaque/groupe/marque).

**Sources BigQuery** :
- **Commandes** : `hess-data.salesforce_source_views.v_sf_feuille_de_marge`,
  VN+VD, `Statut__c IN ('Approuvée', 'Soumise pour approbation')`, sur
  `Date_de_commande__c`. **Pas de dédoublonnage par châssis** — décidé
  volontairement : les châssis "bouchons" (`12345678`, `00000000...`,
  `XXXXXXXX`) fusionnaient à tort des commandes distinctes.
- **Facturations** : `hess-data.salesforce_source_views.v_sf_vente`,
  `Statut__c = 'Validée'`, VN+VD, sur `Date_de_vente__c`, hors 7 canaux
  (`Cession, Export, Intra-groupe sauf Primocar, Marchands, MRA, Primocar,
  Rétrocession (confrère)`).
- **Objectifs** : `hess-data.budget.objectifs_commandes_facturation`, filtré
  `Activité = 'VN'`, année/mois courants. **Fiabilité confirmée par Quentin**
  (2026-09-24).

**Normalisations appliquées** : `FIAT PROFESSIONAL → FIAT`,
`MOBILIZE → RENAULT`, v&eacute;los exclus, concessions de Bâle exclues (hors
périmètre). BMW Motorrad codé `BMW` côté objectifs mais `BMW MOTORRAD` côté
réalisé Salesforce — recodé explicitement dans la requête.

**Cas particulier BMW Motorrad** : pas de commande dans Salesforce pour cette
activité — remplacé par un **déclaratif mensuel**
(`Nb_commande_d__claratif`, saisi manuellement) utilisé comme réalisé "mois à
date" (année courante et année précédente, pas de détail jour). **Conséquence
à surveiller dans le mail** : les colonnes J-1 et 7 jours affichent 0 pour
ces lignes même quand le mois à date est réel (ex. BMWM Besançon : J-1=0,
7j=0, MTD=13/16 commandes) — pas un bug, mais risque de lecture trompeuse
("aucune activité") si affiché sans note. **Décision (2026-09-24)** : ajouter
une note explicite sur les lignes BMW Motorrad dans le mail (ex. "suivi
mensuel déclaratif, pas de détail J-1/7j").

**Calcul du prorata temporis** : jours ouvrés réels (lundi-vendredi, hors
fériés nationaux listés jusqu'en 2027), pas un simple ratio jour du mois /
nombre de jours du mois. Trois valeurs constantes par extrait quotidien
(`Extrait_ComFact!$J$2/$K$2/$L$2` = jours ouvrés écoulés/total/restants du
mois), réutilisées telles quelles dans toutes les formules `BLOC 2`.

**Colonnes calculées** (`BLOC 2`, répétées pour les 2 flux Commandes et
Facturations) : J-1, 7 jours, moyenne hebdo sur les 4 semaines précédentes,
mois à date, mois à date N-1, objectif du mois, manque à date, taux
d'atteinte %, projection fin de mois, reste à faire par jour ouvré, tendance.
```
Manque à date            = ROUND(MTD - Objectif × jo_écoulés/jo_mois; 1)
Taux atteinte %          = ROUND(MTD / Objectif × 100; 1)                 [vide si Objectif=0]
Projection fin de mois   = ROUND(MTD × jo_mois/jo_écoulés; 0)             [vide si jo_écoulés=0]
Reste à faire/jour ouvré = ROUND(MAX(Objectif-MTD; 0) / jo_restants; 1)   [vide si jo_restants=0]
```

**Tendance** (classification à 2 signaux : direction annuelle + vitesse
récente — évite de qualifier de "confirmée" une tendance qui repart déjà
dans l'autre sens) :
```
SI MAX(MTD; MTD_N-1) < 5                                      → "· Volume trop faible"
SINON SI MTD_N-1 = 0                                           → "Nouveau"
SINON SI (MTD-MTD_N-1)/MTD_N-1 ≥ +10% ET 7j ≥ moy_hebdo×0,8    → "↑ Hausse confirmée"
SINON SI (MTD-MTD_N-1)/MTD_N-1 ≤ -10% ET 7j ≤ moy_hebdo×1,2    → "↓ Baisse confirmée"
SINON SI 7j > moy_hebdo×1,2                                    → "↗ Accélère"
SINON SI 7j < moy_hebdo×0,8                                    → "↘ Ralentit"
SINON                                                           → "→ Stable"
```

**Grain et totaux** : une ligne par concession × marque, plus des lignes de
total par Plaque et par marque au niveau groupe. **Ligne "TOTAL GROUPE"
retirée par Quentin (2026-09-25)** — cohérence avec le Bloc VO équivalent
(§ci-dessous), qui n'en a jamais eu. Totaux calculés par `SUMIFS` sur
`Extrait_ComFact` avec un critère `"<>§"` (chaîne improbable comme valeur de
comparaison) pour agréger "toutes les valeurs" quand la ligne est un total,
sans dupliquer une formule séparée sans filtre — la logique reste valable
pour les totaux Plaque et marque, seule la ligne Groupe a disparu.

**Validé (2026-09-24)**, chiffres historiques observés au niveau groupe
avant retrait de la ligne : Commandes 2 145 mois à date / objectif 2 904
(73,9%, tendance stable) ; Facturations 1 327 mois à date / objectif 2 662
(49,8%, tendance hausse confirmée) — écart révélateur entre les deux flux
(le groupe commandait à un rythme proche de l'objectif mais facturait en
retard).

### 2.x Ancienne piste abandonnée — anomalie "aide non respectée"

Objectif initial : sur une vente VN à marge négative, vérifier que les aides
indiquées sur la feuille de marge approuvée se retrouvent bien dans le
dossier de vente. Constat sur données réelles (2026-01-01→09-16, 43 994
ventes VN+VD) : seulement 9 des 161 ventes à marge négative avaient un écart
d'aide non nul — question ouverte non tranchée sur le périmètre VD et sur la
condition marge négative. **Bloquée définitivement** sur le nom exact du
champ "montant d'aide" côté vente dans `v_sf_vente`, jamais communiqué par le
service data. Remplacée par le Bloc 2 ci-dessus — non reprise sauf demande
explicite si le champ manquant est un jour communiqué.

## 3. Bloc 3 — Stock VN/VD

**Statut : terminé et validé (2026-09-18)** — P1 (synthèse) et P2 (détail
top-5) fonctionnels sur données réelles.

**Source** : `hess-data.datamart_stock.etat_actuel_stock` (nom de table
confirmé par une requête BigQuery exécutée avec succès le 2026-09-17), jointe
à `hess-data.datamart_stock.vehicules` sur `CRC_vehicule` pour récupérer
`Serie_VIN`/`Libelle_marque`/`Libelle_modele` (absents de `etat_actuel_stock`
elle-même, confirmé 2026-09-17 — pas de colonne marque/modèle/VIN dans la
table stock).

Fichier Sheet : `10cOmCg_e8JKKpaHY0pI6QTPWLehO_VVfVAU6bXAROWE`, tabs
`DM_Stock_VN_VD` (Connected Sheet BigQuery) → `Extrait_Stock_VN_VD`
(extraction finale) → `Bloc 3 - P1 Stock VN_VD` (synthèse par concession) et
`Bloc 3 - P2 Stock VN_VD` (détail top-5).

**Filtre retenu** : `Est_VN_VD_ou_VO IN ('VN', 'VD')` — choisi explicitement
par Quentin plutôt que `VN_VO_new_def` (champ écarté, jugé redondant).
Exclusions : `Est_vehicule_courtoisie = 0` (**champ INT64**, ne pas comparer à
`'0'` entre guillemets — erreur rencontrée et corrigée le 2026-09-17),
`Source = 'Icar'`, `Date_achat IS NOT NULL`.

**Distribution réelle observée** (25 000 lignes lues, avant filtre Source/date) :
VO 18 578, VN 3 524, VD 2 898.

**Piège de données rencontré** : `Nb_jours_depuis_date_achat` (champ natif de
`etat_actuel_stock`) est **vide à 100%** sur l'échantillon VN/VD lu (4 947 + 3
660 lignes) — non exploitable tel quel, remplacé par un calcul Sheet.

**Champs retenus** (après un premier jet trop calqué sur le VO — Quentin :
*"il faut trouver d'autres indicateurs pertinents"*, le VN se vendant sur
commande et non sur stock à écouler comme le VO ; sans
prix/destination/photo écartés, remplacés par des indicateurs orientés
commande/contremarque) — voir requête ci-dessous pour la liste exacte, + VIN
ajouté a posteriori le 2026-09-18, + `Code_concession`/`Code_Plaque`
(RECHERCHEX vers le Référentiel Concession).

**Requête BigQuery validée (version finale, avec VIN)** :
```sql
SELECT
  s.Concession, s.Est_VN_VD_ou_VO, s.Statut_de_stock, s.Detail_statut_stock,
  s.Numero_de_stock, s.CRC_vehicule, v.Serie_VIN, v.Libelle_marque,
  v.Libelle_modele, s.Date_achat, s.Numero_commande_constructeur,
  s.Date_commande_constructeur, s.Date_commande_client,
  s.Date_livraison_a_client, s.Est_contremarque, s.Prix_achat,
  s.Somme_options_constructeur, s.Somme_options_complementaires,
  s.Somme_frais, s.Montant_surestimation, s.Somme_aides
FROM `hess-data.datamart_stock.etat_actuel_stock` s
LEFT JOIN `hess-data.datamart_stock.vehicules` v
  ON s.CRC_vehicule = v.CRC_vehicule
WHERE s.Est_VN_VD_ou_VO IN ('VN', 'VD')
  AND s.Est_vehicule_courtoisie = 0
  AND s.Source = 'Icar'
  AND s.Date_achat IS NOT NULL
ORDER BY s.Concession, s.Date_achat DESC
```

**Colonnes calculées côté Sheet dans `Extrait_Stock_VN_VD`** (lettres finales,
après insertion du VIN — A-U = colonnes de la requête ci-dessus dans l'ordre,
puis) :

- **Ancienneté depuis l'achat** (V, depuis J=Date_achat) :
  `=SI(J2="";"";AUJOURDHUI()-J2)`
- **Durée de contremarque** (W, depuis O=Est_contremarque, M=Date_commande_client) :
  `=SI(ET(O2=1;M2<>"");AUJOURDHUI()-M2;"")`
- **Valeur_stock** (X, depuis P=Prix_achat, Q=Somme_options_constructeur,
  R=Somme_options_complementaires, S=Somme_frais, T=Montant_surestimation,
  U=Somme_aides) — `ZN()` n'existe pas dans Sheets, remplacé par `N()`
  (convertit texte/vide en 0) : `=N(P2)+N(Q2)+N(R2)+N(S2)+N(T2)-N(U2)`
- `Code_concession` (Y), `Code_Plaque` (Z) : RECHERCHEX vers le Référentiel.
- **Rang âge VN** (AA) : `=SI($B2="VN"; COUNTIFS($Y:$Y;$Y2;$B:$B;"VN";$V:$V;">"&$V2)+1; 999)`
- **Rang âge VD** (AB) : `=SI($B2="VD"; COUNTIFS($Y:$Y;$Y2;$B:$B;"VD";$V:$V;">"&$V2)+1; 999)`
- **Rang contremarqué** (AC) : `=SI($O2=1; COUNTIFS($Y:$Y;$Y2;$O:$O;1;$W:$W;">"&$W2)+1; 999)`
- *(Une colonne "Écart commande client → livraison" avait été ajoutée puis
  retirée par Quentin le 2026-09-18 — pas retenue.)*

**Piège de formule rencontré** : le motif `IF(condition; COUNTIFS(...)+1; "")`
(texte vide pour les non-qualifiants) casse le filtre `QUERY` en aval —
remplacer par **`999`** (sentinelle numérique) résout le problème, confirmé
en comparant au motif réellement utilisé dans `Extrait_Stock_VO` (Bloc 4 VO).
Autre piège : `QUERY` peut mal deviner si la 1ʳᵉ ligne de la plage est un
en-tête quand la plage commence à la ligne 2 d'un onglet — ajouter `; 0` en
3ᵉ argument force "pas d'en-tête" et corrige un `QUERY` qui renvoie 0 ligne
sans erreur visible.

**P1 — synthèse par concession** (une ligne par `Code_concession`, liste via
`=UNIQUE(Extrait_Stock_VN_VD!Y2:Y)`) :
```
Stock VN :            =COUNTIFS(Extrait_Stock_VN_VD!$Y:$Y;$A2;Extrait_Stock_VN_VD!$B:$B;"VN")
Stock VD :             =COUNTIFS(Extrait_Stock_VN_VD!$Y:$Y;$A2;Extrait_Stock_VN_VD!$B:$B;"VD")
Stock âgé VN (+6 mois) : =COUNTIFS(Extrait_Stock_VN_VD!$Y:$Y;$A2;Extrait_Stock_VN_VD!$B:$B;"VN";Extrait_Stock_VN_VD!$V:$V;">180")
Stock âgé VD (+6 mois) : =COUNTIFS(Extrait_Stock_VN_VD!$Y:$Y;$A2;Extrait_Stock_VN_VD!$B:$B;"VD";Extrait_Stock_VN_VD!$V:$V;">180")
Contremarqué +90j :      =COUNTIFS(Extrait_Stock_VN_VD!$Y:$Y;$A2;Extrait_Stock_VN_VD!$O:$O;1;Extrait_Stock_VN_VD!$W:$W;">90")
```
**Validé (2026-09-18)** sur données réelles, ex. BMW Belfort : 27 VN, 10 VD, 2
âgés VN, 7 âgés VD, 0 contremarqué.

**P2 — détail top-5 par concession** (basé sur les colonnes de rang, **sans
seuil** — top 5 le plus ancien/long peu importe s'il dépasse 180j/90j, décidé
2026-09-18 pour garantir 5 lignes même sur les concessions à faible volume ;
le seuil reste dans P1 pour le comptage) :
```
Stock âgé VN :  =QUERY(Extrait_Stock_VN_VD!A2:AC; "SELECT Y, E, G, H, I, V WHERE AA <= 5 ORDER BY Y, V DESC"; 0)
Stock âgé VD :  =QUERY(Extrait_Stock_VN_VD!A2:AC; "SELECT Y, E, G, H, I, V WHERE AB <= 5 ORDER BY Y, V DESC"; 0)
Contremarqué :  =QUERY(Extrait_Stock_VN_VD!A2:AC; "SELECT Y, E, G, H, I, W WHERE AC <= 5 ORDER BY Y, W DESC"; 0)
```
Colonnes renvoyées : Code_concession, N° de stock, VIN, Marque, Modèle, puis
Ancienneté (ou Durée de contremarque).

**Validé (2026-09-18)** sur données réelles — ex. VIN `WBY51GM0705598336`
(BMW X2, Belfort, 218j d'ancienneté). Point de qualité de donnée noté, pas un
bug : quelques lignes source ont un `Code_concession` vide (`" "`), formant
un groupe à part en tête de liste triée.

**Seuils de calibration retenus** (méthode percentile sur données réelles,
même approche que le Bloc 8 VO) :
- Ancienneté sans commande client : médiane 81j, P75 148j, **P90 274j** (sur
  3 494 VN sans commande client / 4 947, soit 70% — trop fréquent pour être
  l'anomalie en tant que telle, d'où le seuil à 6 mois/180j retenu plutôt que
  la simple absence de commande).
- Durée de contremarque : médiane 25j, P75 79j, **P90 290j** (sur 1 600
  véhicules contremarqués) — seuil retenu 90j (entre médiane et P90).

## 4. Bloc 4 — Couverture, Excès de stock, Comparaison Plaque

**Statut : terminé et validé (2026-09-18)** — regroupe en un seul bloc/onglet
ce qui est réparti sur 3 blocs côté VO (Bloc 5 Couverture, Bloc 6 Excès, Bloc
7 Santé Plaque), **grain concession × marque × modèle** (plus fin que le VO,
qui était juste par concession) — décidé ainsi car l'information sert aussi
au futur mail directeur de plaque, contrairement au VO où le niveau plaque
avait été explicitement exclu du périmètre V1.

**Dépendance identifiée avant de construire** : la couverture (`Stock ÷
Ventes moyennes mensuelles`) a besoin d'une source de **ventes** VN, absente
jusque-là (le seul travail ventes VN était le Bloc 2, en pause). Résolu sans
déplafonner le Bloc 2 : nouvelle source de ventes dédiée, sans lien avec la
partie feuille de marge/aide en pause.

**Changement de source ventes en cours de route** : la première version
utilisait `v_sf_vente` (Salesforce), mais `Modele_Vehicule__c` y est vide ou
en code technique sur une grande partie des lignes (ex. "1", "IX 1" au lieu
d'un libellé). Remplacé par **`hess-data.datamart_ventes.entete_du_dossier`**
jointe à **`hess-data.datamart_ventes.vehicules`** sur `CRC_vehicule_vendu` =
`CRC_vehicule` (même principe que le Bloc 3, mais un `vehicules` distinct de
celui de `datamart_stock` — à confirmer si c'est en fait une table partagée).

**Requête ventes validée** (agrégée directement en SQL, sur demande de
Quentin plutôt que de ramener toutes les lignes) :
```sql
SELECT
  e.Concession, v.Libelle_marque, v.Libelle_modele,
  COUNT(*) AS nb_ventes_90j, COUNT(*) / 3 AS ventes_moy_mensuelle
FROM `hess-data.datamart_ventes.entete_du_dossier` e
LEFT JOIN `hess-data.datamart_ventes.vehicules` v
  ON e.CRC_vehicule_vendu = v.CRC_vehicule
WHERE e.Est_VN_VD_ou_VO IN ('VN', 'VD')
  AND e.Source = 'Icar'
  AND e.Date_de_vente >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY e.Concession, v.Libelle_marque, v.Libelle_modele
ORDER BY e.Concession, v.Libelle_marque, v.Libelle_modele
```
Fichier/tabs : même fichier Sheet que le Bloc 3
(`10cOmCg_e8JKKpaHY0pI6QTPWLehO_VVfVAU6bXAROWE`) — `DM_Vente_VN_VD` →
`Extrait_Vente_VN_VD` (A=Concession, B=Libelle_marque, C=Libelle_modele,
D=nb_ventes_90j, E=ventes_moy_mensuelle, F=Code_concession, G=Code_Plaque,
H=Marque harmonisée, I=Modèle harmonisé).

**Piège de données rencontré (majeur) : désaccord de libellés marque/modèle
entre sources**. Comparaison réelle stock (`vehicules` datamart_stock) vs
ventes (Salesforce, avant migration) : **163 paires marque/modèle sur 344
sans correspondance exacte côté ventes** (47% des ventes concernées) — écarts
du type préfixes/suffixes commerciaux ("Nouvelle", "Société", accents,
codes techniques vs libellés). Résolu par une **table de transco construite
par Quentin** dans l'onglet `Mapping Marque Modèle` du même fichier (colonnes
`Marque (source), Libellé modèle (source), Marque harmonisée, Modèle
harmonisé`) — couvre l'intégralité des paires, pas seulement les 163 en écart.
Les deux extraits (stock et ventes) ont chacun 2 colonnes "harmonisée(s)"
calculées par rapprochement à cette table (`RECHERCHEX` sur clé concaténée
`Marque&"|"&Modèle`, avec repli sur la valeur d'origine via `SIERREUR` si pas
trouvée dans le mapping).

**Piège de données rencontré (mineur) : stock plaque attribué à Renault
Mulhouse**. Renault Mulhouse héberge une partie du stock consolidé de la
Plaque Renault, ce qui gonflait artificiellement ses propres chiffres
d'excès. Résolu par Quentin directement dans le mapping référentiel : ce
stock plaque est retiré du rattachement concession de Mulhouse, mais reste
compté au niveau plaque (où il a du sens).

**Onglet `BLOC 4 Couverture VN`** — une ligne par concession × marque ×
modèle harmonisés, liste générée via :
```
=UNIQUE(FILTER({Extrait_Stock_VN_VD!Y2:Y8774\Extrait_Stock_VN_VD!AD2:AD8774\Extrait_Stock_VN_VD!AE2:AE8774}; Extrait_Stock_VN_VD!Y2:Y8774<>""))
```
(le `FILTER` sur `Code_concession<>""` exclut délibérément les lignes non
rattachées à une concession — **39% des lignes brutes (464/1175) avant
filtrage**, jugé non prioritaire à creuser par Quentin — "ce n'est pas
important" ; à garder en tête si un doute de volumétrie apparaît plus tard.)

Colonnes et formules (A=Code_concession, B=Marque harm., C=Modèle harm.,
issus du `UNIQUE` ci-dessus) :
```
D Stock :              =COUNTIFS(Extrait_Stock_VN_VD!$Y:$Y;$A2;Extrait_Stock_VN_VD!$AD:$AD;$B2;Extrait_Stock_VN_VD!$AE:$AE;$C2)
E Ventes moy. :         =SUMIFS(Extrait_Vente_VN_VD!$E:$E; Extrait_Vente_VN_VD!$F:$F; $A2; Extrait_Vente_VN_VD!$H:$H; $B2; Extrait_Vente_VN_VD!$I:$I; $C2)
F Couverture :          =SI($E2=0;"Infini";$D2/$E2)
G Excès de stock :      =SI($D2>$E2; $D2-$E2; 0)
H Ancien_nb :           =COUNTIFS(Extrait_Stock_VN_VD!$Y:$Y;$A2;Extrait_Stock_VN_VD!$AD:$AD;$B2;Extrait_Stock_VN_VD!$AE:$AE;$C2;Extrait_Stock_VN_VD!$V:$V;">180")
I Rang (top 3 excès) : =SI($G2>=12; COUNTIFS($A:$A;$A2;$G:$G;">"&$G2)+1; 999)
J Code_Plaque :         =RECHERCHEX($A2; Extrait_Stock_VN_VD!$Y:$Y; Extrait_Stock_VN_VD!$Z:$Z)
K Stock Plaque :        =COUNTIFS(Extrait_Stock_VN_VD!$Z:$Z;$J2;Extrait_Stock_VN_VD!$AD:$AD;$B2;Extrait_Stock_VN_VD!$AE:$AE;$C2)
L Ventes moy. Plaque :  =SUMIFS(Extrait_Vente_VN_VD!$E:$E; Extrait_Vente_VN_VD!$G:$G; $J2; Extrait_Vente_VN_VD!$H:$H; $B2; Extrait_Vente_VN_VD!$I:$I; $C2)
M Couverture Plaque :   =SI($L2=0;"Infini";$K2/$L2)
```

**Podium top 3 par concession** (mêmes conventions que le Bloc 3 : sentinelle
`999`, argument `0` pour forcer l'absence d'en-tête) :
```
=QUERY(A2:I1677; "SELECT A, B, C, D, E, G WHERE I <= 3 ORDER BY A, G DESC"; 0)
```

**Seuil d'excès de stock — calibrage (méthode percentile)** : sur les 711
lignes propres (`Code_concession` non vide), médiane 2, P75 6, **P90 12**,
P95 17, max 51 (cas réel : REN_STRASBOURG Clio, 71 en stock, 20,3 ventes/mois,
51 d'excès). **Seuil retenu : ≥12** (P90). Avant nettoyage des lignes non
rattachées, le max apparent était 2550 — entièrement dû aux lignes sans
concession, à ne pas utiliser pour calibrer quoi que ce soit.

**Validé (2026-09-18)** sur données réelles, ex. BMW Belfort X1 : couverture
concession 2 mois vs couverture Plaque 3 mois (cohérent, pas d'écart
flagrant) ; BMW X5 : 8 mois concession vs 7 mois Plaque.

## 5. Bloc 6 — Anomalies Ventes VN/VD

**Statut : terminé et validé (2026-09-23)**. Reprend le sujet volontairement
différé le 2026-09-16 — pas de vérification "aide non respectée" (toujours
en pause, cf. Bloc 2), mais couvre marge négative, marge positive suspecte et
détention longue sur VD.

**Sources** (`hess-data.datamart_ventes`) :
- `entete_du_dossier` — un dossier de vente par ligne (déjà utilisé au Bloc 4).
- `lignes_du_dossier` — le détail ligne à ligne de chaque dossier (véhicule,
  options, remises, transfert de marge...), jointe sur `id_ligne_entete`.
- `configuration_champ_calcule` — table de config qui indique, pour chaque
  `Code_ligne_du_dossier`, à quel agrégat (`Marge_HT`, `Montant_surestimation`,
  `Cout_acquisition`, `Remises`, `Montant_des_aides`...) la ligne contribue.
  **Piège rencontré** : cette table a des doublons sur certains codes
  (`COMMISSIONS` ×5, `TVA` ×2, mêmes flags mais libellés différents) —
  `SELECT DISTINCT` sur les seules colonnes de flags utilisées résout le
  problème sans perte d'information (vérifié : les flags sont identiques
  entre doublons).
- `hess-data.datamart_stock.vehicules` (même table que le Bloc 3, **pas**
  `datamart_ventes.vehicules` cette fois — répond à la question ouverte du
  Bloc 4 sur la table à utiliser, au moins pour ce bloc).

**Fenêtre** : **5 derniers jours** (`BETWEEN J-5 AND J-1`) — repassée de
J-1 strict à 5 jours par Quentin le 2026-09-25 (le J-1 strict, lui-même
un repassage depuis 7 jours glissants le 2026-09-23, s'est révélé trop
étroit en pratique). Le commentaire en tête de la requête BigQuery est
resté à "4 derniers jours" après ce changement — texte à corriger, la
logique (`INTERVAL 5 DAY`) est correcte.

**Calcul de la marge** : reproduit la logique déjà validée dans l'outil
Tableau existant plutôt que d'inventer un calcul — notamment le **transfert
de marge**, qui reprend telle quelle la formule Tableau "fixed:Montant
surestimation Icar" (ligne `SURESTIMATION AP`, ou le montant vente/achat non
nul selon le cas). Deux marges calculées en parallèle pour se recouper :
- `marge_brute_vehicule_ht` — reconstruite composant par composant (CA − coût
  d'acquisition + remise + transfert de marge + aides au châssis), **le
  véhicule seul**.
- `marge_dossier_icar_ht` — la marge complète du dossier calculée par Icar,
  **véhicule + périphériques/transformation** (accessoires, financement...).

**Requête BigQuery validée** — fichier
`16xQnrbCZpPP2sDy4WxJvglRdIVYkwx31wiWC_n0lKcg`, tabs `entete_du_dossier`,
`vehicules`, `lignes_du_dossier` (Connected Sheets) → `DM Vente` →
`Extrait Vente VN/VD` :
```sql
WITH dossiers AS (
  SELECT id_ligne_entete, Numero_dossier_DMS, Concession, Vendeur,
    Est_VN_VD_ou_VO AS type_vehicule, Date_de_vente, Date_achat,
    CRC_vehicule_vendu, Destination_du_vehicule_canal_vente AS destination
  FROM `hess-data.datamart_ventes.entete_du_dossier`
  WHERE Date_de_vente = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    AND Est_VN_VD_ou_VO IN ('VN', 'VD')
),
config_dedup AS (
  SELECT DISTINCT Code_ligne_du_dossier, Marge_HT, Montant_surestimation,
    Prix_de_vente_du_vehicule_seul, Options_constructeur, Remises,
    Cout_acquisition, Montant_des_aides
  FROM `hess-data.datamart_ventes.configuration_champ_calcule`
),
marges AS (
  SELECT
    l.id_ligne_entete,
    ROUND(SUM(CASE WHEN c.Marge_HT = 1 THEN l.Prix_vente - l.Prix_achat ELSE 0 END), 2) AS marge_dossier_icar_ht,
    ROUND(SUM(CASE WHEN c.Prix_de_vente_du_vehicule_seul = 1 OR c.Options_constructeur = 1 THEN l.Prix_vente ELSE 0 END), 2) AS ca_brut_vehicule_ht,
    ROUND(SUM(CASE WHEN c.Cout_acquisition = 1 THEN l.Prix_achat ELSE 0 END), 2) AS cout_acquisition_ht,
    ROUND(SUM(CASE WHEN c.Remises = 1 THEN l.Prix_vente ELSE 0 END), 2) AS remise_ht,
    ROUND(SUM(CASE WHEN c.Montant_surestimation = 1 THEN
      CASE WHEN l.Code_ligne_du_dossier = 'SURESTIMATION AP' THEN l.Prix_vente
           WHEN l.Prix_vente = 0 THEN l.Prix_achat
           WHEN l.Prix_achat = 0 THEN l.Prix_vente END
      ELSE 0 END), 2) AS transfert_de_marge_ht,
    ROUND(-SUM(CASE WHEN c.Montant_des_aides = 1 THEN l.Prix_achat ELSE 0 END), 2) AS aides_au_chassis_ht
  FROM `hess-data.datamart_ventes.lignes_du_dossier` l
  JOIN config_dedup c ON c.Code_ligne_du_dossier = l.Code_ligne_du_dossier
  WHERE l.id_ligne_entete IN (SELECT id_ligne_entete FROM dossiers)
  GROUP BY 1
)
SELECT
  d.Numero_dossier_DMS AS numero_dossier, veh.Serie_VIN AS vin, veh.Immat AS immatriculation,
  d.Concession, veh.Libelle_marque AS marque, veh.Libelle_modele AS modele,
  d.type_vehicule AS vn_vd, d.Vendeur, veh.Libelle_categorie_vehicule AS categorie,
  d.destination, veh.Energie AS energie, d.Date_de_vente, d.Date_achat AS date_achat_vehicule,
  m.ca_brut_vehicule_ht, m.cout_acquisition_ht, m.remise_ht, m.transfert_de_marge_ht,
  m.aides_au_chassis_ht,
  ROUND(m.ca_brut_vehicule_ht - m.cout_acquisition_ht + m.remise_ht + m.transfert_de_marge_ht + m.aides_au_chassis_ht, 2) AS marge_brute_vehicule_ht,
  m.marge_dossier_icar_ht
FROM dossiers d
LEFT JOIN marges m ON m.id_ligne_entete = d.id_ligne_entete
LEFT JOIN `hess-data.datamart_stock.vehicules` veh ON veh.CRC_vehicule = d.CRC_vehicule_vendu
ORDER BY d.Date_de_vente DESC, d.Concession, d.Numero_dossier_DMS
```

**Piège de donnée** : la jointure `vehicules` échoue sur certains dossiers
(marque/modèle vides, ex. dossiers Lexus LBX et TOY_METZ observés) — le
calcul de marge et la détection d'anomalie fonctionnent quand même puisqu'ils
ne dépendent pas de cette jointure, seul l'affichage marque/modèle est vide.

**Colonnes calculées côté Sheet** (`Extrait Vente VN/VD`, après la requête) :
`Code_concession`/`Code_Plaque` (`RECHERCHEX` sur le nom de concession, via
un onglet `Mapping` local alimenté par `IMPORTRANGE` depuis le Référentiel
Concession — **piège rencontré** : la formule `IMPORTRANGE` doit être saisie
puis autorisée manuellement une première fois dans l'UI Sheets, sinon les
`RECHERCHEX` en aval échouent silencieusement sans qu'aucune erreur ne soit
visible côté requête elle-même), `Durée de détention` (VD uniquement, calculée
côté Sheet : `Date_de_vente − date_achat_vehicule`, pas besoin de la
redemander à BigQuery), `% Marge brute Véhicule`
(`marge_brute_vehicule_ht ÷ ca_brut_vehicule_ht`).

**Règles de classification retenues** (2026-09-23, formules construites une
par une puis vérifiées sur données réelles) :

1. **Rien à signaler** : marge véhicule négative mais entièrement expliquée
   par le transfert de marge (`marge_brute_vehicule_ht − transfert_de_marge_ht ≥ 0`)
   — le transfert de marge résout tout, pas la peine de remonter.
2. **Pas à signaler (OK)** : marge véhicule négative mais marge dossier
   complète positive (les périphériques/transformation compensent) — sauf
   l'exception ci-dessous.
3. **Anomalie VD** : marge (hors transfert) négative sur un VD, avec la
   durée de détention affichée en contexte — laissée à l'appréciation du
   lecteur (dépréciation), pas classée automatiquement bon/mauvais.
4. **À corriger** :
   - Marge (hors transfert) négative sur un **VN**.
   - Véhicule non identifié (jointure `vehicules` en échec).
   - **Exception à la règle 2** : marge véhicule fortement négative, aucune
     aide au châssis, **et** marge dossier également négative — dans ce cas
     précis, les périphériques ne compensent pas non plus, donc à corriger.
     Seuil générique en cellule `AA1` (valeur absolue) sauf pour **BMW**, qui
     a son propre seuil en **pourcentage de marge (-1,5%)** plutôt qu'en
     valeur absolue. Une calibration marque par marque a été tentée le
     2026-09-23 (percentiles sur 6 mois de données réelles) mais
     **abandonnée** : sur toutes les marques hors BMW/MINI, seules RENAULT
     (12 dossiers) et BMW MOTORRAD (14 dossiers) atteignaient un volume
     suffisant (≥5) sur 6 mois — trop peu pour généraliser marque par marque.
     `AA1` reste donc un seuil générique unique pour toutes les marques hors
     BMW/MINI, non recalibré.
   - **MINI est totalement exclu** de toute anomalie (aucune remontée, quel
     que soit le montant) — décision explicite de Quentin, raison métier non
     documentée plus précisément.
5. **À vérifier** :
   - Marge faible négative (≤ -500€), sans aide au châssis, **Particuliers
     uniquement**, hors BMW et MINI.
   - Marge positive faible (entre 0 et 500€), sans aide au châssis
     (suspicion d'aide manquante), **Particuliers uniquement** — piège
     rencontré : le filtre "Particuliers" avait été oublié sur cette
     deuxième règle lors d'une fusion de formules, corrigé après coup.

**Bloc 6 — listing final** (onglet `BLOC 6 - Anomalie Vente VN-VD`) :
```
=QUERY('Extrait Vente VN/VD'!A2:AB; "SELECT A, U, V, E, F, G, J, S, T, X, Z, AB WHERE X != '' OR Z != '' OR AB != '' ORDER BY U"; 0)
```
(A=numero_dossier, U/V=Code_concession/Code_Plaque, E/F=marque/modèle,
G=vn_vd, J=destination, S/T=les deux marges, X/Z/AB=les 3 colonnes
d'anomalie). **Piège rencontré** : omettre le 3ᵉ argument `; 0` (indique à
`QUERY` qu'il n'y a pas d'en-tête à interpréter) provoque une ligne d'en-tête
parasite qui réapparaît au milieu des résultats.

**Validé (2026-09-23)** sur données réelles — 14 dossiers remontés sur 7
jours glissants, réparties sur les 3 catégories, plusieurs marques
(BMW, Renault, Nissan, Hyundai, Toyota, Lexus).

### 5.1 Mises à jour du 2026-09-25

- **Seuil "À vérifier" (marge positive faible)** : abaissé de 500€ à
  **200€** (`$T2<200` dans la formule de la règle 5).
- **Colonnes de `Extrait Vente VN VD` réordonnées** par Quentin — `% Marge
  brute Véhicule` déplacée de `AA` à `U`, ce qui décale tout le reste
  (`Code_concession, Code_Plaque, Durée de détention, Anomalie VD, Pas a
  signaler` ↦ `V, W, X, Y, Z`) et place `A signaler` en `AA` (`A vérifier`
  reste en `AB`, dernière colonne). **Toute référence de colonne
  précédemment documentée dans ce fichier pour ce bloc est à revérifier sur
  le Sheet avant réutilisation.**
- **Bug corrigé — marges négatives VN non signalées quand une aide est
  présente** : la règle "À corriger" ne testait le cas marge/dossier
  négatifs que si `aide=0` — 16 dossiers réels trouvés avec une aide
  substantielle (1 300€ à 9 681€) mais un dossier resté négatif malgré
  elle, invisibles dans les 3 colonnes de classification. Corrigé en
  retirant la condition `aide=0` de la règle et en adaptant le message
  ("marge négative sans aide" vs "marge négative malgré aide, dossier
  négatif") :
  ```
  =IF($E2="MINI"; "";
    IF($E2="BMW";
      IF(AND($U2<=-0,015; $T2<0);
        IF($R2=0; "À corriger - marge négative sans aide, dossier négatif"; "À corriger - marge négative malgré aide, dossier négatif");
        ""
      );
      IF(AND($S2<=$Z$1; $T2<0);
        IF($R2=0; "À corriger - marge négative sans aide, dossier négatif"; "À corriger - marge négative malgré aide, dossier négatif");
        ""
      )
    )
  )
  ```
  **Bug encore ouvert** : `$Z$1` référence l'en-tête de sa propre colonne
  ("Pas a signaler", texte) au lieu d'un seuil numérique — comparaison
  nombre/texte toujours vraie côté Sheets (même piège que documenté dans
  `CADRAGE_APV.md` §4 pt.4), donc le seuil générique hors BMW n'est pas
  réellement appliqué. Emplacement du vrai seuil non identifié à ce jour —
  question ouverte (§7).
- **Règle de tri/troncature du listing final** : alignée sur la règle VO
  (`CADRAGE_VO.md` §11, inversée le 2026-09-25) — **montant décroissant en
  premier, date décroissante en cas d'égalité**, top 5 + "+N autres
  anomalies" si le volume dépasse 5 dossiers pour une concession un jour
  donné. Pas encore nécessaire en pratique (volumes observés faibles), mais
  la règle est fixée pour quand ce sera le cas.

## 6. Maquette mail VN

**Statut : structure validée (2026-09-23)**, maquette construite sur la
concession pilote Renault/Nissan Mulhouse, à partir de données réelles issues
des Blocs 1, 3, 4 et 6 ci-dessus.

**Fichier** : [`docs/mockup_email_vn.html`](mockup_email_vn.html) — reprend
telle quelle la charte graphique du mockup VO (navy `#2D3250` / gold
`#C8AA73`, Montserrat, thème clair fixe — les clients mail ne respectent pas
fiablement le thème sombre).

**Structure retenue** (ordre final) :
1. Header + titleblock (concession, "chiffres de la veille").
2. 4 tuiles KPI : Leads reçus J-1, Couverture stock, Stock âgé VN (+6 mois),
   Anomalies ventes.
3. Synthèse : un commentaire factuel unique pointant l'anomalie la plus
   significative du jour — voir règle de rédaction ci-dessous.
4. **Anomalies ventes** (tableau, colonnes VIN/véhicule/marge/motif).
5. **Leads VN** (reçus/non traités, J-1 et 7j).
6. **Qualité du stock VN/VD** : compteurs (Stock VN/VD, âgé VN/VD +6 mois,
   contremarqué +90j) + 3 mini-listes des véhicules les plus anciens (VN, VD,
   contremarqué), issues de l'onglet `BLOC 3 P2 Stock VN_VD`.
7. **Rotation & couverture** : tableau concession vs Plaque (Stock, ventes
   moy. mensuelle, couverture), agrégé à partir des lignes du Bloc 4 sur les
   modèles propres à la concession.
8. **Excès de stock** : podium top 3 modèles (Bloc 4).
9. Footer.

**Décision d'ordre des sections (2026-09-23)** : Anomalies ventes en premier
juste après la Synthèse — c'est le contenu le plus actionnable (perte
d'argent à corriger). Puis Leads (actions du jour : relances). Le stock passe
en dernier : il évolue lentement, plus informatif qu'urgent. Décision
explicite de Quentin, retenue après un test de réorganisation en 3 sections
(fusion des blocs stock) présenté puis écarté au profit de la structure
d'origine à 5 sections — préférée telle quelle.

**Décision de cadence (2026-09-23)** : le stock reste envoyé **quotidiennement**
malgré son évolution lente, avec les listes top-3 statiques (les plus
anciens). Une approche "n'afficher que les nouveautés depuis la veille" a été
envisagée mais écartée pour l'instant, car elle suppose une historisation
qui n'est pas encore construite — à reconsidérer plus tard.

**Règle de rédaction du commentaire de synthèse** : rester strictement
factuel, ne jamais inventer de lien causal entre deux blocs qui partagent
un mot-clé/modèle sans preuve réelle (ex. rejeté : lier un excès de stock
Clio à une perte de marge sur un dossier Clio, alors que rien ne les relie
réellement). Un vrai recoupement inter-blocs doit être présenté comme "deux
signaux distincts sur le même véhicule/modèle", jamais comme une causalité,
sauf si elle est réellement établie. Une perte substantielle et chiffrée
(ex. -5 265€) doit être signalée directement plutôt que reformulée.

**Décisions d'affichage du tableau Anomalies ventes** : VIN affiché (pas
d'immatriculation disponible sur les ventes VN fraîches, champ vide côté
Icar) ; pas de pastille de statut ("à corriger"/"à vérifier") affichée — la
classification (§5) sert au tri interne, pas à l'affichage destinataire.

**Comparaison Plaque au niveau agrégat concession** : en plus du détail
modèle par modèle déjà présent dans le Bloc 4, le mail affiche désormais un
agrégat concession vs Plaque pour la Rotation & couverture (somme des
colonnes Stock/Ventes moy. Plaque du Bloc 4 sur les seuls modèles portés par
la concession).

**Limite connue de la maquette** : les données proviennent de Sheets
rafraîchis à des dates différentes (Leads : 14/09, Stock/Ventes : 23/09) —
pas encore synchronisés comme pour le VO. Quentin met en place une
actualisation automatique des Sheets pour résoudre ce point (2026-09-23, en
cours).

**Décision de périmètre Bloc 4 dans le mail (2026-09-23)** : la comparaison
Plaque (colonnes Stock/Ventes moy./Couverture Plaque du Bloc 4, y compris
l'agrégat concession vs Plaque de la section "Rotation & couverture"
ci-dessus) est **réservée à un futur mail Directeur de plaque**, sur le même
principe que le Bloc 7 VO — elle ne restera pas dans le mail Service à
terme. Le détail concession seul (couverture, excès de stock) reste dans le
mail Service. La maquette actuelle inclut encore la comparaison Plaque ;
retrait à faire quand le mail Service sera finalisé pour de vrai (pas encore
fait, maquette non modifiée à ce stade).

**Intégration du Bloc 2 (2026-09-24)** : section "Commandes & Facturations vs
Objectifs" ajoutée entre Anomalies ventes et Leads VN (pacing d'objectif,
plus directement actionnable qu'un simple compteur d'activité, mais moins
urgent qu'une anomalie déjà constatée). Format compact inspiré de la
maquette APV de Corentin (`docs/mockup_email_apv.html`, relue avant de
construire cette section) : ligne de synthèse "valeur MTD / objectif (%,
tendance)" plutôt qu'un tableau à 10 colonnes par flux — le `BLOC 2` Sheet
a beaucoup plus de colonnes (J-1, 7j, moy. hebdo, MTD, MTD N-1, objectif,
manque à date, taux, projection, reste à faire, tendance × 2 flux) que ce
qui est montré dans le mail ; seuls MTD/Objectif/% par marque sont affichés
en tableau, le reste (manque à date, projection) reste dans le Sheet sans
remonter dans le mail V1. Données réelles Renault/Nissan Mulhouse
(concession `RENNIS_MULHOUSE`), lues directement dans `BLOC 2` : Commandes
168/254 (66,1%, stable), Facturations 182/216 (84,3%, hausse confirmée) ;
détail par marque (Renault, Dacia, Nissan, Alpine — Peugeot exclu, volume
nul ce mois-ci).

**Tuiles KPI "Tendance Commande/Facturation" (2026-09-24, corrigé)** : la
Tendance du Bloc 2 croise **2 comparaisons distinctes**, pas une seule
(cf. formule §2) — niveau (mois à date vs même période l'an dernier, dates
calendaires égales) et rythme (7 derniers jours vs moyenne hebdo des 4
semaines précédentes). Une première version de la tuile n'affichait que le
% de niveau, ce qui laissait croire que c'était le seul critère derrière le
qualificatif ("Stable", "Hausse confirmée"...) — **corrigé** : la tuile
affiche le qualificatif (flèche + mot, valeur brute du Sheet), et un
tooltip explique les 2 comparaisons avec leurs valeurs réelles (ex.
niveau 168 vs 179 = -6,1%, rythme 42 vs 41,25 = 102%), sur le même principe
que le tooltip déjà utilisé pour le score de vigilance.

**Note BMW Motorrad — conditionnelle, pas démontrée sur cette maquette** :
Renault/Nissan Mulhouse ne porte pas la marque BMW Motorrad, donc la note
documentée au §2 ("suivi mensuel déclaratif, pas de détail J-1/7j") n'a pas
de données réelles à afficher ici. À template-driver : la note doit
apparaître uniquement sur les lignes marque = BMW Motorrad, pas codée en
dur pour toutes les concessions.

## 7. Questions ouvertes VN

1. **Bloc 4, table `vehicules`** : confirmer si `hess-data.datamart_ventes.vehicules`
   est une table distincte de `hess-data.datamart_stock.vehicules` ou la même
   partagée entre les deux datasets — le Bloc 6 utilise `datamart_stock.vehicules`
   avec succès, penche pour "table partagée", à confirmer.
2. **Bloc 4, lignes non rattachées** : 39% des lignes stock/ventes brutes
   n'ont pas de `Code_concession` — mis de côté par Quentin, mais à garder en
   tête si des écarts de volumétrie inattendus apparaissent plus tard.
3. **Bloc 6, seuil générique "marge fortement négative"** pour les marques
   autres que BMW — non calibré (calibration marque par marque tentée et
   abandonnée le 2026-09-23, volume insuffisant ; seule BMW a un seuil
   dédié, en %, MINI est exclu). **Aggravé le 2026-09-25** : la cellule
   actuellement référencée par la formule (`$Z$1`) contient l'en-tête de
   sa propre colonne, pas un nombre — le seuil générique n'est donc pas
   réellement appliqué en pratique (comparaison nombre/texte toujours
   vraie). Emplacement du vrai seuil (s'il a existé) non retrouvé — à
   confirmer avec Quentin avant de corriger la référence.
4. **Existe-t-il une spec équivalente à `Spec_Mail_IA_ChefVentesVN`** —
   toujours pas, contrairement au VO qui a une spec dédiée.

## 8. Prochaines étapes

1. ~~Intégrer le Bloc 2 (Commandes & Facturations vs Objectifs) à la
   maquette mail VN~~ **fait (2026-09-24)** — voir §6. La note BMW Motorrad
   reste à implémenter en conditionnel côté mail réel (pas démontrable sur
   la maquette Mulhouse, qui ne porte pas cette marque).
2. Retirer la comparaison Plaque du mail Service (maquette + mail réel) une
   fois le futur mail Directeur de plaque cadré — décision de périmètre
   prise (§6), reste à exécuter.
3. Suivre la mise en place par Quentin de l'actualisation automatique des
   Sheets, puis vérifier que la maquette mail tourne sur des données toutes
   alignées à la même date.
