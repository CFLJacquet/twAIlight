import socket
import time
import struct

from threading import Thread

PORT = 5555  # TODO à changer pour le tournoi
HOTE = "127.0.0.1"  # TODO à changer pour le tournoi
NAME = "TwAIlight"


class JoueurClient(Thread):
    def __init__(self, name=NAME):
        Thread.__init__(self)
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOTE, PORT))

    def run(self):
        self.send_NME()

        while True:
            command = self.getcommand()

            if command == b"SET":
                print("SET from server")
                n, m = struct.unpack("bb", self.sock.recv(2))
                print("{} lines, {} columns".format(n, m))

            elif command == b"HUM":
                print("HUM from server")
                human_location = []
                n = struct.unpack("b", self.sock.recv(1))[0]
                for _ in range(n):
                    human_location.append(struct.unpack("bb", self.sock.recv(2)))
                print(human_location)
            elif command == b"HME":
                print("HME from server")
                x, y = struct.unpack("bb", self.sock.recv(2))
                print("({},{}) : start location".format(x, y))
            elif command == b"MAP":
                print("MAP from server")
                n = struct.unpack("b", self.sock.recv(1))[0]
                positions = []
                for _ in range(n):
                    x, y, nb_hum, nb_vamp, nb_wv = struct.unpack("bbbbb", self.sock.recv(5))
                    positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                print(positions)
            elif command == b"UPD":
                print("UPD from server")
                n = struct.unpack("b", self.sock.recv(1))[0]
                positions = []
                for _ in range(n):
                    x, y, nb_hum, nb_vamp, nb_wv = struct.unpack("bbbbb", self.sock.recv(5))
                    positions.append((x, y, nb_hum, nb_vamp, nb_wv))
                print(positions)
            elif command == b"END":
                print("END from server")
            elif command == b"BYE":
                print("BYE from server")
                break
        self.sock.close()

    def getcommand(self):
        commande = bytes()
        while len(commande) < 3:
            commande += self.sock.recv(3 - len(commande))
        return commande

    def send_NME(self):
        print("Sending NME for " + self.name)
        paquet = bytes()
        t = len(self.name.encode('ascii'))
        paquet += "NME".encode('ascii')
        paquet += struct.pack("1b", t)
        paquet += self.name.encode('ascii')
        self.sock.send(paquet)

    def send_MOV(self, moves):
        print("Sending MOV")
        n = len(moves)
        paquet = bytes()
        paquet += "MOV".encode("ascii")
        paquet += struct.pack("1b", n)
        for move in moves:
            paquet += struct.pack("bbbbb", *move)
        self.sock.send(paquet)


if __name__ == "__main__":
    Joueur_1 = JoueurClient()

    Joueur_1.start()
    time.sleep(1)
    moves = [(5, 4, 1, 5, 3),(5, 4, 2, 4, 4)]
    Joueur_1.send_MOV(moves)
    time.sleep(1)
    moves = [(4, 4, 3, 3, 4),(5,3,1,4,3)]
    Joueur_1.send_MOV(moves)
    time.sleep(1)
    moves = [(3, 4, 3, 3, 3), (4, 3, 1, 3, 3)]
    Joueur_1.send_MOV(moves)
    time.sleep(1)
    moves = [(3, 3, 4, 3, 2)]
    Joueur_1.send_MOV(moves)
    time.sleep(1)
    moves = [(3, 2, 4, 2, 2)]
    Joueur_1.send_MOV(moves)
    time.sleep(1)
    moves = [(2, 2, 4, 2, 3)]
    Joueur_1.send_MOV(moves)