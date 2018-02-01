Le fichier de base est Client_Joueur.py .
Il contient la classe Joueur_Client qui peut jouer et communiquer avec le serveur du projet. 
La méthode de classe next_moves est la méthode qui décide du prochain mouvement (par défaut, c'est la fonction aléatoire de Charles).

Le fichier Joueur_Interne.py contient une classe héritée de Joeur_Client, qui communique avec le serveur interne.

Notre serveur interne est dans le fichier Serveur_Interne.py. 
Pour lancer le jeu, on 'start' (comme un thread) une instance de ServeurInterne.
ServeurInterne est initialisé avec deux joueurs internes et une carte (instance de MapInterne dans le fichier Map_Interne.py)

Pour tester un nouvel algo de calcul du prochains mouvements: 
 * Si on veut un joueur en local (interne), on crée une instance héritée de JoueurInterne, à laquelle on surcharge la fonction next_moves,
 * Si on veut un joueur avec le serveur du projet, on crée une instance héritée de Joueur_Client, à laquelle on on surcharge la fonction next_moves.