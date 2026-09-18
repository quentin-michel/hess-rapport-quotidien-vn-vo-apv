-- Requete a coller dans un connecteur BigQuery natif Sheets (onglet
-- "Extrait J-1", DATA_SOURCE), sur le meme modele que les autres onglets
-- de detail journalier du projet (voir docs/CADRAGE_APV.md §1.2 et §9).
--
-- Volontairement etroite (J-1 seulement, pas d'historique dans cette
-- requete) : l'accumulation dans le temps se fait cote onglet "Historique"
-- via le script Apps Script docs/apps-script/historique_forfaits_append.gs,
-- pas ici.
--
-- Aucun forfait exclu (decision du 2026-09-18, y compris ceux factures a
-- 0 EUR). Garde-fous techniques uniquement :
--   - Identifiant_groupe_forfait n'est PAS unique seul (verifie sur
--     donnees reelles, se repete entre OR differents) -> toujours grouper
--     par (id_ligne_entete, Identifiant_groupe_forfait).
--   - Libelle_type_document = 'Facture' (exclut les lignes 'Avoir') :
--     Facture_avoirisee seul est insuffisant, car l'avoir associe a une
--     facture peut etre emis a une AUTRE date (donc hors de la fenetre
--     J-1) - une ligne Avoir isolee dans la fenetre produit un faux
--     forfait a prix/quantites negatifs si on ne filtre pas sur le type de
--     document lui-meme (verifie sur donnees reelles, 2026-09-18).
--   - Est_ferme=1, Est_annule=0 : filtres structurels deja utilises
--     partout ailleurs dans le projet.
--   - a_une_ligne_entete : evite de confondre un forfait reellement
--     gratuit (0 EUR) avec un artefact de decoupage de fenetre.
--
-- Fraicheur (2026-09-18, meme principe que le reste du classeur APV, voir
-- CADRAGE_APV.md §5) : programmer l'actualisation de ce connecteur a 11h00
-- (Donnees > Connecteurs de donnees > Extrait J-1 > Actualisation
-- programmee), apres la remontee des sources APV dans BigQuery (9h-10h) -
-- pas besoin d'elargir la fenetre a J-2/J-1 tant que ce calage est respecte.
--
-- Colonnes texte/contexte d'abord, cles techniques ensuite, donnees
-- numeriques regroupees a la fin (demande explicite du 2026-09-18).
--
-- clients.Nom_prenom : donnee nominative (table clients labellisee
-- "donnees_personnelles" cote BigQuery) - jointe via CRC_client_facture
-- (client facture), pas conducteur/proprietaire.

WITH forfait_lignes AS (
  SELECT
    f.id_ligne_entete, f.Identifiant_groupe_forfait, f.Id_date_document,
    f.Est_entete_forfait, f.Est_ligne_forfait, f.Libelle_type_operation,
    f.Libelle_type_imputation, f.Quantite_facturation, f.PAMP_facturation,
    f.Montant_HT_facturation, f.Code_intervention, f.Libelle_detail_intervention,
    f.Libelle_detail_operation, f.Reference_ecran
  FROM `hess-data.datamart_apres_vente.facturation_detaillee_or` f
  WHERE f.Id_date_document = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    AND f.Identifiant_groupe_forfait IS NOT NULL
    AND f.Identifiant_groupe_forfait != ''
    AND f.Libelle_type_document = 'Facture'
),
agg AS (
  SELECT
    id_ligne_entete,
    Identifiant_groupe_forfait,
    ANY_VALUE(Id_date_document) AS Date_reference,
    MAX(CASE WHEN Est_entete_forfait = 1 THEN Code_intervention END) AS Code_intervention,
    MAX(CASE WHEN Est_entete_forfait = 1 THEN Libelle_detail_intervention END) AS Libelle_forfait,
    MAX(CASE WHEN Est_entete_forfait = 1 THEN Libelle_type_imputation END) AS Libelle_type_imputation,
    STRING_AGG(
      CASE WHEN Est_ligne_forfait = 1 AND Libelle_type_operation = 'Pièce'
           THEN CONCAT(Libelle_detail_operation, ' [', Reference_ecran, '] x',
                        CAST(Quantite_facturation AS STRING), ' (PAMP ',
                        CAST(ROUND(PAMP_facturation, 2) AS STRING), '€)')
      END, ' | ' ORDER BY Libelle_detail_operation
    ) AS Detail_pieces,
    SUM(CASE WHEN Est_entete_forfait = 1 THEN Montant_HT_facturation ELSE 0 END) AS Prix_forfait_HT,
    SUM(CASE WHEN Est_ligne_forfait = 1 AND Libelle_type_operation = 'Pièce'
             THEN IFNULL(PAMP_facturation, 0) ELSE 0 END) AS Cout_PR,
    SUM(CASE WHEN Est_ligne_forfait = 1 AND Libelle_type_operation = "Main d'oeuvre"
             THEN IFNULL(Quantite_facturation, 0) ELSE 0 END) AS Heures_MO,
    LOGICAL_OR(Est_entete_forfait = 1) AS a_une_ligne_entete
  FROM forfait_lignes
  GROUP BY 1, 2
)
SELECT
  -- contexte
  a.Date_reference,
  e.Concession,
  e.Societe,
  e.Numero_OR_DMS,
  c.Nom_prenom AS Nom_client,
  a.Libelle_type_imputation AS Canal_imputation,
  e.Categorie_client AS Canal_categorie_client,
  a.Code_intervention,
  a.Libelle_forfait,
  -- cles techniques
  a.id_ligne_entete,
  a.Identifiant_groupe_forfait,
  a.Detail_pieces,
  -- donnees numeriques
  a.Prix_forfait_HT,
  a.Cout_PR,
  a.Heures_MO,
  60.0 AS Taux_horaire_MO_estime,
  ROUND(a.Heures_MO * 60.0, 2) AS Cout_MO_estime,
  ROUND(a.Prix_forfait_HT - a.Cout_PR - (a.Heures_MO * 60.0), 2) AS Marge_estimee
FROM agg a
JOIN `hess-data.datamart_apres_vente.entete_or` e USING (id_ligne_entete)
LEFT JOIN `hess-data.datamart_apres_vente.clients` c ON c.CRC_client = e.CRC_client_facture
WHERE a.a_une_ligne_entete
  AND e.Est_ferme = 1
  AND e.Est_annule = 0
ORDER BY Marge_estimee ASC
