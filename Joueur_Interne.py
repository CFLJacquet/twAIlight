from Client_Joueur import JoueurClient


class JoueurInterne(JoueurClient):
    def __init__(self, q_p_s, q_s_p, name=None, debug_mode=False):
        super().__init__(name=name, debug_mode=debug_mode)
        self.queue_player_server = q_p_s
        self.queue_server_player = q_s_p

    def run(self):
        if self.debug_mode: print(self.name + " has joined the game.")
        self.send_NME()
        while True:
            command = self.getcommand()

            if command == "SET":
                n, m = self.queue_server_player.get()
                self.create_map((n, m)) # Pas la peine d'intervertir ici
                if self.debug_mode: print(self.name + ": SET received")

            elif command == "HUM":
                human_location = []
                n = self.queue_server_player.get()
                for _ in range(n):
                    human_location.append(self.queue_server_player.get())
                self.locate_humans(human_location)
                if self.debug_mode: print(self.name + ": HUM received")

            elif command == "HME":
                x, y = self.queue_server_player.get()
                self.home = (x, y)
                self.define_race()
                if self.debug_mode: print(self.name + ": HME received")
                print(self.name + " is a " + ("vampire" if self.is_vamp else "werewolf"))

            elif command == "MAP":
                n = self.queue_server_player.get()
                positions = []
                for _ in range(n):
                    x, y, nb_hum, nb_vamp, nb_wv = self.queue_server_player.get()
                    positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                self.update_map(list(positions))
                self.define_race()
                if self.debug_mode: print(self.name + ": MAP received")

            elif command == "UPD":
                if self.debug_mode: print(self.name + ": UPD detected")
                n = self.queue_server_player.get()
                if n:
                    positions = []
                    for _ in range(n):
                        x, y, nb_hum, nb_vamp, nb_wv = self.queue_server_player.get()
                        positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                    if self.debug_mode: print(positions)
                    self.update_map(positions)
                if self.debug_mode: print(self.name + ": UPD received")
                self.send_MOV(self.next_moves(show_map=False))
                if self.debug_mode: print(self.name + ": MOV sent")

            elif command == "END":
                self.init_game()
                if self.debug_mode: print(self.name + ": END received")

            elif command == "BYE":
                if self.debug_mode: print(self.name + ": BYE received")
                break
            else:  # Commande inconnue
                if self.debug_mode: print(self.name + ' Unknown command :' + str(command))
                command = self.getcommand()

    def getcommand(self):
        command = self.queue_server_player.get(True)
        return command

    def send_NME(self):
        self.queue_player_server.put("NME")
        self.queue_player_server.put(self.name)

    def send_MOV(self, moves):
        self.queue_player_server.put("MOV")
        self.queue_player_server.put(len(moves))
        for move in moves:
            self.queue_player_server.put(move)


if __name__=="__main__":
    pass