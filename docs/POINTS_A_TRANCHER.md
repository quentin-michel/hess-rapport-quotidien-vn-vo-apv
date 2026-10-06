# Points à trancher — fiches de règles condensées (2026-10-06)

Depuis le 2026-10-06, Claude ne lit plus les cadrages complets pour composer les mails :
il lit des fiches condensées, `rapport/regles/<type>.md` (voir `docs/WORKFLOW.md` §4).
En les rédigeant, on a relevé des endroits où le cadrage et la maquette se contredisent,
ou que rien ne tranche. **Chaque fiche contient déjà un choix provisoire** (indiqué
ci-dessous) : les mails partent avec ce choix tant que le point n'est pas tranché.

Pour trancher : corriger la fiche concernée (et le cadrage si la décision est
durable), puis cocher le point ici.

## VN — `rapport/regles/vn.md` (Quentin)

- [ ] **Ordre des blocs.** CADRAGE_VN §6 : Synthèse → Anomalies ventes → Commandes/
  Facturations → Leads. Maquette : Leads → Cde/Fact → Anomalies → Stock.
  *Provisoire : ordre de la maquette.*
- [ ] **Tuiles KPI.** §6 : Leads, Couverture, Stock âgé VN, Anomalies. Note du 24/09 et
  maquette : Leads, tendance Commandes, tendance Facturations, Anomalies.
  *Provisoire : maquette.*
- [ ] **Barème météo VN.** Aucun barème validé (CADRAGE §9 : non calculé dans les
  Sheets). *Provisoire : brouillon de la maquette* — +2 si ≥ 3 anomalies de vente ;
  0/+1/+2/+3 selon le retard sur l'objectif à date (pire de commandes et facturations,
  paliers 0 %, −5 %, −10 %), retard = `Manque à date` ÷ (`Mois à date` − `Manque à
  date`). Ouvert : la couverture de stock compte-t-elle ? Masquer l'icône à faible volume
  (comme le VO sous 3 ventes/mois) ?
- [ ] **% en rouge dans le tableau Cde/Fact.** La maquette passe en rouge sous 50 %,
  aucun seuil écrit. Plus logique : comparer à la part de jours ouvrés écoulés.
  *Provisoire : pas de règle de couleur.*
- [ ] **Fenêtre des anomalies.** Bloc 6 = 5 derniers jours, la maquette dit « sur J-1
  strict ». *Provisoire : « N dossiers sur les 5 derniers jours ».*
- [ ] **Tri des anomalies.** CADRAGE_VO §11 (appliqué au VN) : plus grosse perte
  d'abord ; la maquette met +449 € avant −2 123 €. Pas de date de vente pour départager.
  *Provisoire : pire marge d'abord (ordre du Sheet).*
- [ ] **Comparaison Plaque dans le mail Service.** La maquette garde « Comparaison Plaque
  non disponible pour cet envoi test ». *Provisoire : ni comparaison ni mention.*
- [ ] **Couleur de la couverture.** Verte dans la maquette, aucune zone normale définie.
  *Provisoire : pas de couleur.*
- [ ] **Stock de la rotation.** La maquette prend Stock VN + Stock VD de P1, les ventes
  viennent du Bloc 4 (qui ignore les modèles vendus sans stock restant) : numérateur et
  dénominateur pas tout à fait sur le même périmètre.
- [ ] **Lignes d'excès à modèle harmonisé vide** (modèles non mappés, chiffres faux).
  *Provisoire : ne pas les présenter comme un modèle.* Masquer ou étiqueter ?
- [ ] **Seuil « marge fortement négative » hors BMW** (bug `$Z$1`) : le nombre
  d'anomalies peut être gonflé.
- [ ] **Règle « à vérifier »** : le cadrage écrit « marge faible négative (≤ −500 €) »,
  formulation étrange. *Provisoire : recopiée telle quelle.*

## VO — `rapport/regles/vo.md` (Quentin)

