# -*- coding: utf-8 -*-
from copy import deepcopy
from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Algorithmes.Sommet_du_jeu import SommetDuJeu
from Cartes.Map_Dust2 import MapDust2

class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """

class AlgoMinMaxH2(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """
    def next_moves(self,show_map=True):
        depth_max=5
        if show_map: self.map.print_map()
        racine = SommetDuJeu(depth=depth_max, game_map=deepcopy(self.map), is_vamp=self.is_vamp)
        return racine.next_move()

if __name__=="__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoMinMaxH2
    MapDust2 = MapDust2
    Serveur=ServeurInterne(MapDust2,Joueur1,Joueur2,name1="ALEA",name2="MINIMAX")
    Serveur.start()
