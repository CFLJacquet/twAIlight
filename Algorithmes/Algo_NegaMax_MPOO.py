# -*- coding: utf-8 -*-
from copy import deepcopy, copy
from twAIlight.Joueur_Interne import JoueurInterne
from twAIlight.Serveur_Interne import ServeurInterne
from twAIlight.Algorithmes.Sommet_du_jeu_NegaMax_MPOO import SommetDuJeu_NegaMax_MPOO
from twAIlight.Cartes.Map_Silv_Map8 import Map8
from twAIlight.Map_Silv import Map


class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """


class AlgoNegMax_MPOO(JoueurInterne):
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
        stay_enabled = False

        if show_map: self.map.print_map()

        racine = SommetDuJeu_NegaMax_MPOO(
            depth=self.depth_max,
            nb_group_max=self.nb_group_max,
            stay_enabled=stay_enabled,
            nb_cases=self.nb_cases,
            game_map=copy(self.map),
            is_vamp=self.is_vamp,
            init_map=True)
        return racine.next_move()

    @classmethod
    def nb_vertices_created(cls):
        return SommetDuJeu_NegaMax_MPOO.nb_vertices_created()


if __name__ == "__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoNegMax_MPOO
    carte= Map8
    Serveur = ServeurInterne(carte, Joueur1, Joueur2, name1="ALEA", name2="NegaMax_MPO")
    Serveur.start()