# Fiche de composition — mail VO (niveau Service, une concession)

À lire avec `rapport/consignes_composition.md` (règles générales) et la maquette
`docs/mockup_email_vo.html`. Ne contient que ce qui est propre au VO. Lire chaque colonne
**par son nom d'en-tête** ; nombres au format français (virgule).

## 0. Lecture des faits — pièges

- Ignorer les lignes à code concession vide ou `" "` (ex. total « Groupe Hess ») et les lignes vides.
- **`vo_bloc7_sante_plaque` : ne pas l'utiliser** — Santé Plaque est exclu du mail Service,
  réservé au mail Plaque. (CADRAGE_VO §9, §14 pt.9)
- Onglets à tableaux côte à côte (`vo_bloc4_stock_detail`, `vo_bdc_ouverts`) : une ligne
  gardée peut mêler plusieurs concessions. Ne lire un tableau que sur les lignes où **sa
  propre** colonne code concession vaut la concession du mail.
- `Tendance_ventes_pct` (et `…_Plaque`) est un **ratio** : `0,49` = +49 %, `-0,21` = −21 %.
- Deux notions de « commande » : `vo_bloc2_offres` = offres **créées** dans la fenêtre et
  acceptées ; `vo_bloc9_commandes_facturations` = BDC par **date de confirmation**. Ne jamais
  les additionner ni les comparer ; le narratif Commandes se base sur le Bloc 9 seul. (CADRAGE_VO §4)
- Fenêtres : Bloc 3 = 7 jours glissants ; Bloc 8 = hier ; Blocs 4/5/6 = photo du jour.
  Bloc 8 vide un lundi = normal (ventes du dimanche).
- `Delai_median_livraison_j` vide (ex. BMW Motorrad) → « non disponible ».
- Jamais de référence de fichier, d'onglet ou de colonne dans le mail. (CADRAGE_VO §14 pt.5)

## 1. Ordre des sections (celui de la maquette)

En-tête (nom + météo) → 4 tuiles KPI → Synthèse → Leads VO → Offres VO & Facturations vs
Objectifs → Anomalies achat & reprise → Anomalies ventes → État du stock → Rotation &
couverture → Excès de stock — top 3 modèles → pied. (CADRAGE_VO §14 pt.11)

## 2. En-tête et tuiles KPI

- Bandeau : logo seul. Surtitre « Rapport quotidien · Véhicules d'Occasion », titre =
  `nom_concession` tel quel. (CADRAGE_VO §14 pts 1-2)
- Tuiles, dans l'ordre : **Leads reçus J-1** = `Leads_recus_J1` ; **Couverture stock** =
  `Couverture_mois` (1 décimale + « mois ») ; **Tendance ventes 30j** = `Tendance_ventes_pct`
  × 100, arrondi, signé (« +7% », « -21% », « 0% ») ; **Anomalies ouvertes** = nb de lignes
  Bloc 3 + nb de lignes Bloc 8 de la concession. (CADRAGE_VO §14 pt.3, §15)

## 3. Icône météo — score de vigilance

Score calculé à la composition (le Sheet ne le calcule pas), somme de 3 critères :

