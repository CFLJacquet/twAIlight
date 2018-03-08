from collections import defaultdict
import random
from itertools import combinations, product
from copy import deepcopy
from math import log2, pow, floor

import numpy as np
from scipy import signal

from twAIlight.Map import Map


class NumpyMap(Map):
    """
    Carte du jeu amélioré avec numpy : 
    Par défaut : Dust_2
    _______________
    |    |    |    |
    _______________
    | 2V | 1H | 2W |
    _______________
    |    |    |    |
    _______________
    self.content est un numpy array de taille (largeur, hauteur, 3)
     - self.content[:,:,0] est la carte/matrice des humains
    _______________
    |  0 |  0 |  0 |
    _______________
    |  0 |  1 |  0 |
    _______________
    |  0 |  0 |  0 |
    _______________
     - self.content[:,:,1] est la carte/matrice des vampires
     - self.content[:,:,2] est la carte/matrice des loup-garou
    """
    
    @classmethod
    def init_map_class(cls, map_size, initial_positions):
        """Crée la table de hashage des mouvements possibles, et renseigne les attributs de populations maximales de la
        classe.

        Méthode de hashage d'un élément de la carte en s'inspirant du hashage de Zobrist.
        https://en.wikipedia.org/wiki/Zobrist_hashing

        :param map_size: taille de la carte (x_max, y_max)
        :param initial_positions: contenu de la carte (np.array)
        :return: None
        """
        # On cherche à connaitre nos constantes sur les effectifs des espèces en présence
        x_max, y_max = map_size

        # Somme des populations d'humains sur la carte
        sum_human_pop = initial_positions.take([2], axis=1).sum()
        # Population maximale d'une espèce de monstre 
        n_monster_max = initial_positions.take([3,4], axis=1).max()

        cls.__N_MONSTER_MAX = n_monster_max + sum_human_pop

        # On calcule le nombre de cartes différentes possibles

        # avec 2 types de joueurs différents avec (n_monster_max+sum_human_pop) effectifs sur cette case
        # le max est pour le cas de l'initialisation d'un joueur (sa carte est au départ vide)
        N_possible_boxes = max(1, (2 * n_monster_max + 2 * sum_human_pop - 1) * x_max * y_max + sum_human_pop)

        # Nombre de bit sur lequel coder au minimum les positions
        n_bit = floor(log2(N_possible_boxes))
        # Marge sur la taille du bit de codage pour éviter les collisions
        m_bit = 10
        # Hash maximal
        nombre_max_hashage = pow(2, n_bit + m_bit)

        # Création de la table de hashage
        table = defaultdict(lambda: random.randint(0, nombre_max_hashage))

        # Le hash d'une case vide est nul
        for i, j in product(range(x_max), range(y_max)):
            table[(i, j, 0, 0, 0)] = 0

        cls.__HASH_TABLE = table

    @classmethod
    def hash_position(cls, position):
        return super().hash_position(tuple(position))

    def __init__(self, map_size=None, initial_positions=list(), debug_mode=False):
        """
        Initialise la carte
        :param map_size: dimensions de la carte
        :param initial_positions: (np.array)    [[x1, y1, h1, v1, w1]
                                                 [x2, y2, h2, v2, w2]]
        :param debug_mode: mode debug (boolean)
        """
        # Par Défaut Carte The Trap
        if map_size is None:
            self.size = (3, 3)
        else:
            self.size = map_size
        self._content = np.zeros((self.size[0], self.size[1], 3), dtype='uint16')
        self._populations = np.zeros(3, dtype='uint16') # 0 Humains, 0 Vampires, 0 Werewolves
        self._hash = 0

        if initial_positions == [] and map_size is None:
            initial_positions = np.array([[0, 1, 0, 2, 0], [1, 1, 1, 0, 0], [2, 1, 0, 0, 2]], dtype='intp')  # 2 vampire, 1 humain, 2 loup-garou

        # On crée la table de hashage des mouvements et d'autres paramètres sur les effectifs de la carte
        Map.init_map_class(self.size, initial_positions)

        # On ajoute les cases non vides avec update pour bien hasher notre carte
        self.update_content(initial_positions)

        self.UPD = []  # Liste des changements lors d'un update de la carte
        self.debug_mode = debug_mode

    def update_content(self, positions):
        """
        Mise à jour simple de la carte
        :param positions: (np.array)    [[x1, y1, h1, v1, w1]
                                         [x2, y2, h2, v2, w2]]
        :return: None
        """
        # Si on transpose positions => [[x1, x2]
        #                               [y1, y2]
        #                               [h1, h2]
        #                               [v1, v2]
        #                               [w1, w2]]
        pos_row = positions.T[0] # np.array([x1, x2])
        pos_col = positions.T[1] # np.array([y1, y2])

        # On récupère l'ancien contenu [o_hi, o_vi, o_wi] de la case xi, yi
        # old_content = [[o_h1, o_v1, o_w1]
        #                [o_h2, o_v2, o_w2]]
        old_content = self.content[pos_row, pos_col]

        # On ajoute les positions xi, yi
        # old_content_w_pos = [[x1, y1, o_h1, o_v1, o_w1]
        #                      [x2, y2, o_h2, o_v2, o_w2]]
        old_content_w_pos = np.hstack((pos_row[:, np.newaxis], pos_col[:, np.newaxis], old_content))        

        # On applique le hash à chaque [xi, yi, o_hi, o_vi, o_wi]
        np.apply_along_axis(self.hash_position, 1, old_content_w_pos)


        # On récupère le nouveau contenu [n_hi, n_vi, n_wi] de la case xi, yi
        # new_content = [[n_h1, n_v1, n_w1]
        #                [n_h2, n_v2, n_w2]]
        new_content = positions.take([2,3,4], axis=1) # eq. positions[:, 2:]

        # On met à jour la carte
        self.content[pos_row, pos_col] = new_content

        # On met à jour la population
        self._populations = np.sum(new_content-old_content, axis=0)

        # On ajoute les positions xi, yi
        # new_content_w_pos = [[x1, y1, n_h1, n_v1, n_w1]
        #                      [x2, y2, n_h2, n_v2, n_w2]]
        new_content_w_pos = np.hstack((pos_row[:, np.newaxis], pos_col[:, np.newaxis], new_content))        

        # On applique le hash à chaque [xi, yi, n_hi, n_vi, n_wi]
        np.apply_along_axis(self.hash_position, 1, new_content_w_pos)
    


    def print_map(self):
        """ Affiche la carte et des scores
        :return: None
        """
        def print_cell(t):
            RACE = ("H", "V", "W")
            cell_text = "| "
            for i in range(3):
                cell_text += bool(t[i]) * "{}{}".format(t[i], RACE[i])
            if len(cell_text) == 2:
                cell_text += "   "
            else:
                cell_text += " "
            print(cell_text, end='')
        
        def print_row(t):
            print("_" * (self.size[0] * 5))
            np.apply_along_axis(print_cell, 1, t)
            print("|")


        # Carte
        for col in self.content.swapaxes(0,1):
            print_row(col)
        print("_" * (self.size[0] * 5))

        # Score
        n_hum, n_vamp, n_lg = tuple(self.populations)
        print(
            "Vampires {} | Werewolves {} | Remaining Humans: {}".format(
                n_vamp, n_lg, n_hum))

if __name__ == "__main__":
    carte = NumpyMap()
    carte.print_map()
    #carte.update_content(np.array([[0,0,5,0,0]]))
    #print(carte.content)
    #import pdb; pdb.set_trace()