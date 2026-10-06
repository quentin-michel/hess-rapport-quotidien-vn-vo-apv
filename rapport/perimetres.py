"""Étape 0 du workflow : liste des plaques à traiter, une par job GitHub (matrice).

Écrit dans $GITHUB_OUTPUT (ou affiche en local) :
- a_faire  : « oui » s'il y a quelque chose à faire (hors créneau = « non »)
- passage  : matin, midi ou vide (lancement manuel)
- mails    : types de mail à générer, ex. « vn,vo »
- matrice  : JSON [{"plaque": "...", "concessions": "toutes" | "CODE1,CODE2"}, ...]
- attendues: codes plaque séparés par des virgules (contrôle du récapitulatif)

Passages planifiés : config.PERIMETRES_CRON. Lancement manuel : --plaque reçoit un code,
plusieurs codes séparés par des virgules, ou « toutes » (toutes les plaques du
Référentiel) ; --concessions ne s'applique que si une seule plaque est choisie.

Usage : python -m rapport.perimetres [--passage auto] [--mails vn,apv] [--plaque PLQ_X] [--concessions toutes]
"""

import argparse
import json
import os

from . import config
from .collecte import maintenant_paris
from .sheets import lire_onglet


def plaques_referentiel():
    lignes = lire_onglet(config.REFERENTIEL, "Concessions_Plaques", "A1:D500")
    i_plaque = lignes[0].index("Code_Plaque")
    return sorted({l[i_plaque] for l in lignes[1:] if len(l) > i_plaque and l[i_plaque]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passage", default="auto", choices=["auto", "matin", "midi"])
    ap.add_argument("--mails", default="")
    ap.add_argument("--plaque", default="")
    ap.add_argument("--concessions", default="")
    args = ap.parse_args()

    passage = args.passage
    if passage == "auto":
        passage = next((p for p, h in config.HEURE_PASSAGE.items() if h == maintenant_paris().hour), None)
    if args.mails:
        types = [m.strip() for m in args.mails.split(",") if m.strip()]
    elif passage:
        types = [m for m, c in config.MAILS.items() if c["passage"] == passage]
    else:
        types = []

    matrice = []
    if types:
        if args.plaque:
            demandees = args.plaque.strip()
            plaques = plaques_referentiel() if demandees.lower() == "toutes" else \
                [p.strip() for p in demandees.split(",") if p.strip()]
            concessions = args.concessions.strip() if len(plaques) == 1 and args.concessions.strip() else "toutes"
            matrice = [dict(plaque=p, concessions=concessions) for p in plaques]
        else:
            matrice = [dict(plaque=p["plaque"],
                            concessions=p["concessions"] if isinstance(p["concessions"], str)
                            else ",".join(p["concessions"]))
                       for p in config.PERIMETRES_CRON]

    sorties = dict(a_faire="oui" if matrice else "non", passage=passage or "", mails=",".join(types),
                   matrice=json.dumps(matrice, ensure_ascii=False),
                   attendues=",".join(m["plaque"] for m in matrice))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            for k, v in sorties.items():
                f.write(f"{k}={v}\n")
    for k, v in sorties.items():
        print(f"{k} = {v}")


if __name__ == "__main__":
    main()
