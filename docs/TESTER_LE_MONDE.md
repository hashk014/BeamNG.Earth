# Tester notre génération du monde

Cette branche contient les améliorations du trafic européen et de la génération
des routes et bâtiments. Le lanceur officiel `.exe` utilise sa propre copie du
serveur : pour tester notre code, il faut démarrer celui de ce dossier.

## Démarrer

1. Ferme le lanceur officiel BeamNG.Earth et son serveur s'ils tournent.
2. Double-clique sur `run_server.bat` à la racine de ce projet. Laisse la fenêtre
   ouverte. L'environnement Python est déjà préparé sur cette machine.
3. Lance BeamNG.drive et charge la carte **BeamNG.Earth**. Si elle était déjà
   ouverte, recharge-la après le démarrage de notre serveur.
4. Attends la fin du chargement près de la voiture. Si le statut indique
   « Offline » ou « Degraded », note-le dans ton retour.

Si la fenêtre du serveur affiche une erreur, garde son texte ou une capture.
Un port déjà occupé signifie généralement qu'un autre serveur est encore lancé.
Il n'est pas nécessaire d'effacer le cache des cartes : les sources sont
réutilisées et les maillages sont reconstruits dans la nouvelle session.

## Parcours de 15 à 20 minutes

Utilise d'abord une voiture standard, puis garde la même voiture et les mêmes
réglages graphiques pour comparer deux essais.

| Essai | Action | Défaut à chercher |
| --- | --- | --- |
| Ville, sans trafic | Aux Sables-d'Olonne, autour de `46.502598, -1.780002`, roule dans les petites rues à 20 puis 50 km/h | Route trop large, trottoir dans une voie, trou, saut de suspension, mur qui flotte |
| Courbes et relief | Sur une route de montagne que tu connais, passe lentement un lacet, puis une montée et une descente | Virage coupé, pointe de chaussée, bosse artificielle à un raccord, voiture qui traverse le sol |
| Ronds-points | Active trois voitures IA. Observe plusieurs entrées, puis augmente progressivement le trafic | Contresens, refus de priorité, voiture bloquée, trajectoire qui traverse l'îlot |
| Bâtiments | Regarde les maisons depuis la rue puis en caméra libre, notamment autour des cours | Cour remplie, hauteur ou toit aberrant, fondation visible, collision décalée |
| Streaming | Roule plusieurs kilomètres, fais demi-tour et reviens | Terrain qui disparaît, bâtiment qui change, chargement bloqué, chute brutale des FPS |

Pour varier les données, le benchmark du projet propose aussi Amsterdam
(`52.3702, 4.8840`) et Lauterbrunnen (`46.5935, 7.9089`). Ce sont des endroits
à tester, pas des endroits déjà validés par cette passe. Commence surtout par
un quartier que tu connais : tu repéreras mieux ce qui ne ressemble pas au réel.

Une cour fermée par de vrais murs n'est pas nécessairement accessible en voiture.
Inspecte-la en caméra libre sans attendre qu'un passage soit inventé.

## Me signaler un défaut

À l'endroit exact, appuie sur **Ctrl + Maj + E**. Le rapport du mod capture la
position, une image et les informations de la session. Ajoute un titre précis
et enregistre avec **Save report**. Pour une saccade, utilise **Ctrl + Maj + Y**
et continue le parcours pendant les 30 secondes du profilage.

Les rapports sont dans :

```text
%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\beamngearth\reports
```

Donne-moi le nom du dossier créé, ou utilise le bouton **Open folder** et copie
son chemin ici. Je pourrai lire le rapport local. Tu n'as pas besoin de créer
une issue GitHub pour chaque défaut.

Ajoute simplement :

```text
Endroit ou coordonnées :
Problème : ce que je vois / ce qui devrait être là
Reproduction : sens de circulation, vitesse, voiture, trafic activé ou non
Priorité : bloque la conduite / gêne beaucoup / seulement visuel
Rapport : nom ou chemin du dossier
```

Une courte vidéo est utile pour les sauts, collisions et saccades. Si le rendu
diffère du vrai lieu, une photo de référence ou un lien cartographique aide à
distinguer une erreur de génération d'une donnée source absente.

Pour la prochaine passe, les retours les plus utiles sont trois défauts précis
et reproductibles, chacun à son emplacement. On corrigera d'abord ceux qui
empêchent de conduire, puis les erreurs de forme, puis l'habillage visuel.
