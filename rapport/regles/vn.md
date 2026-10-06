# Règles de composition — mail VN (niveau Service, une concession)

Fiche condensée qui remplace `CADRAGE_VN.md` pour composer le mail. Les règles générales
(chiffres, date, HTML email-safe, largeur, objet, « Rien à signaler ») sont dans
`consignes_composition.md` et `CADRAGE.md` §3/§6 : non répétées ici.

## 0. Lecture des faits
- Colonnes lues **par nom d'en-tête** (noms réels ci-dessous). Ignorer toute ligne dont le
  code concession est vide ou vaut `" "`.
- Format français dans les faits : virgule décimale, % parfois en texte (`-9,39%`), dates
  `JJ/MM/AAAA`. Afficher `1 234`, `2,3`, `-2 123€` (espace insécable).
- S-LEASE, `Stock Plaque Renault`, Renault Saint-Avold, Fiat Saint-Etienne, Bâle : exclus
  volontairement. MINI n'a jamais d'anomalie de vente (exclusion voulue).
Source : DATA_MAP_VN §2-3, CADRAGE_VN §5.

## 1. Structure (ordre de la maquette `docs/mockup_email_vn.html`)
Header + titre (« Rapport quotidien · Véhicules Neufs », `nom_concession`, date des
données, icône météo §2) → 4 tuiles KPI §3 → Synthèse §4 → Leads VN §5 → Commandes &
Facturations vs Objectifs §6 → Anomalies ventes §7 → État du stock §8 → Rotation &
couverture §9 → Excès de stock top 3 §10 → Footer §11.
Source : ordre validé par Quentin le 2026-10-06 (= maquette).

## 2. Icône météo — score de vigilance VN (barème validé le 2026-10-06, calculé par Claude)
- La couverture de stock ne compte pas dans le score. **Pas d'icône** (ni mot) si les
  ventes moyennes mensuelles de la concession (somme des `Ventes moy` de `BLOC 4`, §9) sont
  < 3 : un score sur un volume trop faible serait trompeur.
- Anomalies ventes (nb de dossiers §7) ≥ 3 → +2, sinon 0.
- Retard vs objectif à date, **pire des 2 flux** (ligne `TOTAL` concession, §6) :
  ≥ 0 % → 0 ; 0 à -5 % → +1 ; -5 à -10 % → +2 ; < -10 % → +3.
  Retard % = `Manque à date` ÷ (`Mois à date` − `Manque à date`).
- Score → icône : 0-1 Soleil `&#9728;` ; 2-3 Nuage `&#9729;` ; 4-5 Pluie `&#127783;` ;
  6+ Orage `&#9928;`. Mot sous l'icône comme la maquette.
- `title` : « Score de vigilance X/5 — anomalies ventes (N, +p pt, seuil 3),
  retard commandes|facturations -x,x % vs objectif (+p pts). »
Source : maquette (tooltip), CADRAGE_VO §15.

## 3. Tuiles KPI (dans cet ordre)
| Tuile | Valeur |
|---|---|
| Leads hier | `Leads_recus_J1` (`vn_bloc1_leads`) |
| Commande · tendance | `Cde – Tendance`, ligne `TOTAL` concession (`vn_bloc2_commandes_facturations`) |
| Facturation · tendance | `Fact – Tendance`, même ligne |
| Anomalies signalées | nb de dossiers §7, rouge `#B0413E` si > 0 |
- Tendance Sheet → tuile, **mot seul, sans flèche** (les flèches Unicode ↑ ↓ ↗ ↘ → ne
  s'affichent pas dans tous les clients mail) : `↑ Hausse confirmée` → « Hausse » (vert
  `#2E7D5F`) ; `↓ Baisse confirmée` → « Baisse » (rouge) ; `↗ Accélère` → « Accélère »,
  `↘ Ralentit` → « Ralentit », `→ Stable` → « Stable », `Nouveau` (navy) ;
  `· Volume trop faible` → « Volume faible ».
- `title` de la tuile : niveau `Mois à date` vs `Mois à date N-1` (± %), rythme `7 jours`
  vs `Moy. hebdo 4 sem.` (%), puis « Tendance Sheet : <valeur brute> ».
Source : CADRAGE_VN §2 (formule Tendance), §6 (tuiles KPI).