- [ ] **Comparaison Plaque dans Rotation & couverture.** CADRAGE_VO §14 pt.8 et la
  maquette l'affichent dans le mail Service ; la carte des données vérifiée (main,
  05/10) réserve ces colonnes au mail Directeur. *Provisoire : cadrage + maquette.*
- [ ] **Liste « CL en retard ».** Maquette et §14 pt.7 l'affichent, mais le tableau
  source a été retiré de `BLOC 4 Stock_P2`. *Provisoire : liste « Clients en attente de
  livraison » tirée de `BLOC 2_2 BDC Ouvert` (BDC signés depuis plus de 15 jours, top 5
  par ancienneté)* — mesure l'ancienneté depuis la signature, pas depuis la date de
  livraison demandée. À valider.
- [ ] **Nom du vendeur dans `BDC Ouvert`** : « à décider avant de l'afficher » selon le
  cadrage. *Provisoire : non affiché.*
- [ ] **Critère couverture du score météo** : « zone normale » jamais définie.
  *Provisoire : 0 pt, « non évalué ».* Conséquence : max réel 5, l'Orage (6+) est
  inatteignable.
- [ ] **Bornes de tendance** à exactement −5 % et −10 % : de quel côté ?
- [ ] **Commandes vs Plaque** : la maquette compare la concession à la Plaque, mais le
  mail de concession ne reçoit pas la ligne total Plaque. *Provisoire : comparaison
  seulement si la ligne est présente.*
- [ ] **Tri des anomalies de vente « par montant »** : lu comme la valeur absolue de la
  marge (−6 000 € avant +4 900 €). À confirmer.
- [ ] **Tableau Anomalies achat** : la maquette ne montre que le cas « Rien à signaler ».
  *Provisoire : colonnes et top 5 repris du bloc Anomalies ventes.*
- [ ] **Deux « commandes » dans la même section** (offres et Bloc 9). *Provisoire : les
  deux, sans les additionner ni les comparer.*
- [ ] **Libellés des pastilles de tendance** : la maquette abrège (« ↑ Hausse »), le
  Sheet dit « ↑ Hausse confirmée ». *Provisoire : libellé du Sheet ; couleur neutre pour
  Stable / Nouveau / Volume trop faible.*
- [ ] **Ligne total de `BLOC 2_1`** : le cadrage dit qu'il n'y en a pas, la carte vérifiée
  dit qu'elle est gardée volontairement. Sans effet sur le mail de concession.

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

- [ ] **Signaux du barème Atelier sans colonne actuelle dans `Analyse Globale`** :
  - efficience cession interne J-1 sur la journée entière (ancienne AX) —
    *provisoire : 0 pt* ;
  - alerte écart CA PR interne (ancienne AY) — *provisoire : écart % PR interne (V)
    < −30 %* ;
  - écart / alerte CA PR externe (anciennes BA/BB) — *provisoire : (BC − BD) ÷ BD
    < −30 %* ;
  - valeur des pièces magasin vendues à perte J-1 (ancienne AZ) — *provisoire : somme
    des marges négatives des lignes Magasin de la liste des ventes à perte.*
- [ ] **Paliers « pièces à perte 100-250 € » et « forfaits −50 à −200 € »** : par ligne ou
  total du jour ? *Provisoire : total du jour.*
- [ ] **Unité de l'écart marge PR interne vs mix (AD)** : fraction ou points ?
- [ ] **Encours sous 20 j de CA** : §12.3 dit « Rien à signaler », le mail du 30/09
  montrait quand même le top 5. *Provisoire : §12.3.*
- [ ] **Maquette APV à aligner sur la fiche** : n° OR cité dans la synthèse, ventes à perte
  limitées aux « 4 plus significatives » sans client ni réceptionnaire, pas de bloc
  remises forcées Magasin, pas de tuiles objectifs.

## Hors fiches

- [ ] **Isuzu Châlons** (plaque Hyundai) : pas de données VO ni APV propres. Ses mails VO
  et APV ne sont pas composés (test du 06/10), son mail VN part sans date de données. La
  retirer du Référentiel pour le rapport, ou la rattacher à Hyundai Châlons ?
