<h1 align='center'> Projet TwAIlight </h1>
<p align='center'>
<i>Option ISIA - Centrale Paris <br>
Mars 2018 <hr></i></p>

**Auteurs** : Chloé Gobé, Eymard Houdeville, Charles Jacquet, Silvestre Perret, Mathieu Seris<br>

## Index

1.  [Présentation générale](#description)

    1.  [Introduction](#subparagraph1)
    2.  [Arborescence détaillée du projet](#subparagraph2)
    3.  [Pour tester un nouvel algorithme](#subparagraph3)
    4.  [Pour lancer un joueur pour jouer sur le serveur le jour du tournoi](#subparagraph4)

2.  [Méthode de développement](#test)

3.  [Algorithmes](#alg)

4.  [Heuristique](#strat)

5.  [Approches testées et imaginées](#approches)

    1.  [Différents comportements](#behaviors)
    2.  [Multiprocessing](#multiprocessing)
    3.  [Exploration de l'arbre](#exploration)
    
6.  [Mesures de performance, tests et conclusions](#perf)

Le but de ce projet est de développer une intelligence artificielle capable de jouer au jeu "Vampire contre Loups-Garou". Les règles du jeu sont dans le fichier "Projetv10b.pdf".
Ce github contient notre implémentation des algorithmes que nous proposons pour le tournoi du 23 Mars 2018.

## <a name="description"></a>1. Présentation générale

### <a name="subparagraph1"></a>i. Introduction

Extrait du sujet:

> Dans un monde lointain, des êtres mortels et ordinaires vivaient une vie paisible. Mais un soir, à la nuit tombée, leurs terres furent le témoin d’une lutte acharnée entre deux espèces : les Vampires et les Loups-Garous.

NB : comme convenu ce readme se concentre sur les stratégies et algorithmes impleméntés par l'équipe et ne développe pas les aspects liés à la communication avec le serveur.

### <a name="subparagraph2"></a>ii - Arborescence détaillée du projet

* **twAIllight** : Repertoire principal du projet

  * **Cartes** : Les différentes cartes sur lesquelles nous pouvons tester notre IA

  * **Morpion** : L'idée de ce dossier Morpion est d'implémenter et de tester sur un problème plus simple différentes approches avant de transposer celles-ci à jeu Vampire vs Loup-garous. Ce dossier nous permet de 1) vérifier que nous avons bien compris les stratégies et algorithmes et que nous les pensons pertinentes pour notre problème 2) Posséder une base qui nous permet d'itérer et de développer plus rapidement les algorithmes sur le jeu Vamp vs LG.

    * **Map_Morpion.py** : La "carte" du morpion

    * **Sommet_du_Jeu_Aléatoire.py** : Un base-case, il faut au moins battre cet algorithme simpliste (ie : ne pas tricher, prendre des décisions qui nous permettent de l'emporter contre ce joueur aveugle)

    Ce dossier contient aussi nos différents algorithmes pour le jeu du morpion:

    * **Sommet_du_Jeu_AlphaBeta_Oriente.py**
    * **Sommet_du_Jeu_AlphaBeta.py**
    * **Sommet_du_Jeu_MinMax_Transposition.py**
    * **Sommet_du_Jeu_MinMax.py**
    * **Sommet_du_Jeu_NegaMax_Transposition.py**
    * **Sommet_du_Jeu_NegaMax_Transposition_Oriente.py**
    * **Sommet_du_Jeu** :
    * **Tournoi** : Organisation d'un tournoi entre IA

- **Test** : Nos tests

- **MetaStrategy** : Dossier explorant la piste des heuristiques

  * **StrategyHumanFirst** : Cherche à développer une IA qui va essayer d'optimiser son jeu afin d'attaquer le plus d'humains possibles de façon à devenir nombreux.

- **Algorithmes** : Les différents algorithmes développés et testés pour le tournoi.
  Ces algorithmes héritent tous de la classe JoueurInterne.

  Ce dossier contient deux types de fichiers:

  * Les algorithmes eux-mêmes,
  * Les "représentations du monde" qu'ils utilisent (les fichiers Sommets_du_jeu)

  Ces différents algorithmes sont expliqués plus loin dans ce document.

  * **Algo_Customized_Evaluation.py**
  * **Algo_MinMax.py**
  * **Algo_MonteCarloTreeSearch.py**
  * **Algo_NegaMax_MPOO.py**
  * **Algo_Negamax_MPO_2.py**
  * **Algo_Negamax_MPO_3.py**
  * **Algo_NegaMax_Oriente.py**
  * **Algo_NegaMax_Probable_outcome.py**
  * **Algo_NegaMax.py**
  * **Algo_Temporal_Difference_0.py**<br>
  * **Sommet_du_Jeu_MinMax_Transposition.py**
  * **Sommet_du_Jeu_MonteCarlo.py**
  * **Sommet_du_Jeu_NegaMax_MPOO.py**
  * **Sommet_du_Jeu_NegaMax_MPO_2.py**
  * **Sommet_du_Jeu_NegaMax_probable_outcome.py**
  * **Sommet_du_Jeu_NegaMax_Transposition_Oriente.py**
  * **Sommet_du_Jeu_NegaMax_Transposition.py**
  * **Sommet_du_Jeu_Temporal_Diffrence_0.py**
  * **Sommet_du_Jeu.py**

- **Log_cProfile** : contient les logs des profils effectués pour optimiser le temps de réponse de nos algorithmes.

- **V3.3** : Fichier de claroline pour lancer une partie avec le serveur du Projet

- **Joueur.py** :
  Le fichier de base est Joueur.py .
  Il contient la classe Joueur qui peut jouer et communiquer avec le serveur du projet.
  La méthode de classe next_moves est la méthode qui décide du prochain mouvement (par défaut, c'est la fonction aléatoire).

- **Joueur_interne.py** :
  Le fichier Joueur_Interne.py contient une classe héritée de Joueur, qui communique avec le serveur interne. Seules les méthodes de communication ont été surchargées.
  Par défaut, le joueur interne joue aléatoirement et split nos unités aléatoirement.

- **Map.py** : La représentation de la carte du jeu et les méthodes afférentes que nos IA utilisent

- **Serveur_interne.py** : Le fichier contenant notre simulation de serveur
  Notre serveur interne est dans le fichier Serveur_Interne.py.
  Pour lancer le jeu en interne, on 'start' (comme un thread) une instance de ServeurInterne.
  ServeurInterne est initialisé avec deux classes de joueurs internes et une carte (classe Map du fichier Map.py ou héritées).

- **Tournoi.py** : La possibilité d'organiser des tournois entre nos IA (entre elles) ou contre l'algorithme aléatoire qui nous sert de benchmark.
  Le fichier Tournoi permet d'effectuer des duels entre différents algo de décision (du dossier Algorithmes), sur plusieurs cartes données (du dossier Cartes).

- **Darwin_Search.py** : L'idée de la recherche darwinienne est de tester et de classer nos différents algorithmes en effectuant un très grand nombre de tournois entre différentes instances avec des hyperparamètres différents (un hyperparamètre sera typiquement le nombre de groupe d'adversaires max que l'on considère quand on cherche à faire un mouvement)

  On créé des pool aléatoires de combat dans lesquelles on effectue tous les combats possibles: lorsque ces combats sont effectués on classe les algorithmes en fonction de leur win rate et on ne garde que les top N algos. Les autres sont remplacés aléatoirement par des individus générés par un produit cartésien dans l'espace des hyper paramètres.
  Au bout d'un grand nombre d'itérations les algorithmes qui se maintiennent dans la pool sont supposés être parmi les meilleurs.

  Les paramètres de ce tournoi un peu spécial sont:

  N_GAME : le nombre de parties par carte (chaque carte est appelée dans une pool)
  POOL_SIZE : la Taille des pools de combats
  N_SURVIVORS : le nombre de survivants que l'on garde dans chaque pool à la suite des combats (on garde Top N_SURVIVORS sur POOL_SIZE individus)
  TIMER : Nombre d'itérations

  Une variante intéressante de cet algorithme est la variante où l'on autorise la pool à contenir plusieurs fois un même individu: autrement dit imaginons que l'individu A survive à la pool 1. On autorise l'ajout de ce même individu A à notre pool B. Résultat: si l'individu A est effectivement le meilleur on devrait avoir tendance à voir notre pool se remplir au fur et à mesure de cet individu A (un espèce qui devient prépondérante dans l'éco système)


### <a name="subparagraph3"></a>iii. Pour tester un nouvel algorithme

* Si on veut un joueur en local ("interne"), on crée une classe héritée de JoueurInterne, à laquelle on surcharge la fonction next_moves,
* Si on veut un joueur avec le serveur du projet, on crée une classe héritée de Joueur, à laquelle on surcharge la fonction next_moves.

### <a name="subparagraph4"></a>iv. Pour lancer un joueur pour jouer sur le serveur le jour du tournoi

* Créer dans un fichier une classe héritée de Joueur (dans Joueur.py), qui override la méthode next_moves de Joueur
* Ecrire dans ce fichier

```python
if __name__=='__main__':
  Joueur_1=NotreClasseHéritéeDeJoueur()
  Joueur_1.start()
  Joueur_1.join()
```

* Lancer le serveur
* Taper dans le terminal (avec XXX.X.X.X YYYY l'hote et le port du serveur)

```bash
python MonAlgo.py XXX.X.X.X YYYY
```

<i>Attention toutes les classes du dossier Algorithmes héritent de la classe JoueurInterne pour pouvoir les appeler (ici) avec notre moteur de jeu interne ! Ne pas hésiter à modifier le code pour le tester sur le serveur .exe </i>
<hr>

## <a name="test"></a>2.Méthode de développement

Notre approche est globalement la suivante:

##### Step 0: Un problème plus simple

Pour nous appropier les algorithmes nous avons utilisé un problème plus simple (le Morpion). Nous pensons pouvoir appréhender complétement l'arbre de jeu du Morpion.

Voici un exemple de résultats d'un tournoi sur les algorithmes développés sur le jeu du Morpion : 

Match Aleatoire vs MinMax: score 0V 1N 9D <br>
Match Aleatoire vs AlphaBeta: score 0V 0N 10D <br>
Match Aleatoire vs AlphaBetaOriente: score 0V 2N 8D <br>
Match Aleatoire vs MinMax_Transposition: score 0V 0N 10D <br>
Match Aleatoire vs Negamax_Oriente: score 0V 2N 8D <br>
Match Aleatoire vs Negamax: score 0V 0N 10D<br>
<br>
Match MinMax vs AlphaBeta: score 0V 10N 0D<br>
Match MinMax vs AlphaBetaOriente: score 0V 10N 0D<br>
Match MinMax vs MinMax_Transposition: score 0V 10N 0D<br>
Match MinMax vs Negamax_Oriente: score 0V 10N 0D<br>
Match MinMax vs Negamax: score 0V 10N 0D<br>
Match AlphaBeta vs AlphaBetaOriente: score 0V 10N 0D<br>
Match AlphaBeta vs MinMax_Transposition: score 0V 10N 0D<br>
Match AlphaBeta vs Negamax_Oriente: score 0V 10N 0D<br>
Match AlphaBeta vs Negamax: score 0V 10N 0D<br>
Match AlphaBetaOriente vs MinMax_Transposition: score 0V 10N 0D<br>
Match AlphaBetaOriente vs Negamax_Oriente: score 0V 10N 0D<br>
Match AlphaBetaOriente vs Negamax: score 0V 10N 0D<br>
Match MinMax_Transposition vs Negamax_Oriente: score 0V 10N 0D<br>
Match MinMax_Transposition vs Negamax: score 0V 10N 0D<br>
Match Negamax_Oriente vs Negamax: score 0V 10N 0D<br>
<br>
296 sommets ont été créés pour la classe Aleatoire<br>
21138535 sommets ont été créés pour la classe MinMax<br>
21137066 sommets ont été créés pour la classe AlphaBeta<br>
21112573 sommets ont été créés pour la classe AlphaBetaOriente<br>
18326 sommets ont été créés pour la classe MinMax_Transposition<br>
20811 sommets ont été créés pour la classe Negamax_Oriente<br>
24463 sommets ont été créés pour la classe Negamax<br>
<br>
Aleatoire a joué durant 0.00 s.<br>
MinMax a joué durant 860.40 s.<br>
AlphaBeta a joué durant 657.73 s.<br>
AlphaBetaOriente a joué durant 1609.12 s.<br>
MinMax_Transposition a joué durant 0.29 s.<br>
Negamax_Oriente a joué durant 1.25 s.<br>
Negamax a joué durant 0.42 s.<br>

On se rend compte que les algorithmes développés ont bien tous le même niveau, et ils battent facilement le joueur aléatoire.

Les deux metrics de performances observées ici sont le temps de calcul pour jouer et le nombre de sommets explorés. Notre meilleur algorithme d'après ces metrics est ici MinMax avec une table de transposition (MinMax_Transposition), car on calcule, enregistre et réutilise la valeur de chaque carte.

Nous avons essayé de choisir les mouvements suivants avec la fonction d'évaluation du cours n°3 (sur le nombre de lignes ouvertes) pour améliorer les performances d'élagague. Les algorithmes avec cette approche (suffice -Oriente) explorent bien moins de noeuds, mais la fonction d'évaluation étant peu performante, son calcul pénalise la performance en temps de calcul des algorithmes concernés.

##### Step 1: Utilisation des algorithmes vus en cours

Cf Partie algorithmes

* MinMax
* MinMax avec une table de transposition
* AlphaBeta
* NegaMax (variante de MinMax)
* Monte Carlo Tree Search
* Negascout (variante de NegaMax)

Ici les algorithmes ont un champs d'exploration tellement limités (3 ou 4 coups d'avance) que leur performance en combat se dégrage fortement, si on compare leur performance par rapport au joueur aléatoire.

##### Step 2: Tree pruning, simplification et développement d'heuristiques

<hr>

## <a name="alg"></a>3. Algorithmes

Ces algorithmes reposent sur une surcharge de la fonction next move de joueur interne qui tend généralement à simplifier et à guider de façon plus intelligente l'exploration de notre arbre.

Remarque: ces méthodes ne sont généralement pas exclusives et reposent sur des améliorations apportées à différentes étapes du choix du next_move de nos unités. Autrement dit nous pouvons les combiner (par exemple: Negamax avec transposition et most probable outcome)

### MinMax

Réécriture de la fonction next_move qui applique l'algorithme MinMax au choix de la position.

### Variante Negamax

Simplfication du MinMax qui repose sur le fait que nous sommes dans un jeu à somme nulle.

### Variante Negascout

Amélioration du Negamax n'explorant que des noeuds n'étant pas élagué par l'alphabéta. (version non fonctionnelle ????)

### MonteCarloTreeSearch

Exploration de l'arbre de jeu, selon un critère statistique (Upper Confidence Bound), par simulations. 

Nous avons reussi sur nos ordinateurs avec les approximations décrites plus tard (MPOO) à réaliser 3000 simulations en 2s. Nous utilisons la table de transposition pour enregistrer les simulations d'une carte de départ. Cette approche bien que prometteuse grâce à sa granularité de calcul, ne marche pas aussi bien en pratique. Certaines simulations peuvent durer tellement de temps que l'algorithme peut sauter son tour facilement.

### Optimisation de l'algorithme

* **Ajout d'une table de hashage** <br>
  Cela permet de garder en mémoire les scores des cartes déjà rencontrées afin de ne pas les recalculer (économie de calcul). Tout comme pour le jeu du Morpion, nous avons repris la table de hashage de Zobrist pour hasher les positions d'une carte.

* **Simplification dans la façon dont notre joueur voit la carte** <br>
  Cette variante du Most Probable Outcome effectue des choix drastiques en limitant le nombre de groupes ennemis que nous prenons en compte et en limitant le nombre de sommets que nous explorons à chaque profondeur. Le but est ici de faire abstraction des groupes d'ennemis trop petits que certains de nos concurrents pourrait créer lors du tournoi pour ralentir notre exploration du jeu.


### MPOO
Cette variante du Most Probable Outcome effectue des choix drastiques en:
- Limitant le nombre de groupes ennemis que nous prenons en compte (paramêtre donné en argument à l'arbre Négamax). Cela permet de ne pas être sensible à un ennemi se splitant de multiple fois dans le but de ralentir notre parcours de l'arbre.
- Limitant le nombre de split possible pour chaque case: pas de split en trois (ou plus) groupes, pas de création de groupe de taille inférieur à min(2, taille_du_groupe//3). Enfin toutes les répartitions possibles ne sont pas conservées (on ne regarde que les répartitions 20%/80%, 40%/60%, 60%/40% et 80%/20%)
- Limitant le nombre de cases que nous considérons pour chaque groupes (paramêtre donné en argument à l'arbre Négamax). L'heuristique utilisé pour trier les 8 cases est très simple puisqu'elle ne considère que les contenus de ces 8 cases.

Cela nous permet de limiter fortement le facteur de branchement à chaque profondeur et ainsi d'explorer l'arbre beaucoup plus en profondeur. De plus, les calculs d'heuristiques intermédiaires étant très simples, nous arrivons à calculer environ 10k noeuds/seconde.

Malheureusement, nos heuristiques trop simples nous amenaient souvent à prendre des décisions allant à l'encontre du bon sens et faibles face des algorithmes plus naïfs de type glouton.


### MPO_2
Cette variante du Most Probable Outcome utilise un autre algorithme pour générer les mouvements possibles sur une carte donnée. Le facteur de branchement est ainsi inférieur ou égal à 8.
L'heuristique utilisée pour obtenir ce petit nombre de mouvements est plus lourde que celle précédemment utilisée. Cela limite fortement le nombre de noeuds générable par seconde (environ 600 noeuds/s sur une config vieille de 6 ans).

## <a name="strat"></a>4. Heuristiques

Notre fonction heuristique sur le jeu est

$nombre_monstres - nombre_ennemis$

## <a name="approches"></a>5. Approches testées et imaginées

### <a name="behaviors"></a> i. Avoir différents comportements

Nous aurions aimé mettre en place différents comportements de nos escadrons de monstres en fonction de différentes situations dans lesquelles le jeu se trouverait. Parmi ces différents comportements nous avions imaginé :

* Poursuivre l'ennemi
* Attaquer des humains en priorité
* Eviter l'ennemi
* Avoir un attrait pour le risque et les batailles aléatoires

Ces comportements auraient été déclenchés par différentes conditions sur le plateau :

* Absence d'humains
* Situation délicate à l'approche de la fin du jeu
* Ennemi en faible nombre

### <a name="multiprocessing"></a> ii. Multiprocessing
Nous n'utilisons pas toutes les capacités des ordinateurs à notre disposition malheureusement. Nous avions imaginé pouvoir distribuer plusieurs arbres d'explorations à profondeur différente sur plusieurs processeurs en parallèle. La profondeur d'exploration s'adapterait à la puissance de calcul disponible pour vérifier plusieurs contraintes :
* Toujours renvoyer une proposition de prochains mouvements dans le temps imparti
* Renvoyer la meilleure proposition de prochains mouvements possibles avec le temps imparti avec une profondeur maximale

### <a name="exploration"></a> iii. Exploration de l'arbre pendant les temps d'attente
Nous aurions pu continuer l'exploration de notre arbre de jeu pendant les temps d'attente, c'est-à-dire, pendant que l'adversaire réfléchit sur son prochain coup. Cela aurait permis d'améliorer quelque peu notre exploration (le gain potentiel est assez faible au vu du facteur de branchement élevé de l'abre de jeu, surtout pour estimer le coup d'un adversaire qu'on ne connait pas). Cette approche étant compliquée à mettre en place, nous n'avons pas pris le temps de l'essayer.


## <a name="perf"></a>6. Mesures de performance, test et conclusions

Deux moyens pour comparer la performance des algorithmes:

* **Lancer un tournoi**

  Le fichier Tournoi dans le dossier Tournoi permet d'effectuer des duels entre différents algorithmes de décision (du dossier Algorithmes), sur plusieurs cartes données (du dossier Cartes).

* **Lancer une compétition "darwin" pour avoir une compréhension plus fine des hyper paramètres**

  Le darwin search prend en entrée un algorithme à hyper paramètres et génère une population en effectuant produit cartésien de ces paramètres discrétisés.
  C'est une variante de l'algorithme tournoi un peu spéciale car on va ajouter à un pool de combat aléatoirement ces individus, effectuer un tournoi et ne garder que les n meilleurs (les survivants).
  On répète cette idée pour voir quels algorithmes survivent le plus longtemps (ie restent dans le pool)
