from threading import Thread
from queue import Queue
import time

from Joueur_Interne import JoueurInterne
from Map import Map

PORT = 5555  # TODO à changer pour le tournoi
HOTE = "127.0.0.1"  # TODO à changer pour le tournoi


class ServeurInterne(Thread):
    """
    Imite le serveur de jeu du projet.
    Prend en argument la carte, les deux joueurs et lance une partie lorsqu'on le demarre.
    Par défaut, le premier joueur est un vampire.
    """

    def __init__(self, game_map_class, player_1_class, player_2_class, name1=None, name2=None, debug_mode=False,
                 print_map=True):
        """
        Initialse le serveur interne  avec une carte et deux joueurs
        :param game_map_class: classe de la carte du jeu
        :param player_1_class: classe du joueur 1
        :param player_2_class: classe du joueur 2
        :param name1: nom du joueur 1
        :param name2: nom du joueur 2
        :param debug_mode: (boolean) mode debug
        :param print_map: (boolean) si vrai affiche la carte du jeu à chaque tour
        """
        super().__init__()
        self.queue_server_p1 = Queue()  # Queue de communication serveur vers joueur 1
        self.queue_server_p2 = Queue()  # Queue de communication serveur vers joueur 2
        self.queue_p1_server = Queue()  # Queue de communication joueur 1 vers serveur
        self.queue_p2_server = Queue()  # Queue de communication joueur 2 vers serveur
        self.player_1 = player_1_class(self.queue_p1_server, self.queue_server_p1, name=name1, debug_mode=debug_mode)
        self.player_2 = player_2_class(self.queue_p2_server, self.queue_server_p2, name=name2, debug_mode=debug_mode)
        self.updates_for_1 = []  # liste des changements pour mettre à jour la carte du joueur 1
        self.updates_for_2 = []  # liste des changements pour mettre à jour la carte du joueur 2

        self.map = game_map_class(debug_mode=debug_mode)  # carte de la première partie
        self.map_class= game_map_class # classe de la carte du jeu (pour les rematchs en cas de match nul)

        self.debug_mode = debug_mode  # Pour afficher tous les logs
        self.print_map = print_map  # Pour afficher ou non la carte au cours de la partie
        self.winner = None  # True si c'est le joueur 1 / vampire, False sinon
        self.round_nb = 0  # Numéro de tour joué
        self.start_time=0 # Date de début de la partie

    def run(self):
        """
        Méthode appelée pour lancer le serveur (lorsqu'on tape *server*.start()
        :return: None
        """
        # Démarrage des Joueurs
        self.player_1.start()
        self.player_2.start()

        # Réception des noms des joueurs

        command = self.queue_p1_server.get()  # commande NME
        name_1 = self.queue_p1_server.get()
        print("Server : Joueur 1 : " + str(name_1))

        command = self.queue_p2_server.get()  # commande NME
        name_2 = self.queue_p2_server.get()
        print("Server : Joueur 2 : " + str(name_2))

        # Initialisation du jeu
        self.start_new_game()

        # Affichage de la carte
        if self.print_map: self.map.print_map()
        while True:
            # Réception des mouvements du joueur 1
            moves = self.get_MOV(self.queue_p1_server)

            if self.debug_mode: print('Server : MOV received from ' + self.player_1.name)

            # Vérification des mouvements du joueur 1
            if not self.map.is_valid_moves(moves, is_vamp=True):  # mouvements incorrects
                print("Server : {} a triché !".format(self.player_1.name))
                self.winner = False  # le joueur 1 a perdu
                self.send_both_players(b"END")  # Fin de la partie
                self.send_both_players(b"BYE")  # Fin du jeu
                print("Server : {} gagne !".format(self.player_2.name))
                break

            # Mise à jour et calcul de la nouvelle carte
            # les mouvements du joueur 1 sont valides ici
            self.map.update_and_compute(moves)

            # Tour suivant
            self.round_nb += 1

            # On affiche l'espèce qui doit jouer
            print("Server : Round " + str(self.round_nb) + " : "
                  + ("Vampires" if self.round_nb % 2 else "WereWolves") + " playing")

            # Affichage de la carte
            if self.print_map: self.map.print_map()

            if self.debug_mode: print('Server : Map updated')

            # Cas : la partie est terminée
            if self.map.game_over():
                # Envoi d'un message de fin de partie aux joueurs
                self.send_both_players(b"END")

                # match nul
                if self.map.winner() is None:
                    # On commence une nouvelle partie
                    self.start_new_game()
                    continue

                # joueur 1 gagne
                elif self.map.winner():
                    print("Server : {} gagne !".format(self.player_1.name))
                    self.winner = True  # Joueur 1 a gagné
                    # Fin du jeu envoyé aux joueurs
                    self.send_both_players(b"BYE")
                    break

                # joueur 2 gagne
                else:
                    print("Server : {} gagne !".format(self.player_2.name))
                    self.winner = False  # Joueur 2 a gagné
                    # Fin du jeu envoyé aux joueurs
                    self.send_both_players(b"BYE")
                    break

            if self.debug_mode: print("Server : sending UDP")

            # On envoie la carte mise à jour au joueur 2
            self.send_UPD(to_player_1=False)

            # Le joueur envoie au serveur sa proposition de mouvements
            moves = self.get_MOV(self.queue_p2_server)

            # Vérification des mouvements proposés de joueur 2
            if not self.map.is_valid_moves(moves, is_vamp=False):
                print("Server : {} a triché !".format(self.player_2.name))
                self.winner = True  # Le joueur 1 a gagné
                self.send_both_players(b"END")  # Fin de la partie
                self.send_both_players(b"BYE")  # Fin du jeu
                print("Server : {} gagne !".format(self.player_1.name))
                break

            self.round_nb += 1  # Tour suivant
            # Affichage du tour et de l'expèce qui doit jouer
            print("Server : Round " + str(self.round_nb) + " : "
                  + ("Vampires" if self.round_nb % 2 else "WereWolves") + " playing")

            # Mise à jour de la carte à partir des mouvements proposés par le joueur 2
            self.map.update_and_compute(moves)

            # Affichage de la carte
            if self.print_map: self.map.print_map()

            # Cas : la partie est terminée
            if self.map.game_over():

                # Envoi au deux joueurs de la fin de la partie
                self.send_both_players(b"END")

                # match nul
                if self.map.winner() is None:
                    print('Server : Close Game')
                    self.start_new_game()
                    print('Server : Starting a new game')
                    continue

                # Joueur 1 gagne
                elif self.map.winner():
                    print("Server : {} gagne !".format(self.player_1.name))
                    self.winner = True  # Joueur 1 gagne
                    self.send_both_players(b"BYE")  # Envoi de la fin du jeu aux joueurs
                    break

                # Joueur 2 gagne
                else:
                    print("Server : {} gagne !".format(self.player_2.name))
                    self.winner = False  # Joueur 2 gagne
                    self.send_both_players(b"BYE")  # Envoi de la fin du jeu aux joueurs
                    break

            # Envoi de la carte mise à jour au joueur 1
            self.send_UPD(to_player_1=True)

    # Méthodes de communication avec les joueurs

    def get_MOV(self, queue):
        """ Récupère les mouvements proposés d'un joueur

        :param queue: queue de communication joueur --> serveur
        :return: moves: liste des mouvements
        """
        command = queue.get()  # MOV command
        if self.debug_mode: print("Server/MOV : " + str(command))
        n_move = queue.get()  # Nombre de mouvements
        if self.debug_mode: print("Server/MOV : " + str(n_move))
        moves = []  # liste des mouvements
        for _ in range(n_move):
            moves.append(queue.get())  # Récupération de chaque mouvement

        if self.debug_mode: print("Server/MOV : " + str(moves))
        return moves

    def send_both_players(self, message):
        """ Envoie un message aux deux joueurs en même temps

        :param message: string
        :return: None
        """
        self.queue_server_p1.put(message)
        self.queue_server_p2.put(message)

    def send_UPD(self, to_player_1):
        """ Envoi la liste des mises à jour de la carte à un jour

        :param to_player_1: boolean Vrai si on envoie au Joueur 1 Faux sinon
        :return: None
        """
        updates = self.map.UPD  # Modifications de la carte depuis la dernière mise à jour
        self.updates_for_1 += updates  # on ajoute les modifications la liste tampon du joueur 1
        self.updates_for_2 += updates  # on ajoute les modifications la liste tampon du joueur 2
        if to_player_1:  # Si on doit envoyer les mises à jour au joueur 1
            n = len(self.updates_for_1)  # Nombre de mises à jour à transmettre
            self.queue_server_p1.put(b"UPD")  # Envoi de la commande UPD
            self.queue_server_p1.put(n)  # Envoi du nombre de mises à jour
            for update in self.updates_for_1:
                self.queue_server_p1.put(update)  # Envoi de chaque de mise à jour au joueur 1
            self.updates_for_1 = []  # On vide la liste tampon des modifications de la carte du joueur 1
        else:  # Si on doit envoyer les mises à jour au joueur 2
            n = len(self.updates_for_2)  # Nombre de mises à jour à transmettre
            self.queue_server_p2.put(b"UPD")  # Envoi de la commande UPD
            self.queue_server_p2.put(n)  # Envoi du nombre de mises à jour
            for update in self.updates_for_2:
                self.queue_server_p2.put(update)  # Envoi de chaque de mise à jour au joueur 2
            self.updates_for_2 = []  # On vide la liste tampon des modifications de la carte du joueur 1

    # Méthodes de traitement


    def start_new_game(self):
        """
        Initialise la partie pour les deux joueurs
        :return: None
        """

        # Remise à zéro de la carte

        self.map=self.map_class(debug_mode=self.debug_mode)
        # Compteur de tours
        self.round_nb = 1

        # Mise à zéro des listes tampon de modifications de carte
        self.updates_for_1, self.updates_for_2 = [], []

        # Affichage du premier tour
        print("Server : Round " + str(self.round_nb) + " : " + (
            "Vampires" if self.round_nb % 2 else "WereWolves") + " playing")

        # Envoi des dimensions de la carte aux deux joueurs
        self.send_both_players(b"SET")
        self.send_both_players(self.map.size[::-1])  # Pour imiter le serveur du projet

        # pas de HUM envoyés (c'est différent du serveur de projet)

        # Envoi de la commande Home
        self.queue_server_p1.put(b"HME")
        self.queue_server_p1.put(self.map.home_vampire())  # Case de départ du joueur 1 envoyé
        self.queue_server_p2.put(b"HME")
        self.queue_server_p2.put(self.map.home_werewolf())  # Case de départ du joueur 2 envoyé

        # Envoi de la carte aux joueurs
        self.send_both_players(b"MAP")
        n, elements = self.map.MAP_command()  # Nombres de cases peuplés, coordonnées des cases peuplées

        self.send_both_players(n)  # Envoi du nombre de case peuplé aux deux joueurs
        for quintuplet in elements:
            self.send_both_players(quintuplet)  # Envoi de chaque coordonnées et et populations de chaque case peuplée

        # Let's start the game
        # La commande UPD déclenche le mouvement des pions joueur 1
        self.queue_server_p1.put(b"UPD")
        self.queue_server_p1.put(0)

        # On enregistre la date du début de la partie
        self.start_time=time.time()

        if self.debug_mode: print("Server : New Game settings sent !")


if __name__ == "__main__":
    serveur = ServeurInterne(Map, JoueurInterne, JoueurInterne, name2="Player2")
    serveur.debug_mode = False
    serveur.print_map = True
    serveur.start()
    serveur.join()
    print(serveur.winner)
