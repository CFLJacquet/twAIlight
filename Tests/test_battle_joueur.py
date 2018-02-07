from Joueur import Joueur

import time

class JoueurTestBattle(Joueur):
    # à faire tourner sur le serveur du projet, configurer avec un joueur sur testmap.xml
    def __init__(self):
        super().__init__()

    def next_moves(self, show_map=True):

        time.sleep(1)
        if self.round_played==0:
            return [(5,4,3,4,4)]

        elif self.round_played==1:
            return [(4,4,3,3,3)]

        elif self.round_played ==2:
            return [(3,3,1,3,4),(3,3,1,3,2)]

        elif self.round_played==3:
            return[(3,3,1,2,3),(3,4,1,2,3),(3,2,1,2,3)]

if __name__=="__main__":
    joueur_beta=JoueurTestBattle()
    joueur_beta.start()
