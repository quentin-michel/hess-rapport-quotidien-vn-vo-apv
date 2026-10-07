# Mail Directeur de concession (type `directeur`)

Un mail par concession, niveau 2 de diffusion. Maquette : `docs/mockup_email_directeur.html`.
Faits : toutes les sources VN + VO + APV de la concession.

**À lire avec** : `consignes_composition.md`, `regles/commun.md`, et `regles/vn.md`,
`regles/vo.md`, `regles/apv.md`. **Décision : les barèmes météo et les seuils de chaque
service ne sont pas recopiés ici** ; ils vivent dans les fichiers de service (source
unique, pour qu'une icône Directeur soit toujours identique à celle du mail Service du
même jour). Ce fichier ne dit que ce qui change au niveau Directeur.

## 1. Principe
Synthèse condensée qui ne signale que l'essentiel et le significatif des 3 services, pas
le détail complet. (CADRAGE §7)

## 2. Structure (ordre fixe)
1. En-tête : « Rapport quotidien · Synthèse Direction », `nom_concession`, date des données.
2. **3 mini-cartes météo VN, VO, APV** (dans cet ordre) : icône du service + le fait le
   plus marquant du service en une ligne courte (ex. « Commandes -50% », « 1 CL à 73j »).
3. **Synthèse IA — vue d'ensemble** (cross-service, voir §3).
4. Blocs **VN → VO → APV**, chacun : bandeau titre, **badge** (chiffre clé du bloc),
   **paragraphe de 2 phrases maximum**. **Aucun tableau détaillé.**
5. Pied de page.

(CADRAGE §7)

## 3. Synthèse IA cross-service
- Distincte des synthèses Service : elle **recoupe et priorise entre VN, VO et APV**.
- **Une phrase par service ayant un signal**, ordre VN → VO → APV ; on peut ouvrir sur le
  point le plus préoccupant du jour.
- Mêmes règles de rédaction que `commun.md` §2 (factuel, dossiers concrets, pas de jargon).

(CADRAGE §7)

## 4. Blocs service
- **Bloc entier omis** (ni titre, ni « Rien à signaler ») si le service n'a rien de
  significatif ce jour-là.
- Factuel, **dossiers concrets cités** : immatriculation / VIN / n° de dossier / n° OR.
- **Positif comme négatif** : une tendance positive notable (ex. facturations VO +17 % sur
  l'an dernier) a sa place au même titre qu'une alerte.
- Badge : couleurs de la maquette (rouge `#B0413E` sur `#F6EADA` pour un point négatif,
  or `#A88A56` sur `#F1E7D3` pour un point de vigilance) ; chiffres positifs en `#2E7D5F`.
- Ce qui est « significatif » = ce que le mail Service du même service ferait remonter dans
  sa synthèse (seuils dans vn.md / vo.md / apv.md). Repères : VN = commandes/facturations
  vs objectif et l'an dernier, anomalies ventes, leads non traités ; VO =
  anomalies achat/vente, commandes/facturations vs objectif, couverture ; APV = voir §6.

(CADRAGE §7)

## 5. Icônes météo des mini-cartes
**Pas de nouveau score pour ce niveau** : chaque icône est celle du service, calculée avec
le barème du service sur les faits du jour.
- **VO** : barème de `vo.md` §3 (= CADRAGE_VO §15 : anomalies ouvertes, tendance ventes 30 j,
  couverture). Volume non significatif → **pas d'icône** (carte sans emoji).
- **APV** : barèmes de `apv.md` §8-9 (= CADRAGE_APV §12.6 Atelier, §12.7 Magasin). Le mail
  Service a deux icônes, la mini-carte une seule : **afficher la plus défavorable des
  deux** et faire porter la ligne de la carte sur le département concerné (choix par
  défaut, non tranché dans le cadrage).
- **VN** : barème brouillon de `vn.md` §2 (aucun barème validé dans CADRAGE_VN, score de
  la maquette VN = brouillon).
- Aucun de ces scores n'est calculé dans les Sheets : ne jamais le présenter comme tel
  (pas de mention « score » dans le mail).
- Service sans bloc (rien de significatif) : garder sa mini-carte (icône du jour) avec une
  ligne neutre courte (choix par défaut, non tranché dans le cadrage).

(CADRAGE §7, §9 pt 9 ; consignes règle 6)

## 6. Bloc APV : compteurs de problèmes, pas de CA
- Remonter des **compteurs/signaux de problème** : efficience basse, encours en jours de CA
  (surveillance/alerte/critique), OR en cession interne à efficience trop élevée, remises
  élevées, pièces vendues à perte à des clients (Atelier : hors forfaits, hors intragroupe), forfaits à marge < 10 %, remises forcées.
- **Jamais de CA ni d'objectif APV** (CA MO, CA PR interne/externe, % de réalisation).
- **Exception (décidée le 2026-10-06) — malfaçons et gestes commerciaux** : coût de
  non-qualité, affiché **en montant** :
  - montant d'**hier** (`Analyse Globale`, en-tête « Malfaçons J-1 ») ;
  - **cumul du mois** (« Malfaçons MTD ») ;
  - **% du CA MO du mois** (« % Malfaçons MTD »). Avant le 10 du mois (date des données),
    préciser que le ratio est encore peu significatif (quelques jours de CA).
  - Mention **omise** si aucune malfaçon hier et un cumul du mois non significatif
    (repère : paliers de la météo Atelier, hier ≥ 150 € ou % du mois > 4 % à partir du 10).
  - Le CA MO ne s'affiche pas : il ne sert que de dénominateur au %.

(CADRAGE §7 ; CADRAGE_APV §15 ; DATA_MAP_APV §2.1, §4)
