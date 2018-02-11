# -*- coding: utf-8 -*-

from Joueur import Joueur
from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Map import Map
from Algorithmes.Sommet_du_jeu import SommetDuJeu
from itertools import product
from Cartes.Map_Dust2 import MapDust2

class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """

class AlgoMinMaxH2(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """
    def next_moves(self,show_map=False):
        horizon=3
        if show_map: self.map.print_map()
        sommet = SommetDuJeu(horizon=horizon,game_map=self.map,is_vamp=self.is_vamp)
        new_moves = [sommet.next_move()]
        return new_moves

if __name__=="__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoMinMaxH2
    MapDust2 = MapDust2
    Serveur=ServeurInterne(MapDust2,Joueur1,Joueur2,name1="ALEA",name2="MINIMAX")
    Serveur.start()
