"""Configuration du rapport quotidien : sources, mails, périmètre, destinataires de test.

Les lettres de colonnes ne sont jamais utilisées : chaque onglet est lu en entier et
filtré sur les lignes qui contiennent un code du périmètre (code concession ou code
plaque). Les en-têtes (2 premières lignes) sont toujours conservés pour que la
lecture se fasse par nom de colonne.
"""

REFERENTIEL = "1L-wJkip_8gqk0B4C4edEf_ZIRqDCOMu6KDciFQ4WPnY"

# Périmètre pilote (WORKFLOW.md §5) : Opel/Fiat Dijon et sa plaque.
CONCESSION = "OPELFIAT_DIJON"
PLAQUE = "PLQ_FIATOPEL"

# Mode test : seuls destinataires possibles. Le mode prod n'est pas encore construit.
DESTINATAIRES_TEST = [
    "quentinmichel@hessautomobile.com",
    "corentinlaas@hessautomobile.com",
]
COPIE = ["rapport-quotidien@hessautomobile.com"]
ALERTES = DESTINATAIRES_TEST

# plage : zone lue (par défaut A1:CZ5000) — à réduire sur les gros onglets pour rester
# sous le délai de l'API.
# Contrôles de fraîcheur : "colonne:<en-tête>" (toutes les lignes du périmètre) ou
# "cellule:<A1>" (une cellule fixe). La valeur attendue est J-1 (heure de Paris).
SOURCES = {
    # --- VN ---
    "vn_bloc1_leads": dict(service="VN", classeur="1oQzC5CV8Xqb6oTVAmNakcn3pSJD0yqP1eSdE7guHn80",
                           onglet="BLOC 1 Leads VN", fraicheur="colonne:Date_reference"),
    "vn_bloc2_commandes_facturations": dict(service="VN", classeur="14iuxhKZr34StlxCn8IodM9iquoqH9wnc5EhsBYxBUDE",
                                            onglet="BLOC 2"),
    "vn_bloc3_stock_synthese": dict(service="VN", classeur="10cOmCg_e8JKKpaHY0pI6QTPWLehO_VVfVAU6bXAROWE",
                                    onglet="BLOC 3 P1 Stock VN_VD"),
    "vn_bloc3_stock_detail": dict(service="VN", classeur="10cOmCg_e8JKKpaHY0pI6QTPWLehO_VVfVAU6bXAROWE",
                                  onglet="BLOC 3 P2 Stock VN_VD"),
    "vn_bloc4_couverture": dict(service="VN", classeur="10cOmCg_e8JKKpaHY0pI6QTPWLehO_VVfVAU6bXAROWE",
                                onglet="BLOC 4 Couverture VN"),
    "vn_bloc5_top3_exces": dict(service="VN", classeur="10cOmCg_e8JKKpaHY0pI6QTPWLehO_VVfVAU6bXAROWE",
                                onglet="BLOC 5 TOP 3"),
    "vn_bloc6_anomalies_ventes": dict(service="VN", classeur="16xQnrbCZpPP2sDy4WxJvglRdIVYkwx31wiWC_n0lKcg",
                                      onglet="BLOC 6 - Anomalie Vente VN-VD"),
    # --- VO ---
    "vo_bloc1_leads": dict(service="VO", classeur="14TWu4moVg6lSOT5KLjnTCumeZcx-3M9Xg2vqpt4-ka4",
                           onglet="BLOC 1 Leads", fraicheur="colonne:Date_reference"),
    "vo_bloc2_offres": dict(service="VO", classeur="1C1jMlaD8M1TearS98aiC_J3t6lieq7sp2GdMq_fKDzI",
                            onglet="BLOC 2 Offre", fraicheur="colonne:Date_reference"),
    "vo_bloc9_commandes_facturations": dict(service="VO", classeur="1C1jMlaD8M1TearS98aiC_J3t6lieq7sp2GdMq_fKDzI",
                                            onglet="BLOC 2_1 Com_Fact_Obj"),
    "vo_bdc_ouverts": dict(service="VO", classeur="1C1jMlaD8M1TearS98aiC_J3t6lieq7sp2GdMq_fKDzI",
                           onglet="BLOC 2_2 BDC Ouvert"),
    "vo_bloc3_anomalies_achat": dict(service="VO", classeur="1PdjQzWi0Gbn1KhkaUvC6wPbdyiBIovI_TeB_YhyAraU",
                                     onglet="BLOC 3 Ano Achat"),
    "vo_bloc4_stock_synthese": dict(service="VO", classeur="1NhHCqRM54yWcMomE1Qd0tKGG9KWRV8tvewq9hhCIPfM",
                                    onglet="BLOC 4 Stock_P1"),
    "vo_bloc4_stock_detail": dict(service="VO", classeur="1NhHCqRM54yWcMomE1Qd0tKGG9KWRV8tvewq9hhCIPfM",
                                  onglet="BLOC 4 Stock_P2"),
    "vo_bloc5_couverture": dict(service="VO", classeur="1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU",
                                onglet="BLOC 5 Couverture_VO", plage="A1:Z300"),
    "vo_bloc6_exces_stock": dict(service="VO", classeur="1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU",
                                 onglet="BLOC 6 Excès_Stock", plage="A1:J6000"),
    "vo_bloc7_sante_plaque": dict(service="VO", classeur="1Bw1oFGQD3ejSIScUvUl5pOipe4P5FSSkgEpsIr5BTqU",
                                  onglet="BLOC 7 Santé_Plaque", plage="A1:M6000"),
    "vo_bloc8_anomalies_ventes": dict(service="VO", classeur="110ih-4TOZL8qJD4CHz9avQoHXCN70wU5Pdmcmga1fwI",
                                      onglet="Bloc 8 Ano_Vente"),
    # --- APV ---
    "apv_analyse_globale": dict(service="APV", classeur="1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw",
                                onglet="Analyse Globale", plage="A1:CZ300", fraicheur="cellule:B1"),
    "apv_encours_prioritaires": dict(service="APV", classeur="1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw",
                                     onglet="Encours prioritaires"),
    "apv_pieces_a_perte": dict(service="APV", classeur="1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw",
                               onglet="Analyse pièces client J-1"),
    "apv_efficience_ci": dict(service="APV", classeur="1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw",
                              onglet="Efficience OR CI trop élevé"),
    "apv_remises_elevees": dict(service="APV", classeur="1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw",
                                onglet="Taux remise MO/PR interne élevé"),
    "apv_plaque": dict(service="APV", classeur="1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw",
                       onglet="Plaque APV", fraicheur="cellule:B1"),
    "apv_forfaits_marge_faible": dict(service="APV", classeur="1T_BKjedX0yH7ENq4Z_88OWlGnBUu6RSez5ohLb0YscU",
                                      onglet="Extrait J-1 - Marges<10%"),
    "apv_remises_forcees": dict(service="APV", classeur="1ZZ2Y1EtbonrgOeJ0Zf81XngcZCiifCvtAP2dHczl7GY",
                                onglet="Prix/Remises forcés"),
}

