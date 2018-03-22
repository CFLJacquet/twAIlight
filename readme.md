<h1 align='center'> Projet TwAIlight </h1>
<p align='center'>
<i>Option ISIA - Centrale Paris <br>
Mars 2018 <hr></i></p>

__Auteur__ : Silvestre Perret, Mathieu Seris, Chloé Gobé, Charles Jacquet, Eymard Houdeville <br>

## Index
1. [Présentation générale](#description)
      1. [Introduction](#subparagraph1)
      2. [Arborescence détaillée du projet](#subparagraph1)
2. [Présentation et représentation du problème](#rep)
      1. [Le fichier Map](#map)
3. [Approches testées et méthode de développement](#test)
4. [Algorithmes](#alg)
      1. [MinMax](#minmax)
5. [Heuristiques](#strat)
6. [Mesures de performance, tests et conclusions](#perf)
      1. [Tournoi](#subparagraph1)
      2. [Tournoi Darwin](#subparagraph1)

Le but de ce projet est de développer une intelligence artificielle capable de jouer au jeu "Vampire contre Loups-Garou". Les règles du jeu sont dans le fichier "Projetv10b.pdf".
Ce github contient notre implémentation des algorithmes que nous proposons pour le tournoi du 23 Mars 2018.

## <a name="description"></a>2. Présentation et représentation du problème

### Introduction

Extrait du sujet:

>Dans un monde lointain, des êtres mortels et ordinaires vivaient une vie paisible. Mais un soir, à la nuit tombée, leurs terres furent le témoin d’une lutte acharnée entre deux espèces : les Vampires et les Loups-Garous.

NB: comme convenu ce readme se concentre sur les stratégies et algorithmes impleméntés par l"équipe et ne développe pas les aspects liés à la communication avec le serveur.

### Arborescence détaillée du Projet

- **twAIllight** Repertoire principal du projet

  - **Cartes** : Les différentes cartes sur lesquelles nous pouvons tester notre IA

  - **Joueur.py** :
  Le fichier de base est Joueur.py .
  Il contient la classe Joueur qui peut jouer et communiquer avec le serveur du projet.
  La méthode de classe next_moves est la méthode qui décide du prochain mouvement (par défaut, c'est la fonction aléatoire de Charles).

  - **Joueur_interne.py** :
  Le fichier Joueur_Interne.py contient une classe héritée de Joueur, qui communique avec le serveur interne. Seules les méthodes de communication ont été surchargées.
  Par défaut, le joueur interne joue aléatoirement et split nos unités aléatoirement.

  - **Map.py** : La représentation de la carte du jeu et les méthodes afférentes que nos IA utilisent

  - **Serveur_interne.py** : Le fichier contenant notre simulation de serveur
  Notre serveur interne est dans le fichier Serveur_Interne.py.
  Pour lancer le jeu en interne, on 'start' (comme un thread) une instance de ServeurInterne.
  ServeurInterne est initialisé avec deux classes de joueurs internes et une carte (classe Map du fichier Map.py ou héritées).

  - **Tournoi.py** : La possibilité d'organiser des tournois entre nos IA (entre elles) ou contre l'algorithme aléatoire qui nous sert de benchmark.
  Le fichier Tournoi dans le dossier Tournoi permet d'effectuer des duels entre différents algo de décision (du dossier Algorithmes), sur plusieurs cartes données (du dossier Cartes).

  - **Darwin_Search.py** : L'idée de la recherche darwiniennes est de tester et de classer nos différentes algorithmes en effectuant un très grand nombre de tournois entre différentes instances avec des hyperparamètres différents (un hyperparamètre sera typiquement le nombre de groupe d'adversaire max que l'on considère quand on cherche à faire un mouvement)

  - **Morpion.py** : L'idée de ce dossier Morpion est d'implémenter et de tester sur un problème plus simple différentes approches avant de transposer celles-ci à jeu Vampire vs Loup-garous. Ce dossier nous permet de 1) vérifier que nous avons bien compris les stratégies et algorithmes et que nous les pensons pertinentes pour notre problème 2) Posséder une base qui nous permet d'itérer et de développer plus rapidement les algorithmes sur le jeu Vamp vs LG.

    - **Map_Morpion.py** : La "carte" du morpion

    - **Sommet_du_Jeu_Aléatoire.py** : Un base-case, il faut au moins battre cet algorithme simpliste (ie : ne pas tricher, prendre des décisions qui nous permettent de l'emporter contre ce joueur aveugle)

    Ce dossier contient aussi nos différents algorithmes pour le jeu du morpion:

    - **Sommet_du_Jeu_AlphaBeta_Oriente.py**
    - **Sommet_du_Jeu_AlphaBeta.py**
    - **Sommet_du_Jeu_MinMax_Transposition.py**
    - **Sommet_du_Jeu_MinMax.py**
    - **Sommet_du_Jeu_NegaMax_Transposition.py**
    - **Sommet_du_Jeu_NegaMax_Transposition_Oriente.py**
    - **Sommet_du_Jeu** :
    - **Tournoi** : Organisation d'un tournoi entre IA

  - **Test.py** : Nos tests unitaires

  - **Missions.py** : Dossier explorant la piste des heuristiques
    - **Human First.py** :

  - **Algorithmes** : Les différents algorithmes développés et testés pour le tournoi.
  Ces algorithmes héritent tous de la classe JoueurInterne.

  Ce dossier contient deux types de fichiers:
  - Les algorithmes eux-mêmes,
  - Les "représentations du monde" qu'ils utilisent (les fichiers Sommets_du_jeu)

Ces différents algorithmes sont expliqués plus loin dans ce document.

    - **Algo_Customized_Evaluation.py**
    - **Algo_MinMax.py**
    - **Algo_MonteCarloTreeSearch.py**
    - **Algo_NegaMax_MPOO.py**
    - **Algo_NegaMax_Oriente.py**
    - **Algo_NegaMax_Probable_outcome.py**
    - **Algo_NegaMax.py**
    - **Algo_Temporal_Difference_0.py**

    - **Sommet_du_Jeu_MinMax_Transposition.py**
    - **Sommet_du_Jeu_MonteCarlo.py**
    - **Sommet_du_Jeu_NegaMax_MPOO.py**
    - **Sommet_du_Jeu_NegaMax_probable_outcome.py**
    - **Sommet_du_Jeu_NegaMax_Transposition_Oriente.py**
    - **Sommet_du_Jeu_NegaMax_Transposition.py**
    - **Sommet_du_Jeu_Temporal_Diffrence_0.py**
    - **Sommet_du_Jeu.py**


  De façon générale,  pour tester un nouvel algo de décision:
    * Si on veut un joueur en local ("interne"), on crée une classe héritée de JoueurInterne, à laquelle on surcharge la fonction next_moves,
    * Si on veut un joueur avec le serveur du projet, on crée une classe héritée de Joueur, à laquelle on surcharge la fonction next_moves.

## <a name="test"></a>3. Approches testées et méthode de développement

Notre approche est globalement la suivante:

##### Step 0: Un problème plus simple
Pour nous appropier les algorithmes nous avons utilisé un problème plus simple (le Morpion).

##### Step 1: Utilisation des algorithmes vus en cours
Cf Partie algorithmes

##### Step 2: Tree pruning, simplification et développement d'heuristiques

## <a name="alg"></a>4. Algorithmes

Ces algorithmes reposent sur une surcharge de la fonction next move de joueur interne qui tend généralement à simplifier et à guider de façon plus intelligente l'exploration de notre arbre.

Remarque: ces méthodes ne sont généralement pas exclusives et reposent sur des améliorations apportées à différentes étapes du choix du next_move de nos unités. Autrement dit nous pouvons les combiner (par exemple: Negamax avec transposition et most probable outcome)

### <a name="a"></a> i. Variantes reposant sur une simplification du calcul des prochaines étapes potentielles du jeu

#### MinMax
Réécriture de la fonction next_move qui applique l'algorithme minmax au choix de la position.

#### Variante Negamax
Simplfication du MinMax qui repose sur le fait que nous sommes dans un jeu à somme nulle.

#### Most probable outcome
Variante du negamax dans notre code qui simplifie grandement l'arbre en ne conservant que les noeuds à probabilité (ceux issus des combats par exemple) les plus probables (avec la probabilité la plus élévée).
Cette méthode de pruning oblige notre joueur à ne considérer que les issues les plus probables de chaque tour et allège de façon importante les calculs.

### MonteCarlo

### <a name="a"></a> ii. Améliorations liées au calcul

#### Variante MinMax with Transposition
Variante du MinMax avec une table de hashage qui permet de garder une mémoire des calculs de coùuts/gains (économie de calcul)

### <a name="a"></a> iii. Variantes reposant sur une simplification dans la façon dont notre joueur voit la carte

#### MPOO
Cette variante du Most Probable Outcome effectue des choix drastiques en:
- Limitant le nombre de groupes ennemis que nous prenons en compte
- Limitant le nombre de sommets que nous explorons à chaque profondeur

### Nota bene, Pour lancer un joueur pour jouer sur le serveur le jour du tournoi:
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

## <a name="strat"></a>5. Heuristiques

Nous avons pensé à différentes heuristiques (et méta heuristiques) que nous n'avons malheureusement pas complètement eu le temps d'implémenter.

 (insérer les heuristiques de Chloé)
 
## <a name="perf"></a>6. Mesures de performance, remarques et conclusions

Deux moyens pour comparer la performance des algorithmes:

- Lancer un tournoi
Le fichier Tournoi dans le dossier Tournoi permet d'effectuer des duels entre différents algo de décision (du dossier Algorithmes), sur plusieurs cartes données (du dossier Cartes).

- Lancer une compétition "darwin" pour avoir une compréhension plus fine des hyper paramètres:
Le darwin search prend en entrée un algorithme à hyper paramètres et génère une population en effectuant produit cartésien de ces paramètres discrétisés.
C'est une variante de l'algorithme tournoi un peu spéciale car on va ajouter à un pool de combat aléatoirement ces individus, effectuer un tournoi et ne garder que les n meilleurs (les survivants).
On répète cette idée pour voir quels algorithmes survivent le plus longtemps (ie restent dans le pool)
