# -*- coding: utf-8 -*-
from copy import deepcopy
from time import time

from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Algorithmes.Sommet_du_jeu_MCTS_MPOO import SommetMonteCarlo
from Map_Silv import Map
from Cartes.Map_Dust2 import MapDust2
from Cartes.Map_TheTrap import MapTheTrap
from Cartes.Map_Silv_Map8 import  Map8
from Cartes.Map_Silv_Ligne13 import MapLigne13


class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """


class AlgoMCTSMPOO(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """

    def create_map(self, map_size):
        """ Crée une carte à la taille map_size et l'enregistre dans l'attribut map

        :param map_size: (n,m) dimension de la carte
        :return: None
        """
        self.map = Map(map_size=map_size) # Map_Silv
    
    def next_moves(self, show_map=True):
        if show_map: self.map.print_map()

        racine = SommetMonteCarlo(game_map=deepcopy(self.map), is_vamp=self.is_vamp,
                                  depth=11,
                                  nb_group_max=2,
                                  stay_enabled=False,
                                  nb_cases=[None, 1, 1, 1, 1, 2, 1, 2, 2, 3, 2, 5]
                                  )


        start_time = time()
        while time() < start_time + 2:
            racine.MCTS()

        max_child = max(racine.children,
                        key=lambda child: child.n_wins / child.n_games if child.n_games != 0 else 0)
        robust_child = max(racine.children, key=lambda child: child.n_games)

        if max_child == robust_child:
            return max_child.previous_moves
        else:
            n_threshold = max_child.n_games / 4
            selected_children = filter(lambda child: child.n_games > n_threshold, racine.children)
            return max(selected_children,
                       key=lambda child: child.n_wins / child.n_games if child.n_games != 0 else 0).previous_moves

    @classmethod
    def nb_vertices_created(cls):
        return SommetMonteCarlo.nb_vertices_created()


if __name__ == "__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoMCTSMPOO
    Carte = MapLigne13
    Serveur = ServeurInterne(Carte, Joueur1, Joueur2, name1="Aléatoire", name2="MonteCarlo", print_map=True,
                             debug_mode=False)
    Serveur.start()
    Serveur.join()
    print(AlgoMCTSMPOO.nb_vertices_created())
