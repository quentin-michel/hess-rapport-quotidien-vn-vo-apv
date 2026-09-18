# gws — Google Workspace CLI minimal (lecture Sheets)

Recree le 2026-09-18 apres la perte du binaire original suite a un crash/
reinstall de l'appli Claude (voir `docs/CADRAGE.md` pour l'historique complet
et le contexte d'usage). Reproduit volontairement la meme syntaxe que
documentee a l'origine, pour ne rien casser dans les habitudes/commandes deja
notees ailleurs dans le projet.

**Important** : cet outil vit dans ce depot (versionne, partage entre Quentin
et Corentin) plutot que dans un dossier propre a l'appli — c'est justement
pour eviter de reperdre l'outil si l'appli plante a nouveau.

## Installation (a faire sur chaque machine)

Prerequis : Python >= 3.9, avec `pip`.

```bash
cd tools/gws
python -m pip install -e .
```

Ceci installe une commande `gws` (via un script `gws.exe`/`gws`) dans le
dossier `Scripts`/`bin` de l'environnement Python utilise. **Verifier que ce
dossier est bien dans le `PATH`** (sur Windows, `python -m pip show gws` puis
`Location:` indique le prefixe ; le sous-dossier `Scripts` doit etre dans le
`PATH` utilisateur — a ajouter une fois pour toutes si besoin).

## Configuration OAuth (une fois par machine/compte)

Il faut un fichier `client_secret.json` (client OAuth "Desktop app" du projet
GCP `controlegestion`) place dans `~/.config/gws/client_secret.json` — a
obtenir aupres de Quentin/Corentin s'il est absent (ne pas versionner ce
fichier, c'est un secret).

```bash
gws auth login --readonly --services sheets
```

Ouvre une page de connexion Google dans le navigateur, puis sauvegarde le
token dans `~/.config/gws/token.json` (se rafraichit automatiquement ensuite,
tant que le refresh token n'est pas revoque).

## Commandes

Lister les onglets d'un classeur :

```bash
gws sheets spreadsheets get --params '{"spreadsheetId": "ID_DU_CLASSEUR"}'
```

Lire une plage precise d'un onglet :

```bash
gws sheets +read --spreadsheet ID_DU_CLASSEUR --range "NomOnglet!A1:Z100"
```

Un onglet de type `DATA_SOURCE` (connecteur BigQuery natif Sheets) renvoie une
erreur `Unable to parse range` a la lecture — normal, voir `docs/CADRAGE.md`
et `docs/CADRAGE_APV.md` §5 (lire l'onglet GRID correspondant a la place).

## Limites connues (identiques a l'outil original)

- Lecture seule uniquement (scope `spreadsheets.readonly`) — ecrire dans un
  Sheet reste toujours fait a la main par Quentin/Corentin, jamais par cet
  outil ni par Claude (decision de principe du projet).
- Un resultat de plusieurs Mo (au-dela d'un ou deux milliers de lignes) reste
  trop volumineux pour etre charge d'un coup dans le contexte de Claude — d'ou
  le principe des onglets "prets a publier" deja agreges/bornes cote Sheet.
