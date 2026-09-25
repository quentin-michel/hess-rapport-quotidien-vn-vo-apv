# Cadrage — APV (Après-Vente)

Voir [`CADRAGE.md`](CADRAGE.md) pour le cadrage transverse (objectif général,
architecture, destinataires, décisions communes aux 3 services).

**Statut : architecture reconstruite et étendue au groupe entier (2026-09-10/11),
objectifs MO/PR/PR externe branchés et seuils recalibrés (2026-09-14) — en
avance sur le séquencement initial** (le cadrage global priorisait VO, mais
Corentin a repris et largement dépassé l'état "prêt côté données" du
2026-09-08 ci-dessous, qui est **obsolète**).

**Priorité (2026-09-23) : formalisation du mail**, sur la base des blocs
déjà construits et validés (`Analyse Globale`, `Encours prioritaires`,
`Analyse pièces J-1`, `Efficience OR CI trop élevé`, `Taux remise MO/PR
interne élevé`) — voir §8 pt.1 et §12. **Le chantier anomalies forfaits
(§9-10 : marge estimée, forfaits pièces suspectes) est mis en pause**,
gardé comme piste à reprendre plus tard une fois le mail lui-même
formalisé — décision explicite de Corentin, pas d'abandon.

## 1. Source

**Rapport quotidien APV** (`1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw`).

### 1.1 Le constat du 2026-09-08 est caduc

L'état initial (un seul tableau récapitulatif limité à la plaque Renault,
détaillé plus bas en note historique) a été entièrement reconstruit les
2026-09-10/11 pour deux raisons :
1. **Volumétrie** : les extraits bruts (facturation, temps, magasin) sur 35
   jours glissants explosaient en nombre de cellules dès qu'on sortait du
   pilote Renault (limite du connecteur BigQuery natif Sheets : 5M cellules).
2. **Passage au groupe entier** — plus seulement la plaque Renault.

### 1.2 Architecture actuelle : historique agrégé + détail J-1

