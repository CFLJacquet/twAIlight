# -*- coding: utf-8 -*-
import threading
import random
from time import sleep, time
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
from queue import Queue
from copy import deepcopy, copy

from twAIlight.Joueur import Joueur
from twAIlight.Joueur_Interne import JoueurInterne
from twAIlight.Serveur_Interne import ServeurInterne
from twAIlight.Algorithmes.Sommet_du_jeu_NegaMax_MPO_2 import SommetDuJeu_NegaMax_MPOO
from twAIlight.Cartes.Map_Map8 import Map8
from twAIlight.Cartes.Map_Ligne13 import MapLigne13


class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """
    def next_moves(self, show_map=True):
        if self.debug_mode: print(self.name + '/next_moves Map : ' + str(self.map.content))
        if show_map: self.map.print_map()

        return next(self.map.i_next_relevant_moves_2(self.is_vamp, nb_group_max=None, stay_enabled=False))

class AlgoNaive(JoueurInterne):

    #def create_map(self, map_size):
    #    """ Crée une carte à la taille map_size et l'enregistre dans l'attribut map
    #
    #    :param map_size: (n,m) dimension de la carte
    #    :return: None
    #    """
    #    self.map = Map(map_size=map_size) # Map_Silv

    def next_moves(self, show_map=True):
        next_move =  next(self.map.i_next_relevant_moves_3(
            self.is_vamp))
        print("Naive: ", next_move)
        return next_move



def worker(depth_max, game_map, is_vamp):
    racine = SommetDuJeu_NegaMax_MPOO(
        depth=depth_max,
        game_map=game_map,
        is_vamp=is_vamp,
        init_map=True)

    return racine.next_move()

def abortable_worker(func, *args, **kwargs):
    timeout = kwargs.get('timeout', None)
    p = ThreadPool(1)
    res = p.apply_async(func, args=args)
    try:
        out = res.get(timeout)  # Wait timeout seconds for func to complete.
        return out
    except multiprocessing.TimeoutError:
        print("Aborting due to timeout")
        p.terminate()
        raise

class AlgoNegMax_MPOO(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """

    def next_moves(self, show_map=True):

        if show_map: self.map.print_map()
        
        pool = multiprocessing.Pool()
        depths = [2,4,6,8] #list of arguments
        next_moves = []
        for depth in depths:
            abortable_func = partial(abortable_worker, worker, timeout=5.0)
            args = depth, deepcopy(self.map), self.is_vamp
            pool.apply_async(abortable_func, args=args, callback=next_moves.append)
        pool.close()
        pool.join()

        print(next_moves)
        next_move = next_moves[-1]

        print("MPOO:", next_move)
        return next_move


    @classmethod
    def nb_vertices_created(cls):
        return SommetDuJeu_NegaMax_MPOO.nb_vertices_created()


if __name__ == "__main__":
    Joueur2 = AlgoNegMax_MPOO
    Joueur1 = AlgoAleatoireInterne
    carte= MapLigne13
    Serveur = ServeurInterne(carte, Joueur1, Joueur2, name1="Joueur1", name2="Joueur2", print_map=True, debug_mode=False)
    Serveur.start()


    """ Joueur_1=AlgoNegMax_MPOO()
    Joueur_1.start()
    Joueur_1.join() """
