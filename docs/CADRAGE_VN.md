# Cadrage — VN (Véhicules Neufs)

Voir [`CADRAGE.md`](CADRAGE.md) pour le cadrage transverse (objectif général,
architecture, destinataires, décisions communes aux 3 services).

**Statut : non démarré.** Développement après VO (et probablement après APV) —
voir la priorisation dans `CADRAGE.md` §3 et §7.

## 1. Source

**Aucun Sheet "Rapport quotidien VN" n'existe sur le Drive** (vérifié
2026-09-08). Décision prise : il faut le créer, sur le modèle de VO/APV — action
non réalisée à ce jour (une première tentative de copie automatique du Sheet VO
a été faite par erreur puis annulée le 2026-09-08, voir historique du projet —
la création doit se faire sur accord explicite, par Quentin/Corentin, avec la
bonne source BigQuery pour le Neuf dès la création plutôt qu'en deux temps).

## 2. Décisions

- Aucune à ce jour au-delà du cadrage transverse.

## 3. Questions ouvertes VN

1. **Quelle source/vue BigQuery pour le Neuf ?** (l'équivalent VN de
   `v_sf_vehicule_stock`/`v_sf_vente` utilisés pour VO — à déterminer, la copie
   brute de VO pointerait à tort sur des sources VO).
2. **Qui crée le Sheet et quand** (dépend de l'avancement VO/APV).
3. **Existe-t-il une spec équivalente à `Spec_Mail_IA_ChefVentesVN` ?** —
   probablement à écrire sur le modèle du spec VO (`Spec_Mail_IA_ChefVentesVO_v3`)
   une fois VO validé en pilote.

## 4. Prochaines étapes

En attente — rien à faire tant que VO (et probablement APV) n'est pas avancé.
