# -*- coding: utf-8 -*-
from copy import deepcopy
from time import time

from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Algorithmes.Sommet_du_jeu_Temporal_Difference_0 import  SommetOutcome_TemporalDifference, SommetChance_TemporalDifference
from Cartes.Map_Dust2 import MapDust2
from Cartes.Map_TheTrap import MapTheTrap
from Cartes.Map_Map8 import Map8


class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """


class AlgoTemporalDifference0(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """
    def next_moves(self, show_map=True):
        if show_map: self.map.print_map()
        racine = SommetOutcome_TemporalDifference(game_map=deepcopy(self.map), is_vamp=self.is_vamp)

        start_time = time()
        while time() < start_time + 2:
            racine.temporal_difference_0()

        if racine.is_vamp:
            return max(racine.children, key=lambda child: child.value).previous_moves
        else:
            return min(racine.children, key=lambda child: child.value).previous_moves


    @classmethod
    def nb_vertices_created(cls):
        return SommetOutcome_TemporalDifference.nb_vertices_created() + SommetChance_TemporalDifference.nb_vertices_created()


if __name__ == "__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoTemporalDifference0
    MapDust2 = MapDust2
    Serveur = ServeurInterne(MapDust2, Joueur1, Joueur2, name1="Aléatoire", name2="TD0", print_map=True,
                             debug_mode=False)
    Serveur.start()
    Serveur.join()
    print(AlgoTemporalDifference0.nb_vertices_created())
