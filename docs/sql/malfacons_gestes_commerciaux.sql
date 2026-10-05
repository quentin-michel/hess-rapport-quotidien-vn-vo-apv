-- Requete a coller dans un connecteur BigQuery natif Sheets (classeur
-- "Rapport quotidien APV", onglet DATA_SOURCE "Malfaçons et gestes co"),
-- extrait natif (GRID) + colonne "Code concession" en formule a droite,
-- sur le meme modele que les autres onglets de detail du projet.
--
-- Malfacons et gestes commerciaux (cout de non-qualite atelier) = lignes
-- de cession interne (Affectation = 'CESSION') imputees sur l'une des 10
-- fiches retenues par Corentin le 2026-10-05 (meme liste que le filtre
-- Tableau "Fiche_imputee" et que la recette R7 du skill
-- hess-apv-facturation-bigquery, validee au centime vs Tableau : mai 2026
-- = 89 758,02 EUR) :
--   CI MALFACON CARR / MECA
--   CI GESTE COMMERCIAL CARR / MECA
--   CI REPARATION A CHARGE DE L'ATELIER CARR / MECA
--   CI TEMPS PASSE NON FACTURE / CI TEMPS PASSE NON FACTURE CARR
--   CI OPERATION SPECIALES APV / CI OPERATIONS SPECIALES APV CARR
-- Ne PAS elargir aux variantes MAG, FG, VN, VO, VD (gestes commerciaux
-- magasin/commerce, hors definition : +30 % environ).
--
-- Fenetre : du 1er du mois de J-1 jusqu'a J-1 inclus (le 1er du mois, la
-- requete renvoie donc tout le mois precedent). Le mail lit le detail
-- d'hier (Date_document = J-1) et le cumul du mois sur le meme onglet.
--
-- Grain : 1 ligne = 1 OR x 1 fiche x 1 date x 1 type de document. Les
-- avoirs restent (montants negatifs) : la mesure de reference est le net
-- (factures - avoirs), comme dans Tableau.
--
-- Mesure = Prix_vente_net (vue gestion, forfaits ventilés MO/PR : la ligne
-- Forfait vaut 0).
--
-- Perimetre Tableau : OR ouverts depuis le 2024-01-01 (regle de parite du
-- skill BigQuery). Les rares OR plus anciens encore factures sont exclus.
--
-- Client : proprietaire du vehicule (CRC_client_proprietaire). Sur une
-- cession interne, le client facture est le site lui-meme, pas le client
-- concerne par la malfacon ou le geste. Donnee nominative (table clients
-- "donnees_personnelles") : noms reels dans le Sheet et les mails,
-- jamais dans un fichier commite.
--
-- Actualisation programmee du connecteur : 11h00, comme les autres
-- extraits APV (sources remontees dans BigQuery entre 9h et 10h).
--
-- Libelle_detail_intervention : texte libre saisi par l'atelier (motif de
-- la malfacon ou du geste). Un OR peut porter plusieurs interventions sur
-- la meme fiche : elles sont regroupees, separees par " | ".
--
-- N° OR = Numero_OR_DMS (comme les autres onglets APV et les mails). La cle
-- technique Numero_OR ("P0065...") est retiree a la demande de Corentin
-- (2026-10-05) : le n° DMS, combine a la concession, suffit.
--
-- Colonnes texte/contexte d'abord, cles ensuite, donnees numeriques a la
-- fin (convention du projet).

WITH bornes AS (
  SELECT
    DATE_SUB(CURRENT_DATE('Europe/Paris'), INTERVAL 1 DAY) AS j1,
    DATE_TRUNC(DATE_SUB(CURRENT_DATE('Europe/Paris'), INTERVAL 1 DAY), MONTH) AS debut_mois
)
SELECT
  e.Regroupement_concessions_APV AS Concession,
  f.Id_date_document AS Date_document,
  IF(ENDS_WITH(f.Fiche_imputee, 'CARR'), 'Carrosserie', 'Mécanique') AS Activite,
  f.Fiche_imputee,
  STRING_AGG(DISTINCT TRIM(f.Libelle_detail_intervention), ' | ') AS Libelle_detail_intervention,
  e.Categorie_OR,
  e.Receptionnaire,
  c.Nom_prenom AS Nom_client,
  v.Immat AS Immatriculation,
  f.Libelle_type_document AS Type_document,
  e.Numero_OR_DMS,
  f.Numero_document,
  ROUND(SUM(IF(f.Libelle_type_operation = "Main d'oeuvre", f.Prix_vente_net, 0)), 2) AS Montant_MO,
  ROUND(SUM(IF(f.Libelle_type_operation = 'Pièce', f.Prix_vente_net, 0)), 2) AS Montant_PR,
  ROUND(SUM(IF(f.Libelle_type_operation NOT IN ("Main d'oeuvre", 'Pièce'), f.Prix_vente_net, 0)), 2) AS Montant_autres,
  ROUND(SUM(f.Prix_vente_net), 2) AS Montant_total
FROM `hess-data.datamart_apres_vente.facturation_detaillee_or` f
CROSS JOIN bornes b
JOIN `hess-data.datamart_apres_vente.entete_or` e
  ON e.id_ligne_entete = f.id_ligne_entete AND e.Date_ouverture >= '2024-01-01'
LEFT JOIN `hess-data.datamart_apres_vente.clients` c
  ON c.CRC_client = e.CRC_client_proprietaire
LEFT JOIN `hess-data.datamart_apres_vente.vehicules` v
  ON v.CRC_vehicule = e.CRC_vehicule
WHERE f.Id_date_document BETWEEN b.debut_mois AND b.j1
  AND f.Affectation = 'CESSION'
  AND REGEXP_CONTAINS(f.Fiche_imputee,
      r"^CI (MALFACON (CARR|MECA)|GESTE COMMERCIAL (CARR|MECA)|REPARATION A CHARGE DE L'ATELIER (CARR|MECA)|TEMPS PASSE NON FACTURE|OPERATION SPECIALES APV|OPERATIONS SPECIALES APV CARR)")
GROUP BY Concession, Date_document, Activite, f.Fiche_imputee, e.Categorie_OR,
  e.Receptionnaire, Nom_client, Immatriculation, Type_document, e.Numero_OR_DMS, f.Numero_document
ORDER BY Concession, Date_document DESC, Montant_total DESC
