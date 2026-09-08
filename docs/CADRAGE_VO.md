# Cadrage — VO (Véhicules d'Occasion)

Voir [`CADRAGE.md`](CADRAGE.md) pour le cadrage transverse (objectif général,
architecture, destinataires, décisions communes aux 3 services).

**Statut : priorité de développement actuelle (2026-09-08).**

## 1. Source

**Rapport quotidien VO** (`1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU`).

État constaté le 2026-09-08 (11 tableaux inspectés) : **pas de couche "prêt à
publier"** — aucune valeur J-1, aucune colonne anomalie sur données calculées.
Seulement des flags qualitatifs isolés (`Marge négative`, `Analyse santé` type
SAIN/CORRECT, `Action recommandée`) répartis sur des tableaux différents :

1. Mapping source BigQuery → codes concession
2. Glossaire
3. Grille de notation des écarts Offre/ICAR (`Anomalie | Seuil définitif`,
   `Critère | Mesure | Paliers`)
4. Rapprochement ventes/livraisons non trouvées ICAR
5. Ventes par concession/plaque/date
6. Détail ventes VO avec flags (`numero_vente, concession, canal, marque,
   Famille, date_vente, kilométrage, date_mec, duree_detention, marge_vehicule,
   marge_vente, Marge négative, Marge élevée, Détention longue, Vente rapide,
   Résumé`)
7. Qualité du stock (`Code_Concession, Stock ST/CL/IM/PR, ST jamais publié,
   ST sans destination, ST sans prix, Âge moyen ST, ST >180j/>365j, PR >90/180/365j,
   CL Particulier en retard`)
8. Couverture (`Code_Concession, Stock ST, Ventes VOP 30j, Ventes VOP moyenne
   mensuelle 90j/3, Couverture`)
9. Transferts par concession (`Stock ST, Ventes moyenne mensuelle, Excès,
   Ancien ≥90j, A transférer, Besoin, Où transférer`)
10-11. Santé du stock par plaque puis groupe (`Âge moyen/médian, Différence,
   Analyse santé, Action recommandée`)

## 2. Spécification cible : `Spec_Mail_IA_ChefVentesVO_v3.docx`

Document de référence fourni par Quentin le 2026-09-08. Objectif : un mail par
concession au chef des ventes VO, résumant les points significatifs (leads,
offres, stock, ventes) avec une recommandation actionable.

**Pilote : Plaque Renault**, 9 concessions —
`REN_SAVERNE, REN_SELESTAT, REN_STLOUIS, REN_STRASBOURG, REN_WISSEMBOURG,
RENNIS_BELFORT_MONT, RENNIS_COLMAR, RENNIS_HAGUENAU, RENNIS_MULHOUSE` — c'est le
périmètre de **test** avant diffusion à l'ensemble du groupe. Mails envoyés
uniquement aux 2 adresses de test (Quentin, Corentin) pendant cette phase.

### 8 blocs de contenu (ordre = cycle de vie prospect/véhicule)

| # | Bloc | Fenêtre | Source(s) BigQuery | Correspondance Sheet actuelle |
|---|---|---|---|---|
| 1 | Leads VO | J-1 + 7j glissant | `v_sf_lead` | **Absente** |
| 2 | Offres VO / Reprises | J-1 + 7j glissant | `v_sf_quote` | **Absente** |
| 3 | Anomalies Achat/Reprise | 7j glissant (pas J-1) | `v_sf_achat` | Tableau 3 (grille de notation) — méthodologie présente, **liste quotidienne des dossiers notés ≥4 à vérifier** |
| 4 | Qualité du stock | Photo du jour | `v_sf_vehicule_stock` | Tableau 7 — correspond bien |
| 5 | Rotation-Couverture | 90j glissant /3 | `v_sf_vente` + `v_sf_quote` | Tableau 8 — présent, **"Tendance ventes" et "Délai médian livraison" à vérifier** |
| 6 | Excès de stock | Photo jour × 90j ventes | `v_sf_vehicule_stock` + `v_sf_vente`/`v_sf_vehicule` | Tableau 9 — correspond ("Où transférer" volontairement exclu du mail) |
| 7 | Contexte réseau (Santé Plaque) | — | dérivé du Bloc 6 | Tableaux 10-11 — correspond |
| 8 | Anomalies Ventes | J-1, VOP uniquement | `v_sf_vente` + `v_sf_achat` + `v_sf_quote` | Tableau 6 — présent pour marge/détention/vente rapide, **"Écart FRE significatif" à vérifier** |

Détail complet des champs/tables/filtres par bloc, grille de notation des
anomalies achat/reprise (critères écart date/km/prix/aides, paliers 0-10), et
l'exemple complet (Renault Mulhouse, données réelles telles que fournies à
l'IA) : voir le fichier `Spec_Mail_IA_ChefVentesVO_v3.docx` original (pas
reproduit ici in extenso pour éviter la duplication/désynchronisation — s'y
référer directement).

## 3. Décisions prises (2026-09-08)

- **Blocs 1 (Leads) et 2 (Offres/Reprises)** : construits par **Quentin/Corentin
  dans le Sheet VO** (mécanisme : Connected Sheets, l'extension native BigQuery
  de Google Sheets — même mécanisme que les blocs existants), pas par Claude
  (limite technique, voir `CADRAGE.md` §3).
- **Limites de données du spec, démarrage du prototype sans attendre leur
  résolution :**
  1. Filtre "hors buy-back" non résolu sur les offres de reprise (jointure
     immat, 30% de correspondance) — affiché sans ce filtre pour l'instant.
  2. Grilles de notation des anomalies achat/reprise provisoires (non validées
     Direction Financière).
  3. Distinction "petite maison" vs stock formel non clarifiée avec l'IT.
  4. **Dédup jointure vente↔offre non appliquée** (+23,5% de doublons mesurés)
     — à la différence des 3 points ci-dessus (arbitrages métier), celui-ci
     ressemble à un vrai bug de données : **le correctif (ROW_NUMBER PARTITION
     BY Vehicule_selectionne__c) devrait être appliqué dès le prototype**, pas
     seulement documenté comme limite. *(Point soulevé par Claude, à confirmer
     par Quentin/Corentin.)*
- **Règle explicite pour cette phase : Claude ne touche à aucun Google Sheet.**
  Quentin/Corentin construisent la couche "prêt à publier" + anomalies dans
  Rapport quotidien VO. Claude n'édite ni ne crée rien côté Sheets tant que ce
  n'est pas explicitement redemandé.

## 4. Questions ouvertes VO

1. **Emplacement exact des blocs une fois complétés** (onglet, plage) pour
   chacun des 8 blocs — à communiquer avant que Claude code la lecture.
2. Confirmation que les 4 limites de données listées en §3 sont bien traitées
   comme décidé (documentées vs corrigées pour le point 4).

## 5. Prochaines étapes

1. Quentin/Corentin construisent les 8 blocs dans Rapport quotidien VO
   (formules + Connected Sheets pour les blocs 1-2, structure sur le modèle du
   récapitulatif APV pour le reste).
2. Une fois prêt et l'emplacement communiqué : Claude branche la lecture, le
   commentaire IA et l'envoi, sur les 2 adresses de test, périmètre Plaque
   Renault uniquement.
3. Recette du pilote avant généralisation à VO sur tout le groupe.
