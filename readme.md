<h1 align='center'> Projet TwAIlight </h1>
<p align='center'>
<i>Option ISIA - Centrale Paris <br>
Mars 2018 <hr></i></p>

__Auteur__ : Silvestre Perret, Mathieu Seris, Chloé Gobé, Charles Jacquet, Eymard Houdeville <br>

## Index
1. [Présentation générale](#description)
      1. [Introduction](#subparagraph1)
      2. [Arborescence détaillée du projet](#subparagraph1)
2. [Représentation du problème](#rep)
      1. [Le fichier Map](#map)
3. [Approches testées et méthode de développement](#test)
4. [Algorithmes](#alg)
      1. [MinMax](#minmax)
5. [Stratégies](#strat)
6. [Mesures de performance, tests et conclusions](#perf)
      1. [Tournoi](#subparagraph1)
      2. [Tournoi Darwin](#subparagraph1)

Le but de ce projet est de développer une intelligence artificielle capable de jouer au jeu "Vampire contre Loups-Garou". Les règles du jeu sont dans le fichier "Projetv10b.pdf".
Ce github contient notre implémentation des algorithmes que nous proposons pour le tournoi du 23 Mars 2018.

## <a name="description"></a>1. Présentation et représentation du problème

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

  Pour tester un nouvel algo de décision:

  * Si on veut un joueur en local ("interne"), on crée une classe héritée de JoueurInterne, à laquelle on surcharge la fonction next_moves,
  * Si on veut un joueur avec le serveur du projet, on crée une classe héritée de Joueur, à laquelle on surcharge la fonction next_moves.

    - **Algo_Customized_Evaluation.py** : Une réécriture de la classe JoueurInterne, qui suit une fonction d'évaluation personnalisée

    - **Algo_MinMax.py** : Une réécriture "MinMax" de la classe JoueurInterne
    - **Algo_MonteCarloTreeSearch.py** : Une réécriture "MonteCarlo" de la classe JoueurInterne
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

## <a name="test"></a>1. Approches testées et méthode de développement

Notre approche est globalement la suivante:

##### Step 0: Un problème plus simple
Pour nous appropier les algorithmes nous avons utilisé un problème plus simple (le Morpion).

##### Step 1: Utilisation des algorithmes vus en cours

##### Step 2: Tree pruning, simplification et développement d'heuristiques

## <a name="alg"></a>1. Algorithmes

## <a name="strat"></a>1. Stratégies

## <a name="perf"></a>1. Mesures de performance, remarques et conclusions

Deux moyens pour comparer la performance des algorithmes:

- Lancer un tournoi
Le tournoi est alors effectué sur un jeu de cartes (données en paramètres): on effectue des matchs aller et retour (adversaire A commence puis adversaire B)

- Lancer une compétition "darwin":
Nous nous sommes demandés

Le fichier Tournoi dans le dossier Tournoi permet d'effectuer des duels entre différents algo de décision (du dossier Algorithmes), sur plusieurs cartes données (du dossier Cartes).

# Pour lancer un joueur pour jouer sur le serveur du prof
* Créer dans un fichier une classe héritée de Joueur (dans Joueur.py), qui override la méthode next_moves de Joueur
* Ecrire dans ce fichier 
```python
if __name__=='__main__':
  Joueur_1=NotreClasseHéritéeDeJoueur()
  Joueur_1.start()
  Joueur_1.join()
```
* Lancer le serveur du prof
* Taper dans le terminal (avec XXX.X.X.X YYYY l'hote et le port du serveur du prof)
```bash
python MonAlgo.py XXX.X.X.X YYYY
```


