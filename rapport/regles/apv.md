# Fiche de composition — mail APV (niveau Service : Atelier + Magasin)

Complète `rapport/consignes_composition.md` et la maquette ; remplace `CADRAGE_APV.md`.

## 0. Lecture des faits

- Colonnes lues **par nom d'en-tête** (ligne 2 d'`Analyse Globale`, ligne 1 ailleurs). Les
  lettres entre parenthèses ci-dessous sont un repère au 06/10/2026 (après l'ajout des
  colonnes de signaux), jamais une clé. Les deux colonnes « Valeur pièces … à perte J-1 »
  sont en fin de bloc Magasin/Atelier ; si l'une manque dans les faits, sommer les Marge €
  du canal dans la liste `apv_pieces_a_perte`.
- Sources : `apv_analyse_globale` (1 ligne = la concession ; date de référence B1),
  `apv_encours_prioritaires`, `apv_pieces_a_perte`, `apv_efficience_ci`, `apv_remises_elevees`,
  `apv_malfacons_j1`, `apv_forfaits_marge_faible`, `apv_remises_forcees` (`apv_plaque` : inutile).
- **Listes détail intégrales** : chaque ligne est un cas qualifié ; jamais de « top N » ni de
  plancher en € (même −0,07 €) ; narrées en prose + tableau. (CADRAGE_APV §12.4, 2026-10-05)
- Pas de fichier Excel joint (§12.5, pas construit). Pièges : effet de mix (§3), début de mois (§2, §4).

## 1. Ordre du mail (CADRAGE_APV §12.1-12.2, maquette)

1. Bandeau HESS, titre « Rapport quotidien · Après-Vente », `nom_concession`, date des
   données ; **deux cartes météo indépendantes** : Atelier (gauche), Magasin (droite).
2. **Synthèse du jour** (encadré beige) : un paragraphe « Atelier : », un « Magasin : ».
   État des lieux global des deux départements, **sans n° d'OR, sans immatriculation, sans
   nom** (le détail vit plus bas). Mentionner les malfaçons d'hier et le cumul du mois.
3. Bande **ATELIER** : tuiles KPI → signaux conditionnels → Encours → Efficience cessions
   internes → Remises élevées → Anomalies forfaits → Malfaçons et gestes commerciaux.
4. Séparateur, bande **MAGASIN** : tuiles KPI → Remises/prix forcés → ligne RAS éventuelle.
5. Séparateur, **Ventes à perte du jour** : sous-liste Magasin puis sous-liste Atelier.
6. Pied de page navy de la maquette, sans les mentions « pilote » ni « anonymisé ».

## 2. ATELIER — tuiles KPI fixes (toujours affichées, sans narration) (§12.3)

Source `apv_analyse_globale`. Grille de 3 tuiles par ligne comme la maquette.

| Tuile | En-tête |
|---|---|
| CA MO Net HT J-1 / MTD | CA MO J-1 (D) / CA MO MTD (L) |
| Objectif MO mensuel / % Réal. | objectif MO mensuel (P) / % réalisation (Q) |
| CA PR interne J-1 / MTD | CA PR interne J-1 (T) / CA PR interne MTD (AF) |
| Objectif PR interne mensuel / % Réal. | objectif PR interne mensuel (AJ) / % réalisation (AK) |
| Productivité J-1 | productivité J-1 (AL) |
| Efficience globale J-1 | efficience J-1 (AP) — tuile comme la maquette |

- Objectifs (fixes au cadrage, absents de la maquette) : 2e ligne de la tuile % Réal.
- **% réalisation = CA MTD ÷ objectif du plein mois, sans prorata** : en début/milieu de
  mois un % bas est normal ; le commenter au regard du jour du mois, pas comme une alerte.
- Couleurs de valeur : rouge `#B0413E` défavorable, vert `#2E7D5F` favorable, navy neutre.

## 3. ATELIER — signaux conditionnels (narrés seulement si franchis) (§12.3, §12.6, §14)

Paragraphe court sous les tuiles, absent si aucun signal.
- **Efficience globale J-1** (AP) : < 80 % = trop bas ; 80-90 % = bas ; ≥ 90 % rien.
- **Écart CA** vs moyenne mobile 4 sem. : « Alerte écart CA » (G, MO) ou « Alerte écart CA
  PR interne » (W) = ALERTE.
- **Marge PR interne** : taux marge J-1 (AC) vs marge attendue au mix (AD), écart (AE,
  affiché en % : « −6 % » = −6 points) : ≤ −5 pts à signaler. **Règle effet de mix (§14)** : avant de commenter une marge PR
  interne basse ou en baisse, croiser avec % CA PR interne CLIENT/GARANTIE/CESSION J-1
  (X-Z) et MTD (AG-AI) (et MO : H-J, M-O). Si GARANTIE/CESSION pèsent nettement plus que
  d'habitude, c'est un effet de mix (marges de référence ≈ CLIENT 35 %, GARANTIE 6 %,
  CESSION 7 %) : le dire, ne pas présenter comme une dérive tarifaire. Ne jamais commenter
  une marge globale brute sans ce contexte.

