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