_VN = [s for s, c in SOURCES.items() if c["service"] == "VN"]
_VO = [s for s, c in SOURCES.items() if c["service"] == "VO"]
_APV = [s for s, c in SOURCES.items() if c["service"] == "APV"]

# perimetre : "concession" = lignes du code concession ; "plaque" = code plaque + toutes
# les concessions de la plaque (lues dans le Référentiel).
MAILS = {
    "vn": dict(titre="VN — Opel/Fiat Dijon", passage="matin", perimetre="concession",
               sources=_VN, maquette="docs/mockup_email_vn.html"),
    "vo": dict(titre="VO — Opel/Fiat Dijon", passage="matin", perimetre="concession",
               sources=_VO, maquette="docs/mockup_email_vo.html"),
    "apv": dict(titre="APV — Opel/Fiat Dijon", passage="midi", perimetre="concession",
                sources=_APV, maquette="docs/mockup_email_apv_v2_safe.html"),
    "directeur": dict(titre="Directeur — Opel/Fiat Dijon", passage="midi", perimetre="concession",
                      sources=_VN + _VO + _APV, maquette="docs/mockup_email_directeur.html"),
    "plaque": dict(titre="Plaque Fiat/Opel", passage="midi", perimetre="plaque",
                   sources=_VN + _VO + _APV, maquette="docs/mockup_email_plaque.html"),
}

# Heure locale (Europe/Paris) de chaque passage planifié : le cron GitHub est en UTC et
# ignore le changement d'heure, il est donc planifié sur les deux horaires UTC possibles
# et le script ne garde que celui qui tombe à la bonne heure de Paris.
HEURE_PASSAGE = {"matin": 7, "midi": 11}
