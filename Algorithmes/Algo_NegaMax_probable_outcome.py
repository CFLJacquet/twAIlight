# -*- coding: utf-8 -*-
from copy import deepcopy, copy
from twAIlight.Joueur_Interne import JoueurInterne
from twAIlight.Serveur_Interne import ServeurInterne
from twAIlight.Algorithmes.Sommet_du_jeu_NegaMax_probable_outcome import SommetDuJeu_NegaMax
from twAIlight.Cartes.Map_Dust2 import MapDust2
from twAIlight.Cartes.Map_Map8 import Map8
from twAIlight.Cartes.Map_TheTrap import MapTheTrap


class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """


class AlgoNegMax_MPO(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """

    def next_moves(self, show_map=True):
        depth_max = 5
        nb_group_max = 2
        stay_enabled = False
        if show_map: self.map.print_map()
        racine = SommetDuJeu_NegaMax(
            depth=depth_max,
            nb_group_max=nb_group_max,
            stay_enabled=stay_enabled,
            game_map=copy(self.map),
            is_vamp=self.is_vamp,
            init_map=True)
        return racine.next_move()

    @classmethod
    def nb_vertices_created(cls):
        return SommetDuJeu_NegaMax.nb_vertices_created()


if __name__ == "__main__":
    Joueur1 = AlgoAleatoireInterne
    Joueur2 = AlgoNegMax_MPO
    carte= Map8
    Serveur = ServeurInterne(carte, Joueur1, Joueur2, name1="ALEA", name2="NegaMax_MPO")
    Serveur.start()