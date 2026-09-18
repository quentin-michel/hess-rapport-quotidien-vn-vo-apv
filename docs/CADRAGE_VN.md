# Cadrage — VN (Véhicules Neufs)

Voir [`CADRAGE.md`](CADRAGE.md) pour le cadrage transverse (objectif général,
architecture, destinataires, décisions communes aux 3 services).

**Statut (2026-09-17) : démarré, construction bloc par bloc en cours** — même
méthode que VO (Sheet par bloc, validé sur données réelles avant de documenter).
Bloc 1 (Leads) construit et partiellement validé. Bloc 2 (Commandes/Feuille de
marge) en pause, en attente d'un champ manquant côté data. Bloc 3 (Stock)
requête BigQuery validée, lecture Sheet à valider sur données réelles.

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

## 2. Bloc 2 — Commandes VN / Feuille de marge (EN PAUSE)

**Sources** (Salesforce, `hess-data.salesforce_source_views`) :
- `v_sf_feuille_de_marge` — 127 colonnes, un enregistrement par "feuille de
  marge" (bon de commande VN avec marge prévisionnelle et validations).
- `v_sf_vente` (même table que VO, filtrée `Type__c IN ('VN','VD')`) — colonnes
  confirmées : `Id, numero_vente, Type__c, Canal_de_vente__c, Statut__c,
  Date_de_vente__c, Date_de_livraison__c, Facture_totale__c,
  Montant_vehicule_TTC__c, Marge_Vente__c, Marge_Vehicule__c,
  Montant_Reprise_VO__c, Kilometres__c, Marque_Vehicule__c, Modele_Vehicule__c,
  Energie_vehicule_vendu__c, Immatriculation__c, Concession__c,
  TECH_ConcessionName__c, TECH_Nom_du_vendeur_de_la_vente__c, Nom_du_client__c,
  Vehicule_vendu__c, Vendeur_Id__c` + `Difference_Aides_Ventes_FDM__c` et
  `Feuille_de_marge__c` (ajoutés par le service data le 2026-09-16/17, voir
  ci-dessous).

Fichier de travail (Sheet de test, structure amenée à changer) :
`14iuxhKZr34StlxCn8IodM9iquoqH9wnc5EhsBYxBUDE`.

### 2.1 Comptage des bons de commande

**Règle validée** : un bon de commande compte si `Validation_vendeur__c =
TRUE` **ET** `Date_de_commande__c` = J-1 (pas `Date_de_validation__c`, qui
peut être postérieure — décidé explicitement 2026-09-16, écart entre les deux
dates existant réellement, cf. champ `Ecart_date_validation_commande__c`).
Comptage groupé par `Concession__c`. **Non encore testé sur données réelles.**

### 2.2 Anomalie "aide non respectée" (objectif métier, cf. §2.3 pour le blocage)

Objectif de Quentin : sur une vente VN à marge négative, vérifier que les
aides indiquées sur la feuille de marge approuvée se retrouvent bien dans le
dossier de vente — **au sens B** (comparaison de valeurs, pas juste "y a-t-il
eu une validation ?"), et principalement pour les cas où une aide chiffrée sur
la feuille de marge est absente du dossier de vente final.

Le service data a ajouté, directement dans `v_sf_vente` :
- `Difference_Aides_Ventes_FDM__c` (2026-09-16) — écart pré-calculé entre
  l'aide de la vente et celle de la feuille de marge liée. **Type STRING**,
  séparateur décimal `,` — nécessite
  `SAFE_CAST(REPLACE(champ, ',', '.') AS FLOAT64)` avant tout filtre/tri
  numérique (sinon `No matching signature for operator`).
- `Feuille_de_marge__c` (2026-09-17) — champ de liaison vers
  `v_sf_feuille_de_marge` (jointure supposée sur `Id` — **hypothèse non
  confirmée avec Quentin/le service data à ce jour**).

**Constat sur les données réelles (2026-01-01 → 2026-09-16, VN+VD, 43 994
ventes)** :
- 161 ventes à marge négative au total.
- Seulement **9** d'entre elles ont `Difference_Aides_Ventes_FDM__c ≠ 0` — la
  majorité des marges négatives n'a rien à voir avec un problème d'aide.
- Les écarts trouvés sont substantiels (1 194€ à 10 380€), pas du bruit
  d'arrondi.
- Plusieurs des plus gros écarts sont sur des ventes **VD** (véhicule de
  démonstration), pas VN — **question ouverte non tranchée** : le VD reste-t-il
  dans le périmètre de cette anomalie ?
- Des écarts d'aide substantiels (1 250€ à 2 500€) existent aussi sur des
  ventes à **marge positive** — **question ouverte non tranchée** : l'anomalie
  doit-elle rester conditionnée à "marge négative ET écart d'aide", ou tout
  écart d'aide notable est-il à signaler indépendamment du signe de la marge ?

### 2.3 Point bloquant (2026-09-17)

Il manque le **nom exact du champ "montant d'aide" côté vente** dans
`v_sf_vente` pour finaliser la requête complète (vente + jointure feuille de
marge + numéro de feuille de marge + aide FDM + aide vente). Bloc mis en pause
par Quentin en attendant ce champ — **reprendre à ce point précis**, ne pas
redemander les questions déjà tranchées ci-dessus.

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

## 5. Questions ouvertes VN

1. **Bloc 2 bloqué** : nom du champ aide côté vente (§2.3).
2. **Bloc 2, périmètre VD** : le VD est-il dans le périmètre de l'anomalie
   "aide non respectée" ? (§2.2)
3. **Bloc 2, condition marge négative** : l'anomalie doit-elle rester
   conditionnée à la marge négative, ou tout écart d'aide notable compte ?
   (§2.2)
4. **Bloc 2, jointure** : confirmer que `Feuille_de_marge__c` (vente) pointe
   bien vers `Id` de `v_sf_feuille_de_marge` (hypothèse non vérifiée).
5. **Bloc 4, table `vehicules`** : confirmer si `hess-data.datamart_ventes.vehicules`
   est une table distincte de `hess-data.datamart_stock.vehicules` ou la même
   partagée entre les deux datasets (hypothèse non vérifiée).
6. **Bloc 4, lignes non rattachées** : 39% des lignes stock/ventes brutes
   n'ont pas de `Code_concession` — mis de côté par Quentin, mais à garder en
   tête si des écarts de volumétrie inattendus apparaissent plus tard.
7. **Existe-t-il une spec équivalente à `Spec_Mail_IA_ChefVentesVN`** —
   toujours pas, contrairement au VO qui a une spec dédiée.
8. Bloc restant non encore abordé : anomalies ventes VN (mis de côté
   volontairement pour plus tard, cf. décision 2026-09-16).

## 6. Prochaines étapes

1. Reprendre le Bloc 2 dès que le champ aide-vente est communiqué par le
   service data.
2. Une fois Blocs 1, 3 et 4 stabilisés, revenir sur le Bloc "Anomalies
   ventes VN" (volontairement différé) et le format du mail — y compris la
   question de savoir si le Bloc 4 (comparaison plaque incluse) reste dans le
   mail Service ou est réservé au futur mail directeur de plaque, comme le
   Bloc 7 VO.
