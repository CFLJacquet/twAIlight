# -*- coding: utf-8 -*-
from copy import deepcopy
from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Algorithmes.Sommet_du_jeu_NegaMax_Transposition import SommetDuJeu_NegaMax
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
        depth_max = 3
        if show_map: self.map.print_map()
        racine = SommetDuJeu_NegaMax(depth=depth_max, game_map=deepcopy(self.map), is_vamp=self.is_vamp, init_map=True)
        return racine.next_move()

    @classmethod
    def nb_vertices_created(cls):
        return SommetDuJeu_NegaMax.nb_vertices_created()

if __name__ == "__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoNegaMax
    MapDust2 = MapDust2
    Serveur = ServeurInterne(MapDust2, Joueur1, Joueur2, name1="ALEA", name2="MINIMAX", print_map=True, debug_mode=False)
    Serveur.start()
    Serveur.join()
    print(AlgoNegaMax.nb_vertices_created())