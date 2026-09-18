-- Requete a coller telle quelle dans un connecteur BigQuery natif Sheets
-- (Donnees > Connecteurs de donnees > Se connecter a BigQuery > Requete
-- personnalisee), sur le meme modele que les autres onglets DATA_SOURCE du
-- projet (voir docs/CADRAGE_APV.md §1.2).
--
-- Une seule instruction SELECT (obligatoire pour Connected Sheets - pas de
-- DECLARE ni de script multi-instructions).
--
-- Fenetre : depuis WINDOW_START (a ajuster ci-dessous) jusqu'a aujourd'hui.
-- Connected Sheets remplace le contenu de l'onglet a chaque actualisation :
-- pour un historique qui s'accumule vraiment dans le temps, garder une
-- borne basse FIXE (pas relative a CURRENT_DATE()) - le tableau grandit
-- tout seul a chaque jour de facturation supplementaire dans BigQuery.
-- Si le volume devient trop gros pour Connected Sheets (limite ~5M
-- cellules), il faudra reculer WINDOW_START ou repasser par une table
-- BigQuery dediee alimentee en incremental (scripts historique_marge_
-- forfaits_*.sql conserves dans ce dossier pour cette eventualite).
--
-- Aucun forfait exclu (decision du 2026-09-18, y compris ceux factures a
-- 0 EUR). Garde-fous techniques uniquement :
--   - Identifiant_groupe_forfait n'est PAS unique seul (verifie sur
--     donnees reelles, se repete entre OR differents) -> toujours grouper
--     par (id_ligne_entete, Identifiant_groupe_forfait).
--   - Facture_avoirisee <> 1, Est_ferme=1, Est_annule=0 : filtres
--     structurels deja utilises partout ailleurs dans le projet.
--   - a_une_ligne_entete : evite de confondre un forfait reellement
--     gratuit (0 EUR) avec un artefact de decoupage de fenetre.

WITH forfait_lignes AS (
  SELECT
    f.id_ligne_entete, f.Identifiant_groupe_forfait, f.Numero_OR, f.Id_date_document,
    f.Est_entete_forfait, f.Est_ligne_forfait, f.Libelle_type_operation,
    f.Quantite_facturation, f.PAMP_facturation, f.Montant_HT_facturation,
    f.Code_intervention, f.Libelle_detail_intervention, f.Facture_avoirisee
  FROM `hess-data.datamart_apres_vente.facturation_detaillee_or` f
  WHERE f.Id_date_document >= DATE('2026-01-01')  -- WINDOW_START : a ajuster
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
             THEN IFNULL(PAMP_facturation, 0) * IFNULL(Quantite_facturation, 0) ELSE 0 END) AS Cout_PR,
    SUM(CASE WHEN Est_ligne_forfait = 1 AND Libelle_type_operation = "Main d'oeuvre"
             THEN IFNULL(Quantite_facturation, 0) ELSE 0 END) AS Heures_MO,
    MAX(Facture_avoirisee) AS Avoirise,
    LOGICAL_OR(Est_entete_forfait = 1) AS a_une_ligne_entete
  FROM forfait_lignes
  GROUP BY 1, 2
)
SELECT
  a.Date_reference,
  e.Concession,
  e.Societe,
  a.Numero_OR,
  e.Numero_OR_DMS,
  a.Code_intervention,
  a.Libelle_forfait,
  a.Prix_forfait_HT,
  a.Cout_PR,
  a.Heures_MO,
  60.0 AS Taux_horaire_MO_estime,
  ROUND(a.Heures_MO * 60.0, 2) AS Cout_MO_estime,
  ROUND(a.Prix_forfait_HT - a.Cout_PR - (a.Heures_MO * 60.0), 2) AS Marge_estimee,
  a.id_ligne_entete,
  a.Identifiant_groupe_forfait
FROM agg a
JOIN `hess-data.datamart_apres_vente.entete_or` e USING (id_ligne_entete)
WHERE a.a_une_ligne_entete
  AND (a.Avoirise IS NULL OR a.Avoirise != 1)
  AND e.Est_ferme = 1
  AND e.Est_annule = 0
ORDER BY a.Date_reference DESC, Marge_estimee ASC
