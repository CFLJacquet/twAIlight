import socket
import struct
import sys
import random
from itertools import product
from threading import Thread

PORT = 5555  # TODO à changer pour le tournoi
HOTE = "127.0.0.1"  # TODO à changer pour le tournoi


class JoueurClient(Thread):
    __NAME = "TwAIlight"

    def __init__(self, name=None, debug_mode=False):
        Thread.__init__(self)
        if name is None:
            name=JoueurClient.__NAME
        self.name=name
        self.sock = None
        self.home = None
        self.map_content = None
        self.map_size = None
        self.is_vamp = None
        self.debug_mode=debug_mode

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOTE, PORT))
        self.send_NME()

        while True:
            command = self.getcommand()

            if command == b"SET":
                if self.debug_mode:print(self.name + ": SET from server")
                n, m = struct.unpack("bb", self.sock.recv(2))
                if self.debug_mode:print("{} lines, {} columns".format(n, m))
                self.create_map((m, n))  # on intervertit !

            elif command == b"HUM":
                if self.debug_mode:print(self.name + ": HUM from server")
                human_location = []
                n = struct.unpack("b", self.sock.recv(1))[0]
                for _ in range(n):
                    human_location.append(struct.unpack("bb", self.sock.recv(2)))
                self.locate_humans(human_location)
            elif command == b"HME":
                if self.debug_mode:print(self.name + ": HME from server")
                x, y = struct.unpack("bb", self.sock.recv(2))
                if self.debug_mode:print("({},{}) : start location".format(x, y))
                self.home = (x, y)
            elif command == b"MAP":
                if self.debug_mode:print(self.name + ": MAP from server")
                n = struct.unpack("b", self.sock.recv(1))[0]
                positions = []
                for _ in range(n):
                    x, y, nb_hum, nb_vamp, nb_wv = struct.unpack("bbbbb", self.sock.recv(5))
                    positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                    if self.debug_mode:print(positions)
                self.update_map(positions)
                self.define_race()
            elif command == b"UPD":
                if self.debug_mode:print(self.name + ": UPD from server")
                n = struct.unpack("b", self.sock.recv(1))[0]
                if n:
                    positions = []
                    for _ in range(n):
                        x, y, nb_hum, nb_vamp, nb_wv = struct.unpack("bbbbb", self.sock.recv(5))
                        positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                    if self.debug_mode:print(positions)
                    self.update_map(positions)

                self.send_MOV(self.next_moves())
            elif command == b"END":
                if self.debug_mode:print(self.name + ": END from server")
                self.init_game()

            elif command == b"BYE":
                if self.debug_mode:print(self.name + ": BYE from server")
                break
        self.sock.close()

    def getcommand(self):
        commande = bytes()
        while len(commande) < 3:
            commande += self.sock.recv(3 - len(commande))
        return commande

    def send_NME(self):
        if self.debug_mode:print(self.name + ": Sending NME for " + self.name)
        paquet = bytes()
        t = len(self.name.encode('ascii'))
        paquet += "NME".encode('ascii')
        paquet += struct.pack("1b", t)
        paquet += self.name.encode('ascii')
        self.sock.send(paquet)

    def send_MOV(self, moves):
        if self.debug_mode:print(self.name + " Sending MOV : " + str(moves))
        n = len(moves)
        paquet = bytes()
        paquet += "MOV".encode("ascii")
        paquet += struct.pack("1b", n)
        for move in moves:
            paquet += struct.pack("bbbbb", *move)
        self.sock.send(paquet)

    def create_map(self, size):
        self.map_size = size
        self.map_content = {}
        for i, j in product(range(size[0]), range(size[1])):
            self.map_content[(i, j)] = (0, 0, 0)

    def update_map(self, positions):
        for i, j, n_hum, n_vamp, n_lg in positions:
            self.map_content[(i, j)] = (n_hum, n_vamp, n_lg)

    def init_game(self):
        self.home = None
        self.map_content = None
        self.map_size = None
        self.is_vamp = None

    def define_race(self):
        for i, j in self.map_content:
            if (i, j) == self.home:
                if self.map_content[(i, j)][1]:
                    self.is_vamp = True
                else:
                    self.is_vamp = False
                break

    def locate_humans(self, human_locations):
        pass

    def next_moves(self, show_map=True):
        """ Fonction pour faire bouger nos armées. Il y une probabilité aléatoire uniforme de se déplacer sur les cases
        adjascentes, et une probabilité aléatoire de casser le groupe en 2 s'il y a suffisamment de membres """

        end_position = []
        if self.is_vamp:
            members = [elt for elt in self.map_content if self.map_content[elt][1] != 0]
        else:
            members = [elt for elt in self.map_content if self.map_content[elt][2] != 0]
        if self.debug_mode: print(self.name+'/next_moves Map : ' + str(self.map_content))
        if show_map: self.print_map()
        # On prend une décision pour chaque case occupée par nos armées
        for elt in members:
            x_old = elt[0]
            y_old = elt[1]

            # Scission du groupe ou non
            if self.is_vamp:
                number = self.map_content[elt][1]
            else:
                number = self.map_content[elt][2]

            groupe_1 = random.randint(0, number)
            groupe_2 = number - groupe_1

            def new_position(x_old, y_old, x_max, y_max, end_position):
                available_positions = [(x_old + i, y_old + j) for i in (-1, 0, 1) \
                                       for j in (-1, 0, 1) \
                                       if (x_old + i, y_old + j) != (x_old, y_old) \
                                       and 0 <= (x_old + i) < x_max \
                                       and 0 <= (y_old + j) < y_max
                                       and (x_old + i, y_old + j) not in members # Règle 5
                                       ]
                new_pos=random.choice(available_positions)

                # Respect de la règle 5 du tournoi
                if new_pos in [(i,j) for (i,j,_,_,_) in end_position]:
                    return new_position(x_old, y_old, x_max, y_max, end_position)
                else:
                    return new_pos

            if groupe_1:
                new_pos = new_position(x_old, y_old, self.map_size[0], self.map_size[1], end_position)
                end_position.append((x_old, y_old, groupe_1, new_pos[0], new_pos[1]))
            if groupe_2:
                new_pos = new_position(x_old, y_old, self.map_size[0], self.map_size[1], end_position)
                end_position.append((x_old, y_old, groupe_2, new_pos[0], new_pos[1]))

        return end_position

    def print_map(self):
        print('client_Joueur')
        for j in range(self.map_size[1]):
            # For each row
            print("_"*(self.map_size[0]*5))
            for i in range(self.map_size[0]):
                # For each cell
                print("| ", end='')
                cell_text = "   "
                if (i, j) in self.map_content:
                    race = ("H", "V", "W")
                    for r, k in enumerate(self.map_content[(i, j)]):
                        if k:
                            try:
                                cell_text = str(k)+race[r]+" "
                            except:
                                import pdb; pdb.set_trace()
                print(cell_text, end='')
            print("|")
        print("_"*(self.map_size[0]*5))

        # Score
        nb_vampires = sum(v for h,v,w in self.map_content.values())
        nb_humans = sum(h for h,v,w in self.map_content.values())
        nb_werewolves = sum(w for h,v,w in self.map_content.values())

        score_text = "Scores \t"
        score_text +="Vampire: "+str(nb_vampires)
        score_text += " | "
        score_text += str(nb_werewolves)+" Werewolves,"
        score_text += "\tHumans: "+ str(nb_humans)

        print(score_text)

