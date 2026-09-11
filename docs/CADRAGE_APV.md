# Cadrage — APV (Après-Vente)

Voir [`CADRAGE.md`](CADRAGE.md) pour le cadrage transverse (objectif général,
architecture, destinataires, décisions communes aux 3 services).

**Statut : architecture reconstruite et étendue au groupe entier (2026-09-10/11)
— en avance sur le séquencement initial** (le cadrage global priorisait VO,
mais Corentin a repris et largement dépassé l'état "prêt côté données" du
2026-09-08 ci-dessous, qui est **obsolète**). Reste : rebrancher un dernier
seuil, nettoyer les onglets obsolètes, construire la lecture orchestrateur.

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
- **`Analyse pièces`** — Atelier + Magasin combinés (`Canal` en 1ʳᵉ colonne),
  ventes à perte (`Prix vente net < PAMP`), filtré `Quantité > 0` (exclut les
  lignes de retour/correction — décision : les garder visibles individuellement
  plutôt que de tenter une détection de paires facturé/avoirisé, jugée plus
  fragile) et `Facture_avoirisee/Avoir <> 1`.
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

## 5. Limites de lecture côté outillage Claude

- L'outil `gws` (voir `CADRAGE.md` §3) peut échouer à lire un onglet précis
  sans message d'erreur explicite (renvoie du contenu non lié, ex. un artefact
  d'interface `"Toutes les colonnes"`) sur des onglets volumineux/filtrés —
  observé sur `Détail facturation atelier journalière` et `Historique CA par
  atelier`. Dans ce cas, se fier à une capture d'écran de l'utilisateur plutôt
  qu'insister avec l'outil.
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

**Non tranché** : `Ratio remises/CA` générique (5%, provisoire — probablement
obsolète, remplacé par les 2 lignes ci-dessus, à confirmer/supprimer) et
`Écart CA vs moyenne mobile` (-30% actuel vs -50%+méthode médiane proposée).

## 7. Historique — état du 2026-09-08 (obsolète, gardé pour mémoire)

Avant reconstruction, `Analyse Globale` n'existait que pour la plaque Renault
(13 concessions) avec les colonnes : `Date de référence`, `Nb OR clôturés J-1`,
`CA MO net HT J-1`, `CA moyenne mobile 4 sem.`, `Écart % CA`,
`Alerte écart CA`, `CA PR interne/Externe Net HT J-1`, `Écart % CA PR
Externe`, `Alerte écart CA PR Externe`, `Productivité/Efficience J-1`. Toute
cette section a été reconstruite et étendue depuis (§1-3).

## 8. Questions ouvertes

1. **Nettoyage des onglets obsolètes** (`entete_or`, `Extrait entete_or`, et
   les anciens `Extrait facturation_detaillee`/`Extrait Temps facturé`/
   `Extrait temps passé`/`Extrait Magasin`/`Extrait encours` sur 35j, remplacés
   par l'architecture §1.2) — pas encore fait.
2. **Objectifs MO/PR interne/PR externe** (type "Obj MO M" / "% Avcmt MO M"
   vus dans les rapports Tableau) — dataset BigQuery `hess-data.budget` repéré
   mais pas encore exploré pour brancher ça dans `Analyse Globale`.
3. **`Écart CA vs moyenne mobile`** — seuil à recalibrer (voir §6).
4. Pas encore de lecture orchestrateur ni de format de mail défini pour APV
   (contrairement à VO qui a une spec dédiée, `CADRAGE_VO.md`) — à faire une
   fois `Analyse Globale` jugé stable.

## 9. Prochaines étapes

1. Reconcilier le seuil "Écart CA vs moyenne mobile".
2. Nettoyer les onglets obsolètes.
3. Explorer `hess-data.budget` pour les objectifs.
4. Définir le format du mail APV (contenu, ton, destinataires) — sur le
   modèle de la spec VO une fois ce point ouvert par les deux porteurs.