| Critère | Points |
|---|---|
| Anomalies ouvertes (tuile 4 : Bloc 3 sur 7 j + Bloc 8 d'hier) ≥ 6 | +2 (sinon 0) |
| Tendance ventes 30j ≥ 0 % / entre 0 et −5 % / entre −5 et −10 % / < −10 % | 0 / +1 / +2 / +3 |
| Couverture hors zone normale (`Couverture_mois` < 1,5 ou > 3 mois ; vide = non évalué, 0 pt) | +2 |

Bornes de la tendance : exactement −5 % compte dans le palier « entre −5 et −10 % » (+2) et
exactement −10 % dans « < −10 % » (+3). Zone normale de couverture décidée le 2026-10-06
(mêmes seuils que les actions du Bloc 7).

Score 0-1 `&#9728;` Soleil · 2-3 `&#9729;` Nuage · 4-5 `&#127783;` Pluie · 6+ `&#9928;` Orage.
- Pas de 5ᵉ icône. **Si `Ventes_VOP_moy_mensuelle` < 3 : aucune icône** (volume non significatif).
- `title` de la cellule, comme la maquette : « Score de vigilance X — anomalies ouvertes
  (N, +p pt), tendance ventes T% (+p pt), couverture C mois (+p pt). » (CADRAGE_VO §15)

## 4. Synthèse (commentaire IA)

- Propre au VO : chercher les **recoupements entre blocs** (véhicule en anomalie d'achat
  encore sans prix/photo au stock ; modèle en excès et vendu à perte…) et transformer les
  tendances en risques actionnables, sans recopier les chiffres des blocs.
- Le Bloc 9 (objectifs) n'y remonte que s'il est significatif, jugé sur le rythme des 7
  derniers jours face au rythme nécessaire (`Reste à faire / jour ouvré`), pas sur le seul
  taux d'atteinte. (CADRAGE_VO §13, §14 pt.11)

## 5. Leads VO — `vo_bloc1_leads`

Reçus J-1 `Leads_recus_J1` · Reçus 7j `Leads_recus_7j` · Non traités J-1
`Leads_non_traites_J1` · Non traités 7j `Leads_non_traites_7j`. Toujours affiché. (CADRAGE_VO §3)

## 6. Offres VO & Facturations vs Objectifs — `vo_bloc2_offres` + `vo_bloc9_commandes_facturations`

Une seule section (fusion Bloc 2 + Bloc 9). (CADRAGE_VO §4, §11, §14 pt.11)
- **Compteurs** (Bloc 2), « valeur hier (valeur 7j) » : **Offres VOP acceptées** (et non
  « commandes », pour ne pas les confondre avec les commandes du Bloc 9)
  `Commandes_VOP_acceptees_J1` (`…_7j`), Offres refusées `Offres_refusees_J1` (`…_7j`),
  Reprises acceptées `Reprises_acceptees_J1` (`…_7j`).
- **Narratif (commentaire IA)** depuis la ligne concession du Bloc 9, Commandes puis
  Facturations : niveau = Mois à date vs Mois à date N-1 (%), rythme = 7 jours vs Moy. hebdo
  4 sem. Comparer à la Plaque **seulement** si une ligne total Plaque est dans les faits.
- **Tableau** Commandes / Facturations (colonnes préfixées `Cde – …` / `Fact – …`) : MTD
  (`Mois à date`), Objectif (`Objectif mois`), % (`Taux atteinte %`, à l'unité), Rythme 7j/sem.
  (« `7 jours` / `Moy. hebdo 4 sem.` », arrondis). Ne pas afficher Manque à date ni Projection.
- **Tendance** (`… – Tendance`) = pilule à côté du nom du flux, pas une colonne ; **mot
  seul, sans flèche** (les flèches Unicode ne passent pas dans tous les clients mail), comme
  au VN : Hausse, Baisse, Accélère, Ralentit, Stable, Nouveau, Volume faible. Hausse / Accélère : fond `#E4F1EB`, texte `#2E7D5F` ; Baisse
  / Ralentit : fond `#F6EADA`, texte `#C1793A` ; Stable / Nouveau / Volume trop
  faible : fond `#F8F6F0`, texte `#8A8474`.
- Ligne italique : « Reste à faire : X commandes/jour ouvré et Y facturations/jour ouvré pour
  atteindre l'objectif du mois » (`Reste à faire / jour ouvré`) ; vide ou 0 = objectif atteint.
- Pas de ligne Bloc 9 (Bâle, BMW Motorrad exclus) → tableau « non disponible ».

## 7. Anomalies achat & reprise — `vo_bloc3_anomalies_achat`

- Toutes les lignes de la concession (déjà filtrées : note ≥ 4, 7 jours glissants).
- Tableau au style « Anomalies ventes » : Véhicule (`Immatriculation` monospace +
  `Numero_achat`), Date (`Date_achat`), Anomalie (`Type_anomalie`). **Ne pas afficher la note.**
- Tri `Note_criticite` décroissante, puis `Date_achat` décroissante ; > 5 lignes : top 5 +
  « +N autres anomalies ».
- Vide → « Rien à signaler — aucune anomalie détectée sur les 7 derniers jours glissants. »
- (CADRAGE_VO §5, §10, §14 pt.6)

## 8. Anomalies ventes — `vo_bloc8_anomalies_ventes`

- Sous-titre « Hier · N dossier(s) ». Tableau : Véhicule (`Immatriculation` monospace +
  `Marque` `Modele`), Marge (`Marge_vehicule` signée en € ; `#2E7D5F` gras si positive,
  `#C1793A` gras si négative), Anomalie (`Type_anomalie` + « détention Nj » de `Duree_detention_j`).
- Motifs (déjà calculés, ne pas recalculer) : Marge négative < −1 000 €, Marge élevée
  > 4 000 €, Détention longue > 180 j (ces trois hors canal Primocar) ; Écart FRE significatif
  > 500 € ; Facturation Marchand non autorisée (hors `PRIMO_*`). Motifs cumulables (« + »).
- Tri : **valeur absolue** de `Marge_vehicule` décroissante (−6 000 € avant +4 900 €), puis
  `Date_vente` décroissante ; > 5 :
  top 5 + « +N autres anomalies ».
- Vide → « Rien à signaler — aucune anomalie sur les ventes d'hier. » (CADRAGE_VO §10, §14 pt.10)

## 9. État du stock — `vo_bloc4_stock_synthese`, `vo_bloc4_stock_detail`, `vo_bdc_ouverts`

- Sous-titre « Photo du jour · véhicules ST/CL/IM ». Compteurs : Stock ST `Stock_ST`, Stock CL
  `Stock_CL`, Stock IM `Stock_IM` ; Portefeuille livraison `Portefeuille_livraison`.
  **Aucune mention de « CL en retard »** (ni compteur, ni liste, ni « détail non disponible ») :
  retiré complètement le 2026-10-06, un nouveau bloc plus fiable viendra plus tard.
- **Véhicules à corriger** (détail : Sans prix, Sans destination, Sans photo, Jamais publié ;
  la dernière colonne de chaque tableau = **jours en stock** malgré son nom) : une ligne par
  immatriculation = immat (monospace) + modèle + « — » catégories (« sans photo, jamais
  publié »), jours à droite ; tri jours décroissants, 5 lignes max.
- Ligne italique : « Sans prix (`Sans_prix_nb`) · sans destination (`Sans_destination_nb`) ·
  sans photo (`Sans_photo_nb`) / jamais publié (`Jamais_publie_nb`) ».
- **Bons de commande ouverts les plus anciens (N au total)** — `vo_bdc_ouverts` (BDC signés
  depuis plus de 15 jours, véhicule toujours en cours de livraison) : lignes `Code_concession`
  = la concession, tri `Ancienneté_j` décroissante, 5 max, immat (monospace) + `modele` +
  **nom du vendeur `proprietaire` (affiché, décidé le 2026-10-06)** + « Nj » ; N = `Nb BDC VO`
  (ligne où `Concession` = la concession). Aucun BDC → omettre la sous-liste.
  (CADRAGE_VO §11.1)

## 10. Rotation & couverture — `vo_bloc5_couverture`

- Sous-titre « Moyenne lissée sur 90 jours · comparaison 30j vs 30j précédents ».
- Tableau Concession | « Plaque <nom> » : Ventes moy. mensuelle (`Ventes_VOP_moy_mensuelle`,
  arrondi), Couverture (`Couverture_mois`, 1 décimale + « mois »), Tendance 30j
  (`Tendance_ventes_pct`, ratio → % signé, vert gras si > 0), Délai médian livraison
  (`Delai_median_livraison_j`, « j ») ; colonne Plaque = mêmes noms suffixés `_Plaque`, lus tels quels.
- Une phrase italique (commentaire IA) situant la concession face à la Plaque. (CADRAGE_VO §7, §14 pt.8)

## 11. Excès de stock — top 3 modèles — `vo_bloc6_exces_stock`

- Sous-titre « Stock vs ventes moyennes lissées · seuil d'excès ≥ 3 ».
- Lignes de la concession avec `Exces` ≥ 3, tri `Exces` décroissant, 3 premiers rangs ;
  ex æquo sur une même ligne (« A / B (ex æquo) »).
- Ligne : rang, `Famille` en gras + `Energie` — « stock `Stock`, ventes `Ventes_moy` »
  (arrondi), excès à droite (`#C1793A`). Aucune ligne ≥ 3 → « Rien à signaler ». (CADRAGE_VO §8)

## 12. Pied

Pied de la maquette (« HESS Automobile · Rapport généré automatiquement… ») ; ne pas recopier
sa ligne « [ENVOI TEST] Renault Strasbourg… ».
