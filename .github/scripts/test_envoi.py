"""Test de bout en bout depuis GitHub Actions (PC eteint).

1. Echange le refresh token OAuth de rapport-quotidien@hessautomobile.com
   contre un access token (secrets GWS_CLIENT_ID / GWS_CLIENT_SECRET /
   GWS_REFRESH_TOKEN).
2. Lit le titre du Referentiel Concession (verifie l'acces Sheets).
3. Envoie un mail de test au destinataire TEST_TO via l'API Gmail.

Bibliotheque standard uniquement, aucune dependance a installer.
"""

import base64
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.header import Header
from email.mime.text import MIMEText

REFERENTIEL_ID = "1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY"
EXPEDITEUR = "rapport-quotidien@hessautomobile.com"


def http(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def access_token():
    data = urllib.parse.urlencode({
        "client_id": os.environ["GWS_CLIENT_ID"],
        "client_secret": os.environ["GWS_CLIENT_SECRET"],
        "refresh_token": os.environ["GWS_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    return http("https://oauth2.googleapis.com/token", data)["access_token"]


def main():
    token = access_token()
    auth = {"Authorization": f"Bearer {token}"}
    print("OK  token OAuth obtenu")

    titre = http(
        f"https://sheets.googleapis.com/v4/spreadsheets/{REFERENTIEL_ID}"
        "?fields=properties.title",
        headers=auth,
    )["properties"]["title"]
    print(f"OK  lecture Sheets : {titre}")

    now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    run_url = (
        f"{os.environ.get('GITHUB_SERVER_URL', '')}/"
        f"{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/"
        f"{os.environ.get('GITHUB_RUN_ID', '')}"
    )
    html = f"""<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#2D3250;">
<p>Bonjour,</p>
<p>Ce mail a été envoyé <b>depuis GitHub Actions</b>, sans aucun PC allumé,
par la boîte <b>{EXPEDITEUR}</b>.</p>
<p>Lecture Sheets vérifiée : <i>{titre}</i>.</p>
<p style="color:#8A8474;font-size:12px;">Envoi test — {now} — <a href="{run_url}">run GitHub</a></p>
</div>"""
    msg = MIMEText(html, "html", "utf-8")
    msg["From"] = f"{Header('Rapport quotidien HESS', 'utf-8').encode()} <{EXPEDITEUR}>"
    msg["To"] = os.environ["TEST_TO"]
    msg["Subject"] = Header("[TEST] Envoi automatique depuis GitHub Actions", "utf-8")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    sent = http(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        json.dumps({"raw": raw}).encode(),
        {**auth, "Content-Type": "application/json"},
    )
    print(f"OK  mail envoye a {os.environ['TEST_TO']} (id {sent['id']})")


if __name__ == "__main__":
    main()
