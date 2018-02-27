# -*- coding: utf-8 -*-
from copy import deepcopy
from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Algorithmes.Sommet_du_jeu_NegaMax_Transposition import SommetDuJeu_NegaMax, SommetChance_Negamax
from Cartes.Map_Dust2 import MapDust2
from Cartes.Map_TheTrap import MapTheTrap


class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """


class AlgoNegaMax(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """

    def next_moves(self, show_map=True):
        depth_max = 2
        if show_map: self.map.print_map()
        racine = SommetDuJeu_NegaMax(depth=depth_max, game_map=deepcopy(self.map), is_vamp=self.is_vamp, init_map=True)
        return racine.next_move()

    @classmethod
    def nb_vertices_created(cls):
        return SommetDuJeu_NegaMax.nb_vertices_created() + SommetChance_Negamax.nb_vertices_created()

if __name__ == "__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoNegaMax
    MapDust2 = MapTheTrap
    Serveur = ServeurInterne(MapDust2, Joueur1, Joueur2, name1="ALEA", name2="Negamax", print_map=True, debug_mode=False)
    Serveur.start()
    Serveur.join()
    print(AlgoNegaMax.nb_vertices_created())
    """
    carte=MapDust2()
    carte.update_positions([(0,1,0,0,0),(1,2,0,2,0)])
    carte.print_map()
    racine=SommetDuJeu_NegaMax(is_vamp=False,depth=1,game_map=carte,init_map=True)
    print(racine.next_move())
    """