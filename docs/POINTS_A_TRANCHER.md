# Points à trancher — fiches de règles condensées (2026-10-06)

Depuis le 2026-10-06, Claude ne lit plus les cadrages complets pour composer les mails :
il lit des fiches condensées, `rapport/regles/<type>.md` (voir `docs/WORKFLOW.md` §4).
En les rédigeant, on a relevé des endroits où le cadrage et la maquette se contredisent,
ou que rien ne tranche. **Chaque fiche contient déjà un choix provisoire** (indiqué
ci-dessous) : les mails partent avec ce choix tant que le point n'est pas tranché.

Pour trancher : corriger la fiche concernée (et le cadrage si la décision est
durable), puis cocher le point ici.

## VN — `rapport/regles/vn.md` (Quentin)

- [x] **Ordre des blocs.** *Décidé 2026-10-06 : Leads → Cde/Fact → Anomalies ventes → stock
  (ordre de la maquette).*
- [x] **Tuiles KPI.** *Décidé 2026-10-06 : Leads, tendance Commandes, tendance Facturations,
  Anomalies. Tendances en mot seul, sans flèche (les flèches Unicode ne passent pas dans
  tous les clients mail).*
- [x] **Barème météo VN.** *Décidé 2026-10-06 : barème de la maquette validé (« brouillon »
  retiré) ; la couverture ne compte pas ; pas d'icône sous 3 ventes moyennes par mois.*
- [x] **% en rouge dans le tableau Cde/Fact.** *Décidé 2026-10-06 : rouge si la marque est en
  retard sur l'avancement du mois (`Manque à date` < 0), dimanches exclus.*
- [x] **Fenêtre des anomalies.** *Décidé 2026-10-06 : 5 derniers jours (texte de la maquette
  corrigé).*
- [x] **Tri des anomalies.** *Décidé 2026-10-06 : pire marge d'abord (ordre du Sheet).*
- [x] **Comparaison Plaque dans le mail Service.** *Décidé 2026-10-06 : ni comparaison ni
  mention (réservée au mail Directeur).*
- [x] **Couleur de la couverture.** *Décidé 2026-10-06 : aucune.*
- [x] **Stock de la rotation.** *Décidé 2026-10-06 : calcul conservé tel quel.*
- [x] **Lignes d'excès à modèle harmonisé vide.** *Décidé 2026-10-06 : mapping complété ;
  les quelques véhicules restants à modèle vide sont jugés non significatifs. Ne pas les
  présenter comme un modèle.*
- [x] **Seuil « marge fortement négative » hors BMW.** *Décidé 2026-10-06 : 0 € de marge
  véhicule, formule du Sheet conservée telle quelle.*
- [x] **Règle « à vérifier ».** *Décidé 2026-10-06 : marge positive entre 0 et 200 €, sans
  aide au châssis (la formulation « ≤ −500 € » est supprimée).*

## VO — `rapport/regles/vo.md` (Quentin)

- [x] **Comparaison Plaque dans Rotation & couverture.** *Décidé 2026-10-06 : gardée dans le
  mail Service VO (cadrage + maquette).*
- [x] **Liste « CL en retard ».** *Décidé 2026-10-06 : retirée complètement (ni compteur ni
  liste). Un nouveau bloc plus fiable sera ajouté après retour du service Data.*
- [x] **Nom du vendeur dans `BDC Ouvert`.** *Décidé 2026-10-06 : affiché.*
- [x] **Critère couverture du score météo.** *Décidé 2026-10-06 : zone normale = 1,5 à 3 mois
  (seuils du Bloc 7), +2 points hors zone ; l'Orage devient atteignable.*
- [x] **Bornes de tendance** à exactement −5 % et −10 %. *Décidé 2026-10-06 : palier le plus
  sévère (−5 % = +2, −10 % = +3).*
- [x] **Commandes vs Plaque.** *Décidé 2026-10-06 : comparaison seulement si la ligne total
  Plaque est présente.*
