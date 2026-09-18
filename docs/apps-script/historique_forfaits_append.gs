/**
 * Copie chaque jour les lignes de l'onglet "Extrait J-1" (alimente par le
 * connecteur BigQuery, docs/sql/marge_forfaits_j1_extract.sql) vers
 * l'onglet "Historique", sans doublons.
 *
 * Installation :
 * 1. Extensions > Apps Script (dans ce Sheet).
 * 2. Coller ce fichier dans un script (ex: Code.gs).
 * 3. Creer les 2 onglets s'ils n'existent pas encore : "Extrait J-1" et
 *    "Historique" (l'entete de "Historique" est cree automatiquement au
 *    premier lancement si vide).
 * 4. Cote connecteur : programmer l'actualisation de "Extrait J-1" a 11h00
 *    (Donnees > Connecteurs de donnees > Extrait J-1 > Actualisation
 *    programmee) - meme calage que le reste du classeur APV, cf.
 *    CADRAGE_APV.md §5 (donnees dispo 9h-10h, marge de securite a 11h).
 * 5. Declencheurs (icone horloge, colonne de gauche) > Ajouter un
 *    declencheur > fonction appendHistoriqueForfaits, evenement temporel,
 *    quotidien, autour de 11h30 (apres que l'actualisation du connecteur
 *    ait eu le temps de se terminer).
 *
 * Idempotent : rejouable sans creer de doublons (cle Date_reference +
 * id_ligne_entete + Identifiant_groupe_forfait).
 */

var SOURCE_SHEET = 'Extrait J-1';
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
