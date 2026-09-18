-- Creation de la table d'historique des marges de forfaits APV.
-- A executer UNE FOIS par quelqu'un ayant les droits d'ecriture sur le
-- projet BigQuery hess-data (Claude/gws n'a que des droits de lecture,
-- verifie le 2026-09-18 : bigquery.tables.create refuse sur tous les
-- datasets du projet).
--
-- Voir docs/CADRAGE_APV.md pour le contexte complet (chantier "anomalies
-- forfaits", cout MO approximatif convenu avec la BU APV).

CREATE TABLE IF NOT EXISTS `hess-data.datamart_apres_vente.historique_marge_forfaits` (
  Date_reference DATE OPTIONS(description="Id_date_document de la ligne entete forfait (jour de facturation reel)"),
  id_ligne_entete INTEGER OPTIONS(description="FK entete_or.id_ligne_entete"),
  Identifiant_groupe_forfait STRING OPTIONS(description="ATTENTION : pas unique seul, se repete entre OR differents (verifie sur donnees reelles) - la cle reelle d'un forfait est (id_ligne_entete, Identifiant_groupe_forfait)"),
  Numero_OR STRING,
  Numero_OR_DMS STRING,
  Concession STRING OPTIONS(description="Nom brut entete_or.Concession, pas encore resolu au code canonique (fait cote Sheet via Mapping concession)"),
  Societe STRING,
  Code_intervention STRING,
  Libelle_forfait STRING OPTIONS(description="Libelle_detail_intervention de la ligne entete forfait"),
  Prix_forfait_HT FLOAT64 OPTIONS(description="Montant_HT_facturation de la ligne entete (Est_entete_forfait=1)"),
  Cout_PR FLOAT64 OPTIONS(description="Somme PAMP_facturation x Quantite_facturation des lignes Piece du forfait"),
  Heures_MO FLOAT64 OPTIONS(description="Somme Quantite_facturation (heures) des lignes Main d'oeuvre du forfait"),
  Taux_horaire_MO_estime FLOAT64 OPTIONS(description="Taux horaire MO estime applique ce jour-la (convenu avec la BU APV, 60 EUR au lancement, 2026-09-18)"),
  Cout_MO_estime FLOAT64 OPTIONS(description="Heures_MO x Taux_horaire_MO_estime"),
  Marge_estimee FLOAT64 OPTIONS(description="Prix_forfait_HT - Cout_PR - Cout_MO_estime. Aucun forfait exclu (y compris ceux factures 0 EUR, decision du 2026-09-18)"),
  _loaded_at TIMESTAMP OPTIONS(description="Horodatage du run qui a ecrit/reecrit cette ligne")
)
PARTITION BY Date_reference
CLUSTER BY Concession
OPTIONS(description="Historique quotidien de la marge estimee (PR + MO forfaitaire) de chaque forfait facture, tous forfaits inclus. Alimentee par une requete planifiee DELETE+INSERT sur une fenetre glissante de 4 jours (absorbe le retard de fraicheur connu de facturation_detaillee_or). Voir historique_marge_forfaits_daily_refresh.sql.");
