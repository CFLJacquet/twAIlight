import socket
import struct
import sys
import random
from itertools import product
from threading import Thread

from Map import Map

PORT = 5555  # TODO à changer pour le tournoi
HOTE = "127.0.0.1"  # TODO à changer pour le tournoi


class JoueurClient(Thread):
    __NAME = "TwAIlight"

    def __init__(self, name=None, debug_mode=False, joueur_interne=False):
        Thread.__init__(self)
        self.type_interne = joueur_interne
        if name is None:
            name = JoueurClient.__NAME
        self.name = name
        self.sock = None
        self.home = None
        self.map = None
        self.is_vamp = None
        self.debug_mode = debug_mode

    def run(self):
        if not self.type_interne:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOTE, PORT))

        self.send_NME()
        if self.debug_mode: print(self.name + " has joined the game.")
        while True:
            command = self.get_command()

            if command == b"SET":
                if self.debug_mode: print(self.name + ": SET from server")
                n, m = self.get_couple()
                if self.debug_mode: print("{} lines, {} columns".format(n, m))
                self.create_map((m, n))  # on intervertit !

            elif command == b"HUM":
                if self.debug_mode: print(self.name + ": HUM from server")
                human_location = []
                n = self.get_n()
                for _ in range(n):
                    human_location.append(self.get_couple())
                self.locate_humans(human_location)
                if self.debug_mode: print(self.name + ": HUM received")

            elif command == b"HME":
                if self.debug_mode: print(self.name + ": HME from server")
                x, y = self.get_couple()
                if self.debug_mode: print("({},{}) : start location".format(x, y))
                self.home = (x, y)


            elif command == b"MAP":
                if self.debug_mode: print(self.name + ": MAP from server")
                n = self.get_n()
                positions = []
                for _ in range(n):
                    x, y, nb_hum, nb_vamp, nb_wv = self.get_quintuplet()
                    positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                if self.debug_mode: print(positions)

                self.map.update(positions)
                self.define_race()
                print(self.name + " is a " + ("vampire" if self.is_vamp else "werewolf"))

            elif command == b"UPD":
                if self.debug_mode: print(self.name + ": UPD from server")
                n = self.get_n()
                if n:
                    positions = []
                    for _ in range(n):
                        x, y, nb_hum, nb_vamp, nb_wv = self.get_quintuplet()
                        positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                    if self.debug_mode: print(positions)
                    self.map.update(positions)

                if self.debug_mode: print(self.name + ": UPD received")
                # On affiche la carte contre le serveur du projet
                self.send_MOV(self.next_moves(show_map=(not self.type_interne)))
                if self.debug_mode: print(self.name + ": MOV sent")

            elif command == b"END":
                if self.debug_mode: print(self.name + ": END from server")
                self.init_game()

            elif command == b"BYE":
                if self.debug_mode: print(self.name + ": BYE from server")
                break
            else:  # Command inconnue
                if self.debug_mode: print(self.name + ' Unknown command :' + str(command))

        if not self.type_interne: self.sock.close()

    # Méthodes de communication

    def get_command(self):
        commande = bytes()
        while len(commande) < 3:
            commande += self.sock.recv(3 - len(commande))
        return commande

    def get_n(self):
        return struct.unpack("b", self.sock.recv(1))[0]

    def get_couple(self):
        return struct.unpack("bb", self.sock.recv(2))

    def get_quintuplet(self):
        return struct.unpack("bbbbb", self.sock.recv(5))

    def send_NME(self):
        if self.debug_mode: print(self.name + ": Sending NME for " + self.name)
        paquet = bytes()
        t = len(self.name.encode('ascii'))
        paquet += "NME".encode('ascii')
        paquet += struct.pack("1b", t)
        paquet += self.name.encode('ascii')
        self.sock.send(paquet)

    def send_MOV(self, moves):
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
        map_content = {}
        for i, j in product(range(map_size[0]), range(map_size[1])):
            map_content[(i, j)] = (0, 0, 0)
        self.map = Map(map_size, map_content)

    def init_game(self):
        self.home = None
        self.map = None
        self.is_vamp = None

    def define_race(self):
        for i, j in self.map.content:
            if (i, j) == self.home:
                if self.map.content[(i, j)][1]:
                    self.is_vamp = True
                else:
                    self.is_vamp = False
                break

    def locate_humans(self, human_locations):
        pass

    def next_moves(self, show_map=True):
        """ Fonction pour faire bouger nos armées. Il y une probabilité aléatoire uniforme de se déplacer sur les cases
        adjascentes, et une probabilité aléatoire de casser le groupe en 2 s'il y a suffisamment de membres

        show_map permet d'afficher la carte comprise pour un joueur. Très utile pour les parties avec le serveur du
        projet"""

        end_position = []
        if self.is_vamp:
            members = [elt for elt in self.map.content if self.map.content[elt][1] != 0]
        else:
            members = [elt for elt in self.map.content if self.map.content[elt][2] != 0]
        if self.debug_mode: print(self.name + '/next_moves Map : ' + str(self.map.content))
        if show_map: self.map.print_map()
        # On prend une décision pour chaque case occupée par nos armées
        for elt in members:
            x_old, y_old = elt

            # Scission du groupe ou non
            if self.is_vamp:
                number = self.map.content[elt][1]
            else:
                number = self.map.content[elt][2]
            groupe_1 = random.randint(0, number)
            groupe_2 = number - groupe_1

            def new_position(x_old, y_old, x_max, y_max, end_position):
                available_positions = [(x_old + i, y_old + j) for i in (-1, 0, 1) \
                                       for j in (-1, 0, 1) \
                                       if (x_old + i, y_old + j) != (x_old, y_old) \
                                       and 0 <= (x_old + i) < x_max \
                                       and 0 <= (y_old + j) < y_max
                                       and (x_old + i, y_old + j) not in members  # Règle 5
                                       ]
                new_pos = random.choice(available_positions)

                # Respect de la règle 5 du tournoi
                if new_pos in [(i, j) for (i, j, _, _, _) in end_position]:
                    return new_position(x_old, y_old, x_max, y_max, end_position)
                else:
                    return new_pos

            if groupe_1:
                new_pos = new_position(x_old, y_old, self.map.size[0], self.map.size[1], end_position)
                end_position.append((x_old, y_old, groupe_1, new_pos[0], new_pos[1]))
            if groupe_2:
                new_pos = new_position(x_old, y_old, self.map.size[0], self.map.size[1], end_position)
                end_position.append((x_old, y_old, groupe_2, new_pos[0], new_pos[1]))

        return end_position


if __name__ == "__main__":
    Joueur_1 = JoueurClient()
    Joueur_2 = JoueurClient(name="Joueur 3")

    Joueur_1.start()
    Joueur_2.start()
