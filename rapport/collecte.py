"""Étapes 1 et 2 du workflow : contrôle des Sheets puis lecture → build/.

Produit :
- build/plan.json       : passage, date attendue, mails à composer, mails non constructibles
- build/controles.json  : alertes (fraîcheur, erreurs #, cohérence, onglets illisibles)
- build/faits/<id>.json  : extrait filtré de chaque onglet utile au mail, où
                          <id> = "<type>__<code concession>" ou "plaque__<code plaque>"

Règle (WORKFLOW.md §2) : un contrôle en échec n'empêche pas l'envoi, il génère une
alerte. Seule exception : un onglet illisible → le mail qui en dépend ne part pas.

Périmètre : une plaque et ses concessions (un job GitHub par plaque, cf. rapport.perimetres).

Usage : python -m rapport.collecte --passage auto|matin|midi [--mails vn,apv]
        [--plaque PLQ_HYUNDAI] [--concessions toutes|CODE1,CODE2] [--sortie build]
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

from . import config
from .sheets import lire_onglet

ERREUR_CELLULE = re.compile(r"^#(REF!|N/A|VALUE!|DIV/0!|NAME\?|ERROR!|NUM!|NULL!)")
DATE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")


def maintenant_paris():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Europe/Paris"))
    except Exception:  # pas de base de fuseaux (poste Windows sans tzdata)
        return dt.datetime.now()


def lire_date(texte):
    m = DATE.search(texte or "")
    return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def cellule(lignes, a1):
    col = 0
    lettres = re.match(r"[A-Z]+", a1).group(0)
    for c in lettres:
        col = col * 26 + ord(c) - 64
    ligne = int(a1[len(lettres):]) - 1
    try:
        return lignes[ligne][col - 1]
    except IndexError:
        return ""


def referentiel_plaque(plaque):
    """Concessions de la plaque {code: nom} et nom de la plaque, lus dans le Référentiel."""
    lignes = lire_onglet(config.REFERENTIEL, "Concessions_Plaques", "A1:D500")
    entete = lignes[0]
    i_code, i_nom = entete.index("Code_Concession"), entete.index("Nom_Concession")
    i_plaque, i_nom_plaque = entete.index("Code_Plaque"), entete.index("Nom_Plaque")
    concessions, nom_plaque = {}, plaque
    for l in lignes[1:]:
        if len(l) > i_nom_plaque and l[i_plaque] == plaque:
            concessions[l[i_code]] = l[i_nom]
            nom_plaque = l[i_nom_plaque]
    return dict(sorted(concessions.items())), nom_plaque


def filtrer(lignes, codes):
    """Garde les 2 premières lignes (en-têtes) et les lignes contenant un code du périmètre."""
    entetes = lignes[:2]
    corps = [l for l in lignes[2:] if any(c.strip() in codes for c in l)]
    return entetes, corps


def controler_fraicheur(source_id, conf, lignes, entetes, corps, attendue, alertes):
    regle = conf.get("fraicheur")
    if not regle:
        return None
    type_, cible = regle.split(":", 1)
    if type_ == "cellule":
        dates = [lire_date(cellule(lignes, cible))]
    else:
        en_tete = next((e for e in entetes if cible in e), None)
        if en_tete is None:
            alertes.append(dict(niveau="alerte", source=source_id,
                                message=f"colonne de date « {cible} » introuvable"))
            return None
        i = en_tete.index(cible)
        dates = [lire_date(l[i]) for l in corps if len(l) > i]
    dates = [d for d in dates if d]
    if not dates:
        alertes.append(dict(niveau="alerte", source=source_id, message="aucune date de référence lisible"))
        return None
    trouvee = max(dates)
    if trouvee != attendue:
        alertes.append(dict(niveau="alerte", source=source_id,
                            message=f"données du {trouvee:%d/%m/%Y}, attendu {attendue:%d/%m/%Y} (J-1)"))
    return trouvee.isoformat()


def controler_erreurs(source_id, entetes, corps, alertes):
    n = sum(1 for l in entetes + corps for c in l if ERREUR_CELLULE.match(c.strip()))
    if n:
        alertes.append(dict(niveau="alerte", source=source_id,
                            message=f"{n} cellule(s) en erreur (#REF!, #VALUE!…) dans les lignes du périmètre"))


def controler_coherence_plaque_apv(cache, plaque, alertes):
    """Plaque APV « pièces en marge négative » doit égaler le nombre de lignes de la liste
    Analyse pièces client J-1 pour la plaque (panne silencieuse du 2026-10-02)."""
    plq, pieces = cache.get("apv_plaque"), cache.get("apv_pieces_a_perte")
    if not plq or not pieces:
        return
    ent_plq = plq[1] if len(plq) > 1 else []
    col = next((i for i, e in enumerate(ent_plq) if "marge négative" in e.lower()), None)
    ent_p = pieces[0]
    if col is None or "Plaque" not in ent_p:
        alertes.append(dict(niveau="alerte", source="apv_plaque",
                            message="contrôle pièces à perte impossible (en-tête introuvable)"))
        return
    attendu = sum(1 for l in pieces[1:] if len(l) > ent_p.index("Plaque") and l[ent_p.index("Plaque")] == plaque)
    ligne = next((l for l in plq[2:] if l and l[0] == plaque), None)
    valeur = ligne[col] if ligne and len(ligne) > col else ""
    if str(attendu) != valeur.strip():
        alertes.append(dict(niveau="alerte", source="apv_plaque",
                            message=f"{plaque} : « pièces en marge négative » = {valeur or 'vide'} "
                                    f"alors que la liste Analyse pièces client J-1 en compte {attendu}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passage", default="auto", choices=["auto", "matin", "midi"])
    ap.add_argument("--mails", default="", help="types imposés, ex. vn,apv (ignore le passage)")
    ap.add_argument("--plaque", default="", help="code plaque (défaut : 1re entrée de config.PERIMETRES_CRON)")
    ap.add_argument("--concessions", default="",
                    help="« toutes » ou codes séparés par des virgules")
    ap.add_argument("--sortie", default="build")
    args = ap.parse_args()

    now = maintenant_paris()
    attendue = now.date() - dt.timedelta(days=1)
    passage = args.passage
    if passage == "auto":
        passage = next((p for p, h in config.HEURE_PASSAGE.items() if h == now.hour), None)
    if args.mails:
        types = [m.strip() for m in args.mails.split(",") if m.strip()]
    elif passage:
        types = [m for m, c in config.MAILS.items() if c["passage"] == passage]
    else:
        types = []

    os.makedirs(os.path.join(args.sortie, "faits"), exist_ok=True)
    plan = dict(passage=passage, date_attendue=attendue.isoformat(),
                genere_le=now.isoformat(timespec="minutes"), mails=[], non_construits=[])
    alertes = []
    if not types:
        print(f"Hors créneau ({now:%H:%M} à Paris) : rien à faire.")
        json.dump(plan, open(os.path.join(args.sortie, "plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(alertes, open(os.path.join(args.sortie, "controles.json"), "w", encoding="utf-8"))
        return

    plaque = args.plaque or config.PERIMETRES_CRON[0]["plaque"]
    toutes, nom_plaque = referentiel_plaque(plaque)
    if not toutes:
        sys.exit(f"Plaque {plaque} inconnue du Référentiel (onglet Concessions_Plaques).")
    defaut = config.PERIMETRES_CRON[0]["concessions"]
    choix = args.concessions or ("" if args.plaque else defaut if isinstance(defaut, str) else ",".join(defaut))
    if not choix or choix.strip().lower() == "toutes":
        concessions = toutes
    else:
        codes = [c.strip() for c in choix.split(",") if c.strip()]
        inconnues = [c for c in codes if c not in toutes]
        if inconnues:
            sys.exit(f"Concession(s) hors de la plaque {plaque} : {', '.join(inconnues)}")
        concessions = {c: toutes[c] for c in codes}
    plan["perimetre"] = dict(plaque=plaque, nom_plaque=nom_plaque, concessions=concessions)
    print(f"Périmètre : {nom_plaque} — {len(concessions)} concession(s) : {', '.join(concessions)}")

    # instances de mail : (id, type, codes du périmètre, contexte)
    instances = []
    for t in types:
        if config.MAILS[t]["perimetre"] == "plaque":
            instances.append((f"{t}__{plaque}", t, {plaque, *toutes},
                              dict(plaque=plaque, nom_plaque=nom_plaque, concessions_plaque=toutes)))
        else:
            for code, nom in concessions.items():
                instances.append((f"{t}__{code}", t, {code},
                                  dict(concession=code, nom_concession=nom, plaque=plaque, nom_plaque=nom_plaque)))

    cache, illisibles = {}, {}
    for source_id in sorted({s for t in types for s in config.MAILS[t]["sources"]}):
        conf = config.SOURCES[source_id]
        try:
            cache[source_id] = lire_onglet(conf["classeur"], conf["onglet"], conf.get("plage", "A1:CZ5000"))
            print(f"OK  {source_id} ({len(cache[source_id])} lignes)")
        except Exception as e:
            illisibles[source_id] = str(e)
            alertes.append(dict(niveau="bloquant", source=source_id, message=f"onglet illisible : {e}"))
            print(f"ERR {source_id} : {e}", file=sys.stderr)

    deja_controle = set()
    for mail_id, t, codes, contexte in instances:
        conf_mail = config.MAILS[t]
        manquantes = [s for s in conf_mail["sources"] if s in illisibles]
        if manquantes:
            plan["non_construits"].append(dict(mail=mail_id, raison="onglet(s) illisible(s) : " + ", ".join(manquantes)))
            continue
        nom = contexte.get("nom_concession") or nom_plaque
        faits = dict(mail=mail_id, type=t, titre=f"{conf_mail['libelle']} — {nom}", maquette=conf_mail["maquette"],
                     date_attendue=attendue.isoformat(), perimetre=sorted(codes), **contexte, sources={})
        dates = []
        for source_id in conf_mail["sources"]:
            conf = config.SOURCES[source_id]
            lignes = cache[source_id]
            entetes, corps = filtrer(lignes, codes)
            # alertes de contrôle une seule fois par (source, périmètre), préfixées du périmètre
            cle = (source_id, tuple(sorted(codes)))
            alertes_mail = []
            date_trouvee = controler_fraicheur(source_id, conf, lignes, entetes, corps, attendue, alertes_mail)
            controler_erreurs(source_id, entetes, corps, alertes_mail)
            if cle not in deja_controle:
                deja_controle.add(cle)
                for a in alertes_mail:
                    a["message"] = f"[{contexte.get('concession', plaque)}] {a['message']}"
                    alertes.append(a)
            if date_trouvee:
                dates.append(date_trouvee)
            faits["sources"][source_id] = dict(service=conf["service"], onglet=conf["onglet"],
                                               date_donnees=date_trouvee, entetes=entetes, lignes=corps)
        # date affichée dans le mail : la plus ancienne date trouvée (le lecteur doit voir le retard)
        faits["date_donnees"] = min(dates) if dates else None
        json.dump(faits, open(os.path.join(args.sortie, "faits", f"{mail_id}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        plan["mails"].append(mail_id)

    if "plaque" in types or "apv" in types:
        controler_coherence_plaque_apv(cache, plaque, alertes)

    json.dump(plan, open(os.path.join(args.sortie, "plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(alertes, open(os.path.join(args.sortie, "controles.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Passage {passage} — {len(plan['mails'])} mail(s) : {plan['mails']} — "
          f"non construits : {plan['non_construits']} — alertes : {len(alertes)}")


if __name__ == "__main__":
    main()
