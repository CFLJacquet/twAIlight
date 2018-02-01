from threading import Thread
import xml.etree.ElementTree as ET
import random
from queue import Queue
from itertools import combinations
from collections import defaultdict

from Joueur_Interne import JoueurInterne
from Map_Interne import MapInterne

PORT = 5555  # TODO à changer pour le tournoi
HOTE = "127.0.0.1"  # TODO à changer pour le tournoi


class ServeurInterne(Thread):
    def __init__(self, game_map, player_1_class, player_2_class, name1=None, name2=None, debug_mode=False):
        super().__init__()
        self.queue_server_p1 = Queue()
        self.queue_server_p2 = Queue()
        self.queue_p1_server = Queue()
        self.queue_p2_server = Queue()
        self.player_1 = player_1_class(self.queue_p1_server, self.queue_server_p1, name=name1, debug_mode=debug_mode)
        self.player_2 = player_2_class(self.queue_p2_server, self.queue_server_p2, name=name2, debug_mode=debug_mode)
        self.p1_winner = None
        self.map = game_map
        self.round_nb = 1  # Numéro du tour
        self.debug_mode = debug_mode

    def run(self):
        # Démarrage des Joueurs
        self.player_1.start()
        self.player_2.start()

        _ = self.queue_p1_server.get()
        _ = self.queue_p2_server.get()
        name_1 = self.queue_p1_server.get()
        name_2 = self.queue_p2_server.get()
        print("Server : Joueur 1 : " + str(name_1))
        print("Server : Joueur 2 : " + str(name_2))

        self.start_new_game()
        self.map.print_map()
        while True:
            moves = self.get_MOV(self.queue_p1_server)
            if self.debug_mode: print('Server : MOV received from ' + self.player_1.name)
            if not self.check_moves(moves, is_player_1=True):
                print("Server : {} a triché !".format(self.player_1.name))
                self.p1_winner = False
                self.send_both_players("END")
                self.send_both_players("BYE")
                print("Server :{} gagne !".format(self.player_2.name))
                break

            self.map.update(moves)

            self.map.print_map()
            if self.debug_mode: print('Server : Map updated')
            if self.map.game_over():
                self.send_both_players("END")
                if self.map.winner() is None:
                    self.start_new_game()
                    continue
                elif self.map.winner():
                    print("Server : {} gagne !".format(self.player_1.name))
                    self.p1_winner = True
                    self.send_both_players("BYE")
                else:
                    print("Server : {} gagne !".format(self.player_2.name))
                    self.p1_winner = False
                    self.send_both_players("BYE")

            if self.debug_mode: print("Server : sending UDP")

            self.send_UPD()

            self.round_nb += 1
            print("Server : Round " + str(self.round_nb))

            moves = self.get_MOV(self.queue_p2_server)

            if not self.check_moves(moves, is_player_1=False):
                print("Server : {} a triché !".format(self.player_2.name))
                self.p1_winner = True
                self.send_both_players("END")
                self.send_both_players("BYE")
                print("Server : {} gagne !".format(self.player_1.name))
                break

            self.map.update(moves)
            self.map.print_map()
            if self.map.game_over():
                self.send_both_players("END")
                if self.map.winner() is None:
                    self.start_new_game()
                    print('Server : Starting a new game')
                    continue
                elif self.map.winner():
                    print("Server : {} gagne !".format(self.player_1.name))
                    self.p1_winner = True
                    self.send_both_players("BYE")
                else:
                    print("Server : {} gagne !".format(self.player_2.name))
                    self.p1_winner = False
                    self.send_both_players("BYE")

            self.send_UPD()

    def check_moves(self, moves, is_player_1):
        moves_checked = []
        if len(moves) == 0:
            return False
        for i, j, n, x, y in moves:
            if abs(i - x) > 1 or abs(j - y) > 1:
                return False
            n_initial = self.map.map_content[(i, j)][1 if is_player_1 else 2]
            n_checked = sum([n_c for (i_c, j_c, n_c, _, _) in moves_checked if (i_c, j_c) == (i, j)])
            if n_initial < n_checked + n:
                return False
            moves_checked.append((i, j, n, x, y))
        # Règle 5
        for move_1, move_2 in combinations(moves, 2):
            if (move_1[0], move_1[1]) == (move_2[3], move_2[4]):
                return False
            if (move_1[3], move_1[4]) == (move_2[0], move_2[1]):
                return False
        return True

    def get_MOV(self, queue):
        command = queue.get()  # MOV command
        if self.debug_mode: print("Server/MOV : " + str(command))
        n_move = queue.get()
        if self.debug_mode: print("Server/MOV : " + str(n_move))
        moves = []
        for _ in range(n_move):
            moves.append(queue.get())

        if self.debug_mode: print("Server/MOV : " + str(moves))
        return moves

    def send_both_players(self, message):
        self.queue_server_p1.put(message)
        self.queue_server_p2.put(message)

    def send_UPD(self):
        updates = self.map.UDP
        n = len(updates)
        self.send_both_players("UPD")
        self.send_both_players(n)
        for update in updates:
            self.send_both_players(update)

    def start_new_game(self):
        self.round_nb = 1
        print("Server : Round " + str(self.round_nb))
        self.send_both_players("SET")
        self.send_both_players(self.map.map_size)
        # pas de HUM

        self.send_both_players("MAP")
        n, elements = self.map.MAP_command()

        self.send_both_players(n)
        for quintuplet in elements:
            self.send_both_players(quintuplet)

        self.queue_server_p1.put("HME")
        self.queue_server_p1.put(self.map.home_1)
        self.queue_server_p2.put("HME")
        self.queue_server_p2.put(self.map.home_2)

        # Let's start the game
        self.queue_server_p1.put("UPD")
        self.queue_server_p1.put(0)
        self.queue_server_p1.put([])

        if self.debug_mode: print("Server : New Game settings sent !")










if __name__ == "__main__":
    serveur = ServeurInterne(MapInterne(), JoueurInterne, JoueurInterne, name2="Player2")
    serveur.debug_mode=False
    serveur.start()
