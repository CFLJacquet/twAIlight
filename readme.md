Projet TwAIlight
=====

# Comment tester son IA ?
Le fichier de base est Client\_Joueur.py .
Il contient la classe Joueur\_Client qui peut jouer et communiquer avec le serveur du projet. 
La méthode de classe next\_moves est la méthode qui décide du prochain mouvement (par défaut, c'est la fonction aléatoire de Charles).

Le fichier Joueur\_Interne.py contient une classe héritée de Joueur\_Client, qui communique avec le serveur interne. Seules les méthodes de communication ont été surchargées.

Notre serveur interne est dans le fichier Serveur\_Interne.py. 
Pour lancer le jeu en interne, on 'start' (comme un thread) une instance de ServeurInterne.
ServeurInterne est initialisé avec deux joueurs internes et une carte (instance Map dans le fichier Map.py).

__Pour tester un nouvel algo de décision: 
 * Si on veut un joueur en local ("interne"), on crée une instance héritée de JoueurInterne, à laquelle on surcharge la fonction next\_moves,
 * Si on veut un joueur avec le serveur du projet, on crée une instance héritée de Joueur\_Client, à laquelle on surcharge la fonction next\_moves.__
 
