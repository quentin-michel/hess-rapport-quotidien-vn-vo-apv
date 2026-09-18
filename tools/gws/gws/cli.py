"""gws - Google Workspace CLI minimal (lecture seule Google Sheets).

Recree pour le projet hess-rapport-quotidien-vn-vo-apv apres la perte du
binaire original (voir docs/CADRAGE.md). Reproduit volontairement la syntaxe
documentee a l'origine :

    gws auth login --readonly --services sheets
    gws sheets spreadsheets get --params '{"spreadsheetId": "ID"}'
    gws sheets +read --spreadsheet ID --range "Onglet!A1:Z100"

Config/token stockes dans ~/.config/gws (independant du dossier de l'appli
Claude, pour survivre a une reinstallation de l'appli).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

CONFIG_DIR = Path.home() / ".config" / "gws"
CLIENT_SECRET_PATH = CONFIG_DIR / "client_secret.json"
TOKEN_PATH = CONFIG_DIR / "token.json"

SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"

SERVICE_SCOPES = {
    "sheets": "https://www.googleapis.com/auth/spreadsheets.readonly",
}


def die(message: str, code: int = 1) -> None:
    print(f"gws: erreur: {message}", file=sys.stderr)
    sys.exit(code)


def resolve_scopes(services: str, readonly: bool) -> list[str]:
    if not readonly:
        die(
            "seul le mode --readonly est supporte pour l'instant "
            "(coherent avec la decision du projet, voir docs/CADRAGE.md)"
        )
    scopes = []
    for name in services.split(","):
        name = name.strip()
        if name not in SERVICE_SCOPES:
            die(f"service inconnu: {name!r} (disponible: {', '.join(SERVICE_SCOPES)})")
        scopes.append(SERVICE_SCOPES[name])
    if not scopes:
        die("aucun --services fourni")
    return scopes


def cmd_auth_login(args: argparse.Namespace) -> None:
    if not CLIENT_SECRET_PATH.exists():
        die(
            f"fichier client OAuth introuvable : {CLIENT_SECRET_PATH}\n"
            "  (client_secret.json du projet GCP, a obtenir aupres de Quentin/IT si absent)"
        )
    scopes = resolve_scopes(args.services, args.readonly)
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), scopes)
    creds = flow.run_local_server(port=0)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    print(f"Authentifie. Token sauvegarde dans {TOKEN_PATH}")


def get_credentials() -> Credentials:
    if not TOKEN_PATH.exists():
        die("non authentifie - lancez d'abord: gws auth login --readonly --services sheets")
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def api_get(url: str, params: dict | None = None) -> dict:
    creds = get_credentials()
    resp = requests.get(
        url,
        params=params,
        headers={"Authorization": f"Bearer {creds.token}"},
        timeout=30,
    )
    if not resp.ok:
        die(f"appel API echoue ({resp.status_code}): {resp.text}")
    return resp.json()


def cmd_sheets_get(args: argparse.Namespace) -> None:
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        die(f"--params invalide (JSON attendu): {exc}")
    spreadsheet_id = params.get("spreadsheetId")
    if not spreadsheet_id:
        die("--params doit contenir spreadsheetId")
    data = api_get(
        f"{SHEETS_API}/{spreadsheet_id}",
        params={"fields": "properties.title,sheets.properties"},
    )
    title = data.get("properties", {}).get("title", "?")
    print(f"Classeur: {title}")
    for sheet in data.get("sheets", []):
        props = sheet.get("properties", {})
        print(f"  - {props.get('title')}  (type={props.get('sheetType', 'GRID')}, id={props.get('sheetId')})")


def cmd_sheets_read(args: argparse.Namespace) -> None:
    data = api_get(f"{SHEETS_API}/{args.spreadsheet}/values/{args.range}")
    rows = data.get("values", [])
    if not rows:
        print("(plage vide)", file=sys.stderr)
        return
    for row in rows:
        print("\t".join(str(cell) for cell in row))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gws", description=__doc__)
    subparsers = parser.add_subparsers(dest="group", required=True)

    auth = subparsers.add_parser("auth", help="authentification OAuth2")
    auth_sub = auth.add_subparsers(dest="action", required=True)
    login = auth_sub.add_parser("login", help="ouvre le flux OAuth2 dans le navigateur")
    login.add_argument("--readonly", action="store_true")
    login.add_argument("--services", required=True, help="ex: sheets")
    login.set_defaults(func=cmd_auth_login)

    sheets = subparsers.add_parser("sheets", help="commandes Google Sheets")
    sheets_sub = sheets.add_subparsers(dest="action", required=True)

    read = sheets_sub.add_parser("+read", help="lit une plage precise d'un onglet")
    read.add_argument("--spreadsheet", required=True, help="ID du classeur")
    read.add_argument("--range", required=True, help='ex: "Onglet!A1:Z100"')
    read.set_defaults(func=cmd_sheets_read)

    spreadsheets = sheets_sub.add_parser("spreadsheets", help="metadonnees du classeur")
    spreadsheets_sub = spreadsheets.add_subparsers(dest="subaction", required=True)
    get = spreadsheets_sub.add_parser("get", help="liste les onglets d'un classeur")
    get.add_argument("--params", required=True, help='JSON, ex: \'{"spreadsheetId": "ID"}\'')
    get.set_defaults(func=cmd_sheets_get)

    return parser


def main(argv: list[str] | None = None) -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