## 4. Synthèse (spécificités VN, en plus de CADRAGE §3)
- Suivre le signal le plus fort, souvent la plus grosse perte §7 : citer le montant tel
  quel, le véhicule (immatriculation si renseignée, sinon VIN) et le contexte (détention,
  absence d'aide). 2e phrase possible sur Commandes/Facturations si l'écart à l'objectif
  ou à l'an dernier est fort (chiffre + comparaison, marques les plus en retard).
- **Jamais de causalité inventée** entre blocs qui partagent un modèle (excès de Clio ≠
  cause d'une perte sur une Clio) : au mieux « deux signaux distincts sur le même modèle ».
Source : CADRAGE_VN §6, CADRAGE §3 règle 9.

## 5. Leads VN — `vn_bloc1_leads` (`BLOC 1 Leads VN`)
- En ligne : Reçus hier `Leads_recus_J1`, Reçus 7 j `Leads_recus_7j`, Non traités hier
  `Leads_non_traites_J1`, Non traités 7 j `Leads_non_traites_7j`. Pas de ligne → « Rien
  à signaler ». Des non traités nombreux = affaires potentiellement perdues (synthèse).
Source : CADRAGE_VN §1.

## 6. Commandes & Facturations vs Objectifs — `vn_bloc2_commandes_facturations` (`BLOC 2`)
- En-têtes : `Plaque`, `Concession`, `Marque`, puis `Cde – …` / `Fact – …` : `J-1`,
  `7 jours`, `Moy. hebdo 4 sem.`, `Mois à date`, `Mois à date N-1`, `Objectif mois`,
  `Manque à date`, `Taux atteinte %`, `Projection fin de mois`, `Reste à faire / jour
  ouvré`, `Tendance`.
- `Concession` = code de la concession : `Marque = TOTAL` → totaux (paragraphe, note,
  tuiles, météo) ; autres marques → tableau. Ignorer la ligne à marque vide (tout à 0), les
  totaux plaque (`Concession = TOTAL`) et groupe (`Plaque` vide).
- Sous-titre « Mois à date ». Paragraphe IA (règles de la synthèse) : par flux, niveau vs
  an dernier (%), % de l'objectif du mois, marques les plus en retard / proches de la cible.
- Tableau par marque (alphabétique) : Marque | Cde MTD | Cde Obj. | Cde % | Fact MTD |
  Fact Obj. | Fact %. % = `Taux atteinte %` arrondi à l'entier, « — » si objectif = 0.
  Omettre une marque à 0 en MTD et en objectif sur les 2 flux. **% en rouge gras si la
  marque est en retard sur l'avancement du mois** : `Manque à date` < 0 pour ce flux
  (équivaut à `Taux atteinte %` < part des jours ouvrés écoulés, dimanches exclus, selon le
  calendrier du flux : Commandes lundi-samedi, Facturations lundi-vendredi). Sinon couleur
  normale.
- Note grise italique : « Reste à faire : x,x commandes/jour ouvré et y,y facturations/jour
  ouvré pour atteindre l'objectif du mois » (`Reste à faire / jour ouvré` de la ligne
  `TOTAL`, 1 décimale ; vide ou 0 = objectif atteint).
- **BMW Motorrad** : `Cde – Mois à date` = déclaratif mensuel, `J-1`/`7 jours` à 0 ne
  signifient pas « aucune activité ». Sur cette ligne seulement : note « suivi mensuel
  déclaratif, pas de détail jour/semaine ».
- Ne remontent pas : manque à date, projection, J-1, 7 jours, moy. hebdo.
Source : CADRAGE_VN §2, §6 (intégration Bloc 2, précision du 25/09, note BMW Motorrad).

## 7. Anomalies ventes — `vn_bloc6_anomalies_ventes` (`BLOC 6 - Anomalie Vente VN-VD`)
- En-têtes : `numero_dossier`, `vin`, `immatriculation`, `Code_concession`, `marque`,
  `modele`, `vn_vd`, `destination`, `marge_brute_vehicule_ht`, `marge_dossier_icar_ht`,
  `Durée de détention`, `Anomalie VD`, `A signaler`, `A vérifier`.
- 1 ligne = 1 dossier déjà classé par le Sheet (ventes des **5 derniers jours**, J-5 à
  J-1) : tout l'afficher, sans plancher en €. Sous-titre « N dossiers sur les 5 derniers
  jours ». Aucune ligne → « Rien à signaler ».
- Colonnes : VIN (monospace gras navy) | Véhicule = `modele` `vn_vd` · `destination` |
  Marge = `marge_brute_vehicule_ht` à l'euro, signée, vert si > 0, rouge si < 0 | Anomalie.
- Anomalie = texte de la colonne remplie **sans préfixe de catégorie** (« À corriger - »…),
  pas de pastille de statut. VD : ajouter « détention Nj ». Marge positive faible sans
  aide → « aide au châssis possible manquante ».
- `vin`/`modele` vides = véhicule non identifié, anomalie à part entière : afficher
  « véhicule non identifié » + `numero_dossier`.
- Tri : perte la plus forte d'abord (marge croissante, ordre du Sheet), marges positives
  ensuite. Plus de 5 dossiers : top 5 + « +N autres anomalies ».
- Logique du Sheet (pour comprendre, pas à recalculer) : perte couverte par le transfert de
  marge → non listé ; marge véhicule < 0 mais dossier > 0 → non listé ; VN à marge hors
  transfert < 0 → listé ; VD idem → listé avec la détention ; marge et dossier négatifs,
  avec ou sans aide → listé (seuil hors BMW : 0 € de marge véhicule, décidé le 2026-10-06 ;
  BMW : ≤ -1,5 % de marge) ; à vérifier = Particuliers, sans aide, hors BMW/MINI, marge positive entre 0
  et 200 €.
Source : CADRAGE_VN §5, §5.1, §6 (affichage) ; DATA_MAP_VN Bloc 6.

## 8. État du stock — `vn_bloc3_stock_synthese` + `vn_bloc3_stock_detail`
- Sous-titre « Photo du jour ». Compteurs (`BLOC 3 P1 Stock VN_VD`, clé `Code_Concession`) :
  `Stock VN`, `Stock VD`, `Stock âgé VN (+6 mois)`, `Stock âgé VD (+6 mois)`,
  `Contremarqué +90j`. Âgé = > 180 j depuis l'achat ; contremarqué = > 90 j depuis la
  commande client. Ligne absente → « Rien à signaler ».
- 3 mini-listes (`BLOC 3 P2 Stock VN_VD`, 3 tableaux côte à côte : `Code_concession`,
  `Numéro Stock`, `VIN`, `marque`, `modele`, puis jours dans `Stock âgé VN` / `Stock âgé VD`
  / `Contremarqué`) : « VN les plus anciens », « VD les plus anciens », « Contremarqués
  depuis le plus longtemps ». **3 lignes chacune**, jours décroissants : marque (gras
  monospace) + modèle, « Nj » à droite. Pas de seuil (les 3 plus anciens même sous 180/90 j) ;
  le P2 peut dépasser 5 lignes (ex æquo) : garder les 3 premiers. Liste vide → l'omettre.
Source : CADRAGE_VN §3, §6.

## 9. Rotation & couverture — `vn_bloc4_couverture` (`BLOC 4 Couverture VN`)
- Sous-titre « Stock total (VN+VD) ÷ ventes moyennes mensuelles, tous modèles confondus ».
- Tableau 1 colonne (nom de la concession) : Stock = `Stock VN` + `Stock VD` (§8) ; Ventes
  moy. mensuelle = somme des `Ventes moy` de la concession (ventes VN+VD 90 j ÷ 3,
  1 décimale) ; Couverture = Stock ÷ ventes, 1 décimale, « mois » (ventes 0 → « non
  calculable »). En-tête réel de couverture : `Couveture` (faute dans le Sheet).
- **Pas de comparaison Plaque** dans le mail Service (`Stock Plaque`, `Ventes moy. Plaque`,
  `Couverture Plaque` réservés au mail Directeur de plaque), ni de note à son sujet.
Source : CADRAGE_VN §4, §6 (décision de périmètre Bloc 4).

## 10. Excès de stock — top 3 modèles — `vn_bloc5_top3_exces` (`BLOC 5 TOP 3`)
- Sous-titre « Stock vs ventes moyennes sur 90 jours ». Lignes de la concession (déjà
  filtrées excès ≥ 12, 3 max), `Excès de stock` décroissant. Aucune → « Rien à signaler ».
- Podium : rang (pastille navy) | `Modèle harmonisé` en gras — « stock `Stock`, ventes
  `Ventes moy` (1 décimale) » | `Excès de stock` entier, orange `#C1793A`.
- `Modèle harmonisé` vide = modèles non référencés regroupés par marque, chiffre faux : ne
  pas le présenter comme un modèle.
Source : CADRAGE_VN §4 (seuil P90 = 12), DATA_MAP_VN Bloc 4.

## 11. Footer
« HESS Automobile · Rapport généré automatiquement, données BigQuery & Google Sheets »,
puis `nom_concession` · données du JJ/MM/AAAA. Pas de
mention « [ENVOI TEST] » ni « comparaison Plaque non incluse ».
