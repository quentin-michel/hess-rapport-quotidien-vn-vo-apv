/**
 * Copie chaque jour les lignes de l'onglet "Extrait J-1 (grid)" vers
 * l'onglet "Historique", sans doublons.
 *
 * "Extrait J-1" (le connecteur BigQuery lui-meme, docs/sql/
 * marge_forfaits_j1_extract.sql) est un onglet DATA_SOURCE, pas une
 * grille de cellules classique - Apps Script (comme gws/l'API Sheets) ne
 * peut pas le lire fiablement directement (meme principe deja documente
 * pour les autres onglets DATA_SOURCE du classeur APV, cf.
 * CADRAGE_APV.md §5). D'ou l'onglet intermediaire "Extrait J-1 (grid)",
 * qui materialise le resultat en vraies cellules via :
 *   =QUERY('Extrait J-1'!A:S, "select *", 1)
 * (en A1 de ce nouvel onglet) - c'est CET onglet-la que le script lit.
 *
 * Installation :
 * 1. Creer l'onglet "Extrait J-1 (grid)" avec la formule QUERY ci-dessus.
 * 2. Creer l'onglet "Historique" s'il n'existe pas deja (entete cree
 *    automatiquement au premier lancement du script si vide).
 * 3. Extensions > Apps Script (dans ce Sheet).
 * 4. Coller ce fichier dans un script (ex: Code.gs).
 * 5. Cote connecteur : programmer l'actualisation de "Extrait J-1" a 11h00
 *    (Donnees > Connecteurs de donnees > Extrait J-1 > Actualisation
 *    programmee) - meme calage que le reste du classeur APV, cf.
 *    CADRAGE_APV.md §5 (donnees dispo 9h-10h, marge de securite a 11h).
 * 6. Declencheurs (icone horloge, colonne de gauche) > Ajouter un
 *    declencheur > fonction appendHistoriqueForfaits, evenement temporel,
 *    quotidien, autour de 11h30 (apres que l'actualisation du connecteur
 *    ait eu le temps de se terminer - la formule QUERY se recalcule toute
 *    seule des que le connecteur change, pas besoin d'un declencheur pour
 *    l'onglet grid lui-meme).
 *
 * Idempotent : rejouable sans creer de doublons (cle Date_reference +
 * id_ligne_entete + Identifiant_groupe_forfait).
 */

var SOURCE_SHEET = 'Extrait J-1 (grid)';
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

/**
 * Meme principe qu'appendHistoriqueForfaits, pour le flux "Forfaits
 * pieces suspectes" (detection n3, docs/sql/forfaits_pieces_suspectes.sql
 * et CADRAGE_APV.md §10) - fonction et declencheur separes de
 * appendHistoriqueForfaits (ajoutee le 2026-09-2x, sans toucher au flux
 * marges qui tournait deja).
 *
 * Cle de dedoublonnage differente : inclut Reference_ecran en plus du
 * forfait, car plusieurs pieces suspectes peuvent coexister sur un meme
 * forfait (sinon la 2e serait prise pour un doublon de la 1ere).
 *
 * Lit directement l'onglet DATA_SOURCE "Forfaits pièces suspectes" (pas
 * d'onglet grid intermediaire ici, contrairement au flux marges) - a
 * surveiller si des erreurs de lecture apparaissent un jour dans
 * Executions (Apps Script) ; le cas echeant, appliquer le meme correctif
 * que pour "Extrait J-1" (onglet grid via QUERY, ou "Extraire" natif).
 *
 * "0 ligne ajoutee" la plupart des jours est attendu (le filtre rarete<=2
 * + PAMP>=150€ est volontairement strict), pas un signe de bug.
 */
function historiserForfaitsSuspects() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var source = ss.getSheetByName('Forfaits pièces suspectes');
  var historique = ss.getSheetByName('Forfaits suspects');

  if (!source) { Logger.log('Onglet source introuvable.'); return; }
  if (!historique) { Logger.log('Onglet historique introuvable.'); return; }

  var sourceData = source.getDataRange().getValues();
  if (sourceData.length < 2) { Logger.log('Rien a copier.'); return; }

  var header = sourceData[0];
  var rows = sourceData.slice(1);

  if (historique.getLastRow() === 0) historique.appendRow(header);

  var colonnesCle = ['date_doc', 'id_ligne_entete', 'Identifiant_groupe_forfait', 'Reference_ecran'];
  var idxCle = colonnesCle.map(function (nom) {
    var idx = header.indexOf(nom);
    if (idx === -1) throw new Error('Colonne "' + nom + '" introuvable.');
    return idx;
  });

  var histData = historique.getDataRange().getValues();
  var existingKeys = {};
  for (var i = 1; i < histData.length; i++) {
    existingKeys[idxCle.map(function (idx) { return histData[i][idx]; }).join('|')] = true;
  }

  var toAppend = rows.filter(function (row) {
    return !existingKeys[idxCle.map(function (idx) { return row[idx]; }).join('|')];
  });

  if (toAppend.length === 0) { Logger.log('Rien de nouveau.'); return; }

  historique.getRange(historique.getLastRow() + 1, 1, toAppend.length, header.length).setValues(toAppend);
  Logger.log(toAppend.length + ' ligne(s) ajoutee(s).');
}
