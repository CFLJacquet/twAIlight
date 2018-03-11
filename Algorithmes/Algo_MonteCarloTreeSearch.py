# -*- coding: utf-8 -*-
from copy import deepcopy
from time import time

from twAIlight.Joueur_Interne import JoueurInterne
from twAIlight.Serveur_Interne import ServeurInterne
from twAIlight.Algorithmes.Sommet_du_jeu_MonteCarlo import SommetOutcome_MonteCarlo, SommetChance_MonteCarlo
from twAIlight.Cartes.Map_Dust2 import MapDust2
from twAIlight.Cartes.Map_TheTrap import MapTheTrap
from twAIlight.Cartes.Map_Map8 import Map8
from twAIlight.Cartes.Map_Random import MapRandom


class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """


class AlgoMonteCarlo(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """
    
    def next_moves(self, show_map=True):
        if show_map: self.map.print_map()

        racine = SommetOutcome_MonteCarlo(game_map=deepcopy(self.map), is_vamp=self.is_vamp)

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
        return SommetOutcome_MonteCarlo.nb_vertices_created() + SommetChance_MonteCarlo.nb_vertices_created()


if __name__ == "__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoMonteCarlo
    Carte = MapRandom
    Serveur = ServeurInterne(Carte, Joueur1, Joueur2, name1="Aléatoire", name2="MonteCarlo", print_map=True,
                             debug_mode=False)
    Serveur.start()
    Serveur.join()
    print(AlgoMonteCarlo.nb_vertices_created())
