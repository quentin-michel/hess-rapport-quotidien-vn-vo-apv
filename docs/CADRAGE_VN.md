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

## 4. Questions ouvertes VN

1. **Bloc 2 bloqué** : nom du champ aide côté vente (§2.3).
2. **Bloc 2, périmètre VD** : le VD est-il dans le périmètre de l'anomalie
   "aide non respectée" ? (§2.2)
3. **Bloc 2, condition marge négative** : l'anomalie doit-elle rester
   conditionnée à la marge négative, ou tout écart d'aide notable compte ?
   (§2.2)
4. **Bloc 2, jointure** : confirmer que `Feuille_de_marge__c` (vente) pointe
   bien vers `Id` de `v_sf_feuille_de_marge` (hypothèse non vérifiée).
5. **Existe-t-il une spec équivalente à `Spec_Mail_IA_ChefVentesVN`** —
   toujours pas, contrairement au VO qui a une spec dédiée.
6. Blocs restants non encore abordés : anomalies ventes VN (mis de côté
   volontairement pour plus tard, cf. décision 2026-09-16), contexte
   plaque/réseau (probablement hors périmètre du mail Service, comme pour le
   Bloc 7 VO).

## 5. Prochaines étapes

1. Reprendre le Bloc 2 dès que le champ aide-vente est communiqué par le
   service data.
2. Valider le Bloc 3 (Stock) sur des lignes réelles d'une concession pilote,
   puis définir les règles d'anomalie.
3. Une fois Blocs 1-3 validés, revenir sur le Bloc "Anomalies ventes VN"
   (volontairement différé) et le format du mail.
