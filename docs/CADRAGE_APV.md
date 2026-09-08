# Cadrage — APV (Après-Vente)

Voir [`CADRAGE.md`](CADRAGE.md) pour le cadrage transverse (objectif général,
architecture, destinataires, décisions communes aux 3 services).

**Statut : prêt côté données, développement après VO** (VO priorisé le
2026-09-08 malgré cet avantage — choix assumé du porteur du projet).

## 1. Source

**Rapport quotidien APV** (`1MtgVOe17uB4gjb88Dgx-AgRbp3SMr44Rr8kdw0qumYw`).

État constaté le 2026-09-08 : **la couche "prêt à publier" + anomalies existe
déjà**, dans un tableau récapitulatif quotidien avec les colonnes exactes :

`Date de référence` · `Nb OR clôturés J-1` · `CA MO net HT J-1` ·
`CA moyenne mobile 4 sem.` · `Écart % CA` · **`Alerte écart CA`** ·
`CA PR interne Net HT J-1` · `CA PR Externe Net HT J-1` ·
`Écart % CA PR Externe` · **`Alerte écart CA PR Externe`** ·
`Productivité J-1` · `Écart % Productivité` · **`Alerte productivité basse`** ·
`Efficience J-1`

Valeurs d'anomalie observées : `ALERTE`, `ALERTE PRODUCTIVITE BASSE`.

**L'orchestrateur peut lire ce tableau tel quel** — pas de travail Sheet
supplémentaire identifié à ce jour pour ce service.

Les autres tableaux du Sheet (mapping BigQuery→codes, paramètres/seuils, détail
OR, temps passé/pointage, ventes pièces magasin) sont des données source/calcul
intermédiaire, pas à lire directement par l'orchestrateur.

## 2. Décisions

- Aucune décision spécifique APV distincte du cadrage transverse à ce jour.

## 3. Questions ouvertes APV

1. **Emplacement exact du tableau récapitulatif** (nom de l'onglet, plage
   précise) — le nom de l'onglet n'a pas pu être récupéré par l'export texte
   utilisé pour l'inspection, seuls les en-têtes de colonnes sont connus. À
   pointer avant de coder la lecture.
2. Pas de spec détaillée équivalente à `Spec_Mail_IA_ChefVentesVO_v3` pour APV
   à ce jour — le contenu du mail APV (quels indicateurs, quel format,
   destinataire chef d'atelier) reste à définir/confirmer une même façon que
   pour VO.

## 4. Prochaines étapes

En attente : le développement VO est prioritaire. APV reprend une fois le
pilote VO validé — sujet à ré-ouvrir à ce moment-là (confirmer si un document
de spec dédié APV doit être écrit avant de démarrer, sur le modèle du spec VO).
