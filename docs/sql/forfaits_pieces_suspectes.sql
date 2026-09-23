-- Requete du connecteur BigQuery "Forfaits pieces suspectes" (Sheet
-- "Anomalies forfaits"). Detection n3 du chantier forfaits (cf.
-- CADRAGE_APV.md §8 pt.5 et §10) : reperer une piece chere et inhabituelle
-- facturee dans un forfait sans rapport avec son objet (piste de
-- detection de fraude/erreur de facturation).
--
-- Recuperee depuis les metadonnees du Sheet le 2026-09-23 (le texte d'une
-- requete de connecteur BigQuery natif Sheets n'est pas visible via
-- gws/l'API values.get classique - il faut interroger spreadsheets.get
-- avec fields=dataSources pour l'obtenir).
--
-- Methode :
--   1. Classification du forfait en "famille" par mots-cles (regex) sur
--      son libelle - REVISION_ENTRETIEN, PNEUS, FREINAGE, CLIMATISATION,
--      DISTRIBUTION, BATTERIE, EMBRAYAGE, SUSPENSION. Un forfait qui ne
--      matche aucun mot-cle est ignore (famille NULL) - cette detection
--      ne couvre donc pas tous les types de forfaits (ex. carrosserie,
--      controles divers).
--   2. Baseline : pour chaque (famille, libelle de piece), nombre
--      d'occurrences sur tout l'historique AVANT J-3 (depuis 2025-01-01).
--   3. Fenetre d'analyse : J-3 a aujourd'hui (plus large que le J-1 strict
--      du flux marges).
--   4. Filtre "suspect" : occurrence baseline <= 2 (jamais/quasi jamais
--      vue pour cette famille) ET PAMP >= 150 EUR (seuil de materialite,
--      pour ne pas noyer le signal dans des pieces rares mais bon marche).
--
-- Meme piege deja documente pour le flux marges : Identifiant_groupe_forfait
-- n'est pas unique seul, toujours (id_ligne_entete, Identifiant_groupe_forfait).

DECLARE fenetre_debut DATE DEFAULT DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY);

WITH forfaits AS (
  SELECT id_ligne_entete, Identifiant_groupe_forfait, ANY_VALUE(Id_date_document) AS date_doc,
         MAX(CASE WHEN Est_entete_forfait=1 THEN Libelle_detail_intervention END) AS libelle_forfait
  FROM `hess-data.datamart_apres_vente.facturation_detaillee_or`
  WHERE Identifiant_groupe_forfait IS NOT NULL AND Identifiant_groupe_forfait != ''
    AND Libelle_type_document = 'Facture'
    AND Id_date_document BETWEEN '2025-01-01' AND CURRENT_DATE()
  GROUP BY id_ligne_entete, Identifiant_groupe_forfait
),
familles AS (
  SELECT *,
    CASE
      WHEN REGEXP_CONTAINS(UPPER(libelle_forfait), r'REVISION|ENTRETIEN|VIDANGE') THEN 'REVISION_ENTRETIEN'
      WHEN REGEXP_CONTAINS(UPPER(libelle_forfait), r'PNEU|PERMUTATION|MONTE\s?ROUES') THEN 'PNEUS'
      WHEN REGEXP_CONTAINS(UPPER(libelle_forfait), r'FREIN|PLAQUETTE|DISQUE') THEN 'FREINAGE'
      WHEN REGEXP_CONTAINS(UPPER(libelle_forfait), r'CLIM') THEN 'CLIMATISATION'
      WHEN REGEXP_CONTAINS(UPPER(libelle_forfait), r'DISTRIBUTION|COURROIE') THEN 'DISTRIBUTION'
      WHEN REGEXP_CONTAINS(UPPER(libelle_forfait), r'BATTERIE') THEN 'BATTERIE'
      WHEN REGEXP_CONTAINS(UPPER(libelle_forfait), r'EMBRAYAGE') THEN 'EMBRAYAGE'
      WHEN REGEXP_CONTAINS(UPPER(libelle_forfait), r'AMORTISSEUR|SUSPENSION') THEN 'SUSPENSION'
    END AS famille
  FROM forfaits
),
familles_valides AS (SELECT * FROM familles WHERE famille IS NOT NULL),
pieces AS (
  SELECT f.id_ligne_entete, f.Identifiant_groupe_forfait, f.famille, f.date_doc, f.libelle_forfait,
         p.Libelle_detail_operation, p.Reference_ecran, p.PAMP_facturation, p.Quantite_facturation
  FROM familles_valides f
  JOIN `hess-data.datamart_apres_vente.facturation_detaillee_or` p
    ON p.id_ligne_entete = f.id_ligne_entete AND p.Identifiant_groupe_forfait = f.Identifiant_groupe_forfait
  WHERE p.Est_ligne_forfait = 1 AND p.Libelle_type_operation = 'Pièce'
    AND p.Libelle_type_document = 'Facture'
),
baseline AS (
  SELECT famille, Libelle_detail_operation, COUNT(*) AS nb_occurrences_baseline
  FROM pieces WHERE date_doc < fenetre_debut
  GROUP BY famille, Libelle_detail_operation
),
fenetre AS (SELECT * FROM pieces WHERE date_doc >= fenetre_debut)
SELECT
  CURRENT_TIMESTAMP() AS date_extraction,
  f.date_doc, e.Concession, e.Numero_OR_DMS, e.Receptionnaire,
  f.famille, f.libelle_forfait, f.id_ligne_entete, f.Identifiant_groupe_forfait,
  f.Libelle_detail_operation, f.Reference_ecran, f.PAMP_facturation, f.Quantite_facturation,
  IFNULL(b.nb_occurrences_baseline, 0) AS rarete_historique
FROM fenetre f
JOIN `hess-data.datamart_apres_vente.entete_or` e USING (id_ligne_entete)
LEFT JOIN baseline b USING (famille, Libelle_detail_operation)
WHERE IFNULL(b.nb_occurrences_baseline, 0) <= 2 AND f.PAMP_facturation >= 150
ORDER BY f.PAMP_facturation DESC;
