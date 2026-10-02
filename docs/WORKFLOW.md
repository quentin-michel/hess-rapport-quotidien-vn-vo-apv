# Workflow GitHub Actions — rapport quotidien VN/VO/APV

**Statut : proposition (2026-10-02), décisions de Corentin intégrées, à valider avec Quentin avant construction.**
Rédigée par Corentin avec Claude. Prolonge le plan validé le 2026-09-30
(`CADRAGE.md` §10) et intègre les leçons de la session du 2026-10-02
(`DATA_MAP_APV.md` §8).

## 1. Vue d'ensemble

```
Déclencheur : cron (planifié) ou lancement manuel
        │
   1. CONTRÔLE ── Sheets à jour (date de réf. = J-1) ? erreurs # ? compteurs = sources ?
        │            ✗ → mail d'alerte à Quentin + Corentin (onglet, date trouvée, problème)
        │                puis ON CONTINUE quand même
        ▼
   2. LECTURE ─── Python lit les onglets par NOM D'EN-TÊTE → faits.json
        │            (une entrée par concession × service, + Directeur et Plaque)
        │            onglet illisible / en-tête disparu → ce mail-là ne part pas (signalé dans l'alerte)
        ▼
   3-4. SYNTHÈSE + MISE EN PAGE ── Claude compose chaque mail HTML complet à partir de
        │            faits.json, de la maquette email-safe du mail et des règles des cadrages
        │            date réelle des données dans l'en-tête de chaque mail (« Données du 30/09 »)
        │            contrôle : chaque nombre du mail est recherché dans faits.json ;
        │            ceux qu'on ne retrouve pas sont listés dans le récapitulatif
        ▼
   5. ENVOI ───── API Gmail depuis rapport-quotidien@hessautomobile.com
        │            mode test → tout vers Quentin + Corentin
        │            mode prod → destinataires des onglets Destinataire (Référentiel Concession)
        ▼
   6. TRACE ──── rapport-quotidien@ en copie VISIBLE (Cc) de chaque mail
                 = l'historique des envois, c'est la boîte mail elle-même
                 + récapitulatif de fin de passage à Quentin + Corentin
```

## 2. Décisions prises (2026-10-02, Corentin)

| Sujet | Décision |
|---|---|
| Contrôles en échec (fraîcheur, erreurs `#`, cohérence) | **On envoie quand même** et on alerte Quentin + Corentin. La date réelle des données est affichée dans chaque mail pour que le lecteur le voie |
| Exception | Onglet illisible ou en-tête attendu introuvable : le mail concerné ne peut pas être construit, il ne part pas (signalé dans l'alerte). Les autres partent |
| Trace des envois | `rapport-quotidien@` en **copie visible (Cc)** de chaque mail |
| Historique des envois | **Stocké dans la boîte mail** elle-même, pas de fichier ni d'onglet `Historique_Envois` |
| Premier mail automatisé | **APV de Dijon** (`OPELFIAT_DIJON`), en mode `test` |
| Passages | **Deux par jour** : ~7h30 (VN, VO) et ~11h45 (APV, Directeur, Plaque) — Sheets VO rafraîchis entre 6h et 7h, classeur APV à 11h00 ; le cron GitHub est en UTC et ignore le changement d'heure → planifier les deux horaires UTC possibles, le script vérifie l'heure de Paris |
| Anti-doublon | **Pas d'anti-doublon** (pas de droit de lecture sur la boîte) : un passage relancé à la main renvoie les mails, à faire en connaissance de cause |
| HTML générés (noms réels) | **Rien n'est stocké côté GitHub** (pas d'artefact, donc pas de durée de conservation à gérer). La seule copie est dans la boîte `rapport-quotidien@`. Pas de mode `apercu` : pour relire un mail avant de l'ouvrir aux destinataires, on utilise le mode `test` |
| Token OAuth | **Validé avec l'IT** (2026-10-02) : le refresh token stocké en secret GitHub convient pour le cron |

## 3. Règles de construction

- **Lecture par nom d'en-tête, jamais par lettre** : les colonnes bougent (réagencement
  d'`Analyse Globale` le 2026-10-02). En-tête attendu absent → arrêt du mail concerné.
- **Contrôles de cohérence**, pas seulement de fraîcheur : un compteur doit être confronté
  à sa liste source (`Plaque APV!G` est resté à 0 sans que rien ne le signale, cf.
  `DATA_MAP_APV.md` §8 pt.7).
- **Composition par Claude** via `anthropics/claude-code-action` (secret
  `CLAUDE_CODE_OAUTH_TOKEN` déjà en place), avec les consignes de
  `rapport/consignes_composition.md` : Claude lit `faits.json`, la maquette du mail et
  les règles des cadrages (`CADRAGE.md` §3/§6/§7/§8, règle effet de mix
  `CADRAGE_APV.md` §14, compteurs plutôt que CA au niveau Plaque), et écrit le HTML
  complet. **Choix de la V1 (2026-10-02)** : Claude compose tout le mail plutôt que de
  remplir des gabarits Python figés — c'est ce qui a produit les mails validés du
  30/09, et les règles de sélection (top 5, omission de bloc, icônes) restent dans les
  cadrages au lieu d'être recodées. Des gabarits déterministes pourront remplacer cette
  étape bloc par bloc si le contrôle des chiffres signale trop d'écarts.
- **Modes** : `test` (tout vers Quentin + Corentin, défaut du cron au début) et `prod`
  (vrais destinataires). Lancement manuel : choix du mode, du périmètre (concession,
  plaque) et de la date.
- **Données personnelles** : les HTML générés contiennent des noms réels — jamais publiés
  comme artefacts ni commités (règle d'anonymisation, `CADRAGE.md` §6).
- **Échec d'un run** : la notification native de GitHub (mail automatique au propriétaire
  du workflow) sert de filet de sécurité si le workflow plante avant d'envoyer l'alerte.

## 4. Organisation du dépôt (construite le 2026-10-02, branche `workflow-dijon`)

```
.github/workflows/rapport-quotidien.yml   ← cron (2 passages) + lancement manuel
rapport/
  config.py                  ← sources (classeur/onglet), mails, périmètre Dijon, destinataires de test
  sheets.py                  ← lecture Sheets + envoi Gmail (token GitHub ; en local : CLI gws, sans envoi)
  collecte.py                ← étapes 1-2 : contrôles + extraits filtrés → build/faits/<mail>.json
  consignes_composition.md   ← étapes 3-4 : consignes données à Claude
  envoi.py                   ← étapes 5-6 : contrôle des chiffres, envoi test, récapitulatif
```

`build/` (faits, mails, récapitulatif) n'est jamais commité : il contient des noms réels.

**Lancer à la main** : onglet Actions → « Rapport quotidien » → *Run workflow*, en
choisissant les mails (`vn,vo,apv,directeur,plaque` par défaut). En local, pour la mise
au point : `python -m rapport.collecte --mails vo --sortie build` puis
`python -m rapport.envoi --sec` (n'envoie rien).

## 5. Ordre de construction

1. Mail **APV Dijon** de bout en bout, en mode `test`.
2. VN et VO Dijon.
3. Mail Directeur Opel/Fiat Dijon et mail Plaque Fiat/Opel.
4. Toute la Plaque Fiat/Opel, puis ouverture aux vrais destinataires (mode `prod`).
