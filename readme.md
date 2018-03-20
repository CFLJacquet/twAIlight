# Projet TwAIlight

# Présentation

Le fichier de base est Joueur.py .
Il contient la classe Joueur qui peut jouer et communiquer avec le serveur du projet.
La méthode de classe next_moves est la méthode qui décide du prochain mouvement (par défaut, c'est la fonction aléatoire de Charles).

Le fichier Joueur_Interne.py contient une classe héritée de Joueur, qui communique avec le serveur interne. Seules les méthodes de communication ont été surchargées.

Notre serveur interne est dans le fichier Serveur_Interne.py.
Pour lancer le jeu en interne, on 'start' (comme un thread) une instance de ServeurInterne.
ServeurInterne est initialisé avec deux classes de joueurs internes et une carte (classe Map du fichier Map.py ou héritées).

# Pour tester un nouvel algo de décision:

* Si on veut un joueur en local ("interne"), on crée une classe héritée de JoueurInterne, à laquelle on surcharge la fonction next_moves,
* Si on veut un joueur avec le serveur du projet, on crée une classe héritée de Joueur, à laquelle on surcharge la fonction next_moves.

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
```shell
python MonAlgo.py XXX.X.X.X YYYY
```

