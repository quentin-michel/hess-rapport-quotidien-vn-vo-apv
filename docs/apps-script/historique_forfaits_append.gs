/**
 * Copie chaque jour les lignes de l'onglet "Extrait J-1 - Marges<10%" vers
 * l'onglet "Historique", sans doublons.
 *
 * Le connecteur BigQuery lui-meme ("Data source Forfait marges", docs/sql/
 * marge_forfaits_j1_extract.sql) est un onglet DATA_SOURCE, pas une grille
 * de cellules classique - Apps Script (comme gws/l'API Sheets) ne peut pas
 * le lire fiablement directement (meme principe deja documente pour les
 * autres onglets DATA_SOURCE du classeur APV, cf. CADRAGE_APV.md §5).
 * D'ou l'onglet intermediaire "Extrait J-1 - Marges<10%", une **extraction
 * native Sheets** (Donnees > Extraction, pas une formule QUERY) qui
 * materialise le resultat en vraies cellules - c'est CET onglet-la que le
 * script lit.
 *
 * Corrige le 2026-09-29 : le script pointait vers un nom d'onglet obsolete
 * ("Extrait J-1", puis "Extrait J-1 (grid)" selon les versions) qui ne
 * correspondait plus a l'onglet reellement present dans le classeur apres
 * renommage(s) successifs (seuil de marge ajuste 5% -> 10%) - plantait
 * avec "Onglet introuvable".
 *
 * Ce fichier ne contient plus que ce flux (marges). Le flux "Forfaits
 * pieces suspectes" (historiserForfaitsSuspects) a ete retire le
 * 2026-09-29 : vu son faible volume, sa requete BigQuery couvre
 * desormais l'annee entiere plutot qu'une fenetre glissante de J-3
 * (docs/sql/forfaits_pieces_suspectes.sql), donc l'extrait natif Sheets
 * ("Forfaits suspects") est deja a jour et complet a chaque actualisation
 * - plus besoin d'accumuler via Apps Script. Voir CADRAGE_APV.md §10.
 *
 * Installation :
 * 1. Verifier que l'onglet "Extrait J-1 - Marges<10%" existe (extraction
 *    native du connecteur "Data source Forfait marges").
 * 2. Creer l'onglet "Historique" s'il n'existe pas deja (entete cree
 *    automatiquement au premier lancement du script si vide).
 * 3. Extensions > Apps Script (dans ce Sheet).
 * 4. Coller ce fichier dans un script (ex: Code.gs).
 * 5. Cote connecteur : programmer l'actualisation de "Data source Forfait
 *    marges" a 11h00 (Donnees > Connecteurs de donnees > Actualisation
 *    programmee) - meme calage que le reste du classeur APV, cf.
 *    CADRAGE_APV.md §5 (donnees dispo 9h-10h, marge de securite a 11h).
 * 6. Declencheurs (icone horloge, colonne de gauche) > Ajouter un
 *    declencheur > fonction appendHistoriqueForfaits, evenement temporel,
 *    quotidien, autour de 11h30 (apres que l'actualisation du connecteur
 *    et de l'extraction native aient eu le temps de se terminer).
 *
 * Idempotent : rejouable sans creer de doublons (cle Date_reference +
 * id_ligne_entete + Identifiant_groupe_forfait).
 *
 * Si ce nom d'onglet change encore un jour (nouveau seuil de marge par
 * exemple), penser a mettre a jour SOURCE_SHEET ci-dessous ET a verifier
 * dans *Exécutions* (Apps Script) que le declencheur ne plante pas
 * silencieusement pendant des jours avant qu'on s'en aperçoive - c'est
 * exactement ce qui s'est passe ici.
 */

var SOURCE_SHEET = 'Extrait J-1 - Marges<10%';
var HISTORIQUE_SHEET = 'Historique';

function appendHistoriqueForfaits() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var source = ss.getSheetByName(SOURCE_SHEET);
  var historique = ss.getSheetByName(HISTORIQUE_SHEET);

  if (!source) {
    throw new Error('Onglet "' + SOURCE_SHEET + '" introuvable.');
  }
  if (!historique) {
    throw new Error('Onglet "' + HISTORIQUE_SHEET + '" introuvable.');
  }

  var sourceData = source.getDataRange().getValues();
  if (sourceData.length < 2) {
    Logger.log('Extrait J-1 vide, rien a copier.');
    return;
  }

  var header = sourceData[0];
  var rows = sourceData.slice(1);

  if (historique.getLastRow() === 0) {
    historique.appendRow(header);
  }

  var idxDate = header.indexOf('Date_reference');
  var idxEntete = header.indexOf('id_ligne_entete');
  var idxGroupe = header.indexOf('Identifiant_groupe_forfait');
  if (idxDate === -1 || idxEntete === -1 || idxGroupe === -1) {
    throw new Error('Colonnes cle (Date_reference / id_ligne_entete / Identifiant_groupe_forfait) introuvables dans l\'entete.');
  }

  var histData = historique.getDataRange().getValues();
  var existingKeys = {};
  for (var i = 1; i < histData.length; i++) {
    var key = buildKey(histData[i], idxDate, idxEntete, idxGroupe);
    existingKeys[key] = true;
  }

  var toAppend = rows.filter(function (row) {
    return !existingKeys[buildKey(row, idxDate, idxEntete, idxGroupe)];
  });

  if (toAppend.length === 0) {
    Logger.log('Rien de nouveau a ajouter (deja present dans Historique).');
    return;
  }

  historique
    .getRange(historique.getLastRow() + 1, 1, toAppend.length, header.length)
    .setValues(toAppend);

  Logger.log(toAppend.length + ' ligne(s) ajoutee(s) a Historique.');
}

function buildKey(row, idxDate, idxEntete, idxGroupe) {
  return [row[idxDate], row[idxEntete], row[idxGroupe]].join('|');
}