Principe validé et appliqué à tout le domaine APV (Atelier + Magasin + Temps) :
séparer ce qui sert à **calculer les tendances** (agrégé, léger, plusieurs
semaines/mois d'historique) de ce qui sert à **détecter une anomalie précise**
(détail ligne à ligne, mais seulement J-1). Un extrait détaillé sur plusieurs
semaines n'est jamais nécessaire : soit on agrège (léger), soit on ne regarde
qu'un jour (léger aussi) — c'est le croisement des deux qui aurait été lourd.

| Bloc | Historique agrégé (35j glissants, sert J-1/moyenne mobile/MTD) | Détail J-1 (sert la détection d'anomalie) |
|---|---|---|
| Facturation Atelier | `Historique CA Atelier` → extraction **`Historique CA par atelier`** (Concession, Date, CA_MO_Net_HT, CA_PR_interne_Net_HT, Cout_PR_interne, Nb_OR_clotures) | `Facturation détaillée Atelier` → extraction **`Détail facturation atelier journalière`** (34 col. + Categorie_client, Nom_client, Code concession ajoutés) |
| Magasin | `Historique CA Magasin` → **`Historique CA par Magasin`** (Concession, Date, CA_PR_Externe_Net_HT, Cout_PR_Externe) | `Magasin` → **`Détail facturation magasin journaliere`** (19 col. + Code concession) |
| Temps (Efficience/Productivité) | `Historique Efficience + Productivité` → **`Historique efficience/prod`** (Concession, Date, Temps_facture_total, Rappel_temps_passe_total, Temps_facture_cession_interne, Rappel_temps_passe_cession_interne, Temps_passe_total) | `Temps facturés journaliers` → **`Temps facturés par jour`** ; `Temps passés journaliers` → **`Temps passés par jour`** |
| Encours | *(pas de fenêtre glissante nécessaire — voir §1.3)* | `Encours` → **`Encours à date`** |
| CA mensuel (nouveau, 2026-09-11) | `Historique CA mensuel par atelier` → **`Historique CA mensuel ateliers`** (Concession, Mois, CA_MO_Net_HT, CA_PR_interne_Net_HT) — 7 mois glissants, sert un ratio "jours de CA" (§2.6) | — |

**Les onglets de gauche (`Historique CA Atelier`, `Facturation détaillée
Atelier`, `Historique Efficience + Productivité`, `Temps facturés/passés
journaliers`, `Encours`, `Historique CA Magasin`, `Magasin`, `Historique CA
mensuel par atelier`, `Obj APV`) sont conservés intentionnellement** — ce sont
des onglets **DATA_SOURCE** (connecteurs BigQuery live d'origine, ère pilote),
gardés parce qu'ils portent le **rafraîchissement programmé** des données
(scheduled refresh Connected Sheets) : les supprimer casserait l'automatisation
des extractions quotidiennes. Ce ne sont donc pas des onglets morts à nettoyer
— seuls leurs successeurs GRID (colonne de droite) sont lus par les formules
et par `gws` (les onglets DATA_SOURCE renvoient une erreur `"Unable to parse
range"` à la lecture par l'API Sheets `values.get`, ce qui est normal pour ce
type d'onglet, pas un bug).

Chaque table (agrégé ou détail) source ses jointures sur `entete_or`
(`Est_ferme=1 AND Est_annule=0`), sauf le Magasin qui joint
`lignes_pieces`/`entete_pieces`. `Numero_OR` (le champ opaque type
`P0331162784302026`) a été retiré de l'extraction Atelier — inutile, seul
`Numero_OR_DMS` (le numéro reconnu par les ateliers, vérifié identique au champ
`entete_or.Numero_OR_DMS`) est gardé.

### 1.3 Cas particulier : les encours

`v_sf_passages_ateliers_en_cours` (source Salesforce, `hess-data.salesforce_source_views`)
n'a pas de problème de volumétrie par construction : c'est une photo de
l'état actuel (OR encore ouverts), pas une fenêtre de N jours qui grossit avec
la profondeur d'historique — extraction groupe entier ≈ 10 500 lignes.
Filtre obligatoire : `Statut__c NOT IN ('Cloture','Annulé')` (la table contient
aussi tout l'historique clos depuis 2019) et `nom_compte != 'VOXTUR'` (compte
parasite, non-HESS, à exclure). Champ `Date_MAJ_valo_comptable__c` = date du
dernier recalcul batch de la valorisation comptable (~75% des encours partagent
la même date un jour donné) — à distinguer de `Date_de_mise_a_jour__c`
(activité réelle par OR, étalée dans le temps).

**Piège de nommage confirmé sur données réelles (20/20 échantillons, écart
strictement nul)** : `Montant_MO_PR_Encours__c` = **total MO+PR** (malgré son
nom), et `Montant_Actuel_PR_PAMP__c` = le **PR seul**, valorisé au coût (PAMP).
`Montant_MO_Encours__c` (MO seul) + `Montant_Actuel_PR_PAMP__c` (PR seul) =
`Montant_MO_PR_Encours__c` exactement. Ne jamais additionner
`Montant_MO_Encours__c` + `Montant_MO_PR_Encours__c` (ça double-compte le MO).

Champ `OR_ferme_depuis_plus_de_2_mois__c` **non fiable** — vérifié sur données
réelles : à `TRUE` uniquement sur des OR annulés il y a 0-13 jours, jamais sur
les 88 455 OR réellement clôturés depuis des mois. Champ buggé ou calculé sur
une autre logique que son nom ; ne pas l'utiliser.

## 2. Regroupement par code canonique (2026-09-11)

Constat : plusieurs marques peuvent partager un même site physique et donc un
même destinataire de mail (ex. `Renault Mulhouse`, `Nissan Mulhouse`,
`Alpine Mulhouse`, `Dacia Mulhouse` → toutes `RENNIS_MULHOUSE`). Agréger par
nom de concession brut aurait fait apparaître ces sites en double. Toutes les
tables (agrégées et détail) portent donc désormais une colonne "Code
canonique" (`VLOOKUP` contre `Mapping concession`, onglet local dupliqué du
Référentiel de Quentin — **jamais modifié, seulement complété avec de
nouvelles lignes** pour les sources Magasin (`entete_pieces.Regroupement_Concession_APV`)
et Encours (`v_sf_account.nom_compte`), absentes à l'origine), et
`Analyse Globale` groupe désormais sur ce code, pas sur le nom brut.

### 2.1 Cas où un même texte doit résoudre vers 2 codes différents (2026-09-14)

`Mapping concession` est une table à plat (texte → code), donc **un même
texte brut ne peut pointer que vers un seul code** — problème rencontré avec
`Isuzu Châlons` (site partagé avec Hyundai Châlons côté APV, mais compte
Salesforce/stock distinct côté commerce VN/VO) : décision métier = rattacher
à `HYU_CHALONS` uniquement pour l'APV (encours + objectifs), en gardant
`ISUZU_CHALONS` pour le stock/commerce, hors de ce périmètre.

Solution : une colonne `E` (`Cle_recherche` = `A2&"||"&C2`, soit
`Source_BigQuery||Valeur_Source`) ajoutée à `Mapping concession`, utilisée
seulement par les 2 formules concernées (`Encours à date`, `Objectif APV`)
via `INDEX/MATCH` avec repli sur le `VLOOKUP` simple existant :
```
=IFERROR(INDEX('Mapping concession'!$D:$D; MATCH("entete_or||"&$A2; 'Mapping concession'!$E:$E; 0)); IFERROR(VLOOKUP($A2; 'Mapping concession'!$C:$D; 2; FALSE); $A2))
```
Les autres onglets gardent leur `VLOOKUP` simple intact (pas concernés par la
collision). Attention : le `MATCH`/`VLOOKUP` Sheets ignore la casse mais
**pas les accents** — la ligne de override doit reprendre l'orthographe exacte
(accents compris) telle qu'elle apparaît dans la source réelle.

### 2.2 Audit transco (2026-09-24/25) — bug `#REF!` trouvé, clé composée pas
toujours nécessaire

**Contexte** : le classeur `Référentiel Concession` de Quentin a été
restructuré — l'onglet source y a été renommé `Mapping concession` →
`Mapping_Sources`, et n'a **jamais eu** la colonne `Cle_recherche` (E) :
cette colonne n'existe que dans la copie locale du classeur APV principal
(§2 ci-dessus), ajoutée spécifiquement ici.

**Bug de production trouvé en auditant toutes les formules référençant
`Mapping concession`** (`Encours à date`, `Objectif APV`, et les 7 autres
onglets en `VLOOKUP` simple) : les formules `Encours à date` et
`Objectif APV` pointent en réalité vers **`#REF!`** au lieu de
`'Mapping concession'!$E:$E` — la plage a dû être supprimée puis recréée à
un moment, cassant la référence des formules qui la ciblaient (les
formules qui recréent la colonne fonctionnent, mais celles qui la
*consultent* depuis un autre onglet restent orphelines). Conséquence
silencieuse : `Encours à date` retombe sur la valeur brute non transcodée
sur **toutes** ses lignes (pas de repli `VLOOKUP`) ; `Objectif APV`
fonctionne quand même grâce à son repli `VLOOKUP` imbriqué, mais pas via le
chemin `Cle_recherche` prévu à l'origine. **Correctif** (répare le bug et
simplifie, cf. raisonnement ci-dessous) :
```
=IFERROR(VLOOKUP($B2; 'Mapping concession'!$C:$D; 2; FALSE); $B2)   ' Encours à date, col. V
=IFERROR(VLOOKUP($A2; 'Mapping concession'!$C:$D; 2; FALSE); $A2)   ' Objectif APV, col. J
```
Pas encore appliqué dans le Sheet au moment de la rédaction — à faire.

**Clarification du principe (2026-09-25)** : la clé composée
(`Source||Valeur`) ne sert qu'à distinguer une collision **entre le
périmètre APV et le périmètre commerce/stock** (le cas Isuzu/Hyundai
Châlons, §2.1). Elle n'a jamais été nécessaire pour distinguer Atelier de
Magasin **à l'intérieur** de l'APV (`entete_or` vs `entete_pieces`) : les
deux résolvent au même code pour un même site. Conséquence pratique : un
onglet/classeur qui ne mélange que des sources 100% APV (comme
`Anomalies forfaits` ou `Prix/Remises forcées`) peut se contenter d'un
`RECHERCHEV` simple, sans clé composée — seuls les onglets qui touchent
aussi une source commerce/stock (aucun cas identifié à ce jour en dehors
d'`Encours à date`/`Objectif APV`, qui de toute façon n'en ont pas
vraiment besoin comme démontré ci-dessus) en auraient l'utilité.

**Import filtré aux sources APV** (au lieu d'importer tout
`Mapping_Sources`, qui inclut aussi le commerce/stock `v_sf_*`) — utilisé
pour les classeurs externes (`Anomalies forfaits`, `Prix/Remises forcées`) :
```
=QUERY(IMPORTRANGE("<url Référentiel Concession>";"Mapping_Sources!A:D");"select Col1, Col2, Col3, Col4 where Col1 = 'entete_or' or Col1 = 'entete_pieces'";1)
```
Pour le classeur APV principal lui-même, l'audit complet des 9 onglets
dépendants a confirmé que **3 sources** sont réellement utilisées :
`entete_or`, `entete_pieces` (via `Regroupement_Concession_APV`, pour le
Magasin) et `v_sf_account` (pour `Encours à date`) — un filtre à ce
classeur-là devrait inclure les 3, si jamais appliqué (pas fait à ce jour,
ce classeur reste sur l'import complet non filtré).

**`Prix/Remises forcées`** (classeur externe, mélange Atelier/Magasin dans
une seule requête BigQuery) — **corrigé le 2026-09-25**, diagnostic
initial révisé : `e.Regroupement_Concession_APV` n'est **pas** un champ
groupé (vérifié en BigQuery — pour Dijon il vaut exactement la même
chose que `e.Concession`/`eo.Concession`, ex. "Opel Dijon"), donc changer
de champ dans la requête n'aurait rien réglé. Le vrai bug était **côté
Sheet** : l'onglet `Prix/Remises forcés` avait déjà une colonne `Code
concession` avec un `RECHERCHEV`, mais elle pointait vers un onglet
`Mapping` renommé depuis en `Mapping concessions` — la référence était
orpheline, et comme le `VLOOKUP` était enveloppé dans un `IFERROR(...;
$A2)`, l'échec était avalé silencieusement et retombait sur la valeur
brute (même famille de bug que le `#REF!` `Encours à date`/`Objectif
APV` ci-dessus : onglet source renommé, référence externe cassée).
Corrigé en remplaçant `Mapping!$C:$D` par `'Mapping concessions'!$C:$D`
dans la formule, et le fallback silencieux par `"MAPPING MANQUANT: "&$A2`
pour rendre visible tout futur cas de mapping manquant. Vérifié sur les
~1000 lignes de l'extrait du jour : 0 `MAPPING MANQUANT`, regroupements
multi-marques corrects (`Opel Dijon`/`Fiat Dijon` → `OPELFIAT_DIJON`,
`Nissan Belfort`/`Renault Belfort`/`Renault Montbéliard` →
`RENNIS_BELFORT_MONT`, etc.).

## 3. Onglets construits (2026-09-11)

- **`Analyse Globale`** — 1 ligne par code concession canonique (liste
  dynamique auto-étalée), toutes les colonnes du tableau récapitulatif
  d'origine (§ historique ci-dessous) + nouvelles :
  - Encours : `Nb OR en cours`, `Valeur encours MO+PR`, 3 tranches d'ancienneté
    (90-180j / 180-365j / +365j) en nombre **et** en valeur, `Dépréciation des
    encours`.
  - Nouveau 2026-09-11 : **`Encours en jours de CA`** (`Valeur encours MO+PR`
    ÷ CA Atelier moyen journalier des 6 derniers mois **complets**, calculé
    depuis `Historique CA mensuel ateliers`) + alerte 3 paliers (20j
    surveillance / 30j alerte / 40j critique — calibré sur données réelles,
    médiane groupe ≈ 10j, P90 ≈ 29j).
- **`Encours prioritaires`** — top 5 par code concession des OR en cours de
  plus de 30 jours, triés par score (`Montant_MO_PR_Encours__c` × ancienneté).
  Colonnes : Code concession, N° OR, Immatriculation, Ancienneté, Montant MO
  encours, Montant PR encours, Valeur totale OR, Dépréciation (colonne Score
  masquée, sert uniquement au tri).
- **`Analyse pièces J-1`** — Atelier + Magasin combinés (`Canal` en 1ʳᵉ
  colonne), ventes à perte (`Prix vente net < PAMP`), filtré `Quantité > 0`
  (exclut les lignes de retour/correction — décision : les garder visibles
  individuellement plutôt que de tenter une détection de paires
  facturé/avoirisé, jugée plus fragile) et `Facture_avoirisee/Avoir <> 1`.
  **Étendu le 2026-09-23** (réceptionnaire, nom client, canal de vente,
  catégorie client, prix brut, remises, marge % — voir §11 pour le détail
  complet, la formule tenue à jour a évolué par rapport à cette
  description d'origine).
- **`Efficience OR trop élevé`** — OR en cession interne (`Est_interne=1`)
  dont l'efficience dépasse 105% (seuil recalibré depuis 110%, `Référentiel
  métier`). Construit en `QUERY` + `FILTER` séparés (pas de `HAVING` — voir
  piège Sheets §4).
- **`Taux remise MO/PR interne élevé`** — OR dont le taux de remise (canal
  CLIENT, catégorie Particuliers uniquement — les autres catégories
  faussaient la calibration) dépasse 15% (MO) ou 20% (PR interne). Seuils
  calibrés sur P90 réel du **ratio par OR** (32%/33%), volontairement
  redescendus à 15%/20% après clarification que le ratio agrégé € (~9-13%,
  cohérent avec Tableau) et le percentile par OR ne mesurent pas la même
  chose — voir §4.
- **`Objectif APV`** (nouveau, 2026-09-14) — extrait GRID simple depuis
  `hess-data.datamart_apres_vente.objectifs_apv` (pas de souci volumétrique,
  ~1800 lignes/an groupe entier), filtré `Annee_objectif >=
  EXTRACT(YEAR FROM CURRENT_DATE())` (jamais d'année en dur, reste valable au
  changement d'année). 1 ligne par concession brute × mois — **pas déjà
  agrégé au code canonique** malgré le nom du champ source
  (`Regroupement_concessions_APV`), il faut le passer par `Mapping concession`
  comme les autres sources (voir §2.1 pour le cas Isuzu/Hyundai). Colonnes
  utilisées dans `Analyse Globale` : `Objectif_MO_mensuel`,
  `Objectif_PR_interne_mensuel`, `Objectif_PR_externe_mensuel` (le détail
  `Objectif_PR_interne_client_mensuel` et `Objectif_magasin_mensuel` — ce
  dernier = PR interne + PR externe — sont disponibles dans l'extrait mais
  pas exploités pour l'instant).
- **`Analyse Globale` — objectifs & réalisation (2026-09-14)** : 3 blocs
  ajoutés juste après chaque CA MTD correspondant (MO, PR interne, PR externe)
  — `Objectif [...] mensuel` (`SUMIFS` sur `Objectif APV` filtré
  code canonique + année/mois de `$B$1`) et `% Réalisation [...]` (`CA [...]
  MTD ÷ Objectif [...] mensuel` — comparaison au **plein mois**, pas de
  prorata au jour, même convention que le "% Avcmt" vu dans les rapports
  Tableau). A nécessité d'ajouter `CA PR Externe Net HT MTD`, qui n'existait
  pas encore.

## 4. Pièges Google Sheets rencontrés (à connaître avant de retoucher les formules)

1. **Séparateur de tableau `{...}` en locale FR** : `\` pour juxtaposer des
   colonnes (pas `,`, déjà pris par `;` comme séparateur d'arguments).
2. **`SUMIFS`/`AVERAGEIFS` n'acceptent pas une plage calculée** (ex.
   `$C:$C+$D:$D`) comme argument de plage — il faut une vraie référence, ou
   scinder en deux appels et additionner les résultats après coup.
3. **`QUERY` ne supporte pas bien `having` combiné à une expression calculée**
   (`sum(x)/sum(y)`) sur une plage Sheets — `PARSE_ERROR`. Solution : `QUERY`
   sans `having`, puis `FILTER` séparé sur le résultat.
4. **`IFERROR(...;"")` casse les comparaisons `>seuil`** : un texte est
   toujours "supérieur" à un nombre en Sheets, donc une cellule vide-texte
   passe à tort un test `>0,15`. Toujours utiliser `IFERROR(...;0)` quand le
   résultat sert ensuite de condition de comparaison.
5. **Une formule matricielle (`SORT`/`UNIQUE`/`FILTER`) ne s'étale pas si les
   cellules en dessous contiennent déjà quelque chose** — vider toute la
   plage cible avant de coller, pas juste la cellule d'ancrage.
6. **`INDEX(plage; 0; {1,2,3})` pour sélectionner des colonnes n'est pas
   fiable** dans Google Sheets (contrairement à Excel) — préférer garder
   toutes les colonnes et masquer celles à ne pas afficher.
7. **Réorganiser des colonnes est sûr par glisser-déposer natif** (sélectionner
   les colonnes par leur lettre, glisser jusqu'à la ligne bleue d'insertion) —
   Sheets réajuste alors automatiquement toutes les références de formules.
   Attention : ce n'est vrai que pour les formules natives à la feuille (ex.
   `Analyse Globale`) — ce n'est **pas** comparable au risque de décalage vu
   sur les onglets d'extraction BigQuery (§ historique), où c'est la *requête*
   qui change de forme, pas une action Sheets qui sait réajuster les refs.
8. **Un même texte peut avoir besoin de résoudre vers 2 codes canoniques
   différents selon le domaine source** (ex. Isuzu Châlons : APV vs
   commerce/stock) — voir §2.1 pour la solution (clé composée
   `Source||Valeur` + `INDEX/MATCH`, pas un `VLOOKUP` à plat).

## 5. Limites de lecture côté outillage Claude

- L'outil `gws` (voir `CADRAGE.md` §3) peut échouer à lire un onglet précis
  sans message d'erreur explicite (renvoie du contenu non lié, ex. un artefact
  d'interface `"Toutes les colonnes"`) sur des onglets volumineux/filtrés —
  observé sur `Détail facturation atelier journalière` et `Historique CA par
  atelier`. **Cause identifiée (2026-09-11)** : les onglets GRID alimentés par
  formules dépendant d'un onglet source DATA_SOURCE ne se recalculent
  côté serveur Google que lorsqu'un humain a le fichier ouvert (ou déclenche
  un rafraîchissement) — `gws`/l'API lit l'état calculé en mémoire, qui peut
  être resté "vide" si personne n'a rouvert le fichier récemment. Se fier à
  une capture d'écran de l'utilisateur, ou lui demander de rouvrir/rafraîchir
  l'onglet puis relire.
  **Résolu (2026-09-17)** : actualisation programmée configurée sur le
  classeur (Google Sheets → onglet DATA_SOURCE → "Plus" à côté d'Actualiser
  → "Options d'actualisation" → "Actualisation programmée") à **11h00**,
  calée avec une marge de sécurité d'1h après la remontée des sources APV
  dans BigQuery confirmée par le service data (entre 9h et 10h). Un seul
  réglage pour tout le classeur (s'applique à tous les onglets DATA_SOURCE).
  Attention : la programmation tourne sous le compte de qui l'a configurée
  et se met en pause si quelqu'un d'autre modifie la source de données —
  à reprendre en rééditant/sauvegardant si ça arrive.
- **Lire un onglet DATA_SOURCE directement (pas son extrait GRID) échoue**
  avec `"Unable to parse range"` — normal, l'API `values.get` ne sait pas
  adresser ce type d'onglet par nom simple. Ne pas insister, lire l'extrait
  GRID correspondant à la place.
- **BigQuery : décalage de fraîcheur constaté sur `facturation_detaillee_or`**
  (2026-09-11) — la table peut avoir 1-2 jours de retard par rapport à
  `CURRENT_DATE()`. Toujours tester une nouvelle requête avec une date fixe
  connue avant de la basculer en `DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)`
  dynamique, sous peine d'extraire 0 ligne silencieusement (et d'écraser une
  extraction précédente qui fonctionnait).

## 6. Seuils calibrés (`Référentiel métier`, méthode P90 sur données réelles)

| Paramètre | Valeur | Base de calibration |
|---|---|---|
| Vieux encours (3 paliers) | 90j / 180j / 365j | validé, ancien |
| Efficience cession interne | remplacé par "Efficience OR trop élevé" | 105% (P... voir §3) |
| Productivité | 80% | validé, ancien |
| Encours jours CA — surveillance/alerte/critique | 20j / 30j / 40j | médiane ~10j, P90 ~29j, groupe entier |
| Taux remise MO client (Particuliers) | 15% | P90 réel = 32% côté par-OR, redescendu (voir §3) |
| Taux remise PR interne client (Particuliers) | 20% | P90 réel = 33% côté par-OR, redescendu |
| Écart % CA MO vs moyenne mobile | -30% (conservé) | distribution réelle (67 concessions) : P10 = -33%, P25 = -14,9%, médiane = +19,2% — le seuil actuel colle déjà quasi exactement au P10, le -50% proposé aurait été trop permissif |

**Abandonné (2026-09-14)** : alerte "Écart % CA PR Externe" — jamais
implémentée en réalité (en-tête sans formule), et la distribution réelle
(P10 = **-99,2%**, médiane +42%) montre que ce CA est bien trop volatil au
jour le jour (mi-journées, samedis) pour qu'un seuil en % soit pertinent.
Colonnes `Écart % CA PR Externe` et `Alerte écart CA PR Externe` supprimées
d'`Analyse Globale` ; `CA PR Externe moyenne mobile 4 sem.` conservée comme
simple repère, sans alerte associée. `Ratio remises/CA` générique (5%,
provisoire) reste non tranché — probablement obsolète, remplacé par les 2
lignes taux de remise ci-dessus, à confirmer/supprimer.

## 7. Historique — état du 2026-09-08 (obsolète, gardé pour mémoire)

Avant reconstruction, `Analyse Globale` n'existait que pour la plaque Renault
(13 concessions) avec les colonnes : `Date de référence`, `Nb OR clôturés J-1`,
`CA MO net HT J-1`, `CA moyenne mobile 4 sem.`, `Écart % CA`,
`Alerte écart CA`, `CA PR interne/Externe Net HT J-1`, `Écart % CA PR
Externe`, `Alerte écart CA PR Externe`, `Productivité/Efficience J-1`. Toute
cette section a été reconstruite et étendue depuis (§1-3).

## 8. Questions ouvertes

1. Pas encore de lecture orchestrateur ni de format de mail défini pour APV
   (contrairement à VO qui a une spec dédiée, `CADRAGE_VO.md`) — `Analyse
   Globale` est désormais jugé stable (objectifs branchés, seuils recalibrés),
   donc ce point peut être attaqué. Un mockup HTML illustratif a été construit
   et testé avec de vraies données (`Renault/Nissan Mulhouse`, 2026-09-09,
   voir `docs/mockup_email_apv.html`) pour discuter de la structure, mais la
   maquette/config finale du mail reste à trancher (icône de vigilance façon
   VO ? mail unique Atelier+Magasin ou séparé par destinataire ? sections à
   garder/retirer ?).
2. `Ratio remises/CA` générique (5%, provisoire, `Référentiel métier`) —
   probablement obsolète depuis les 2 seuils de taux de remise dédiés (§6), à
   confirmer/supprimer.
3. `Objectif_PR_interne_client_mensuel` et `Objectif_magasin_mensuel`
   (disponibles dans `Objectif APV` mais pas encore exploités) — voir si un
   usage se présente.
4. **Aucun indicateur sur le stock PR** (stock de pièces détachées en
   magasin) à ce stade — tout ce qui est construit couvre les *ventes* de
   pièces (Analyse pièces, Magasin/PR externe), pas le *stock* lui-même.
   Besoins exprimés (2026-09-14) :
   - **Alertes sur les niveaux de stock** (à définir : rupture / surstock).
   - **Stock dormant** (rotation très faible) et **stock mort** (aucun
     mouvement depuis longtemps) — distinction à formaliser (seuils
     d'ancienneté/rotation).
   - **Propositions de transfert de stock entre magasins**, pertinentes au
     regard des ventes de la référence concernée : détecter une référence
     dormante/morte dans un magasin alors qu'elle se vend régulièrement dans
     un autre, et suggérer un transfert plutôt qu'un rachat.

   Piste à explorer : `hess-data.datamart_apres_vente.stock_pr_categories`
   (référencé dans la description de `entete_pieces` comme table de
   jointure stock via `Magasin`), pas encore examinée — à vérifier si elle
   porte le niveau de stock par référence et par magasin, ou seulement des
   catégories agrégées.
5. **Chantier anomalies sur les forfaits (2026-09-14, détection n°1 en
   cours de construction — voir §9).** Trois détections identifiées :
   - **Forfaits en marge négative** — en cours, voir §9.
   - **Écarts de tarification d'un même type de forfait** (ex. "forfait
     freins") entre les différents ateliers d'une même **plaque** — pas
     commencé. La notion de plaque existe déjà côté `Objectif APV` (colonne
     `Plaque`, ex. "Plaque BMW", "Plaque Renault") mais pas encore dans
     `Mapping concession` / `Analyse Globale` (qui ne portent que le code
     canonique par site) ; à vérifier si un référentiel plaque ↔ code
     canonique existe déjà ailleurs avant d'en recréer un.
   - **Pièces incohérentes avec le type de forfait** dans lequel elles sont
     intégrées (ex. une pièce hors-sujet facturée dans un forfait donné) —
     pas commencé.

## 9. Anomalies forfaits — marge estimée (2026-09-18, en pause depuis le 2026-09-23)

**Contexte** : premier des 3 chantiers forfaits de §8 pt.5 attaqué — la
détection de forfaits en marge négative. Accord métier avec la BU APV : un
**coût MO estimé forfaitaire de 60€/heure** (pas le vrai coût de revient
horaire par concession) permet de calculer une marge estimée complète
(PR + MO), pas seulement PR comme envisagé initialement en §8 pt.5.

**Structure de données validée sur `facturation_detaillee_or`** (données
réelles, échantillons multiples) :
- Un forfait facturé produit 1 ligne "entête" (`Est_entete_forfait=1`,
  `Libelle_type_operation='Forfait'`) qui porte le **prix facturé réel**
  (`Montant_HT_facturation`) + N lignes "composition"
  (`Est_ligne_forfait=1`) qui décrivent ce qu'il contient
  (`Libelle_type_operation` = `Pièce`, `Main d'oeuvre`, `Sous traitance`,
  `Peinture`...), **toujours à `Montant_HT_facturation=0`** (le client ne
  paie pas ces lignes séparément). Pour les lignes `Pièce` :
  `PAMP_facturation` porte le coût réel. Pour les lignes `Main d'oeuvre` :
  `Quantite_facturation` porte les heures (pas de coût direct, d'où le taux
  60€/h estimé).
- **Bug corrigé (2026-09-18)** : `PAMP_facturation` est déjà le **coût
  total de la ligne** (quantité incluse), **pas un coût unitaire** — la
  première version de la requête le multipliait par `Quantite_facturation`,
  gonflant artificiellement `Cout_PR` (vérifié sur donnée réelle : la
  référence huile "0888083590FR" facturée à des quantités différentes
  7,5L/5,4L donne exactement le même ratio `PAMP/quantité` = 3,39€/L dans
  les deux cas, preuve que `PAMP_facturation` scale déjà avec la quantité).
  `Cout_PR` = simplement `Σ(PAMP_facturation)` des lignes Pièce, **sans**
  multiplier par `Quantite_facturation`.
- **Piège confirmé sur données réelles (2026-09-18)** :
  `Identifiant_groupe_forfait` n'est **pas unique seul** — il se répète
  entre OR différents (vérifié : plusieurs cas avec 2-3 OR distincts
  partageant le même identifiant sur 30 jours). La clé réelle d'un forfait
  est **`(id_ligne_entete, Identifiant_groupe_forfait)`** — jamais grouper
  sur `Identifiant_groupe_forfait` seul.
- **Piège classique confirmé (même famille que `Code_concession` vide en
  VO, cf. `CADRAGE_VO.md` §3)** : `Identifiant_groupe_forfait` peut être
  une **chaîne vide `''` plutôt que NULL** — un filtre `IS NOT NULL` seul
  laisse passer toutes les lignes hors-forfait (MO/PR facturées seules)
  regroupées à tort sous une fausse clé `''`. Toujours filtrer
  `Identifiant_groupe_forfait IS NOT NULL AND Identifiant_groupe_forfait != ''`.
- **Piège avoir confirmé sur données réelles (2026-09-18)** : `Facture_avoirisee`
  sur la ligne "Facture" originale ne suffit **pas** à exclure les
  corrections — l'`Avoir` associé est souvent émis à une **autre date**
  (logique : on ne peut pas créditer une vente avant qu'elle existe), donc
  hors de la fenêtre J-1 de la requête. Une ligne `Avoir` isolée dans la
  fenêtre (prix/quantités négatifs) produit un faux forfait en marge très
  négative si on ne filtre pas sur le type de document lui-même. Filtrer
  directement `Libelle_type_document = 'Facture'` (exclut les lignes
  `Avoir`), peu importe où se trouve leur facture d'origine.

**Formule retenue** :
```
Cout_PR        = Σ(PAMP_facturation) des lignes Pièce du forfait (deja le cout total, pas unitaire)
Heures_MO      = Σ(Quantite_facturation) des lignes Main d'oeuvre du forfait
Cout_MO_estime = Heures_MO × 60 (taux convenu avec la BU APV, stocké en
                 colonne à chaque ligne, pas en dur dans la requête, pour
                 rester correct si le taux est renégocié plus tard)
Marge_estimee  = Prix_forfait_HT (ligne entête) − Cout_PR − Cout_MO_estime
```

**Décision (2026-09-18, affinée deux fois le même jour) : aucun forfait
exclu du *calcul*** de la marge (y compris ceux facturés à 0€, gestes
commerciaux/garantie — décision initiale après vérification que ces cas
sont en réalité rares, 2,3% des forfaits réels un jour donné une fois le
piège de la clé vide corrigé ; l'hypothèse initiale de ">50% de gratuités"
reposait sur ce bug et était fausse).

**Seuil retenu pour le *résultat*/l'historique : taux de marge estimé <
10%** (`Marge_estimee / Prix_forfait_HT`), pas une marge brute en euros.
Relevé de 5% à 10% le 2026-09-23, décision prise en réunion — remplace le
seuil initial du 2026-09-18, une seule tranche (pas de niveaux de
sévérité). Choix initial motivé par calibrage sur données réelles (méthode
déjà utilisée pour les seuils VO Bloc 8, cf. `CADRAGE_VO.md` §11) —
distribution du taux de marge sur 30 jours (15 701 forfaits facturés) :

| Seuil taux de marge | % des forfaits en dessous |
|---|---|
| < 0% (négatif strict) | 4,5% |
| < 5% | ~7-9% (seuil initial du 2026-09-18) |
| < 10% | 8,9% (**seuil retenu depuis le 2026-09-23**) |
| < 20% | 17,9% |
| < 30% | 30,8% |

Médiane à 41,8%. **Garde-fou** :
un forfait à prix nul (0€) mais avec un coût réel (PR ou MO) n'a pas de
taux de marge défini (division par 0) — remonté quand même explicitement
(`Prix_forfait_HT <= 0 AND coût > 0`), sinon il échapperait au filtre.
Colonne `Taux_marge_estime_pct` ajoutée à l'extrait pour visibilité (vide
pour ce cas particulier, cohérent avec le taux non défini).

**Remises : déjà prises en compte, vérifié (2026-09-18)** — `Montant_HT_facturation`
de la ligne entête forfait est **net de remise**, pas le prix de liste brut.
Preuve sur données réelles : `Prix_unitaire_HT_facturation −
Remise_appliquee_montant_facturation = Montant_HT_facturation` exactement
(ex. 162,50 − 5,00 = 157,50), sur plusieurs échantillons. `Prix_forfait_HT`
(donc `Marge_estimee`) reflète donc bien le prix réellement facturé au
client, pas un prix théorique avant négociation commerciale.

**Volumétrie validée (recalculée après correction du bug PAMP ci-dessus)** :
~750 forfaits/jour groupe entier (hors piège clé vide), dont ~**5%** en
marge négative (39 sur 717 forfaits facturés à un prix non nul, échantillon
du 2026-09-08) — cohérent avec un taux d'anomalie "rare et notable" (à
comparer aux 3-5% ciblés pour les anomalies VO). Le périmètre retenu ici
reste l'**historisation complète**, pas une simple alerte : pas de seuil de
sélectivité à caler pour l'instant, mais ce taux confirme que le signal
"marge négative" restera lisible dans l'historique (pas noyé dans du bruit).
Exemple réel (2026-09-08) : forfait "carrosserie" (Opel Saint-Dizier) sans
pièce (`Cout_PR=0`), 4,25h de MO facturé 200€ mais coûtant 255€ estimé
(4,25 × 60€) → marge ≈ **-55€**, un cas typique où le forfait est sous-tarifé
par rapport au temps de main-d'œuvre réellement nécessaire, pas un problème
de pièces.

**Architecture retenue** — nouveau Sheet dédié `Anomalies forfaits` (créé
par Corentin, `docs.google.com/spreadsheets/d/1T_BKjedX0yH7ENq4Z_88OWlGnBUu6RSez5ohLb0YscU`),
séparé du fichier principal `Rapport quotidien APV` (déjà à 27 onglets) :
- Onglet **`Extrait J-1`** : connecteur BigQuery natif Sheets, requête
  [`docs/sql/marge_forfaits_j1_extract.sql`](sql/marge_forfaits_j1_extract.sql)
  (J-1 strict, pas de fenêtre glissante) — actualisation programmée à
  **11h00**, même calage que le reste du classeur APV (données APV dispo
  9h-10h, cf. §5). Colonnes (texte/contexte d'abord, clés techniques
  ensuite, données numériques regroupées à la fin, demande explicite de
  Corentin) : `Date_reference, Concession, Societe, Numero_OR_DMS,
  Nom_client, Canal_imputation, Canal_categorie_client, Receptionnaire,
  Code_intervention, Libelle_forfait, id_ligne_entete,
  Identifiant_groupe_forfait, Detail_pieces, Prix_forfait_HT,
  Taux_remise_forfait_pct, Cout_PR, Heures_MO, Taux_horaire_MO_estime,
  Cout_MO_estime, Marge_estimee, Taux_marge_estime_pct` (`Receptionnaire` et
  `Taux_remise_forfait_pct` ajoutés le 2026-09-23, ainsi qu'un filtre
  `Est_interne = 0` au WHERE — exclut les OR internes/cessions).
  `Detail_pieces` liste les pièces du forfait (nom + référence + quantité +
  PAMP, via `Libelle_detail_operation`/`Reference_ecran` sur les lignes
  `Pièce`). `Canal_imputation` = `Libelle_type_imputation` (niveau ligne,
  ex. CLIENT/GARANTIE/ASSURANCES/CESSION), `Canal_categorie_client` =
  `Categorie_client` (niveau OR, ex. Particuliers/Flottes/Loueurs/MRA/
  Primocar) — les deux gardés, ce sont deux dimensions différentes.
  `Nom_client` vient de `clients.Nom_prenom` via `CRC_client_facture`
  (donnée nominative, table `clients` labellisée "données personnelles"
  côté BigQuery).
- Onglet **`Extrait J-1 (grid)`** (ajouté le 2026-09-18) : `Extrait J-1` est
  un onglet DATA_SOURCE (connecteur BigQuery), pas une grille de cellules
  classique — même limite déjà documentée en §5 pour les autres
  connecteurs du classeur (illisible directement par l'API Sheets/`gws`,
  et pareil pour Apps Script `getDataRange()`). Onglet intermédiaire qui
  matérialise le résultat en vraies cellules via
  `=QUERY('Extrait J-1'!A:S, "select *", 1)` en `A1` — c'est cet onglet-là
  que lit le script Apps Script, pas le connecteur brut.
- Onglet **`Historique`** : accumule les lignes de `Extrait J-1 (grid)` jour après
  jour. Un connecteur BigQuery natif **remplace** le contenu à chaque
  actualisation (ne peut pas s'auto-accumuler) — alimenté par un **Apps
  Script** ([`docs/apps-script/historique_forfaits_append.gs`](../apps-script/historique_forfaits_append.gs),
  déclencheur temporel quotidien vers 11h30, après l'actualisation du
  connecteur), avec déduplication par la clé `(Date_reference,
  id_ligne_entete, Identifiant_groupe_forfait)` pour rester rejouable sans
  risque.
- **Piste envisagée puis écartée pour l'instant** : une table BigQuery
  dédiée alimentée par une requête planifiée — écartée car Claude/`gws` n'a
  que des **droits de lecture** sur le projet BigQuery `hess-data`
  (`bigquery.tables.create` refusé, testé et confirmé sur tous les datasets
  du projet), et la solution Sheet+Apps Script répond au besoin sans droits
  supplémentaires. Scripts
  [`docs/sql/historique_marge_forfaits_create_table.sql`](sql/historique_marge_forfaits_create_table.sql)
  et [`_daily_refresh.sql`](sql/historique_marge_forfaits_daily_refresh.sql)
  conservés dans le repo si le volume dépasse un jour la limite Connected
  Sheets (~5M cellules) et qu'il faut y revenir.

**Statut (2026-09-23) : en production.** Le pipeline `Extrait J-1` →
`Extrait J-1 - Marges<5%` (extrait natif Sheets, pas la formule `QUERY`
initialement envisagée) → `Historique` tourne quotidiennement, historique
alimenté depuis le 2026-09-18 sans erreur signalée. Colonnes enrichies en
cours de route (ajoutées directement dans le connecteur par Corentin,
resynchronisées dans `docs/sql/marge_forfaits_j1_extract.sql` le
2026-09-23) : `Receptionnaire` (juste après `Categorie_client`) et
`Taux_remise_forfait_pct` (juste après `Prix_forfait_HT`) ; filtre
additionnel `e.Est_interne = 0` (exclut les OR internes).

**Transcodification concession ajoutée (2026-09-23)** : le classeur
`Anomalies forfaits` étant séparé du classeur principal, la colonne
`Concession` des flux forfaits (marges et pièces suspectes) remontait le
nom brut (`entete_or.Concession`), pas le code canonique. Résolu via un
`IMPORTRANGE` de `Mapping concession` + `INDEX/EQUIV` ligne par ligne (pas
en `ARRAYFORMULA` — piège rencontré : ne se vectorise pas, répète le
résultat de la 1ʳᵉ ligne partout). Détail complet :
[`docs/sheets-formulas/transco_concession_anomalies_forfaits.txt`](../sheets-formulas/transco_concession_anomalies_forfaits.txt).

**Point clarifié (2026-09-23), pas un bug** : certains forfaits ressortent
avec `Prix_forfait_HT = 0` alors que la facture affiche un prix — normal,
`Montant_HT_facturation` (utilisé pour `Prix_forfait_HT`) est **net de
remise** ; quand la remise appliquée est de 100% (geste commercial forcé,
`Remise_forcee = 1`), le prix net est bien 0€ même si le prix de liste
affiché sur la facture est non nul. Confirmé sur données réelles le
2026-09-23 (tous les cas échantillonnés avaient
`Remise_appliquee_pourcentage_facturation = 100`). C'est justement à ça que
sert la colonne `Taux_remise_forfait_pct` : elle rend ce cas visible dans
le Sheet plutôt que de le laisser passer pour une anomalie de calcul.

## 10. Forfaits pièces suspectes — détection n°3 (2026-09-2x, en pause depuis le 2026-09-23)

**Contexte** : reprend la détection n°3 identifiée en §8 pt.5 ("pièces
incohérentes avec le type de forfait"), reformulée par Corentin comme une
question de fraude potentielle : *repérer une pièce chère et inhabituelle
facturée dans un forfait qui n'a rien à voir avec elle*. Construit dans une
session Claude Chat séparée (pas Claude Code) pendant une indisponibilité
temporaire de l'outil, sans accès à `gws` ni au repo — d'où la
resynchronisation faite ici a posteriori (2026-09-23).

**Méthode** (requête complète :
[`docs/sql/forfaits_pieces_suspectes.sql`](sql/forfaits_pieces_suspectes.sql)) :
1. **Classification en `famille`** par mots-clés (regex) sur le libellé du
   forfait : `REVISION_ENTRETIEN`, `PNEUS`, `FREINAGE`, `CLIMATISATION`,
   `DISTRIBUTION`, `BATTERIE`, `EMBRAYAGE`, `SUSPENSION`. **Limite connue** :
   un forfait qui ne matche aucun mot-clé est ignoré (`famille` NULL) — la
   détection ne couvre donc pas tous les types de forfaits (ex.
   carrosserie, contrôles divers, forfaits génériques).
2. **Baseline historique** : pour chaque couple (famille, libellé de
   pièce), nombre d'occurrences sur tout l'historique **avant J-3** (depuis
   2025-01-01) — construit la distribution normale de ce qui compose
   habituellement chaque famille de forfait.
3. **Fenêtre d'analyse** : J-3 à aujourd'hui (plus large que le J-1 strict
   du flux marges, cf. §9).
4. **Filtre "suspect"** — double critère : occurrence baseline **≤ 2**
   (jamais/quasi jamais vue pour cette famille) **ET** coût de la pièce
   (`PAMP_facturation`) **≥ 150€** (seuil de matérialité, pour ne pas noyer
   le signal dans des pièces rares mais bon marché).

**Même piège clé composite** que le flux marges : toujours grouper par
`(id_ligne_entete, Identifiant_groupe_forfait)`, jamais
`Identifiant_groupe_forfait` seul (§9).

**Architecture** : connecteur BigQuery `Forfaits pièces suspectes`
(DATA_SOURCE) → extrait natif Sheets `Forfaits suspects` (GRID) → historisé
par une fonction Apps Script **séparée** (`historiserForfaitsSuspects`,
[`docs/apps-script/historique_forfaits_append.gs`](../apps-script/historique_forfaits_append.gs)),
avec son propre déclencheur temporel indépendant de celui du flux marges
(pour ne pas risquer de casser un flux qui tournait déjà). **Différence de
clé de dédoublonnage** par rapport au flux marges : inclut
`Reference_ecran` en plus de `(date_doc, id_ligne_entete,
Identifiant_groupe_forfait)` — plusieurs pièces suspectes peuvent coexister
sur un même forfait, sinon la 2ᵉ serait prise pour un doublon de la 1ʳᵉ.

**Statut (2026-09-23)** : en observation, aucune ligne historisée pour
l'instant — **normal, pas un bug** : le filtre (rareté ≤ 2 + coût ≥ 150€)
est volontairement strict, la plupart des jours ne remontent aucun cas.
Pas encore de recul sur le volume réel pour juger si le seuil doit être
ajusté.

**Point technique à surveiller** : contrairement au flux marges (extrait
natif intercalé), `historiserForfaitsSuspects` lit **directement** l'onglet
DATA_SOURCE `Forfaits pièces suspectes` sans extrait intermédiaire. Ça
fonctionne à ce jour (pas d'erreur remontée), mais si des erreurs de
lecture apparaissent un jour dans *Exécutions* (Apps Script), appliquer le
même correctif que pour `Extrait J-1` (extrait natif ou `QUERY`).

## 11. Analyse pièces J-1 — refonte (2026-09-23)

**Contexte** : le bloc `Analyse pièces` d'origine (§3) remontait les pièces
vendues à perte tous canaux confondus, sans distinction client/garantie/
cession ni infos contextuelles. Étendu par Corentin pour ne garder que les
vraies ventes externes et ajouter le contexte nécessaire à l'investigation
(qui a vendu, à qui, à quel prix par rapport au brut).

**Requête/formule complètes** :
[`docs/sql/magasin_detail_journalier.sql`](sql/magasin_detail_journalier.sql)
(connecteur `Magasin`, modifié) et
[`docs/sheets-formulas/analyse_pieces_j1.txt`](../sheets-formulas/analyse_pieces_j1.txt)
(formule `Analyse pièces J-1`, avec le détail des colonnes sources).

**Changements côté connecteur `Magasin`** : ajout de `Nom_client` (jointure
`entete_pieces.CRC_client` → `clients.Nom_prenom`, même table que côté
Atelier pour un format cohérent) ; retrait de `Famille_technique`
(inutilisée) — nombre de colonnes inchangé, donc la colonne `Code
concession` (formule Sheet à droite du connecteur) ne se décale pas.

**Changements de filtre** (décision Corentin, 2026-09-23) — objectif :
ventes externes uniquement, hors intragroupe :
- Atelier : `Affectation = "CLIENT"` **et** `Libelle_type_imputation <>
  "FACTURE INTRA GROUPE ATELIER"` **et** `Categorie_client` pas dans
  `("Intra-groupe sauf Primocar", "Inter sites")`. **Piège découvert en
  vérifiant sur données réelles** : `Affectation="CLIENT"` seul ne suffit
  pas à exclure l'intragroupe — `FACTURE INTRA GROUPE ATELIER` (133 lignes
  sur l'échantillon testé) et `Categorie_client="Intra-groupe sauf
  Primocar"` (109 lignes) s'y cachent tous les deux.
- Magasin : pas de notion "CLIENT uniquement" séparée (pas de champ
  `Affectation` côté Magasin) — exclusion directe de `Categorie_client`
  dans `("Cessions internes - interservices", "Intra-Groupe Renault",
  "Inter sites", "Intra-groupe sauf Primocar")`. `Administration` et
  `Personnel Groupe` gardés comme clients externes (décision explicite,
  pas des catégories intragroupe au sens strict).

**Nouvelles colonnes** (contexte : `Réceptionnaire`/`Nom_Magasinier`,
`Canal de vente` = `Affectation` — vide côté Magasin, `Catégorie client`,
`Nom client` ; numérique, en fin de liste par convention du projet :
`Quantité, Prix brut, Remise montant, Remise %, Prix net, PAMP, Marge €,
Marge %, Remise forcée, Prix forcé`).

**Pièges de champs corrigés en cours de route** :
- `PAMP_facturation` (Atelier) et `Prix_brut_ligne`/`Remise_ligne`
  (Magasin) sont déjà des **totaux de ligne**, pas des valeurs unitaires
  (même piège que documenté pour le chantier forfaits, §9) — contrairement
  à `Prix_unitaire_HT_facturation` (Atelier), qui lui est **bien unitaire**
  (vérifié sur données réelles : `unitaire × quantité − remise = montant
  facturé`, exact).
- **Format de pourcentage non homogène (bug corrigé)** : `Remise_appliquee_
  pourcentage_facturation` (Atelier) est nativement en **points de %**
  (ex. `10.0` = 10%). Les pourcentages calculés côté Magasin (`Remise_ligne
  / Prix_brut_ligne`) et la Marge % (les deux côtés) donnaient au contraire
  une fraction décimale (`0.10`) — corrigé en multipliant ces calculs par
  100, pour que toute la feuille reste sur la même échelle.

**Vérifié avant la refonte** : aucun autre onglet du classeur ne référence
`Analyse pièces` dans ses formules (scan complet des 14 autres onglets
GRID en mode formule, pas juste en valeurs) — le changement de structure
ne casse rien ailleurs.

## 12. Formalisation du mail APV — cadrage (2026-09-24)

**Contexte** : reprise du point ouvert en §8 pt.1. Décision de Corentin de
**construire une version indépendante** (pas calquée sur le mockup
`docs/mockup_email_apv.html` existant ni sur les choix faits par Quentin
pour le mail VN) puis de confronter les deux versions ensuite. Les mockups
de travail eux-mêmes (avec données réelles nominatives) ne sont **pas
versionnés dans le repo** — seules les règles ci-dessous le sont.

### 12.1 Un seul mail, deux départements visuellement séparés

**Un seul mail** envoyé à la fois au responsable Atelier et au responsable
Magasin (pas deux mails séparés) — décidé après avoir constaté que
plusieurs sources de données mélangent déjà les deux canaux (`Analyse
pièces J-1`, `Prix/Remises forcées`), rendant une scission propre du
contenu difficile. Un vrai destinataire Magasin existe (`Contact` du
classeur `Prix/Remises forcées`, colonne `Responsable Magasin`), mais n'est
**pas encore renseigné** dans le Référentiel Concession officiel (seul
`Atelier` y figure à ce jour, cf. §4 de `CADRAGE.md`) — à faire séparément.

À l'intérieur du mail, séparation visuelle claire : une bande de couleur
+ titre `ATELIER` / `MAGASIN` devant chaque groupe de contenu, et **deux
icônes de vigilance indépendantes** (une par département, pas une icône
globale unique comme pour VO).

### 12.2 Synthèse IA : toujours en haut, vue d'ensemble sans détail

Contrairement au principe VO (§3 de `CADRAGE.md`, qui cite des dossiers
précis), la synthèse APV se place **tout en haut du mail**, avant même les
KPI, et donne un **état des lieux global** des deux départements — **sans
numéro d'OR ni détail de dossier**. Le détail nominatif vit dans les
sections narrées plus bas (§12.4) et dans le fichier Excel joint (§12.5).

### 12.3 KPI : fixes vs conditionnels

**KPI fixes** (tuiles chiffrées, sans narration, toujours affichés) :

| Atelier | Magasin |
|---|---|
| CA MO Net HT J-1 | CA PR Externe Net HT J-1 |
| CA MO Net HT MTD | CA PR Externe Net HT MTD |
| Objectif MO mensuel | Objectif PR externe mensuel |
| % Réalisation objectif MO | % Réalisation objectif PR externe |
| CA PR interne Net HT J-1 | Marge PR Externe |
| CA PR interne Net HT MTD | Taux marge % PR Externe |
| Objectif PR interne mensuel | |
| % Réalisation objectif PR interne | |
| Productivité J-1 | |

Toutes disponibles dans `Analyse Globale` (onglet du classeur principal).

**KPI conditionnels agrégés** (narrés, n'apparaissent que si le seuil est
franchi — Atelier uniquement, pas d'équivalent Magasin identifié à ce
jour) :

- **Efficience globale J-1** — à l'inverse de la cession interne, "plus
  haut mieux c'est" (comme Productivité). Alerte seulement si **trop
  bas** : **<80% = trop bas**, **80-90% = bas** (les deux mentionnés,
  intensité différente) ; au-dessus de 90%, rien affiché.
- **Encours en jours de CA** — seuils déjà calibrés (`Référentiel métier`,
  §6) : **20j = surveillance** (affiche le top 5 natif de `Encours
  prioritaires`, sans le retronquer) ; **30j = alerte** (ajoute la
  répartition des vieux encours par tranche d'ancienneté, nombre et
  valeur) ; **40j = critique** (précision maximale sur les encours,
  détail le plus complet possible).

### 12.4 Listes détail OR/pièce : envoyées intégralement, narrées

Principe général (généralisation validée par Corentin, 2026-09-24) : tout
ce qui est **déjà une liste d'anomalies qualifiées au niveau OR ou pièce**
est envoyé **intégralement** (jamais de "top N" tronqué) et **narré en
prose** (pas de tableau brut de chiffres sans explication) — parce que
chaque ligne qui en ressort est par construction un cas à signaler, pas un
volume à résumer :

- **Efficience cessions internes >105%** (Atelier, `Référentiel métier`)
  — seul le dépassement vers le haut compte, pas de seuil bas.
- **Taux de remise élevé** (Atelier, MO>15% ou PR interne>20%, canal
  CLIENT/Particuliers) — nuance de ton : c'est une **alerte à surveiller**
  pour le chef d'atelier, pas une anomalie au sens fraude, mais le
  traitement (envoi intégral, narré) reste identique.
- **Ventes à perte** (Atelier + Magasin, `Analyse pièces J-1`) — affichées
  en deux sous-listes séparées Atelier/Magasin plutôt qu'un tableau mixte,
  cohérent avec le principe de séparation visuelle (§12.1).
  **Précision (2026-09-25)** : ces tableaux doivent toujours inclure le
  **nom du client** et le **nom du réceptionnaire (Atelier) ou magasinier
  (Magasin)**, pas seulement référence/désignation/marge — l'opérationnel
  destinataire a besoin de savoir qui est concerné pour agir. Voir
  `CADRAGE.md` §6 pour la règle noms réels (mail/brouillon Gmail) vs
  anonymisés (fichiers commités sur GitHub).
- **Prix/Remises forcées** (`Prix/Remises forcées`, classeur dédié,
  contact : Corentin) — **filtré sur `type = Magasin` dans un premier
  temps** (PR externe) ; le PR interne Atelier viendra dans un second
  temps, pas prioritaire pour l'instant.
- **Anomalies forfaits** (Atelier) — reprend le chantier §9-10 : forfaits
  en marge estimée <10% + forfaits pièces suspectes, comme source de
  contenu pour cette section du mail (le chantier lui-même reste par
  ailleurs "en observation", cf. §9-10, mais son historique alimente déjà
  le mail dès qu'il y a du contenu).

### 12.5 Fichier Excel joint (nouveau, 2026-09-24)

En complément du mail (qui reste narratif/synthétique), un **fichier Excel
par concession** est joint, avec **un onglet par type d'anomalie** listé en
§12.4 (Ventes à perte, Anomalies forfaits, Remises forcées, Taux de
remise, Efficience cessions internes), reprenant les **mêmes colonnes que
dans les Sheets sources**, filtré sur la concession destinataire — pour
donner accès au détail complet à qui veut creuser, sans alourdir le corps
du mail.

## 13. Prochaines étapes

1. Construire un premier mockup complet du mail APV selon les règles du
   §12, avec de vraies données (en local, pas versionné — voir §12).
2. Confronter cette version avec le mail VN de Quentin une fois les deux
   prêtes.
3. Ajouter un destinataire "Magasin" dans le Référentiel Concession
   officiel (existe déjà dans `Prix/Remises forcées > Contact`, à
   reporter dans le Référentiel partagé).
4. Générer le fichier Excel joint (§12.5) — pas commencé.
5. Corriger le bug `#REF!` trouvé en production sur `Encours à date`
   (colonne V) et `Objectif APV` (colonne J) — voir §2.2, formules de
   correctif déjà données, pas encore appliquées dans le Sheet.
6. ~~Corriger la requête `Prix/Remises forcées` (champ Magasin, §2.2) et
   brancher sa transco une fois fait.~~ **fait (2026-09-25)** — voir §2.2,
   le bug était en réalité côté Sheet (référence orpheline vers l'onglet
   `Mapping` renommé), pas dans la requête BigQuery. Corrigé et vérifié.
5. Trancher le sort du seuil `Ratio remises/CA` générique.
6. Laisser tourner `Forfaits pièces suspectes` (détection n°3, §10) quelques
   semaines pour juger du volume réel et calibrer le seuil si besoin.
7. Détection n°2 (écarts de tarification entre ateliers d'une même Plaque)
   — pas commencée, référentiel Plaque ↔ code canonique toujours à
   vérifier (cf. §8 pt.5).
