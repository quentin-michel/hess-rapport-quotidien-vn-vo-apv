/**
 * Envoie chaque jour un mail recapitulant les forfaits a marge faible
 * (J-1, groupe entier) a une liste de destinataires dediee - Jean Tomei,
 * Jerome Petit, Thierry Oudin (demande du 2026-09-29, HORS PERIMETRE du
 * rapport quotidien APV de Corentin, cf. CADRAGE_APV.md §9.1).
 *
 * Lit directement l'onglet "Extrait J-1 - Marges<10%" - deja filtre
 * strictement sur J-1 et marge<10% par la requete du connecteur BigQuery
 * (§9, CADRAGE_APV.md), pas de filtrage supplementaire a faire ici. C'est
 * un extrait natif Sheets (GRID), pas un onglet DATA_SOURCE - lisible
 * directement avec getDataRange() sans le piege deja documente ailleurs
 * dans ce dossier.
 *
 * Deux points d'entree :
 * - envoyerForfaitsMargeFaible() : envoi reel (GmailApp.sendEmail). Si
 *   aucun forfait a marge faible ce jour-la, N'ENVOIE RIEN (silence =
 *   RAS, pour ne pas spammer les destinataires de mails vides).
 * - simulerForfaitsMargeFaible() : cree un BROUILLON Gmail au lieu
 *   d'envoyer (GmailApp.createDraft), pour relecture avant de brancher le
 *   declencheur automatique. Contrairement a l'envoi reel, cree toujours
 *   un brouillon meme si 0 ligne ce jour-la (pour verifier le rendu du
 *   cas "aucun cas"), et sans piece jointe Excel dans ce cas.
 * Les deux partagent la meme logique de construction du contenu
 * (fonction interne construireContenu_) pour rester synchronisees.
 *
 * Piece jointe Excel : export de l'onglet source lui-meme (toutes les
 * colonnes brutes) via l'URL d'export Google Sheets. Necessite un scope
 * OAuth Drive que Apps Script ne detecte PAS automatiquement pour un
 * simple UrlFetchApp vers une URL en dur - voir "Installation" ci-dessous,
 * etape 2 (manifeste appsscript.json), sinon l'export renvoie une page de
 * connexion au lieu du fichier.
 *
 * Destinataires non codes en dur : lus depuis l'onglet "Destinataires
 * marge faible" (colonne A, sous l'en-tete "Email") - les adresses
 * reelles restent dans le Sheet, jamais commitees dans ce fichier (regle
 * anonymisation du projet, cf. CADRAGE.md §6).
 *
 * Installation :
 * 1. Creer l'onglet "Destinataires marge faible" avec en A1 "Email" et
 *    les adresses des destinataires en dessous (A2, A3, A4...).
 * 2. Extensions > Apps Script > icone Parametres du projet (roue
 *    crantee) > cocher "Afficher le fichier manifeste appsscript.json
 *    dans l'editeur". Ouvrir appsscript.json et ajouter (ou completer)
 *    le tableau "oauthScopes" :
 *      "oauthScopes": [
 *        "https://www.googleapis.com/auth/spreadsheets",
 *        "https://www.googleapis.com/auth/drive.readonly",
 *        "https://www.googleapis.com/auth/gmail.compose",
 *        "https://www.googleapis.com/auth/gmail.send",
 *        "https://www.googleapis.com/auth/script.external_request"
 *      ]
 *    Sans ca, l'export Excel echoue silencieusement (fichier vide ou
 *    page de connexion au lieu du xlsx).
 * 3. Coller ce fichier dans un nouveau script (meme projet que
 *    historique_forfaits_append.gs, ou un projet separe).
 * 4. Lancer manuellement simulerForfaitsMargeFaible() plusieurs fois pour
 *    verifier le rendu (brouillon Gmail + piece jointe Excel) avant de
 *    toucher au declencheur automatique.
 * 5. Une fois satisfait : Declencheurs > Ajouter un declencheur >
 *    fonction envoyerForfaitsMargeFaible, evenement temporel, quotidien,
 *    vers 11h35 (apres l'actualisation du connecteur a 11h00).
 */

var SOURCE_SHEET_MARGE_FAIBLE = 'Extrait J-1 - Marges<10%';
var DESTINATAIRES_SHEET = 'Destinataires marge faible';

function envoyerForfaitsMargeFaible() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var contenu = construireContenu_(ss);

  if (!contenu.rows.length) {
    Logger.log('Aucun forfait a marge faible aujourd\'hui, rien a envoyer.');
    return;
  }

  var destinataires = lireDestinataires_(ss);
  var excelBlob = exporterOngletExcel_(ss, contenu.source);

  GmailApp.sendEmail(destinataires.join(','), contenu.sujet, '', {
    htmlBody: contenu.html,
    attachments: [excelBlob]
  });

  Logger.log(contenu.rows.length + ' forfait(s) envoye(s) a ' + destinataires.join(', ') + '.');
}

function simulerForfaitsMargeFaible() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var contenu = construireContenu_(ss);
  var destinataires = lireDestinataires_(ss);

  var options = { htmlBody: contenu.html };
  if (contenu.rows.length) {
    options.attachments = [exporterOngletExcel_(ss, contenu.source)];
  }

  GmailApp.createDraft(destinataires.join(','), '[SIMULATION] ' + contenu.sujet, '', options);

  Logger.log('Brouillon de simulation cree (' + contenu.rows.length + ' forfait(s)).');
}

