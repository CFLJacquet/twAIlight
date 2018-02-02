from threading import Thread
import xml.etree.ElementTree as ET
import random
from queue import Queue
from itertools import combinations
from collections import defaultdict

from Joueur_Interne import JoueurInterne
from Map import Map

PORT = 5555  # TODO à changer pour le tournoi
HOTE = "127.0.0.1"  # TODO à changer pour le tournoi


class ServeurInterne(Thread):
    def __init__(self, game_map, player_1_class, player_2_class, name1=None, name2=None, debug_mode=False,
                 print_map=True):
        super().__init__()
        self.queue_server_p1 = Queue()  # Queue de communication serveur vers joueur 1
        self.queue_server_p2 = Queue()  # Queue de communication serveur vers joueur 2
        self.queue_p1_server = Queue()  # Queue de communication joueur 1 vers serveur
        self.queue_p2_server = Queue()  # Queue de communication joueur 2 vers serveur
        self.player_1 = player_1_class(self.queue_p1_server, self.queue_server_p1, name=name1, debug_mode=debug_mode)
        self.player_2 = player_2_class(self.queue_p2_server, self.queue_server_p2, name=name2, debug_mode=debug_mode)
        self.updates_for_1 = []  # liste des changements pour mettre à jour la carte du joueur 1
        self.updates_for_2 = []  # liste des changements pour mettre à jour la carte du joueur 2

        self.map = game_map  # carte du jeu

        self.debug_mode = debug_mode  # Pour afficher tous les logs
        self.print_map = print_map  # Pour afficher ou non la carte au cours de la partie
        self.winner = None  # True si c'est le joueur 1 / vampire, False sinon
        self.round_nb = 0  # Numéro du tour

    def run(self):
        # Démarrage des Joueurs
        self.player_1.start()
        self.player_2.start()

        # Réception des noms des joueurs
        _ = self.queue_p1_server.get()
        _ = self.queue_p2_server.get()
        name_1 = self.queue_p1_server.get()
        name_2 = self.queue_p2_server.get()
        print("Server : Joueur 1 : " + str(name_1))
        print("Server : Joueur 2 : " + str(name_2))

        # Initialisation du jeu
        self.start_new_game()

        # Affichage de la carte
        if self.print_map: self.map.print_map()
        while True:
            moves = self.get_MOV(self.queue_p1_server)
            if self.debug_mode: print('Server : MOV received from ' + self.player_1.name)
            if not self.check_moves(moves, is_player_1=True):
                print("Server : {} a triché !".format(self.player_1.name))
                self.winner = False
                self.send_both_players(b"END")
                self.send_both_players(b"BYE")
                print("Server : {} gagne !".format(self.player_2.name))
                break

            self.map.update_and_compute(moves)
            self.round_nb += 1
            print("Server : Round " + str(self.round_nb) + " : "
                  + ("Vampires" if self.round_nb % 2 else "WereWolves") + " playing")
            if self.print_map: self.map.print_map()
            if self.debug_mode: print('Server : Map updated')

            if self.map.game_over():
                self.send_both_players(b"END")
                if self.map.winner() is None:
                    self.start_new_game()
                    continue
                elif self.map.winner():
                    print("Server : {} gagne !".format(self.player_1.name))
                    self.winner = True
                    self.send_both_players(b"BYE")
                    break
                else:
                    print("Server : {} gagne !".format(self.player_2.name))
                    self.winner = False
                    self.send_both_players(b"BYE")
                    break

            if self.debug_mode: print("Server : sending UDP")

            self.send_UPD(to_player_1=False)

            moves = self.get_MOV(self.queue_p2_server)

            if not self.check_moves(moves, is_player_1=False):
                print("Server : {} a triché !".format(self.player_2.name))
                self.winner = True
                self.send_both_players(b"END")
                self.send_both_players(b"BYE")
                print("Server : {} gagne !".format(self.player_1.name))
                break

            self.round_nb += 1
            print("Server : Round " + str(self.round_nb) + " : "
                  + ("Vampires" if self.round_nb % 2 else "WereWolves") + " playing")

            self.map.update_and_compute(moves)
            if self.print_map: self.map.print_map()
            if self.map.game_over():
                self.send_both_players(b"END")
                if self.map.winner() is None:
                    self.start_new_game()
                    print('Server : Starting a new game')
                    continue
                elif self.map.winner():
                    print("Server : {} gagne !".format(self.player_1.name))
                    self.winner = True
                    self.send_both_players(b"BYE")
                    break
                else:
                    print("Server : {} gagne !".format(self.player_2.name))
                    self.winner = False
                    self.send_both_players(b"BYE")
                    break

            self.send_UPD(to_player_1=True)

    def check_moves(self, moves, is_player_1):
        moves_checked = []
        if len(moves) == 0:  # Règle 1
            return False
        if all(n == 0 for _, _, n, _, _ in moves):  # Règle 6
            return False
        for i, j, n, x, y in moves:
            if abs(i - x) > 1 or abs(j - y) > 1:  # Règle 4
                return False
            n_initial = self.map.content[(i, j)][1 if is_player_1 else 2]
            n_checked = sum([n_c for (i_c, j_c, n_c, _, _) in moves_checked if (i_c, j_c) == (i, j)])
            if n_initial < n_checked + n:  # Règle 3
                return False
            moves_checked.append((i, j, n, x, y))
            if n_initial == 0:  # Règle 3 et 2
                return False

        for move_1, move_2 in combinations(moves, 2):  # Règle 5
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

    def send_UPD(self, to_player_1):
        updates = self.map.UPD
        self.updates_for_1 += updates
        self.updates_for_2 += updates
        if to_player_1:
            n = len(self.updates_for_1)
            self.queue_server_p1.put(b"UPD")
            self.queue_server_p1.put(n)
            for update in self.updates_for_1:
                self.queue_server_p1.put(update)
            self.updates_for_1 = []
        else:
            n = len(self.updates_for_2)
            self.queue_server_p2.put(b"UPD")
            self.queue_server_p2.put(n)
            for update in self.updates_for_2:
                self.queue_server_p2.put(update)
            self.updates_for_2 = []

    def start_new_game(self):
        self.round_nb = 1
        self.updates_for_1, self.updates_for_2 = [], []
        print("Server : Round " + str(self.round_nb) + " : " + (
            "Vampires" if self.round_nb % 2 else "WereWolves") + " playing")
        self.send_both_players(b"SET")
        self.send_both_players(self.map.size[::-1])  # Pour imiter le serveur du projet

        # pas de HUM

        self.queue_server_p1.put(b"HME")
        self.queue_server_p1.put(self.map.home_vampire())
        self.queue_server_p2.put(b"HME")
        self.queue_server_p2.put(self.map.home_werewolf())

        self.send_both_players(b"MAP")
        n, elements = self.map.MAP_command()

        self.send_both_players(n)
        for quintuplet in elements:
            self.send_both_players(quintuplet)

        # Let's start the game
        self.queue_server_p1.put(b"UPD")
        self.queue_server_p1.put(0)

        if self.debug_mode: print("Server : New Game settings sent !")


if __name__ == "__main__":
    serveur = ServeurInterne(Map(debug_mode=True), JoueurInterne, JoueurInterne, name2="Player2")
    serveur.debug_mode = False
    serveur.print_map = False
    serveur.start()
    serveur.join()
    print(serveur.winner)
