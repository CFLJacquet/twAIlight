import socket
import struct
import sys
import random
from itertools import product
from threading import Thread
import time

from twAIlight.Map_Silv import Map

PORT = 5555  # TODO à changer pour le tournoi
HOTE = "127.0.0.1"  # TODO à changer pour le tournoi


# HOTE = sys.argv[1]
# PORT = int(sys.argv[2])

class Joueur(Thread):
    """
    Classe représentant un joueur du jeu, communiquant avec le serveur du projet
    """
    __NAME = "TwAIlight"  # Nom par défaut

    def __init__(self, name=None, debug_mode=False, joueur_interne=False):
        """

        :param name: Nom du joueur, si différent du défaut
        :param debug_mode: mode debug (boolean)
        :param joueur_interne: type de joueur (Vrai si joueur interne, Faux si joueur communiquant avec le serveur du projet
        """
        Thread.__init__(self)
        self.type_interne = joueur_interne
        if name is None:
            name = Joueur.__NAME
        self.name = name  # Nom du joueur
        self.sock = None  # Socket de communication avec le serveur (reste à None si le serveur est interne)
        self.home = None  # Case de départ du joueur
        self.map = None  # Carte d'après le joueur
        self.is_vamp = None  # Vrai si le joueur est un vampire, Faux si c'est un loup-garou
        self.debug_mode = debug_mode  # mode debug, pour afficher les logs
        self.round_played = 0  # Compte de tours joués par le joueur

    def run(self):
        """ Méthode appelée quand on lance le thread.

        :return: None
        """

        # Si on est en communication avec le serveur du projet,
        # on lance une communication TCP/IP
        if not self.type_interne:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOTE, PORT))

        # Envoi du nom du joueur au serveur
        self.send_NME()

        if self.debug_mode: print(self.name + " has joined the game.")
        while True:

            # Récupération du type de commande envoyée par le serveur
            command = self.get_command()

            # Le serveur nous envoie les dimensions de la carte
            if command == b"SET":
                if self.debug_mode: print(self.name + ": SET from server")
                n, m = self.get_couple()  # Nos dimensions de cartes
                if self.debug_mode: print("{} lines, {} columns".format(n, m))
                self.create_map((m, n))  # Création de la carte pour le joueur (on intervertit n et m)

            # Le serveur nous envoie la liste de humains présents sur la carte
            elif command == b"HUM":
                if self.debug_mode: print(self.name + ": HUM from server")
                human_location = []
                n = self.get_n()  # Nombre d'humains
                for _ in range(n):
                    human_location.append(self.get_couple())  # get_couple() donne les coordonnées de l'humain
                self.locate_humans(human_location)
                if self.debug_mode: print(self.name + ": HUM received")

            # Le serveur nous envoie notre case de départ
            elif command == b"HME":
                if self.debug_mode: print(self.name + ": HME from server")
                x, y = self.get_couple()  # Notre case de départ
                if self.debug_mode: print("({},{}) : start location".format(x, y))
                self.home = (x, y)  # On enregistre cette case de départ

            # Le serveur nous envoie la carte du jeu pour l'initialiser
            elif command == b"MAP":
                if self.debug_mode: print(self.name + ": MAP from server")
                n = self.get_n()  # Nombre de cases peuplées
                positions = []  # liste des positions des cases peuplées avec leur population
                for _ in range(n):
                    x, y, nb_hum, nb_vamp, nb_wv = self.get_quintuplet()  # tuple représentant une case de la carte
                    positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                if self.debug_mode: print(positions)

                self.map.create_positions(positions)  # On met à jour notre carte à partir des informations du serveur
                # On peut maintenant connaitre notre race, grâce aux infos sur la carte et notre case de départ
                self.define_race()
                print(self.name + " is a " + ("vampire" if self.is_vamp else "werewolf"))

            # Le serveur nous envoie la liste des mises à jour de la carte
            elif command == b"UPD":
                if self.debug_mode: print(self.name + ": UPD from server")
                n = self.get_n()  # nombre de mises à jour envoyées par le serveur
                if n:  # si on a plus d'une modification par rapport à notre carte ...
                    positions = []
                    for _ in range(n):
                        x, y, nb_hum, nb_vamp, nb_wv = self.get_quintuplet()
                        positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                    if self.debug_mode: print(positions)
                    self.map.update_content(positions)  # Mise à jour de la carte du joueur

                if self.debug_mode: print(self.name + ": UPD received")

                # On envoie les mouvements de notre joueur (self.next_moves()) au serveur
                # Explication du show_map : On affiche la carte quand notre joueur n'est pas interne
                self.send_MOV(self.next_moves(show_map=(not self.type_interne)))
                if self.debug_mode: print(self.name + ": MOV sent")

                # On incrémente notre compte de tours joués
                self.round_played += 1
                if self.debug_mode:
                    print(self.name + ": {} round(s) played".format(self.round_played))

            # Le serveur nous signale la fin de la partie
            elif command == b"END":
                if self.debug_mode: print(self.name + ": END from server")
                # Au cas de match nul, on réinitialise le joueur pour une possible prochaine partie
                self.init_game()

            # Le serveur nous signale la fin du jeu et de la communication
            elif command == b"BYE":
                if self.debug_mode: print(self.name + ": BYE from server")
                break
            else:  # Command inconnue
                if self.debug_mode: print(self.name + ' Unknown command :' + str(command))
        # On ferme la communication avec la socket si le joueur n'est pas interne
        if not self.type_interne:
            self.sock.close()

    # Méthodes de communication

    def get_command(self):
        """ Renvoie une type de commande envoyée au joueur par le serveur

        :return: bytes : la commande envoyée par le serveur
        """
        commande = bytes()
        while len(commande) < 3:
            commande += self.sock.recv(3 - len(commande))
        return commande

    def get_n(self):
        """ Renvoie l'entier envoyé par le serveur

        :return: int: entier envoyé
        """
        return struct.unpack("b", self.sock.recv(1))[0]

    def get_couple(self):
        """ Renvoie le couple d'entiers envoyé par le serveur

        :return: (x,y)
        """
        return struct.unpack("bb", self.sock.recv(2))

    def get_quintuplet(self):
        """ Renvoie le quintuplet d'entiers envoyé par le serveur

        :return: (a,b,c,d,e)
        """
        return struct.unpack("bbbbb", self.sock.recv(5))

    def send_NME(self):
        """ Envoie au serveur le nom du joueur

        :return: None
        """
        if self.debug_mode: print(self.name + ": Sending NME for " + self.name)
        paquet = bytes()
        t = len(self.name.encode('ascii'))
        paquet += "NME".encode('ascii')
        paquet += struct.pack("1b", t)
        paquet += self.name.encode('ascii')
        self.sock.send(paquet)

    def send_MOV(self, moves):
        """ Envoie au serveur la liste de mouvements du joueur

        :param moves: list: liste des mouvements du joueur à envoyer au serveur
        :return: None
        """
        if self.debug_mode: print(self.name + " Sending MOV : " + str(moves))
        n = len(moves)
        paquet = bytes()
        paquet += "MOV".encode("ascii")
        paquet += struct.pack("1b", n)
        for move in moves:
            paquet += struct.pack("bbbbb", *move)
        self.sock.send(paquet)

    # Méthode de traitement

    def create_map(self, map_size):
        """ Crée une carte à la taille map_size et l'enregistre dans l'attribut map

        :param map_size: (n,m) dimension de la carte
        :return: None
        """
        self.map = Map(map_size=map_size)

    def init_game(self):
        """ Initialise les attributs du joueur pour commencer une partie

        :return: None
        """
        self.home = None  # Case de départ
        self.map = None  # Carte
        self.is_vamp = None  # Race du joueur

    def define_race(self):
        """ Définit la race du joueur.

        :return:
        """
        # Parcours de la carte à la recherche de la case départ
        for i, j in self.map.content:
            if (i, j) == self.home:
                if self.map.content[(i, j)][1]:  # Vampires présents sur la case de départ
                    self.is_vamp = True
                else:  # Loups-Garous présents sur la case de départ
                    self.is_vamp = False
                break

    def locate_humans(self, human_locations):
        """Fonction vide, on ne traite pas la localisation des humains.
        On a assez d'informations, pour s'en passer."""
        pass


    def next_moves(self, show_map=True):
        """ Fonction pour faire bouger nos armées. Il y une probabilité aléatoire uniforme de se déplacer sur les cases
        adjascentes, et une probabilité aléatoire de casser le groupe en 2 s'il y a suffisamment de membres

        :param show_map: permet d'afficher la carte comprise pour un joueur. Très utile pour les parties avec le serveur du
        projet
        """
        if self.debug_mode: print(self.name + '/next_moves Map : ' + str(self.map.content))
        if show_map: self.map.print_map()

        return random.choice(self.map.next_possible_moves(self.is_vamp))


if __name__ == "__main__":
    # Création des joueurs
    Joueur_1 = Joueur(debug_mode=True)
    Joueur_2 = Joueur(name="Silvestre")

    # Lancement des deux threads des joueurs
    Joueur_1.start()
    Joueur_2.start()