function construireContenu_(ss) {
  var source = ss.getSheetByName(SOURCE_SHEET_MARGE_FAIBLE);
  if (!source) throw new Error('Onglet "' + SOURCE_SHEET_MARGE_FAIBLE + '" introuvable.');

  var sourceData = source.getDataRange().getValues();
  var header = sourceData[0] || [];
  var rows = sourceData.length > 1 ? sourceData.slice(1) : [];

  // Les extractions natives Sheets ("Extraire") ne redimensionnent pas
  // toujours la grille au nombre reel de resultats - une actualisation
  // avec 0 resultat peut laisser des centaines de lignes vides en
  // dessous (deja vu : 999 lignes vides alors que source vide). On ne
  // garde que les lignes ou la concession ET le N° OR sont renseignes.
  var idxConcessionBrut = header.indexOf('Concession');
  var idxOrBrut = header.indexOf('Numero_OR_DMS');
  rows = rows.filter(function (row) {
    return row[idxConcessionBrut] !== '' && row[idxOrBrut] !== '';
  });

  var dateStr = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'dd/MM/yyyy');
  var sujet = 'Forfaits à marge faible - ' + dateStr;

  if (!rows.length) {
    return {
      source: source,
      rows: rows,
      sujet: sujet,
      html: '<p>Bonjour,</p>'
        + '<p>Aucun forfait factur&eacute; le ' + dateStr + ' ne ressort avec une marge estim&eacute;e sous le seuil de 10&nbsp;% (groupe HESS Automobile) &mdash; rien &agrave; signaler aujourd&#39;hui.</p>'
    };
  }

  var idx = {
    date: header.indexOf('Date_reference'),
    concession: header.indexOf('Concession'),
    forfait: header.indexOf('Libelle_forfait'),
    marge: header.indexOf('Marge_estimee')
  };
  Object.keys(idx).forEach(function (cle) {
    if (idx[cle] === -1) throw new Error('Colonne "' + cle + '" introuvable dans l\'en-tete.');
  });

  rows.sort(function (a, b) { return a[idx.marge] - b[idx.marge]; });

  dateStr = Utilities.formatDate(new Date(rows[0][idx.date]), Session.getScriptTimeZone(), 'dd/MM/yyyy');
  sujet = 'Forfaits à marge faible - ' + dateStr;

  // Pas de tableau dans le corps du mail (juge moins lisible que le
  // fichier Excel joint, retire le 2026-09-29) - un texte explicatif et
  // le cas le plus marquant, le detail complet est dans la piece jointe.
  var pire = rows[0];
  var pluriel = rows.length > 1;
  var html = '<p>Bonjour,</p>'
    + '<p>Hier (' + dateStr + '), ' + rows.length + ' forfait' + (pluriel ? 's' : '')
    + (pluriel ? ' facturés' : ' facturé') + ' au sein du groupe HESS Automobile ressort'
    + (pluriel ? 'ent' : '') + ' avec une marge estim&eacute;e inf&eacute;rieure &agrave; 10&nbsp;%. '
    + 'Vous trouverez le d&eacute;tail complet (toutes les concessions concern&eacute;es) dans le fichier Excel joint.</p>'
    + '<p>Le cas le plus marqu&eacute; du jour : <b>' + pire[idx.forfait] + '</b>, chez <b>' + pire[idx.concession]
    + '</b>, avec une marge estim&eacute;e de <b>' + pire[idx.marge] + '&euro;</b>.</p>';

  return { source: source, rows: rows, sujet: sujet, html: html };
}

function lireDestinataires_(ss) {
  var destSheet = ss.getSheetByName(DESTINATAIRES_SHEET);
  if (!destSheet) throw new Error('Onglet "' + DESTINATAIRES_SHEET + '" introuvable.');

  var destinataires = destSheet.getRange('A2:A' + destSheet.getLastRow()).getValues()
    .map(function (r) { return r[0]; })
    .filter(function (v) { return v; });
  if (!destinataires.length) {
    throw new Error('Aucun destinataire configure dans l\'onglet "' + DESTINATAIRES_SHEET + '".');
  }
  return destinataires;
}

// Colonnes retirees de la piece jointe Excel (mais gardees dans l'onglet
// source "Extrait J-1 - Marges<10%" lui-meme, utiles ailleurs pour la
// transco/le routage - cf. §9 CADRAGE_APV.md) : Code concession et Plaque,
// pas utiles pour Jean/Jerome/Thierry, demande du 2026-09-29.
var COLONNES_EXCLUES_EXCEL = ['Code concession', 'Plaque'];

function exporterOngletExcel_(ss, source) {
  var data = source.getDataRange().getValues();
  var header = data[0];
  var indicesExclus = COLONNES_EXCLUES_EXCEL
    .map(function (nom) { return header.indexOf(nom); })
    .filter(function (i) { return i !== -1; });

  var dataFiltree = data.map(function (row) {
    return row.filter(function (_, i) { return indicesExclus.indexOf(i) === -1; });
  });

  var tempSheet = ss.insertSheet('__export_tmp_' + new Date().getTime());
  var blob;
  try {
    tempSheet.getRange(1, 1, dataFiltree.length, dataFiltree[0].length).setValues(dataFiltree);
    SpreadsheetApp.flush();

    var url = 'https://docs.google.com/spreadsheets/d/' + ss.getId() + '/export?format=xlsx&gid=' + tempSheet.getSheetId();
    var token = ScriptApp.getOAuthToken();
    var response = UrlFetchApp.fetch(url, {
      headers: { Authorization: 'Bearer ' + token },
      muteHttpExceptions: true
    });
    if (response.getResponseCode() !== 200) {
      throw new Error('Export Excel echoue (code ' + response.getResponseCode() + ') - verifier le scope Drive dans appsscript.json (voir Installation en tete de fichier).');
    }
    blob = response.getBlob();
  } finally {
    ss.deleteSheet(tempSheet);
  }

  var dateStr = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  return blob.setName('Forfaits marge faible - ' + dateStr + '.xlsx');
}
