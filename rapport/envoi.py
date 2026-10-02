"""Étapes 5 et 6 du workflow : contrôle des chiffres, envoi des mails, récapitulatif.

- Mode test (seul mode disponible) : chaque mail part vers config.DESTINATAIRES_TEST,
  avec rapport-quotidien@ en copie visible (trace = la boîte mail elle-même).
- Les nombres de chaque mail sont comparés aux faits : ceux qui ne s'y retrouvent pas
  sont signalés dans le récapitulatif (le mail part quand même, WORKFLOW.md §2).
- Un récapitulatif part à la fin vers config.ALERTES, préfixé [ALERTE] s'il y a des
  alertes de contrôle, des mails non envoyés ou des chiffres non retrouvés.

Usage : python -m rapport.envoi --mode test [--sortie build] [--sec]
  --sec : n'envoie rien, affiche ce qui serait envoyé (mise au point locale).
"""

import argparse
import html
import json
import os
import re
import sys

from . import config
from .sheets import envoyer_mail

NOMBRE = re.compile(r"(?<![\w-])-?\d[\d   .]*(?:,\d+)?\s?%?(?![\w-])")
BALISE = re.compile(r"<[^>]+>")


def _valeur(token):
    t = token.replace(" ", "").replace(" ", "").replace(" ", "").strip()
    pct = t.endswith("%")
    t = t.rstrip("%")
    if t.count(".") >= 1 and "," not in t and re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")  # séparateur de milliers « 1.234 »
    t = t.replace(",", ".")
    try:
        return float(t), pct
    except ValueError:
        return None, pct


def nombres_faits(faits):
    vals = set()
    for src in faits["sources"].values():
        for ligne in src["entetes"] + src["lignes"]:
            for cellule in ligne:
                for tok in NOMBRE.findall(cellule):
                    v, pct = _valeur(tok)
                    if v is not None:
                        vals.add(v)
                        if pct:
                            vals.add(v / 100)
    return vals


def _proche(c, f):
    """Égalité à l'arrondi près : à l'unité au-delà de 10, au dixième en dessous."""
    if abs(f) >= 10:
        return abs(c - f) <= max(0.51, abs(f) * 0.002)
    return abs(c - f) <= 0.051


def nombres_non_retrouves(html_mail, vals):
    texte = html.unescape(BALISE.sub(" ", re.sub(r"(?is)<(style|head).*?</\1>", " ", html_mail)))
    texte = re.sub(r"\b\d{1,2}/\d{1,2}(/\d{2,4})?\b", " ", texte)  # dates
    absents = []
    for tok in NOMBRE.findall(texte):
        v, pct = _valeur(tok)
        if v is None or (not pct and float(v).is_integer() and abs(v) < 10):
            continue  # petits entiers (rangs, « 7 jours », « top 5 ») : trop ambigus
        if 2020 <= v <= 2030 and not pct:
            continue  # années
        ok = any(_proche(c, f) for c in (v, -v) for f in vals)
        if pct and not ok:  # « 47 % » peut venir d'une fraction 0,47 dans les faits
            ok = any(abs(c - f) <= 0.0051 for c in (v / 100, -v / 100) for f in vals)
        if not ok:
            absents.append(tok.strip())
    return absents


def recap_html(plan, alertes, envoyes, non_envoyes, douteux):
    def liste(items):
        return "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>" if items else "<p><i>Aucun</i></p>"
    blocs = [
        f"<p>Passage <b>{plan.get('passage') or 'manuel'}</b> du {plan.get('genere_le', '')[:16].replace('T', ' ')} "
        f"— données attendues du {plan.get('date_attendue', '')}.</p>",
        "<h3>Mails envoyés</h3>" + liste(envoyes),
        "<h3>Mails non envoyés</h3>" + liste(non_envoyes),
        "<h3>Alertes de contrôle (les mails sont partis quand même)</h3>"
        + liste([f"[{a['source']}] {a['message']}" for a in alertes]),
        "<h3>Chiffres non retrouvés dans les données (à vérifier)</h3>"
        + liste([f"{m} : {', '.join(v[:15])}{' …' if len(v) > 15 else ''}" for m, v in douteux.items() if v]),
    ]
    return ('<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#2D3250;">'
            + "".join(blocs) + "</div>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="test", choices=["test", "prod"])
    ap.add_argument("--sortie", default="build")
    ap.add_argument("--sec", action="store_true")
    args = ap.parse_args()
    if args.mode == "prod":
        sys.exit("Mode prod pas encore construit : seuls les envois de test sont possibles.")

    chemin_plan = os.path.join(args.sortie, "plan.json")
    if not os.path.exists(chemin_plan):
        plan, alertes = {}, [dict(source="collecte", message="la collecte a échoué avant de produire plan.json "
                                                              "(voir le journal du run GitHub)")]
    else:
        plan = json.load(open(chemin_plan, encoding="utf-8"))
        alertes = json.load(open(os.path.join(args.sortie, "controles.json"), encoding="utf-8"))
        if not plan["mails"] and not plan["non_construits"]:
            print("Rien à envoyer (hors créneau).")
            return

    envoyes, non_envoyes, douteux = [], [], {}
    for nc in plan.get("non_construits", []):
        non_envoyes.append(f"{nc['mail']} — {nc['raison']}")
    for mail in plan.get("mails", []):
        fichier_html = os.path.join(args.sortie, "mails", f"{mail}.html")
        fichier_objet = os.path.join(args.sortie, "mails", f"{mail}.json")
        if not (os.path.exists(fichier_html) and os.path.exists(fichier_objet)):
            non_envoyes.append(f"{mail} — mail non composé par l'étape de synthèse")
            continue
        contenu = open(fichier_html, encoding="utf-8").read()
        objet = json.load(open(fichier_objet, encoding="utf-8"))["objet"]
        faits = json.load(open(os.path.join(args.sortie, "faits", f"{mail}.json"), encoding="utf-8"))
        douteux[mail] = nombres_non_retrouves(contenu, nombres_faits(faits))
        objet = f"[TEST] {objet}"
        if args.sec:
            print(f"(sec) {objet} -> {config.DESTINATAIRES_TEST} cc {config.COPIE} — "
                  f"{len(douteux[mail])} chiffre(s) non retrouvé(s) : {douteux[mail][:10]}")
            envoyes.append(f"{mail} — {objet} (non envoyé : mode sec)")
            continue
        try:
            envoyer_mail(config.DESTINATAIRES_TEST, objet, contenu, copie=config.COPIE)
            envoyes.append(f"{mail} — {objet}")
            print(f"OK  envoyé : {objet}")
        except Exception as e:
            non_envoyes.append(f"{mail} — échec d'envoi : {e}")
            print(f"ERR envoi {mail} : {e}", file=sys.stderr)

    probleme = bool(alertes or non_envoyes or any(douteux.values()))
    objet_recap = (f"{'[ALERTE] ' if probleme else ''}Rapport quotidien — passage "
                   f"{plan.get('passage') or 'manuel'} — {len(envoyes)} envoyé(s), "
                   f"{len(non_envoyes)} non envoyé(s), {len(alertes)} alerte(s)")
    corps = recap_html(plan, alertes, envoyes, non_envoyes, douteux)
    if args.sec:
        print(f"(sec) {objet_recap}")
        open(os.path.join(args.sortie, "recap.html"), "w", encoding="utf-8").write(corps)
    else:
        envoyer_mail(config.ALERTES, objet_recap, corps)
    if non_envoyes:
        sys.exit(1)  # le run apparaît en échec dans GitHub : notification native en plus du mail


if __name__ == "__main__":
    main()