## 4. ATELIER — blocs détail

**Encours** (`apv_analyse_globale` : encours en j de CA (BC), Alerte encours (BD) ;
`apv_encours_prioritaires`) (§12.3, §6)
- < 20 j de CA : « Rien à signaler » (citer le nombre de jours).
- 20-29 j **surveillance** : top 5 natif d'`Encours prioritaires` (OR > 30 j, tri par score),
  sans le retronquer : N° OR, Immat., Ancienneté, Valeur OR (+ Site si présent).
- 30-39 j **alerte** : + répartition des vieux encours par tranche 90-180 j / 180-365 j /
  +365 j, en nombre (AV-AX) et en valeur (AY-BA).
- ≥ 40 j **critique** : + détail maximal : nb OR en cours (AT), valeur (AU), dépréciation
  (BB), montants MO/PR et dépréciation par OR du top 5.
- Top 5 plafonné par construction : ne pas le présenter comme exhaustif.

**Efficience cessions internes > 105 %** (`apv_efficience_ci`, tableau d'affichage A:F
seulement, ignorer le tableau décimal I:N) (§12.4)
- Tous les OR, narrés : n° OR, mécanicien/réceptionnaire, temps facturé vs passé, efficience.
  Seul le dépassement vers le haut compte. Badge « N cas » (« critique » si très au-dessus).
  Citer aussi l'efficience cessions internes de la journée (AR) et du mois (AS).

**Remises élevées** (`apv_remises_elevees`) (§12.4, §3)
- OR CLIENT / Particuliers avec remise MO > 15 % ou PR interne > 20 %. Tous listés.
- Ton : **alerte à surveiller** pour le chef d'atelier, pas une fraude. Narration (cas les
  plus marqués) + tableau N° OR, Client, Réceptionnaire, Remise MO, Remise PR (valeur au-delà
  du seuil en rouge gras). N'entre pas dans le score météo.

**Anomalies forfaits** (`apv_forfaits_marge_faible`, forfaits à marge estimée < 10 %,
MO estimée 60 €/h) (§12.4, §9)
- Tous listés : N° OR (Numero_OR_DMS), Client, Forfait (Libelle_forfait), Prix
  (Prix_forfait_HT), Marge est. (Marge_estimee, rouge si < 0). Narrer le plus marqué.
- Si Date_reference ≠ date des données : titre « dernière donnée disponible : JJ/MM, pas de
  J-1 » et le dire dans la phrase.
- Prix 0 € avec Taux_remise_forfait_pct = 100 = geste forcé à 100 %, pas une erreur.
- « Forfaits pièces suspectes » : en pause, pas dans le mail.

