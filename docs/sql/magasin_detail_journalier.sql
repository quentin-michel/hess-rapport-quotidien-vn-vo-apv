-- Requete du connecteur BigQuery "Magasin" (Sheet "Rapport quotidien APV"),
-- qui alimente l'onglet GRID "Détail facturation magasin journaliere"
-- (source du bloc "Analyse pièces J-1", cf. CADRAGE_APV.md).
--
-- Modifiee le 2026-09-23 : ajoute Nom_client (jointure clients.CRC_client,
-- meme table que celle deja utilisee cote Atelier pour un format coherent),
-- retire Famille_technique (inutilisee). Reorganisee pour respecter la
-- convention "donnees numeriques en fin de liste" du projet.
--
-- Point de vigilance : ajouter/retirer une colonne ici decale la colonne
-- "Code concession" ajoutee en formule Sheet a droite du connecteur (dans
-- l'onglet GRID) SEULEMENT si le nombre total de colonnes change. Ici le
-- compte reste identique (Famille_technique retiree, Nom_client ajoutee),
-- donc "Code concession" reste a sa position habituelle.

SELECT
  l.id_ligne, e.Regroupement_Concession_APV AS Concession, e.Magasin, e.Date_document,
  e.Numero_document, e.Avoir, e.Categorie_client, e.Nom_Magasinier,
  c.Nom_prenom AS Nom_client,
  l.Reference, l.Libelle_piece,
  l.Qte_servie, l.Prix_unitaire_net, l.Prix_brut_ligne, l.Remise_ligne,
  l.Prix_net_ligne, l.PAMP, l.Prix_force, l.Remise_forcee
FROM `hess-data.datamart_apres_vente.lignes_pieces` l
JOIN `hess-data.datamart_apres_vente.entete_pieces` e
  ON e.id_entete = l.id_entete AND e.NumIntMostrador = l.NumIntMostrador
LEFT JOIN `hess-data.datamart_apres_vente.clients` c ON c.CRC_client = e.CRC_client
WHERE e.Date_document = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND l.Qte_servie != 0
