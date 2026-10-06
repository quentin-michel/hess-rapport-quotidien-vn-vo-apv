# Mail Plaque (type `plaque`)

Un mail par plaque, niveau 3 de diffusion, couvrant **toutes** les concessions de la
plaque : `concessions_plaque` (code → nom) dans les faits. Maquette :
`docs/mockup_email_plaque.html`. À lire avec `consignes_composition.md` et
`regles/commun.md`. Colonnes lues **par nom d'en-tête** (les lettres citées ne sont que
des repères, elles bougent ; les en-têtes cités reprennent DATA_MAP_APV/VN/VO :
rapprocher du libellé réel de `entetes`).

## 1. Principe et structure
Même logique que le mail Directeur (`directeur.md`) : synthèse IA en tête, blocs
**VN → VO → APV**, **bloc entier omis** si rien de significatif, positif comme négatif,
dossiers concrets cités, pas de jargon. En plus : **le détail par concession** dans chaque
bloc, pour repérer *quelle* concession est en cause.
1. En-tête : « Rapport quotidien · Synthèse Plaque », `nom_plaque`, « N concessions »,
   date des données.
2. **3 tuiles chiffrées** (pas d'icône météo à ce niveau) : VN commandes % objectif
   Plaque ; VO commandes % objectif Plaque ; anomalies ventes VN + VO du réseau.
3. **Synthèse IA — vue d'ensemble réseau** : un paragraphe par service ayant un signal
   (VN → VO → APV), 2 phrases max chacun, en nommant la ou les concessions en cause et les
   concentrations (« 8 des 13 dossiers à Mulhouse »).
4. Blocs : badges (concession la plus en retrait, nombre d'anomalies…) + paragraphe
   (2 phrases) + tableaux compacts par concession (§2-4) avec une ligne **Total Plaque**.

Tableaux : une ligne par concession de `concessions_plaque`, dans l'ordre des codes ; nom
du Référentiel tel quel ; donnée absente = « n.d. » (+ légende « n.d. = non disponible »).
Valeur la plus défavorable en `#B0413E` gras, la plus favorable en `#2E7D5F` gras. Petit
volume (objectif ou nb d'OR très faible) : astérisque + note « taux à lire avec prudence ».

(CADRAGE §8)

## 2. Bloc VN
**Tableau « Commandes & facturations vs objectif — par concession »** :
Concession | Cde % obj. | Fact % obj. | Anomalies.
- Source `vn_bloc2_commandes_facturations` (grain concession × marque + totaux Plaque) :
  % d'une concession = Σ « mois à date » ÷ Σ « objectif du mois » de ses lignes marque,
  par flux (jamais une moyenne de %). Total Plaque = ligne de total Plaque de l'onglet,
  sinon le même Σ/Σ sur toutes les concessions.
- BMW Motorrad : commandes déclaratives mensuelles, pas de détail jour (le noter si
  présent).
- Anomalies = nombre de dossiers de `vn_bloc6_anomalies_ventes` par code concession
  (fenêtre : **5 derniers jours**, à dire dans le texte). Citer le pire dossier (plus forte
  marge négative) : n° de dossier, modèle, concession, marge, aide éventuelle.

**Tableau « Rotation & couverture — par concession »** : Concession | Stock | Ventes moy. |
Couverture (mois).
- Source `vn_bloc4_couverture` (grain concession × marque × modèle) : par concession,
  **Σ Stock** et **Σ Ventes moy.** sur toutes ses lignes, couverture = Σ Stock ÷ Σ Ventes.
  Total Plaque = Σ des concessions, couverture recalculée. Ne pas sommer les colonnes
  « Plaque » (K/L/M), répétées sur chaque ligne.
- Une phrase au-dessus : extrêmes du réseau (couverture la plus basse / la plus haute).

(CADRAGE §8 ; CADRAGE_VN §2, §4, §5)

## 3. Bloc VO
**Tableau « Commandes & facturations vs objectif — par concession »** : mêmes colonnes
qu'en VN.
- Source `vo_bloc9_commandes_facturations` (1 ligne par concession, « Taux atteinte % »
  par flux ; ligne de total Plaque, pas de total groupe).
- Anomalies = nombre de lignes de `vo_bloc8_anomalies_ventes` par `Code_concession` (pas de
  `Code_Plaque` dans cet onglet : filtrer sur les codes de `concessions_plaque` ; fenêtre
  ~hier). Citer le pire dossier (immatriculation, modèle, concession, marge, durée de
  détention) et, s'il y en a, la marge élevée la plus forte en positif.

**Tableau « Rotation & couverture — par concession »** : Concession | Stock | Ventes moy. |
Couverture | Délai livr.
- Source `vo_bloc5_couverture`, lu tel quel : `Stock_ST`, `Ventes_VOP_moy_mensuelle`,
  `Couverture_mois`, `Delai_median_livraison_j`. Total Plaque = colonnes `*_Plaque`
  (`Stock_ST_Plaque`, `Ventes_VOP_moy_mensuelle_Plaque`, `Couverture_mois_Plaque`,
  `Delai_median_livraison_j_Plaque`). Délai vide pour BMW Motorrad : normal.
- Texte : extrêmes vs moyenne Plaque (couverture, délai de livraison, tendance
  `Tendance_ventes_pct` vs `Tendance_ventes_pct_Plaque` si marquante).

**Santé du stock réseau** (Bloc 7 — **réservé à ce mail**, exclu des mails Service) :
- Source `vo_bloc7_sante_plaque` (lignes de la plaque, grain famille × énergie) :
  `Analyse_santé`, `Action_recommandée`, `Stock`, `Exces`, `Age_moyen`, `Age_median`,
  `Couverture_brute`.
- Signaler les familles à stock vieillissant (diagnostic FATIGUÉ, CRITIQUE ou « purger
  anciennes ») avec stock/excès/âge médian et l'action recommandée, **en mots simples**
  (« stock vieillissant, à solder en priorité »), sans recopier les libellés du
  diagnostic ni dire « côté Sheet ».

(CADRAGE §8 ; CADRAGE_VO §7, §9, §10, §11)

## 4. Bloc APV
Sources : `apv_analyse_globale` (1 ligne par concession, « Code plaque » en A) pour les
lignes ; `apv_plaque` (onglet `Plaque APV`, ligne de la plaque) pour **Total Plaque**.

**Règle de niveau** : **compteurs de problèmes, pas de CA ni d'objectifs** (ni CA MO, ni CA
PR, ni % de réalisation, ni CA Magasin). **Exception (2026-10-06)** : malfaçons et gestes
commerciaux en **montant** (hier, cumul du mois) et en **% du CA MO du mois**.

**Totaux Plaque toujours pondérés** (Σ numérateurs ÷ Σ dénominateurs du réseau, lus dans
`Plaque APV`), **jamais une moyenne des % par concession**.

**Tableau « Signaux — par concession »** :

| Colonne mail | Par concession | Total Plaque (`Plaque APV`) |
|---|---|---|
| Effic. | `Analyse Globale` « Efficience J-1 » (AP) | « Efficience J-1 » (B) |
| Prod. | « Productivité J-1 » (AL) | « Productivité J-1 » (C) |
| Pièces- | nb lignes `apv_pieces_a_perte` (Atelier + Magasin) par « Code concession » | « Pièces client en marge négative » (G) |
| Forf.- | nb lignes `apv_forfaits_marge_faible` par « Code concession » | « Forfaits marge <10% » (H) |
| Enc.+90j | Σ des 3 tranches de vieux encours en nombre (90-180 j, 180-365 j, +365 j ; AV-AX) | « Encours +90j » (E) |
| Enc. jCA | « Encours en j de CA » (BC) + « Alerte encours » (BD) | « Encours en j de CA » (F) |
| Malf. hier | « Malfaçons J-1 » (K, €) | « Malfaçons J-1 » (K) |
| Malf. mois | « Malfaçons MTD » (R, €) | « Malfaçons MTD » (L) |
| % CA MO | « % Malfaçons MTD » (S) | « % Malfaçons MTD » (M, pondéré) |

- Seuils de mise en valeur : efficience < 80 % trop bas (rouge), 80-90 % bas ;
  productivité selon « Alerte productivité basse » ; encours en jours de CA 20 j
  surveillance (`#C1793A`), 30 j alerte et 40 j critique (rouge).
- Malfaçons : avant le 10 du mois (date des données), préciser que le % du mois est encore
  peu significatif. Le CA MO ne s'affiche jamais, il ne sert que de dénominateur.
- Très peu d'OR clos (« Nb OR clôturés J-1 ») : astérisque sur Effic./Prod. Légende sous le tableau (comme la maquette) : définitions courtes des colonnes et
  « Total Plaque calculé en pondéré, pas une moyenne simple des % ».

**Autres signaux réseau** (lignes badge + phrase) :
- OR à taux de remise MO/PR interne élevé : total « OR remise élevée » (`Plaque APV` I),
  concentrations par concession depuis `apv_remises_elevees`.
- OR en cession interne à efficience trop élevée (seuil 105 %) : total « OR efficience CI
  élevée » (J), concentrations et OR le plus marqué depuis `apv_efficience_ci` (onglet à
  2 tableaux côte à côte : n'en compter qu'un).
- Remises forcées : pas de total dans `Plaque APV` ; n'en parler que si les faits en
  contiennent (simple comptage par concession).

**Texte** : signaux les plus forts, concentrations (« 43 % des encours +90 j sur deux
concessions »), **signaux croisés** (ex. mêmes OR en pièces à perte et en remise élevée).

(CADRAGE §8 ; CADRAGE_APV §8 pt 5, §12.3, §15 ; DATA_MAP_APV §2.1, §4)