- [x] **Tri des anomalies de vente « par montant ».** *Décidé 2026-10-06 : valeur absolue de
  la marge.*
- [x] **Tableau Anomalies achat.** *Décidé 2026-10-06 : colonnes et top 5 du bloc Anomalies
  ventes, sans la note.*
- [x] **Deux « commandes » dans la même section.** *Décidé 2026-10-06 : les deux, sans les
  additionner ; libellés distincts (« offres acceptées » / « commandes »).*
- [x] **Libellés des pastilles de tendance.** *Décidé 2026-10-06 : mot seul abrégé sans flèche,
  comme au VN.*
- [x] **Ligne total de `BLOC 2_1`.** *Décidé 2026-10-06 : gardée (niveau siège).*

## Directeur et Plaque — `rapport/regles/directeur.md`, `plaque.md`

- [ ] **Icône APV du mail Directeur** : une seule mini-carte pour deux icônes (Atelier,
  Magasin). *Provisoire : la plus défavorable des deux.*
- [ ] **Mini-carte d'un service dont le bloc est omis.** *Provisoire : carte gardée avec
  son icône et une ligne neutre.*
- [ ] **Malfaçons « significatives » au niveau Directeur.** *Provisoire : ≥ 150 € hier, ou
  > 4 % du CA MO du mois à partir du 10 (seuils de la météo Atelier).*
- [ ] **Remises forcées dans le mail Plaque** : pas de total dans `Plaque APV`.
  *Provisoire : simple compteur par concession, si présent dans les faits.*
- [ ] **Maquette Plaque à mettre à jour** : pas encore de colonnes malfaçons (la fiche
  décrit « Malf. hier », « Malf. mois », « % CA MO »), noms de concession abrégés à la
  ville alors que les consignes imposent les noms du Référentiel, jargon (« FATIGUÉ »,
  « côté Sheet »).

## APV — `rapport/regles/apv.md` (Corentin)

- [x] **Signaux du barème Atelier sans colonne actuelle dans `Analyse Globale`** — réglé le
  2026-10-06 : colonnes ajoutées par Corentin (`DATA_MAP_APV.md` §2.1), fiche mise à jour :
  - efficience cession interne J-1 sur la journée entière (ancienne AX) —
    *provisoire : 0 pt* ;
  - alerte écart CA PR interne (ancienne AY) — *provisoire : écart % PR interne (V)
    < −30 %* ;
  - écart / alerte CA PR externe (anciennes BA/BB) — *provisoire : (BC − BD) ÷ BD
    < −30 %* ;
  - valeur des pièces magasin vendues à perte J-1 (ancienne AZ) — *provisoire : somme
    des marges négatives des lignes Magasin de la liste des ventes à perte.*
- [x] **Paliers « pièces à perte 100-250 € » et « forfaits −50 à −200 € »** : **total du
  jour** (Corentin, 2026-10-06).
- [x] **Unité de l'écart marge PR interne vs mix** (AE) : affiché en %, « −6 % » = −6 points
  (vérifié le 2026-10-06).
- [ ] **Encours sous 20 j de CA** : §12.3 dit « Rien à signaler », le mail du 30/09
  montrait quand même le top 5. *Provisoire : §12.3.*
- [x] **Maquette APV à aligner sur la fiche** — *non retenu (Corentin, 2026-10-06) : la fiche fait foi, la maquette reste en l'état* : n° OR cité dans la synthèse, ventes à perte
  limitées aux « 4 plus significatives » sans client ni réceptionnaire, pas de bloc
  remises forcées Magasin, pas de tuiles objectifs.

## Hors fiches

- [ ] **Isuzu Châlons** (plaque Hyundai) : pas de données VO ni APV propres. Ses mails VO
  et APV ne sont pas composés (test du 06/10), son mail VN part sans date de données. La
  retirer du Référentiel pour le rapport, ou la rattacher à Hyundai Châlons ?
