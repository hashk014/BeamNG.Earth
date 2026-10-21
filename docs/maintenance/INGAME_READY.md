# Test en jeu prêt sur ce PC

## Mise à jour du 21 octobre 2026

Le même raccourci **Tester BeamNG Earth** lance maintenant la copie figée
`dist/ingame-ready/runtime-sables-20261021`. Le module d'eau installé a aussi
été mis à jour. Le jeu n'a pas été lancé pendant cette préparation.
L'ancienne copie `runtime-urban` est conservée ; sauvegarde du module d'eau,
des favoris et du manifeste dans `backups/sables-20261021-120602`.

- **TEST 5 - Decathlon - passage inferieur** : parcourir les deux chaussées
  au-dessus du petit tunnel, puis examiner son entrée et la voie inférieure.
  Vérifier l'absence de trou, marche, toit ou collision qui bloque la chaussée.
- **TEST 6 - Tanchet - lac et mer** : longer les berges et le bord de mer.
  Vérifier le niveau visible, les débordements et l'absence d'eau physique
  invisible sur terrain sec. Le niveau réel du lac et le rendu marin restent
  à confirmer ; aucune correction universelle de la mer n'est annoncée.

Les autres favoris et réglages ont été conservés. Les tests hors jeu et le
handshake serveur passent. Les mesures et limites sont dans le
[rapport de cette passe](../research/2026-10-21-sables-underpass-water.md).

Retour du joueur le 21 octobre : la version mise à jour fonctionne globalement
mieux. Ce retour ne constitue pas encore une validation mesurée des collisions,
du niveau du lac ou du rendu de la mer.

## Préparation précédente

Préparé le 20 octobre 2026 pour `1.5.3-europe-preview.2-dev`.
Le raccourci **Tester BeamNG Earth** est sur le Bureau. Il ouvre
`TESTER_EN_JEU.cmd`, puis une copie figée du serveur et du mod dans
`dist/ingame-ready/runtime-urban`. Le vieux Preview 1 n'intervient pas dans ce test.

La correction des bâtiments et trottoirs est préparée pour le prochain
lancement. Fermer le jeu et l'ancienne fenêtre du serveur, puis utiliser le même
raccourci. La copie initiale reste conservée dans `dist/ingame-ready/runtime`.
Le [rapport de cette passe](../research/2026-10-20-urban-ground-contact.md)
précise les corrections, leurs tests et le bâtiment restant à localiser.

## Démarrer

1. Fermer tout ancien serveur Earth et toute session BeamNG encore ouverte.
2. Double-cliquer sur **Tester BeamNG Earth**. Laisser sa fenêtre ouverte.
   Le serveur démarre, puis le jeu en DirectX 11 avec la carte **BeamNG.Earth**
   demandée directement, sans passer par le sélecteur de cartes.
3. Après le chargement, ouvrir **Échap > Mods > BeamNG.Earth > Places**, puis
   choisir **TEST 1 - Les Sables - ville et routes** et **Go**.

Le point de départ standard du mod reste Mount Whitney. Ses données sont
également préparées. Si le jeu était déjà ouvert, le lanceur ne change pas sa
carte : charger BeamNG.Earth dans Freeroam ou relancer le jeu.

La préparation enlève les installations et les commandes à saisir. Le temps de
démarrage du jeu et de génération du terrain reste à mesurer en jeu.

## Vérification courte, environ cinq minutes

| Lieu ajouté aux favoris | Action | À vérifier |
| --- | --- | --- |
| TEST 1, Les Sables | Rouler à 20 puis 50 km/h dans les rues | Routes continues, trottoirs, adhérence et bâtiments |
| TEST 1, Les Sables | World > Decorative doors and benches : désactiver puis réactiver | Objets mis à jour et absence de collision invisible après retrait |
| TEST 4, Monument Valley | World > Rocks : Normal, Low, Off | Quantité de rochers, maintien des arbres et panneaux |
| TEST 2, Amsterdam | Observer quais, rues et terrains bas | Eau cohérente, route sèche praticable, signaler tout débordement |
| TEST 3, Lauterbrunnen | Prendre un virage en pente | Raccords et collisions, absence de trou ou de bosse anormale |

Pour finir, quitter puis relancer afin de vérifier que les valeurs **Rocks** et
**Decorative doors and benches** sont conservées. Remettre ensuite les valeurs
souhaitées. Ne pas augmenter le trafic avant d'avoir essayé sans trafic.

En cas de défaut : **Ctrl + Maj + E**, titre précis, **Save report**.
Pour les saccades : **Ctrl + Maj + Y**, puis continuer à conduire pendant 30 s.
Les rapports sont sous `%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\beamngearth\reports`.
Le guide détaillé est dans [TESTER_LE_MONDE.md](../TESTER_LE_MONDE.md).

## Préparation et preuves

- Mod actuel installé et actif. Les autres mods, véhicules et réglages graphiques
  ont été conservés. Quatre favoris de test ont été ajoutés aux favoris existants.
- Ancien mod et fichiers de réglages sauvegardés dans `backups/ingame-20261020-191443`.
- Modules Rust recompilés depuis ce checkout et inclus dans la copie de test.
  Les 31 tests des noyaux natifs passent avec cette copie.
- 51 tests Python ciblés passent, dont le passage de la carte au lancement
  Windows, Linux natif et Proton, ainsi que les replis via Steam.
- Le vrai processus serveur de la copie répond au handshake protocole 4 / format 4.
  Démarrage et handshake mesurés à 2,671 s sur ce PC. Ce temps exclut le jeu.
- Les données DEM, cartes et images EOX 2016 de cinq petites zones sont préparées
  et relues avec tout accès réseau désactivé : Mount Whitney, Les Sables,
  Amsterdam, Lauterbrunnen et Monument Valley.
- Le jeu n'a pas été démarré pendant cette préparation. Le chargement direct
  utilise l'argument `-level` reconnu par le code du jeu installé. Le parcours
  réel, son rendu et sa durée restent à confirmer par le joueur.

Les zones préparées couvrent environ 0,5 à 1 km de rayon. L'horizon, les images
régionales plus détaillées, la météo et les trajets au-delà peuvent encore
demander Internet. Les maillages sont générés à la connexion : le préchargement
des sources ne constitue pas une carte déjà rendue ni une preuve de jeu hors ligne.

## Retrouver ou restaurer

- Identité de la copie et empreintes des fichiers : `dist/ingame-ready/READY.json`.
- Résultat du contrôle serveur : `dist/ingame-ready/CHECKED.json`.
- Journaux de préparation : `dist/ingame-prefetch-*.log` et `dist/ingame-offline-*.log`.
- Journal du serveur pendant le jeu : `%LOCALAPPDATA%\beamng-earth\logs\server.log`.
- Arrêt : quitter le jeu ou utiliser **Ctrl + C** dans la fenêtre du lanceur.

Pour restaurer, fermer le jeu et le serveur, mettre de côté la copie installée
`mods/unpacked/beamng_earth`, puis remettre le dossier `beamng_earth` sauvegardé
dans ce même emplacement. Les deux fichiers `beamngEarth*.json` sauvegardés vont
dans le dossier `settings` du jeu. Restaurer ces fichiers enlève les changements
de favoris et de réglages effectués depuis la sauvegarde.

Le kit local utilise le Python déjà installé dans `.venv`. Pour tester une
future version depuis les sources, mettre le mod à jour et lancer :

```powershell
.venv/Scripts/python.exe launcher.py --quick-play --gfx dx11
```

Le kit figé ne reçoit pas automatiquement les modifications futures du dépôt.