**Malfaçons et gestes commerciaux** (`apv_malfacons_j1` ; `apv_analyse_globale` :
Malfaçons J-1 (K), Malfaçons MTD (R), % Malfaçons MTD (S)) (§15)
- Définition : cessions internes sur 10 fiches CI (malfaçon, geste commercial, réparation à
  charge de l'atelier, temps passé non facturé, opérations spéciales APV ; méca et carr).
  Montants nets HT, avoirs déduits.
- Phrase : montant d'hier et nb d'OR (OR DMS distincts), le cas le plus lourd (type, n° OR,
  immat., intervention résumée, montant), puis cumul du mois (R) et % du CA MO (S).
- Tableau, tous les OR d'hier, tri par montant décroissant : N° OR (Numero_OR_DMS), Immat.,
  Fiche (abrégée : « Malfaçon méca. », « Geste co. carr. »…), Intervention
  (Libelle_detail_intervention, raccourci si besoin), Réceptionnaire, Client, Montant
  (Montant_total). Badge « N OR · X € ».
- **Avant le 10 du mois** (jour de la date B1) : % MTD très volatil (un seul dossier sur
  peu de CA peut donner 50 %+) → l'afficher avec la réserve « début de mois, ratio peu
  significatif », ne pas l'alarmer.
- Pas de nb d'OR sur le mois (absent des faits) : cumul en € et % seulement. Jour sans cas : « Rien à signaler » en italique, suivi du cumul du mois s'il est non nul.

## 5. MAGASIN — tuiles KPI fixes (§12.3)

| Tuile | En-tête (`apv_analyse_globale`) |
|---|---|
| CA PR Externe J-1 / MTD | CA PR externe J-1 (BE) / CA PR externe MTD (BL) |
| Objectif PR ext. mensuel / % Réal. | objectif (BM) / % réalisation (BN) — même règle « plein mois » |
| Marge PR Externe J-1 / Taux marge | marge (BJ) / taux marge J-1 (BK) |
| Nb pièces vendues J-1 / % vendues à perte J-1 | nb pièces magasin vendues J-1 (BO) / % à perte (BP) |

- Taux marge PR Externe inclut l'Export (marge ≈ 100 %, PAMP vide) : optimiste si fort export.

## 6. MAGASIN — blocs

**Remises/prix forcés** (`apv_remises_forcees`, filtrer **type = Magasin** ; PR interne
Atelier non traité) (§12.4) : tous listés, narrés, avec client et magasinier/réceptionnaire.
Aucun cas : « Rien à signaler » en italique. Hors score.

## 7. Ventes à perte du jour (`apv_pieces_a_perte`, colonne Canal) (§12.4, §11)

- Ventes CLIENT hors intragroupe/inter-sites/Export, prix de vente net < PAMP, quantité > 0,
  hors avoirs. Deux sous-listes : **Magasin**, puis **Atelier**. Toutes les lignes.
- Colonnes obligatoires : N° OR (n° document côté Magasin), Référence, Désignation,
  **Nom du client**, **Réceptionnaire/Nom_Magasinier**, Marge € (rouge gras). Tri par Marge €.
- Intro Magasin : volume de contexte, ex. « 35 pièces vendues à perte sur 339 vendues, soit
  10,3 % » (BO, BP ; nb à perte = nb de lignes Magasin de la liste).
- Aucune ligne d'un canal : « Rien à signaler » pour ce canal.

## 8. Météo Atelier — barème de points (CADRAGE_APV §12.6, §15)

Score calculé au moment de la composition (pas de colonne score dans le Sheet).

| Signal | Mesure | Points |
|---|---|---|
| Encours en j de CA (BC) | 20-29 j / 30-39 j / ≥ 40 j | 1 / 2 / 4 |
| Écart CA = **max** (CA MO, CA PR interne) | « Alerte écart CA » (G) ou « Alerte écart CA PR interne » (W) | 1 (jamais 2) |
| Efficience globale J-1 (AP) | 80-90 % / < 80 % | 1 / 3 |
| « Efficience cessions internes J-1 » (AR, journée entière) | 110-150 % / > 150 % | 1 / 2 |
| « Valeur pièces atelier à perte J-1 » (total du jour, négatif) | perte 100-250 € / 250-500 € / > 500 € | 1 / 2 / 3 |
| Forfaits : somme des Marge_estimee négatives de la liste du jour (total du jour) | −50 à −200 € / −200 à −500 € / < −500 € | 1 / 2 / 3 |
| Écart marge PR interne vs mix (AE, « −6 % » = −6 pts) | −10 à −5 pts / < −10 pts | 1 / 2 |
| Malfaçons J-1 (K) | 150-500 € / 500-1 500 € / > 1 500 € | 1 / 2 / 3 |
| % Malfaçons MTD (S), **seulement si jour de B1 ≥ 10** | > 4 % / > 7 % / > 10 % | 1 / 2 / 3 |

- Paires corrélées dédoublonnées : CA MO / CA PR interne → 1 pt max ; la productivité
  (« Alerte productivité basse ») **ne compte pas**, seule l'efficience globale compte.
- Malfaçons : J-1 **et** MTD **s'additionnent** (jusqu'à 6 pts). Du 1er au 9 : J-1 seul.
- Paliers en € = **total de la journée** (décision du 2026-10-06), jamais ligne par ligne.
- Efficience cessions internes J-1 vide (aucune heure pointée en cession interne) : 0 pt.
  Ne pas la remplacer par la valeur du mois (AS) ni par la liste par OR.
- **Hors score** : remises MO/PR élevées, remises forcées. **Score → icône : 0-1 ☀️ Soleil · 2-4 ☁️ Nuage · 5-8 🌧️ Pluie · ≥ 9 ⛈️ Orage**
  (entités `&#9728;` `&#9729;` `&#127783;` `&#9928;`), libellé « Soleil — productif » etc.

## 9. Météo Magasin — barème de points (CADRAGE_APV §12.7)

| Signal | Mesure | Points |
|---|---|---|
| « Valeur pièces magasin à perte J-1 » (total du jour, négatif) | perte 50-100 € / 100-200 € / > 200 € | 1 / 2 / 3 |
| « Alerte écart CA PR externe » (BH) = ALERTE | écart < −30 % | 1 |
| Taux marge PR Externe J-1 (BK) | 10-15 % / < 10 % | 1 / 2 |

- **Score → icône : 0 ☀️ Soleil (« RAS ») · 1-2 ☁️ Nuage · 3-4 🌧️ Pluie · ≥ 5 ⛈️ Orage.**
  Jamais « RAS » sans avoir vérifié les ventes à perte Magasin du jour.
