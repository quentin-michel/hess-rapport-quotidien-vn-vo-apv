"""Accès Google (Sheets en lecture, Gmail en envoi) pour le rapport quotidien.

Deux modes :
- CI (GitHub Actions) : refresh token OAuth de rapport-quotidien@hessautomobile.com
  dans les variables GWS_CLIENT_ID / GWS_CLIENT_SECRET / GWS_REFRESH_TOKEN.
- Poste local (mise au point) : si ces variables sont absentes, la lecture passe
  par le CLI `gws` (tools/gws) déjà connecté sur le poste. Pas d'envoi en local.

Bibliothèque standard uniquement.
"""

import base64
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from email.header import Header
from email.mime.text import MIMEText

EXPEDITEUR = "rapport-quotidien@hessautomobile.com"
NOM_EXPEDITEUR = "Rapport quotidien HESS"

_token = None


def mode_ci():
    return bool(os.environ.get("GWS_REFRESH_TOKEN"))


def _http(url, data=None, headers=None, essais=3):
    for essai in range(essais):
        try:
            req = urllib.request.Request(url, data=data, headers=headers or {})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            # 429/5xx : on réessaie, le reste remonte tout de suite
            if e.code not in (429, 500, 502, 503, 504) or essai == essais - 1:
                detail = e.read().decode("utf-8", "replace")[:300]
                raise RuntimeError(f"HTTP {e.code} sur {url.split('?')[0]} : {detail}") from e
        except (urllib.error.URLError, TimeoutError):
            if essai == essais - 1:
                raise
        time.sleep(5 * (essai + 1))


def _access_token():
    global _token
    if _token is None:
        data = urllib.parse.urlencode({
            "client_id": os.environ["GWS_CLIENT_ID"],
            "client_secret": os.environ["GWS_CLIENT_SECRET"],
            "refresh_token": os.environ["GWS_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        }).encode()
        _token = _http("https://oauth2.googleapis.com/token", data)["access_token"]
    return _token


def lire_onglet(classeur_id, onglet, plage="A1:CZ5000"):
    """Renvoie l'onglet sous forme de liste de lignes (listes de chaînes, valeurs affichées)."""
    a1 = f"'{onglet}'!{plage}"
    if mode_ci():
        # le nom d'onglet peut contenir un "/" : encodage complet de la plage
        url = (f"https://sheets.googleapis.com/v4/spreadsheets/{classeur_id}/values/"
               f"{urllib.parse.quote(a1, safe='')}?valueRenderOption=FORMATTED_VALUE")
        rep = _http(url, headers={"Authorization": f"Bearer {_access_token()}"})
        return [[str(c) for c in ligne] for ligne in rep.get("values", [])]
    sortie = subprocess.run(
        ["gws", "sheets", "+read", "--spreadsheet", classeur_id, "--range", a1],
        capture_output=True, text=True, encoding="utf-8", timeout=300,
    )
    if sortie.returncode != 0 or sortie.stdout.startswith("gws: erreur"):
        raise RuntimeError(f"lecture impossible ({onglet}) : {(sortie.stdout + sortie.stderr)[:300]}")
    return [ligne.rstrip("\r").split("\t") for ligne in sortie.stdout.split("\n") if ligne.strip("\r")]


def envoyer_mail(destinataires, objet, html, copie=()):
    """Envoie un mail HTML depuis la boîte rapport-quotidien@ (CI uniquement)."""
    if not mode_ci():
        raise RuntimeError("envoi impossible hors GitHub Actions (pas de token Gmail en local)")
    msg = MIMEText(html, "html", "utf-8")
    msg["From"] = f"{Header(NOM_EXPEDITEUR, 'utf-8').encode()} <{EXPEDITEUR}>"
    msg["To"] = ", ".join(destinataires)
    if copie:
        msg["Cc"] = ", ".join(copie)
    msg["Subject"] = Header(objet, "utf-8")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    rep = _http(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        json.dumps({"raw": raw}).encode(),
        {"Authorization": f"Bearer {_access_token()}", "Content-Type": "application/json"},
    )
    return rep["id"]
