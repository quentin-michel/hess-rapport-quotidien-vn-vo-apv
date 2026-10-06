# Règles communes à tous les mails

Complète `rapport/consignes_composition.md` (qui prime et n'est pas répété ici : aucun
chiffre inventé, date, noms réels, blocs sans signal, largeur 900 px, objet). À lire pour
tout mail, avec le fichier de règles du type (vn, vo, apv, directeur, plaque).

## 1. Principe de lisibilité
- Critère de jugement de **tout** le contenu (quoi inclure, à quel niveau de détail) :
  le mail doit être facile à lire et pertinent.
- La synthèse IA **ne répète pas** les chiffres déjà visibles dans les blocs : sa valeur
  ajoutée est la **synthèse croisée entre blocs**, pas un résumé.

(CADRAGE §3)

## 2. Rédaction de la synthèse (et de tout texte rédigé)
1. **Chercher les recoupements** : un même véhicule/dossier/OR présent dans plusieurs blocs
   (ex. signalé à l'achat ET toujours sans prix en stock 7 jours après). Pas limité à
   achat↔stock : leads non traités, anomalies ventes, etc. Suivre le **signal le plus fort
   du jour**, quel que soit son bloc.
2. **Nommer des priorités concrètes** (immatriculation, VIN, n° de dossier, n° OR), pas des
   constats généraux.
3. **Tendance → risque prospectif actionnable** (« sans action, l'écart va se creuser »).
4. **Jamais la note brute d'anomalie** (« noté 4/10 ») : décrire le problème concret
   (écart, délai, manque).
5. **2 phrases maximum, ~350 caractères** au total (synthèse d'un mail Service ; les mails
   Directeur et Plaque ont leur propre format, voir leur fichier).
6. **Une phrase = un signal.** Plusieurs véhicules touchés par le même signal dans une
   phrase : oui. Deux sujets différents dans une phrase : non.
7. **Mener par l'action** (« À publier en priorité : … ») plutôt que par le constat.
8. **Caler la densité sur le volume réel** : un seul signal solide → une seule phrase ; ne
   pas ajouter un point faible pour remplir. Deux signaux réellement forts → deux phrases.
9. **Aucun vocabulaire de classification interne** : ni « à vérifier / à corriger / à
   signaler », ni les états du classificateur de tendance (« hausse confirmée », « baisse
   confirmée », « accélère », « volume trop faible »…). Dire le chiffre et la comparaison
   (« 22 commandes contre un rythme habituel de 32 par semaine, -9,5 % sur l'an dernier »).
   Test : un lecteur qui n'a jamais vu les Sheets comprend la phrase du premier coup.
10. **Pas de causalité inventée** entre deux blocs qui partagent un modèle ou un mot-clé :
    présenter « deux signaux distincts sur le même véhicule/modèle », sauf lien établi. Une
    perte chiffrée substantielle se cite telle quelle.
11. Vocabulaire lecteur : « hier » (pas J-1), « depuis le début du mois » (pas MTD),
    « l'an dernier » (pas N-1) ; aucun nom d'onglet, de colonne ni de classeur.

Exemple validé (2 signaux → 1 retenu, action en tête, ~235 caractères) : « À publier en
priorité : les Clio GH-907-MT et GL-384-ER, signalées à l'achat pour des écarts de
prix/km/délai, sont toujours sans prix de vente 5 à 7 jours après. Sans correction, ces
deux dossiers immobilisent du stock déjà vendable. »

Les **paragraphes narratifs au-dessus des tableaux** (ex. commandes/facturations vs
objectifs) sont aussi du texte IA : mêmes règles. Seuls les tableaux sont de la donnée pure.

(CADRAGE §3 ; CADRAGE_VN §6 ; CADRAGE_VO §14 pt 11)

## 3. Listes tronquées
Quand une liste doit être limitée (top N + « +N autres ») ou qu'on cite « le pire
dossier » : tri par **montant/note décroissant d'abord**, date décroissante seulement à
égalité. (CADRAGE_VO §10, vaut aussi pour VN)

## 4. HTML « email-safe » (compléments)
- Partir de la maquette email-safe et **conserver sa structure en `<table>`** ; ne changer
  que le contenu.
- Couleurs en **hex littéral répété** à chaque usage (aucune `var(--x)`), aucun bloc
  `<style>` ni classe : tout en `style="…"` sur chaque élément (certains clients suppriment
  `<style>`).
- Police système uniquement : `font-family:Arial,Helvetica,sans-serif;` (aucun `<link>`) ;
  thème clair fixe (les clients mail gèrent mal le thème sombre).
- **Icônes météo en emoji Unicode**, jamais en SVG : ☀ `&#9728;` Soleil, ☁ `&#9729;` Nuage,
  🌧 `&#127783;` Pluie, ⛈ `&#9928;` Orage.
- Codes couleur des maquettes : navy `#2D3250`, or `#C8AA73`/`#A88A56`, texte `#3B3A36`,
  gris `#8A8474`, négatif `#B0413E`, vigilance `#C1793A`, positif `#2E7D5F`.

(CADRAGE §6 ; CADRAGE_VN §6)

## 5. Noms réels vs anonymisation
- L'anonymisation (« Client A », « Réceptionnaire B », « Mécanicien A »…) ne vaut que pour
  les fichiers commités sur GitHub, dont les maquettes. **Ne jamais recopier ces
  libellés** : le mail envoyé porte les vrais noms des faits (destinataires légitimes de
  leur périmètre).
- Les mentions « [MAQUETTE] … » / « [ENVOI TEST] … » du pied de page ne se recopient pas.

(CADRAGE §6)