if __name__ == "__main__":
    Joueur_1 = JoueurClient()
    Joueur_2 = JoueurClient(name="Joueur 3")

    Joueur_1.start()
    Joueur_2.start()
    """
    time.sleep(1)
    moves = [(5, 4, 1, 5, 3), (5, 4, 2, 4, 4)]
    Joueur_1.send_MOV(moves)

    time.sleep(1)
    moves = [(2, 3, 3, 2, 2)]
    Joueur_2.send_MOV(moves)

    time.sleep(1)
    moves = [(4, 4, 3, 3, 4), (5, 3, 1, 4, 3)]
    Joueur_1.send_MOV(moves)

    time.sleep(1)
    moves = [(2, 2, 4, 2, 3)]
    Joueur_2.send_MOV(moves)

    time.sleep(1)
    moves = [(3, 4, 3, 3, 3), (4, 3, 1, 3, 3)]
    Joueur_1.send_MOV(moves)

    time.sleep(1)
    moves = [(2, 3, 4, 2, 2)]
    Joueur_2.send_MOV(moves)

    time.sleep(1)
    moves = [(3, 3, 4, 3, 2)]
    Joueur_1.send_MOV(moves)

    time.sleep(1)
    moves = [(2, 2, 4, 3, 2)]
    Joueur_2.send_MOV(moves)"""
