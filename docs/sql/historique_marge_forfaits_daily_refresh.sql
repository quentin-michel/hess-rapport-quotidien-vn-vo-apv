-- Requete a planifier en "Scheduled query" BigQuery (quotidien, apres la
-- fenetre habituelle de fraicheur APV, cf. docs/CADRAGE_APV.md §5 -
-- decalage de 1-2 jours deja observe sur facturation_detaillee_or).
--
-- Idempotente : DELETE puis INSERT sur une fenetre glissante de 4 jours,
-- rejouable sans creer de doublons, et qui rattrape les lignes arrivees en
-- retard dans BigQuery.
--
-- Aucun forfait exclu (decision du 2026-09-18, y compris ceux factures a
-- 0 EUR) - seuls des garde-fous techniques restent :
--   - Identifiant_groupe_forfait n'est PAS unique seul, il se repete entre
--     OR differents (verifie sur donnees reelles) -> toujours grouper par
--     (id_ligne_entete, Identifiant_groupe_forfait), jamais par
--     Identifiant_groupe_forfait seul.
--   - Facture_avoirisee <> 1 et Est_ferme=1/Est_annule=0 : filtres
--     structurels deja utilises partout ailleurs dans le projet (un avoir
--     ou un OR annule n'est pas un forfait vendu, pas une exclusion
--     economique d'un forfait reel).
--   - a_une_ligne_entete : garde-fou contre un groupe dont la ligne entete
--     tomberait hors de la fenetre de 4 jours (rare, evite de confondre
--     un forfait reellement gratuit avec un artefact de fenetre).

DECLARE window_start DATE DEFAULT DATE_SUB(CURRENT_DATE(), INTERVAL 4 DAY);
DECLARE window_end DATE DEFAULT DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY);

DELETE FROM `hess-data.datamart_apres_vente.historique_marge_forfaits`
WHERE Date_reference BETWEEN window_start AND window_end;

INSERT INTO `hess-data.datamart_apres_vente.historique_marge_forfaits`
(Date_reference, id_ligne_entete, Identifiant_groupe_forfait, Numero_OR, Numero_OR_DMS,
 Concession, Societe, Code_intervention, Libelle_forfait, Prix_forfait_HT, Cout_PR,
 Heures_MO, Taux_horaire_MO_estime, Cout_MO_estime, Marge_estimee, _loaded_at)
WITH forfait_lignes AS (
  SELECT
    f.id_ligne_entete, f.Identifiant_groupe_forfait, f.Numero_OR, f.Id_date_document,
    f.Est_entete_forfait, f.Est_ligne_forfait, f.Libelle_type_operation,
    f.Quantite_facturation, f.PAMP_facturation, f.Montant_HT_facturation,
    f.Code_intervention, f.Libelle_detail_intervention, f.Facture_avoirisee
  FROM `hess-data.datamart_apres_vente.facturation_detaillee_or` f
  WHERE f.Id_date_document BETWEEN window_start AND window_end
    AND f.Identifiant_groupe_forfait IS NOT NULL
    AND f.Identifiant_groupe_forfait != ''
),
agg AS (
  SELECT
    id_ligne_entete,
    Identifiant_groupe_forfait,
    ANY_VALUE(Numero_OR) AS Numero_OR,
    ANY_VALUE(Id_date_document) AS Date_reference,
    MAX(CASE WHEN Est_entete_forfait = 1 THEN Code_intervention END) AS Code_intervention,
    MAX(CASE WHEN Est_entete_forfait = 1 THEN Libelle_detail_intervention END) AS Libelle_forfait,
    SUM(CASE WHEN Est_entete_forfait = 1 THEN Montant_HT_facturation ELSE 0 END) AS Prix_forfait_HT,
    SUM(CASE WHEN Est_ligne_forfait = 1 AND Libelle_type_operation = 'Pièce'
             THEN IFNULL(PAMP_facturation, 0) ELSE 0 END) AS Cout_PR,
    SUM(CASE WHEN Est_ligne_forfait = 1 AND Libelle_type_operation = "Main d'oeuvre"
             THEN IFNULL(Quantite_facturation, 0) ELSE 0 END) AS Heures_MO,
    MAX(Facture_avoirisee) AS Avoirise,
    LOGICAL_OR(Est_entete_forfait = 1) AS a_une_ligne_entete
  FROM forfait_lignes
  GROUP BY 1, 2
)
SELECT
  a.Date_reference,
  a.id_ligne_entete,
  a.Identifiant_groupe_forfait,
  a.Numero_OR,
  e.Numero_OR_DMS,
  e.Concession,
  e.Societe,
  a.Code_intervention,
  a.Libelle_forfait,
  a.Prix_forfait_HT,
  a.Cout_PR,
  a.Heures_MO,
  60.0 AS Taux_horaire_MO_estime,
  a.Heures_MO * 60.0 AS Cout_MO_estime,
  a.Prix_forfait_HT - a.Cout_PR - (a.Heures_MO * 60.0) AS Marge_estimee,
  CURRENT_TIMESTAMP() AS _loaded_at
FROM agg a
JOIN `hess-data.datamart_apres_vente.entete_or` e USING (id_ligne_entete)
WHERE a.a_une_ligne_entete
  AND (a.Avoirise IS NULL OR a.Avoirise != 1)
  AND e.Est_ferme = 1
  AND e.Est_annule = 0;
