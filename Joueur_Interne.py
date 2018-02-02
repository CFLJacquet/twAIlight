from Client_Joueur import JoueurClient


class JoueurInterne(JoueurClient):
    def __init__(self, q_p_s, q_s_p, name=None, debug_mode=False):
        super().__init__(name=name, debug_mode=debug_mode, joueur_interne=True)
        self.queue_player_server = q_p_s  # queue de communication du joueur au serveur
        self.queue_server_player = q_s_p  # queue de communication du serveur au joueur

    # Méthodes de communication

    def get_command(self):
        command = self.queue_server_player.get()
        while command not in [b"MAP", b"SET", b"HUM", b"HME", b"UPD", b"END", b"BYE"]:
            command = self.queue_server_player.get()
        return command

    def get_n(self):
        return self.queue_server_player.get()

    def get_couple(self):
        return self.queue_server_player.get()

    def get_quintuplet(self):
        return self.queue_server_player.get()

    def send_NME(self):
        self.queue_player_server.put("NME")
        self.queue_player_server.put(self.name)

    def send_MOV(self, moves):
        self.queue_player_server.put("MOV")
        self.queue_player_server.put(len(moves))
        for move in moves:
            self.queue_player_server.put(move)


if __name__ == "__main__":
    pass
