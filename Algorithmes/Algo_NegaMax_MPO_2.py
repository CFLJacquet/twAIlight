# -*- coding: utf-8 -*-
import threading
import random
from time import sleep, time
from queue import Queue
from copy import deepcopy, copy

from twAIlight.Joueur import Joueur
from twAIlight.Joueur_Interne import JoueurInterne
from twAIlight.Serveur_Interne import ServeurInterne
from twAIlight.Algorithmes.Sommet_du_jeu_NegaMax_MPO_2 import SommetDuJeu_NegaMax_MPOO
from twAIlight.Cartes.Map_Map8 import Map8
from twAIlight.Cartes.Map_Ligne13 import MapLigne13

#from twAIlight.Map_Silv import Map


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
        next_move =  next(self.map.i_next_relevant_moves_2(
            self.is_vamp,
            stay_enabled=False,
            nb_group_max=4,
            nb_cases=8))
        print("Naive: ", next_move)
        return next_move


class TreeParseThread(threading.Thread):
    
    def __init__(self, q_m_s, q_s_m, params):
        threading.Thread.__init__(self)
        self.q_m_s = q_m_s  # queue aller
        self.q_s_m = q_s_m  # queue retour
        self.params = params
        self._stop_event = threading.Event()

    def run(self):
        racine = SommetDuJeu_NegaMax_MPOO(
            depth=self.params['depth_max'],
            game_map=self.params['map'],
            is_vamp=self.params['is_vamp'],
            init_map=True)

        racine.init_queues(self.q_m_s, self.q_s_m)
        racine.next_move()

class AlgoNegMax_MPOO(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne

    """

    def parse_tree(self):
        params = {}
        params['depth_max']    = self.depth_max
        params['map']          = self.map
        params['is_vamp']      = self.is_vamp

        queue_master_slave = Queue()  # Queue aller
        queue_slave_master = Queue()  # Queue retour
        thread = TreeParseThread(queue_master_slave, queue_slave_master, params)
        thread.start()

        thread.join(timeout=self.timeout)

        if queue_slave_master.empty():
            queue_master_slave.put(0)
            print(f'TimeOut for depth: {self.depth_max}!')
            return None
        else:
            next_move = queue_slave_master.get_nowait()
        return next_move

    def next_moves(self, show_map=True):

        if show_map: self.map.print_map()
        
        next_move = next(self.map.i_next_relevant_moves_3(self.is_vamp))
        
        self.depth_max = 4
        self.timeout = 1.9
        
        start = time()
        new_next_move = self.parse_tree()
        if not new_next_move is None:
            next_move = new_next_move
        end = time()

        self.depth_max = 6 if end-start < self.timeout/4 else 5
        self.timeout -= (end-start)
        
        new_next_move = self.parse_tree()
        if not new_next_move is None:
            next_move = new_next_move

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
