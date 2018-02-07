from Joueur import Joueur


class JoueurInterne(Joueur):
    """
    Classe héritée de Joueur, ce joueur peut communiquer avec le serveur interne.
    """

    def __init__(self, q_p_s, q_s_p, name=None, debug_mode=False):
        """ On reprend l'initialisation de Joueur, en y ajoutant nos deux queues de communication
        avec le serveur interne.

        :param q_p_s: queue de communication du joueur au serveur (Player --> Server)
        :param q_s_p: queue de communication du serveur au joueur (Server --> Player)
        :param name: nom du joueur
        :param debug_mode: mode debug (boolean)
        """
        super().__init__(name=name, debug_mode=debug_mode, joueur_interne=True)
        self.queue_player_server = q_p_s  # queue de communication du joueur au serveur
        self.queue_server_player = q_s_p  # queue de communication du serveur au joueur

    # Méthodes de communication
    # On surchage les méthodes de communication (et qu'elles !)

    def get_command(self):
        """Récupère la commande envoyée par le serveur depuis la queue de communication
        :return: command (bytes)
        """
        command = self.queue_server_player.get()
        # On s'assure d'avoir une vraie commande
        while command not in [b"MAP", b"SET", b"HUM", b"HME", b"UPD", b"END", b"BYE"]:
            command = self.queue_server_player.get()
        return command

    def get_n(self):
        """ Renvoie un entier envoyé par le serveur

        :return:  int
        """
        return self.queue_server_player.get()

    def get_couple(self):
        """ Renvoie un couple (coordonnées) envoyée par le serveur

        :return: (x,y) tuple
        """
        return self.queue_server_player.get()

    def get_quintuplet(self):
        """Renvoie un quintuplets d'entiers envoyée par le serveur

        :return: (a,b,c,d,e)
        """
        return self.queue_server_player.get()

    def send_NME(self):
        """ Envoie le nom du joueur au serveur

        :return: None
        """
        # Envoi de la command
        self.queue_player_server.put("NME")
        # Envoi du nom du joueur
        self.queue_player_server.put(self.name)

    def send_MOV(self, moves):
        """ Envoi au serveur la liste de mouvements proposés par le joueur

        :param moves: liste des mouvements
        :return:
        """
        # Envoi de la commande de la trame
        self.queue_player_server.put("MOV")
        # Envoi du nombre de mouvements
        self.queue_player_server.put(len(moves))
        # Envoi de chaque mouvement
        for move in moves:
            self.queue_player_server.put(move)


if __name__ == "__main__":
    pass
