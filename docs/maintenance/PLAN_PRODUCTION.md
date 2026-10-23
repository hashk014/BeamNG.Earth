# BeamNG.Earth : plan de livraison du fork

**Date : 23 octobre 2026.** Périmètre : [hashk014/BeamNG.Earth](https://github.com/hashk014/BeamNG.Earth), branche `preview`.

Ce document fixe les livrables à produire et les conditions de sortie proposées. Il ne lance aucun chantier à lui seul et ne constitue pas une validation en jeu. Ici, « prod » signifie une release publique du fork, téléchargeable, installable et accompagnée de preuves. Le produit reste en bêta tant que ses limites le justifient.

## 1. La décision produit

**La prochaine update doit permettre de rouler correctement et s'installer sans bricolage.** La priorité est de stabiliser la base 1.6, améliorer la qualité des routes, puis livrer un téléchargement public à jour. Ensuite seulement, on ajoute les fonctions qui enrichissent l'expérience.

Un correctif est terminé quand il est reproduit, implémenté, testé et livré avec ses limites. « Le code compile » ne suffit pas à le vendre comme une correction de conduite.

On ne va pas corriger les 133 issues ouvertes avant de publier. On va définir un périmètre de release, traiter ses blocages et assumer publiquement les défauts restants. Une issue non reproduite reste une investigation, pas une promesse de correction.

## 2. Ce qu'on a réellement aujourd'hui

| Élément | État vérifié | Conséquence |
| --- | --- | --- |
| Base upstream | Release [1.6.0-beta](https://github.com/TecnaGamer/BeamNG.Earth/releases/tag/v1.6.0-beta) intégrée via la [PR fork #6](https://github.com/hashk014/BeamNG.Earth/pull/6), merge `6eecbd8` | La remise à niveau du code est faite. |
| Améliorations du fork | Bâtiments, routes étroites, Décathlon, eau bornée, cache personnalisé, réglages rochers/objets et préchargement par zone conservés | Les requalifier sur la 1.6 avant de les présenter comme validés en jeu. |
| Tests automatiques | Source validée sur Windows/Linux ; résultats détaillés dans [VALIDATION.md](VALIDATION.md) | Bonne base technique, sans preuve de rendu, conduite ou FPS. |
| Kit local | Nouvelle copie installée, ancien mod sauvegardé, handshake serveur vérifié | Utilisable pour la recette, pas une distribution publique autonome. |
| Téléchargement public du fork | Toujours [Preview 1, basé sur 1.5.1](https://github.com/hashk014/BeamNG.Earth/releases/tag/v1.5.1-europe-preview.1) | Le travail récent n'est pas encore livré aux utilisateurs de cet exécutable. |
| Issues upstream | Snapshot rafraîchi : 163 rapports, dont 133 ouverts | Le nombre de tickets n'est pas une mesure du nombre de bugs distincts. |

Les résultats du 23 octobre sont ceux du [rapport d'intégration](../research/2026-10-23-upstream-160-integration.md). Ils ne doivent pas être réutilisés comme preuve d'une future version modifiée. La CI du merge final est à vérifier séparément de celle du merge source déjà validé.

## 3. Ordre des updates à produire

Les lots décrivent une séquence de travail, pas des dates promises. Chaque lot doit avoir un responsable nommé avant son démarrage. Aucun responsable ni délai n'est inventé ici.

| Ordre | Update | Ce qu'on doit livrer | Condition de passage |
| --- | --- | --- | --- |
| 1 | Stabilisation et release publique de la base 1.6 | Recette du candidat, corrections bloquantes reproduites, installation fiable, paquet autonome Windows et documentation | Les portes de sortie de la section 7 sont satisfaites. |
| 2 | Qualité des routes et de la conduite | Petites routes lisibles, transitions de largeur propres, jonctions et passages sous ponts praticables | Comparaisons avant/après sur les lieux documentés, avec collision réelle. Un correctif de ce lot peut avancer dans le lot 1 s'il est bloquant. |
| 3 | Préchargement d'itinéraire | Fonction utilisable depuis la carte, bornée, avec progression et reprise | Trajet préparé puis parcouru avec les limites annoncées, interruption et éviction testées. |
| 4 | Villes de nuit | Éclairage configurable et limité autour du joueur | Rendu et coût mesurés en jeu, disparition propre au changement de zone. |
| 5 | Fidélité et contenu supplémentaires | Bâtiments, signalisation, végétation et mobilier plus justes, par petits correctifs | Données disponibles, gain visible et absence de régression démontrés. |

**Règle de capacité : un chantier principal et sa recette.** Pas de refonte simultanée des routes, de l'eau, du GPS et du multijoueur. Les correctifs indépendants restent dans des PR séparées.

## 4. P0 : rendre la release utilisable

### P0.1 : comprendre et traiter le chargement lent

**Demandes :** [#181](https://github.com/TecnaGamer/BeamNG.Earth/issues/181), [#144](https://github.com/TecnaGamer/BeamNG.Earth/issues/144), [#156](https://github.com/TecnaGamer/BeamNG.Earth/issues/156). Ces symptômes peuvent avoir des causes différentes.

**À produire :**

- Un protocole commun : même machine, véhicule, lieu, trajet, paramètres et état du cache. Séparer première visite et cache chaud.
- Une référence 1.5.4, une référence upstream 1.6 et le candidat du fork. Trois passages par scénario pour voir la variabilité.
- Les temps de terrain praticable après téléportation, de disponibilité des routes/bâtiments et les temps de frame p95/p99. Joindre les traces serveur et jeu.
- Un correctif ciblé si le défaut est reproduit, avec un test de la cause et une nouvelle mesure complète.

**Critère de sortie proposé :** aucun nouveau blocage de génération ni chute à travers le sol reproduit sur le parcours de recette. Une dégradation répétée de plus de 10 % du p95 ou du délai de terrain praticable face à la référence retenue doit être corrigée ou faire l'objet d'une décision explicite de périmètre avant publication. Ce seuil est une exigence proposée, pas un résultat déjà mesuré.

**À ne pas vendre :** une hausse de FPS déduite d'un test Python ou d'un ressenti. Le rapport #181 ne fournit pas encore de profil permettant d'annoncer une cause.

### P0.2 : empêcher les défauts de route qui arrêtent la conduite

**Demandes :** [#182](https://github.com/TecnaGamer/BeamNG.Earth/issues/182), [#183](https://github.com/TecnaGamer/BeamNG.Earth/issues/183), [#185](https://github.com/TecnaGamer/BeamNG.Earth/issues/185), [#129](https://github.com/TecnaGamer/BeamNG.Earth/issues/129), [#160](https://github.com/TecnaGamer/BeamNG.Earth/issues/160), [#161](https://github.com/TecnaGamer/BeamNG.Earth/issues/161).

**À produire :**

- Des reproductions avec coordonnées et données conservées pour les rampes abruptes, marches de jonction, portails bouchés et objets dans les voies.
- Des profils longitudinaux continus, des raccords praticables et une collision qui correspond au rendu. Préserver les deux niveaux d'une intersection dénivelée.
- Des tests des routes supérieures et inférieures, dans les deux sens, après régénération.
- Une trace pour le rapport MKAD #185 : le nom d'une grande route ne suffit pas à localiser toutes les anomalies annoncées.

**Coordination obligatoire :** évaluer la [PR upstream #177](https://github.com/TecnaGamer/BeamNG.Earth/pull/177), encore ouverte au refresh, avant de réimplémenter son lissage de passages sous ponts. Elle propose une correction ; elle n'est pas une preuve qu'elle fonctionne dans notre fork. Éviter les doublons avec les PR [#95](https://github.com/TecnaGamer/BeamNG.Earth/pull/95), [#112](https://github.com/TecnaGamer/BeamNG.Earth/pull/112) et [#71](https://github.com/TecnaGamer/BeamNG.Earth/pull/71).

**Critère de sortie :** les parcours retenus ne présentent ni trou, marche bloquante, toit de tunnel dans une voie ou collision invisible. Le correctif de Décathlon reste valide. Une jonction partage une hauteur seulement si la topologie des données la relie réellement ; deux routes proches ne deviennent pas automatiquement une jonction.

### P0.3 : qualifier l'eau sur les lieux bloquants

**Demandes :** [#171](https://github.com/TecnaGamer/BeamNG.Earth/issues/171), [#8](https://github.com/TecnaGamer/BeamNG.Earth/issues/8), [#53](https://github.com/TecnaGamer/BeamNG.Earth/issues/53).

**À produire :** un diagnostic séparant mer, lac, rivière, hauteur du DEM et volume physique ; un correctif borné si nécessaire ; un parcours de berge et de rue après régénération.

**Critère de sortie :** pas d'eau visible ou physique qui rend les routes sèches de recette impraticables. Vérifier Melbourne et Tanchet séparément. Un test réussi sur un lac ne valide pas tous les polders. Les tunnels sous l'eau restent une limite à documenter, sans promettre de les rendre secs.

### P0.4 : fiabiliser l'installation et le choix des dossiers

**Demandes :** [#150](https://github.com/TecnaGamer/BeamNG.Earth/issues/150), [#173](https://github.com/TecnaGamer/BeamNG.Earth/issues/173), [#7](https://github.com/TecnaGamer/BeamNG.Earth/issues/7), [#12](https://github.com/TecnaGamer/BeamNG.Earth/issues/12).

**À produire :**

- Un affichage clair du dossier d'installation du jeu, du dossier utilisateur actif et du cache. Ce sont trois emplacements différents.
- Une correction persistante des chemins proposés, avec validation avant écriture. L'option `--user-dir` existe déjà ; il faut rendre le parcours compréhensible dans le produit distribué.
- Un diagnostic exploitable quand le mod est désactivé, le serveur inaccessible ou le dossier incorrect. Donner l'action de récupération et l'emplacement des journaux.
- Une sauvegarde avant remplacement, sans effacer les favoris, réglages ou autres mods.

**Critère de sortie :** installation testée sur le paquet distribué, y compris un dossier non standard avec espaces, puis mise à jour d'une installation existante. Les paramètres reviennent après relancement. Les tests automatisés utilisent exclusivement leurs dossiers temporaires isolés.

### P0.5 : qualifier GPS et autodrive, fixer le périmètre public

**Demandes :** [#180](https://github.com/TecnaGamer/BeamNG.Earth/issues/180), [#21](https://github.com/TecnaGamer/BeamNG.Earth/issues/21), [#38](https://github.com/TecnaGamer/BeamNG.Earth/issues/38), [#149](https://github.com/TecnaGamer/BeamNG.Earth/issues/149).

**À produire :** lecture des pièces jointes de #180, récupération d'un trajet exact, traces de progression et changement d'origine, distinction entre route GPS introuvable, graphe local et commande du véhicule.

**Critère de sortie :** sur les trajets retenus, le GPS produit un parcours et l'autodrive ne boucle pas ou ne fait pas demi-tour sans raison. Si l'autodrive reste instable, le présenter comme expérimental et fournir un arrêt accessible. Ne pas bloquer toute la release si le mode concerné est explicitement retiré du périmètre annoncé et que la conduite manuelle est validée.

## 5. P1 : produire les améliorations qui justifient l'update

### P1.1 : redonner une bonne lecture aux petites routes

**Demande principale :** [#179](https://github.com/TecnaGamer/BeamNG.Earth/issues/179). Compléments : [#175](https://github.com/TecnaGamer/BeamNG.Earth/issues/175), [#176](https://github.com/TecnaGamer/BeamNG.Earth/issues/176), [#166](https://github.com/TecnaGamer/BeamNG.Earth/issues/166), [#178](https://github.com/TecnaGamer/BeamNG.Earth/issues/178).

**À produire :**

- Une comparaison au même lieu de Taipei entre routes peintes et maillages, avec la même caméra, lumière et qualité de textures. Inclure une ruelle, une route de campagne, une courbe et une pente.
- Des bords nets, une couleur d'asphalte cohérente et des transitions de largeur qui ne pincent pas brutalement la chaussée.
- Le respect des voies OSM quand elles existent, des largeurs mesurées et des séparations réellement cartographiées. Ne pas inventer un terre-plein à partir du seul nombre de voies.
- Un choix de rendu persistant et expliqué si les deux modes restent utiles. Le code possède déjà `BNGE_ROADS_IN_GROUND` : commencer par comparer l'existant. Un mode hybride n'est retenu que s'il améliore le résultat sans trou, superposition ni coût non maîtrisé.

**Critère de sortie :** avant/après visible sur les lieux de recette, absence de scintillement et de rupture lors des transitions, collision conservée, réglage retrouvé après redémarrage et coût mesuré. Le nouveau mode ne devient pas le défaut uniquement parce qu'il est nouveau.

### P1.2 : précharger un itinéraire depuis la carte

**Demandes :** [#165](https://github.com/TecnaGamer/BeamNG.Earth/issues/165), [#10](https://github.com/TecnaGamer/BeamNG.Earth/issues/10), [#28](https://github.com/TecnaGamer/BeamNG.Earth/issues/28), [#30](https://github.com/TecnaGamer/BeamNG.Earth/issues/30).

**Base disponible :** [préchargement par zone](PREFETCH.md), manifestes, reprise, limites de jobs et contrôle hors ligne. Le bouton de préparation d'un itinéraire n'est pas livré.

**À produire :**

- Un parcours simple : choisir la route, sélectionner le corridor à préparer, voir son périmètre et lancer le téléchargement.
- Une progression honnête : données récupérées, erreurs et couverture restante. Un nombre de jobs n'est ni un volume en Go ni un pourcentage de monde généré.
- Pause, annulation, reprise, conservation du travail déjà fait et contrôle des fichiers présents après redémarrage.
- Un plafond de stockage et de travail, un état « espace insuffisant » et une politique claire d'éviction. Refuser un plan trop grand avant son téléchargement.
- Une vérification des sources désormais utilisées par la 1.6, dont les métadonnées OSM et les niveaux de DEM/imagery nécessaires au périmètre annoncé.

**Critère de sortie :** un trajet défini est préparé, interrompu, repris puis parcouru avec les accès réseau coupés pour les sources annoncées. Le produit précise ce qui reste en ligne : recherche, routage, météo, autres zones ou images non préparées selon le périmètre retenu.

**À ne pas promettre :** « carte autonome », « plus besoin du serveur » ou « zéro génération pendant la conduite ». Télécharger les sources et générer un monde sont deux travaux différents.

### P1.3 : terminer la mise en produit des améliorations existantes

**À produire :** intégrer réellement dans le prochain paquet les réglages rochers/objets, le cache personnalisé, les corrections de bâtiments et les limites d'eau ; vérifier leur persistance et leur effet réel. Retirer les liens qui envoient les utilisateurs vers un ancien binaire sans avertissement.

**Critère de sortie :** les fonctions décrites sur la page de release existent dans le fichier téléchargé. Le testeur les retrouve sans commande interne ni modification de fichier. Une fonction encore réservée aux sources est étiquetée comme telle.

## 6. P2 : enrichir après stabilisation

| Chantier | Livrable attendu | Condition de lancement |
| --- | --- | --- |
| Villes de nuit : [#3](https://github.com/TecnaGamer/BeamNG.Earth/issues/3), [#62](https://github.com/TecnaGamer/BeamNG.Earth/issues/62), [#79](https://github.com/TecnaGamer/BeamNG.Earth/issues/79) | Lampadaires et fenêtres éclairées, rayon et nombre de lumières bornés, réglage persistant, nettoyage au changement de carte | Recette nocturne et budget de temps de frame. Sujet déjà prévu upstream : coordonner avant de développer. |
| Bâtiments et végétation : [#2](https://github.com/TecnaGamer/BeamNG.Earth/issues/2), [#154](https://github.com/TecnaGamer/BeamNG.Earth/issues/154), [#185](https://github.com/TecnaGamer/BeamNG.Earth/issues/185) | Éliminer les cas reproduits de façades flottantes et d'objets dans les voies, respecter les données de matériaux disponibles | Localiser précisément les défauts. Évaluer les PR existantes [#69](https://github.com/TecnaGamer/BeamNG.Earth/pull/69) et [#167](https://github.com/TecnaGamer/BeamNG.Earth/pull/167). Un cas qui bloque la conduite remonte en P0. |
| Signalisation et mobilier : [#170](https://github.com/TecnaGamer/BeamNG.Earth/issues/170), [#172](https://github.com/TecnaGamer/BeamNG.Earth/issues/172), [#174](https://github.com/TecnaGamer/BeamNG.Earth/issues/174), [#178](https://github.com/TecnaGamer/BeamNG.Earth/issues/178) | Panneaux orientés, signaux à la bonne hauteur, barrières et trottoirs adaptés à la catégorie de route | Source et orientation fiables ; pas d'objet ou collision dans la voie. |
| Véhicules garés : [#145](https://github.com/TecnaGamer/BeamNG.Earth/issues/145) | Contrôle compréhensible de présence/densité, mise à jour cohérente des objets et collisions | Vérifier le système déjà présent avant d'ajouter un deuxième réglage. |
| Routes en chantier : [#184](https://github.com/TecnaGamer/BeamNG.Earth/issues/184) | Traitement explicite des statuts de construction et cohérence avec la navigation | Données disponibles ; distinguer route existante, projet et route temporairement fermée. |

**Multijoueur :** la base expérimentale BeamMP est déjà intégrée. Produire une recette à deux joueurs avant d'annoncer son support dans le fork : rejoindre, s'éloigner, se retrouver, téléporter, changer de véhicule et reconnecter. Les tests de protocole et de pairs ne remplacent pas cette session. Il n'est pas nécessaire de réécrire BeamMP pour rendre ce statut honnête.

**À repousser :** Street View/photogrammétrie généralisée, export autonome du monde, monuments universels, voies ferrées complètes, intégration dans tous les écrans de voiture et nouveaux backends régionaux en masse. Ces sujets demandent leur propre étude de données, droits, portée et coût. Ils ne doivent pas retarder la prochaine release utile.

## 7. Ce qui autorise une sortie publique

Cette grille s'applique au périmètre annoncé de la release. Les cases restent ouvertes tant qu'une preuve n'est pas liée. Un problème non reproduit doit recevoir une décision documentée ; il ne devient ni « corrigé » par défaut ni un blocage sans fin.

### Produit et conduite

- [ ] Liste des fonctions livrées, modes expérimentaux et défauts connus figée.
- [ ] Version de BeamNG et plateformes supportées annoncées selon les tests réels. Qualifier la cible upstream 0.40.3 ; ne pas étendre cette compatibilité à toutes les versions 0.40 sans vérification.
- [ ] Les défauts bloquants reproduits du périmètre sont corrigés ou le mode concerné est retiré de ce périmètre.
- [ ] Recette conduite manuelle et collisions terminée, avec version, paramètres, véhicule, coordonnées et résultat.
- [ ] Mesures de chargement et de temps de frame archivées ; aucune promesse de performance sans comparaison.
- [ ] Réglages, favoris et dossiers conservés après fermeture, relancement et mise à jour.
- [ ] Statut BeamMP et autodrive formulé selon la validation réelle.

### Code et paquet

- [ ] Commit candidat exact identifié ; différences avec le dernier commit testé expliquées.
- [ ] Régressions ciblées et suites voisines passées ; CI Windows/Linux du candidat vérifiée.
- [ ] Skips et échecs consignés avec leur portée. Les anciens échecs de timing Windows ne servent pas d'excuse automatique à un nouvel échec.
- [ ] EXE Windows construit depuis le commit annoncé, testé après téléchargement et sur une installation isolée, puis sur une mise à jour sauvegardée.
- [ ] Version du lanceur, du serveur et du mod cohérente ; paquet complet avec les modules natifs requis.
- [ ] ZIP de sources vérifié. AppImage et paquet BeamMP publiés seulement avec leurs contrôles propres ; chaque plateforme porte son niveau de validation.
- [ ] Empreintes SHA-256 publiées et comparées aux fichiers réellement hébergés.
- [ ] Mise à jour testée depuis l'ancien binaire public si ce parcours est annoncé. Un test simulé de l'updater ne valide pas la livraison réelle.

### Livraison et retour arrière

- [ ] Tag du fork, changelog, installation et limitations accessibles depuis la release.
- [ ] Attribution upstream et licences conservées, aucune signature ajoutée au nom d'un assistant.
- [ ] Sauvegarde avant remplacement et procédure de restauration testée, sans écraser les données utilisateur non concernées.
- [ ] Ancienne release conservée pour revenir en arrière. Pas de réécriture d'un tag déjà publié.
- [ ] Vérification publique des téléchargements après publication ; page du dépôt et liens de mise à jour cohérents.
- [ ] Journaux et procédure de rapport indiqués ; retour arrière prioritaire si une régression bloquante est confirmée après sortie.

## 8. Parcours de recette à préparer

| Parcours | Ce qu'on doit constater | Preuve à garder |
| --- | --- | --- |
| Démarrage standard / Mount Whitney | Bon mod, connexion serveur, terrain sous la voiture, arrêt propre | Logs de lancement et paramètres du paquet |
| Les Sables, Décathlon : `46.514217, -1.784525` | Deux chaussées supérieures et passage inférieur praticables dans les deux sens | Vidéo, coordonnées, vitesse et collisions observées |
| Lac de Tanchet et mer, favori TEST 6 | Niveau, berges, route sèche et cohérence eau visible/physique | Captures et courte conduite |
| Taipei : `25.05901, 121.55196` | Lisibilité des ruelles, couleurs et transitions du mode de route choisi | Avant/après à caméra et lumière identiques |
| Fortaleza : `-3.76704, -38.66579` et Teresina : `-5.07099, -42.62335` | Passage sous pont sans rampe qui lance ou bloque le véhicule | Profil et vidéo avant/après |
| Melbourne : `-37.827304, 144.939263` | Rue non rendue impraticable par un niveau d'eau erroné | Source du niveau, captures et conduite |
| Amsterdam et Lauterbrunnen, favoris existants | Terrain bas, virages en pente, raccords, bâtiments et trottoirs | Même parcours conservé entre candidats |
| Itinéraire GPS à fixer avec #180 | Routage, progression et changement d'origine cohérents | Départ/arrivée exacts et traces de navigation |

Ne pas improviser la recette à la fin du développement. Conserver les données nécessaires, identifier le scénario avant modification et refaire le même après. Toute récupération ou suppression de fichiers pendant les tests reste confinée à une racine temporaire possédée et vérifiée.

## 9. Livrables attendus à chaque fin de lot

| Livrable | Contenu minimum |
| --- | --- |
| PR ciblée | Problème concret, comportement obtenu, alternatives écartées utiles au reviewer, dépendances upstream et limites |
| Dossier de preuve | Version, données/lieux, commandes, résultats automatiques, recette en jeu et mesures pertinentes |
| Paquet candidat | Fichier installable correspondant au commit et empreinte, ou mention explicite « sources uniquement » |
| Notes de release | Ce qui change pour le joueur, ce qu'il doit faire et les défauts encore connus |
| Retour arrière | Sauvegarde et restauration opérables, sans suppression du cache ou des favoris pour masquer un défaut |
| Suivi maintenu | [STATUS.md](STATUS.md), [ISSUES.md](ISSUES.md), [VALIDATION.md](VALIDATION.md) et ce plan actualisés |

Le développeur produit le patch et les preuves automatiques. Le responsable de recette en jeu reste à désigner ; ne pas présenter une validation utilisateur comme acquise. La personne qui publie vérifie les fichiers hébergés et signe la décision de sortie avec l'identité humaine habituelle du dépôt.

## 10. Le prochain travail, concrètement

### Avancement du 23 octobre : choix du rendu des routes

Le [choix persistant terrain/mesh](ROAD_RENDERING.md) est implémenté dans les
lanceurs source. Le mode terrain reste le défaut. Le mode choisi est transmis
aux workers locaux et distants ; les participants incompatibles ne partagent
pas leurs résultats. Le correctif de partage est proposé à upstream dans la
[PR #187](https://github.com/TecnaGamer/BeamNG.Earth/pull/187).

Les tests de persistance et de processus séparés sont automatisés. Ce travail
prépare la comparaison de #179 ; il ne valide ni l'apparence, ni les collisions,
ni une amélioration de performances. La recette en jeu reste à effectuer et
les portes de sortie de la section 7 restent ouvertes. Le binaire public est
toujours Preview 1 ; voir [VALIDATION.md](VALIDATION.md) pour les preuves source.

1. Nommer le responsable du lot 1 et figer le périmètre de la prochaine release publique.
2. Qualifier le candidat 1.6 existant sur les parcours critiques et capturer les mesures de chargement.
3. Pour le premier chantier visuel, traiter #179 avec une comparaison des deux modes existants. Garder le correctif petit et démontrable.
4. Évaluer #177 sur les cas brésiliens avant d'ouvrir un chantier concurrent sur les ponts.
5. Corriger les blocages reproduits, requalifier le candidat, construire puis publier le paquet conforme à la grille de sortie.
6. Ouvrir ensuite le lot de préchargement d'itinéraire. L'éclairage vient après une base de conduite stable.

**La cible est une update qu'un joueur peut télécharger, installer et utiliser. Les nouveautés supplémentaires doivent servir cette cible, pas repousser sa livraison.**
