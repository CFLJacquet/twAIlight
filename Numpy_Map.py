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
        self._content = np.zeros((self.size[0], self.size[1], 3), dtype='int64')
        self._populations = np.zeros(3, dtype='int64') # 0 Humains, 0 Vampires, 0 Werewolves
        self._hash = 0

        if initial_positions == [] and map_size is None:
            initial_positions = np.array([[0, 1, 0, 2, 0], [1, 1, 1, 0, 0], [2, 1, 0, 0, 2]], dtype='intp')  # 2 vampire, 1 humain, 2 loup-garou

        # On crée la table de hashage des mouvements et d'autres paramètres sur les effectifs de la carte
        Map.init_map_class(self.size, initial_positions)

        # On ajoute les cases non vides avec update pour bien hasher notre carte
        self.update_content(initial_positions)

        self.UPD = []  # Liste des changements lors d'un update de la carte
        self.debug_mode = debug_mode

    @property
    def populations(self):
        return tuple(self._populations)

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
        self._populations += np.sum(new_content-old_content, axis=0)

        # On ajoute les positions xi, yi
        # new_content_w_pos = [[x1, y1, n_h1, n_v1, n_w1]
        #                      [x2, y2, n_h2, n_v2, n_w2]]
        new_content_w_pos = np.hstack((pos_row[:, np.newaxis], pos_col[:, np.newaxis], new_content))        

        # On applique le hash à chaque [xi, yi, n_hi, n_vi, n_wi]
        np.apply_along_axis(self.hash_position, 1, new_content_w_pos)

    def home_vampire(self):
        """
        Renvoie les coordonnées de la case de départ des vampires
        :return: (i,j)
        """
        return divmod(self.content[:,:,1].argmax(), self.content.shape[1])

    def home_werewolf(self):
        """
        Renvoie les coordonnées de la case de départ des loups-garous
        :return: (i,j)
        """
        return divmod(self.content[:,:,2].argmax(), self.content.shape[1])

    def MAP_command(self):
        """
        Renvoie les nombres de cases peuplés et leurs quintuplets (coordonées, population).
        Le quintuplet a pour format (i,j,n_hum, n_vampire, n_loup_garou) avec i,j les coordonnées de la case
        n_humain le nombre d'humains, n_vampire le nombre de vampires et n_loup_garou le nombre de loups garous
        Utilisé par l'envoi des informations de la carte aux joueurs par le serveur
        :return: n (int), elements (list quintuplets)
        """
        i_x, i_y = self.content.nonzero()
        n = i_x.size
        content = self.content[i_x, i_y]
        elements = np.hstack((i_x[:, np.newaxis], i_y[:, np.newaxis], content))
        return n, elements.tolist()

    def create_positions(self, positions):
        """ Crée la carte à partir de la commande MAP reçu par le joueur

        :param positions: liste de quintuplets de la forme (i,j,n_hum, h_vampire, n_loup_garou)
        avec i,j les coordonnées de la case
        :return: None
        """
        positions = np.array(list(map(list,positions)))
        NumpyMap.init_map_class(self.size, positions)
        self.update_content(positions)

    def next_possible_positions(self, is_vamp):
        """
        Une fonction qui génère toutes les positions possibles à partir d'une carte (8 mouvements pour chaque groupe)

        :return: new_positions : un dictionnaire dont les clefs sont (x_old,y_old) et les valeurs les nouvelles positions possibles
        """

        new_positions = defaultdict(list)

        # On récupère toutes les positions initiales possibles
        if is_vamp:  # Le joueur est un loup-garou
            starting_x, starting_y = self.content[:,:,1].nonzero()
        else:  # Le joueur est un loup-garou
            starting_x, starting_y = self.content[:,:,2].nonzero()

        x_max, y_max = self.size

        for x_old, y_old in zip(starting_x, starting_y):

            available_positions = [(x_old + i, y_old + j) for i, j in product((-1, 0, 1), repeat=2) \
                                   if (i, j) != (0, 0) \
                                   and 0 <= (x_old + i) < x_max \
                                   and 0 <= (y_old + j) < y_max
                                   ]  # pas de condition sur la règle 5 ici, pour ne pas être trop restrictif
            for new_pos in available_positions:
                new_positions[(x_old, y_old)].append(new_pos)
        return new_positions

    @staticmethod
    def repartitions_recursive(pop_of_monster, n_case):
        """ Renvoie les répartitions d'au plus pop_of_monster dans n_case

        VERSION MODIFIÉE !!!!
        PAS DE GROUPE DE 1
        :param pop_of_monster: int
        :param n_case: int
        :return: list : liste des répartitions possibles
        """
        repartitions = list()

        #if pop_of_monster == 0:
        #    return [[0] * n_case]
        if n_case == 1:
            for pop_last_case in range(pop_of_monster + 1):
                # Test : Pas de groupe de 1
                if pop_of_monster > 1  :
                    if pop_of_monster-pop_last_case == 1:
                        continue
                    if pop_last_case == 1:
                        continue
                repartitions.append([pop_last_case])
            return repartitions
        for pop_first_case in range(pop_of_monster + 1):
            # Test : Pas de groupe de 1
            if pop_of_monster > 1 :
                if pop_of_monster-pop_first_case == 1:
                    continue
                if pop_first_case == 1:
                    continue
            for rep in NumpyMap.repartitions_recursive(pop_of_monster - pop_first_case, n_case - 1):
                new_rep = [pop_first_case] + rep
                repartitions.append(new_rep)
        return repartitions

    def next_possible_moves(self, is_vamp):
        """ Renvoie toutes les combinaisons possibles de mouvements possibles par un joueur

        :param is_vamp: race du joueur
        :return: liste des mouvements possibles
        """
        next_possible_positions = self.next_possible_positions(is_vamp)

        group_repartitions = {}  # pour chaque groupe, on regarde la répartition de monstres autour de la case de départ

        for (x_old, y_old), next_positions in next_possible_positions.items():

            n_case = len(next_positions)  # Nombre de nouvelles positions possibles

            if is_vamp:
                pop_of_monsters = self.content[x_old, y_old, 1] # Nombre de vampires sur la case
            else:
                pop_of_monsters = self.content[x_old, y_old, 2]  # Nombre de loup-garous sur la case

            # Toutes les possibilités de répartitions à pop_of_monstres monstres sur n_case cases
            repartitions = NumpyMap.repartitions_recursive(pop_of_monsters, n_case)

            group_repartitions[(x_old, y_old)] = repartitions

        # liste des mouvements possibles par le joueur
        next_possible_moves = list()

        # On s'intéresse à toutes les combinaisons possibles de mouvements sur chaque groupe
        for combined_repartitions in product(*group_repartitions.values()):

            moves = np.zeros((1,5), dtype='int64')  # Liste des mouvements

            # Parcours de chaque groupe de monstre
            for (x_old, y_old), repartition in zip(group_repartitions.keys(), combined_repartitions):

                # Pour un groupe de monstre, où vont-ils partir ?
                for i, n_mons in enumerate(repartition):
                    # Au moins un monstre se déplace
                    if n_mons:
                        # Position d'arrivée de ce sous-groupe de monstre
                        x_new, y_new = next_possible_positions[x_old, y_old][i]

                        # Respect de la règle 5
                        if np.all([x_new, y_new] == moves.take([0,1], axis=1)):
                            continue  # On ne rajoute pas cet élément
                        if np.all([x_old, y_old] == moves.take([3,4], axis=1)):
                            continue  # On ne rajoute pas cet élément

                        # On enregistre ce mouvement pour un groupe de monstre
                        moves = np.append(moves, [[x_old, y_old, n_mons, x_new, y_new]], axis=0)

            # Respect de la règle 1
            if moves.shape[0]==1:
                continue
            
            moves = moves[1:,:]

            if not any(np.all(moves == a) for a in next_possible_moves):
                next_possible_moves.append(moves)

        # Respect de la règle 1
        #while [] in next_possible_moves:
        #    next_possible_moves.remove([])

        return next_possible_moves

    def compute_score_map(self, is_vamp):
        """Calcule les scores de chaque cases de la carte et renvoie un nparray

        :return: numpy array des scores de chaque case
        """
        # 1 noyau gaussien, 1 noyau moyenne
        gauss_k = np.array([[1,1,1],[1,2,1], [1,1,1]], dtype='uint8')
        avg_k   = np.ones((3,3), dtype='uint8')
        
        a = 1 if is_vamp else 2
        d = 2 if is_vamp else 1
    
        score_hum = signal.convolve2d(self.content[:,:,0], gauss_k, mode="same")
        score_adv = (signal.convolve2d(self.content[:,:, a], avg_k, mode="same") - self.content[:,:,d]) * self.content[:,:,d]
        score = np.maximum(8 * score_hum, score_adv)
        return score


    def next_ranked_moves(self, is_vamp):
        score = self.compute_score_map(is_vamp)
        ranked_moves = sorted(
            self.next_possible_moves(is_vamp),
            key= lambda moves: np.sum(score[moves.T[3], moves.T[4]]),
            reverse=True)
        return ranked_moves


    def random_moves(self, is_vamp):
        """ Renvoie un mouvement aléatoirement choisi

        :param is_vamp: race du joueur
        :return: liste de mouvements de la forme [(i,j,n,x,y),...]
        """
        # Dictionnaires des mouvements rassemblés, en valeur le nombre de monstres
        concat_moves = defaultdict(int)

        next_possible_positions = self.next_possible_positions(is_vamp)
        # On souhaite avoir au moins un mouvement
        while not concat_moves:
            for (x_old, y_old), next_positions in next_possible_positions.items():

                if is_vamp:
                    pop_of_monsters = self.content[x_old, y_old, 1]  # Nombre de vampires sur la case
                else:
                    pop_of_monsters = self.content[x_old, y_old, 2]  # Nombre de loup-garous sur la case

                # On choisit le nombre de monstres à déplacer un à un.
                n_moving_monsters= random.randint(0,pop_of_monsters)

                for _ in range(n_moving_monsters):
                    concat_moves[(x_old, y_old, *random.choice(next_positions))]+=1

        # On ecrit au bon format notre liste de mouvements attendue
        random_moves=np.zeros((1,5), dtype='int64')
        for (i,j,x,y),n in concat_moves.items():
            np.append(random_moves, [[i,j,n,x,y]], axis=0)

        return random_moves[1:]

    def compute_moves(self, moves):
        """
        Met à jour et traite les déplacements d'un joueur sur la carte
        :param moves: numpy array de quintuplets de la forme (i,j,n,x,y) 
                      pour un déplacement de n individus en (i,j) vers (x,y)
        :return: None
        """
        # Mise à zéro de la liste des modifications de la carte
        self.UPD = []
        # On enregistre la carte actuelle pour la comparer avec sa version à jour
        old_map_content = self.content.copy()

        # Race du joueur
        is_vamp = True if self.content[moves[0,0], moves[0,1], 1] else False

        # Emplacement des batailles, avec le nombre de représentants de notre espèce à cet endroit
        battles_to_run = defaultdict(int)
        for i, j, n, x, y in moves:
            # Libération des cases sources
            if is_vamp:  # le joueur est un vampire
                self.update_content(np.array([[i, j, 0,  self.content[i, j, 1] - n, 0]], dtype='int64'))
            else:  # le joueur est un loup-garou
                self.update_content(np.array([[i, j, 0, 0, self.content[i, j, 2] - n]], dtype='int64'))

            # Chargement des cases cibles
            # On enregistre les modifications sur les cases sans bataille
            # Population de la case cible
            n_hum, n_vamp, n_lg = tuple(self.content[x, y])
            # Si case cible est vide
            if np.all(self.content[x, y] == [0, 0, 0]):
                self.update_content(np.array([[x, y, 0, n * is_vamp, n * (not is_vamp)]], dtype='int64'))

            # Case vide peuplée d'humains
            if n_hum:
                # On enregistre la bataille
                battles_to_run[(x, y)] += n

            # Case cible peuplée d'ami
            # On peuple ces cases
            if n_vamp and is_vamp:
                self.update_content(np.array([[x, y, 0, (n + n_vamp), 0]], dtype='int64'))
            elif n_lg and not is_vamp:
                self.update_content(np.array([[x, y, 0, 0, (n + n_lg)]], dtype='int64'))

            # Case cible avec des ennemis
            if n_vamp and not is_vamp or n_lg and is_vamp:
                # On enregistre la bataille
                battles_to_run[(x, y)] += n

        # On traite les batailles enregistrées
        for x, y in battles_to_run:
            n_att = battles_to_run[(x, y)]  # Nombre d'attaquants
            n_hum, n_vamp, n_lg = tuple(self.content[x, y])  # Populations initiales de la case cible

            ######################## Bataille Humain vs Monstre ##################

            if n_hum:
                if self.debug_mode:
                    print("Bataille contre humains en ({},{})".format(x, y))

                # cas victoire assurée
                if n_hum <= n_att:
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} humains vs {} attaquants".format(n_att, n_hum))
                    n_conv = sum(self.tirage(n_att, n_hum) for _ in range(n_hum))  # Nombre d'humains convertis
                    n_surv = sum(
                        self.tirage(n_att, n_hum) for _ in range(n_att))  # Nombre de survivants de l'espèce attaquante
                    # Enregistrement des nouvelles populations sur la carte
                    self.update_content(np.array([[x, y, 0, is_vamp * (n_surv + n_conv), (not is_vamp) * (n_surv + n_conv)]], dtype='int64'))
                    if self.debug_mode:
                        print("Victoire de l'attaquant ({} survivants, {} humains convertis)".format(n_surv, n_conv))

                # cas victoire non sure
                else:
                    # Victoire de l'attaquant ?
                    victory = self.tirage(n_att, n_hum)
                    if self.debug_mode:
                        print("Probabilité de victoire : {:.2f}% ({} humains vs {} attaquants)".format(
                            Map.proba_p(n_att, n_hum), n_hum, n_att))
                    # Victoire des monstres
                    if victory:
                        n_conv = sum(self.tirage(n_att, n_hum) for _ in range(n_hum))  # Nombre d'humains convertis
                        n_surv = sum(self.tirage(n_att, n_hum) for _ in
                                     range(n_att))  # Nombre de survivants de l'espèce attaquante
                        # Enregistrement des nouvelles populations sur la carte
                        self.update_content(np.array([[x, y, 0, is_vamp * (n_surv + n_conv), (not is_vamp) * (n_surv + n_conv)]], dtype='int64'))

                        if self.debug_mode:
                            print(
                                "Victoire de l'attaquant ({} survivants, {} humains convertis)".format(n_surv, n_conv))
                    else:  # défaite
                        n_surv = n_hum - sum(
                            self.tirage(n_att, n_hum) for _ in range(n_hum))  # Nombre d'humain survivant
                        # Enregistrement des humains survivants sur la carte
                        self.update_content(np.array([[x, y, n_surv, 0,0]], dtype='int64'))
                        if self.debug_mode:
                            print("Défaite de l'attaquant ({} humains survivants)".format(n_surv))


            ###################### Bataille Vampires vs Loups-Garous ########################

            else:
                if self.debug_mode:
                    print("Bataille entres monstres en ({},{})".format(x, y))

                n_def = n_lg if is_vamp else n_vamp  # Nombre de défenseurs

                # Victoire sure
                if n_def * 1.5 <= n_att:
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} attaquants vs {} défenseurs".format(n_att, n_def))

                    n_surv = sum(self.tirage(n_att, n_def) for _ in range(n_att))  # Nombre d'attaquants survivants

                    # Enregistrement des attaquants survivants
                    self.update_content(np.array([[x, y, 0, is_vamp * n_surv, (not is_vamp) * n_surv]], dtype='int64'))

                    if self.debug_mode:
                        print("Victoire de l'attaquant ! {} survivants".format(n_surv))

                # Victoire non sure
                else:
                    # Victoire de l'attaquant
                    victory = self.tirage(n_att, n_def)

                    if self.debug_mode:
                        print("Probabilité de victoire : {:.2f}% ({} défenseurs vs {} attaquants)".format(
                            Map.proba_p(n_att, n_def), n_def, n_att))

                    # Victoire de l'attaquant
                    if victory:
                        n_surv = sum(self.tirage(n_att, n_def) for _ in range(n_att))  # Nombre d'attaquants survivants
                        # Enregistrement sur la carte
                        self.update_content(np.array([[x, y, 0, is_vamp * n_surv, (not is_vamp) * n_surv]], dtype='int64'))

                        if self.debug_mode:
                            print("Victoire de l'attaquant ! {} survivants".format(n_surv))

                    # Victoire du défenseur
                    else:
                        n_surv = n_def - sum(
                            self.tirage(n_att, n_def) for _ in range(n_def))  # Nombre de défenseur survivant
                        # Enregistrement sur la carte
                        self.update_content(np.array([[x, y, 0, (not is_vamp) * n_surv, is_vamp * n_surv]], dtype='int64'))

                        if self.debug_mode:
                            print("Défaite de l'attaquant ({} défenseurs survivants)".format(n_surv))

        # Remplissage de la liste UPD à partir des modifications de la carte
        changed_i, changed_j = np.any(self.content != old_map_content, axis=2).nonzero()
        changed_content = self.content[changed_i, changed_j]
        elements = np.hstack((changed_i[:, np.newaxis], changed_j[:, np.newaxis], changed_content))
        self.UPD += list(map(tuple, elements.tolist()))  # Enregistrement dans la liste UPD


    def possible_outcomes(self, moves):
        """ Evalue une liste de mouvements, et donne en sortie pour chaque issue possible un update des positions
        et la probabilité de la dite issue

        :param moves: nparray de mouvements de la forme [[i1,j1,n1,x1,y1]
                                                         [i2,j2,n2,x2,y2]]
        :return: liste du type [(probabilité associée, liste des mises à jour de positions)...]
        """
        battles_to_run = defaultdict(int)

        # Race du joueur
        is_vamp = True if self.content[moves[0,0], moves[0,1], 1] else False

        peaceful_moves = []  # Liste des nouvelles positions sans bataille

        for move in moves:
            i, j, n_mons, x, y = move
            n_hum, n_vamp, n_lg = tuple(self.content[x, y])
            if is_vamp and n_hum == 0 and n_lg == 0:  # Cas mouvement amical vampire
                peaceful_moves.append(move)
            elif not is_vamp and n_hum == 0 and n_vamp == 0:  # Cas mouvement amical loup-garou
                peaceful_moves.append(move)
            else:
                battles_to_run[(x, y)] += n_mons

        # On parcourt les batailles possibles
        battles_possible_outcomes = {}  # Référence pour chaque bataille les issues possibles
        for (x, y), n_att in battles_to_run.items():
            n_hum, n_vamp, n_lg = self.content[(x, y)]
            possible_outcomes = []
            n_def = n_lg + n_hum if is_vamp else n_vamp + n_hum
            proba_p = self.proba_p(n_att, n_def)

            # Cas bataille contre des humains
            if n_hum:
                # Cas victoire assurée
                if n_att >= n_hum:
                    for k_surv in range(n_hum + n_att + 1):
                        proba_outcome = pow(proba_p, k_surv) * pow((1 - proba_p), n_hum + n_att - k_surv)
                        proba_outcome *= self.binomial_coefficient(k_surv, n_hum + n_att)
                        if is_vamp and proba_outcome:
                            possible_outcomes.append((proba_outcome, (x, y, 0, k_surv, 0)))
                        elif proba_outcome:
                            possible_outcomes.append((proba_outcome, (x, y, 0, 0, k_surv)))
                # Cas victoire non sure
                else:
                    # Si victoire des monstres
                    proba_victory = proba_p
                    for k_surv in range(n_hum + n_att + 1):
                        proba_outcome = pow(proba_p, k_surv) * pow((1 - proba_p), n_hum + n_att - k_surv)
                        proba_outcome *= self.binomial_coefficient(k_surv, n_hum + n_att)
                        if is_vamp:
                            possible_outcomes.append((proba_victory * proba_outcome, (x, y, 0, k_surv, 0)))
                        else:
                            possible_outcomes.append((proba_victory * proba_outcome, (x, y, 0, 0, k_surv)))

                    # Si victoire des humains
                    for k_surv in range(n_hum + 1):
                        proba_outcome = pow(proba_p, n_hum - k_surv) * pow((1 - proba_p), k_surv)
                        proba_outcome *= self.binomial_coefficient(k_surv, n_hum)
                        possible_outcomes.append(((1 - proba_victory) * proba_outcome, (x, y, k_surv, 0, 0)))

            # Cas bataille monstre vs monstre
            else:

                # Cas victoire sure
                if n_att >= 1.5 * n_def:
                    for k_surv in range(n_att + 1):
                        proba_outcome = pow(proba_p, k_surv) * pow((1 - proba_p), n_att - k_surv)
                        proba_outcome *= self.binomial_coefficient(k_surv, n_att)
                        if is_vamp:
                            possible_outcomes.append((proba_outcome, (x, y, 0, k_surv, 0)))
                        else:
                            possible_outcomes.append((proba_outcome, (x, y, 0, 0, k_surv)))
                # Cas victoire non assurée
                else:
                    proba_victory = proba_p

                    # Si victoire de l'attaquant
                    for k_surv in range(n_att + 1):
                        proba_outcome = pow(proba_p, k_surv) * pow((1 - proba_p), n_att - k_surv)
                        proba_outcome *= self.binomial_coefficient(k_surv, n_att)
                        if is_vamp:
                            possible_outcomes.append((proba_victory * proba_outcome, (x, y, 0, k_surv, 0)))
                        else:
                            possible_outcomes.append((proba_victory * proba_outcome, (x, y, 0, 0, k_surv)))

                    # Si défaite de l'attaquant
                    for k_surv in range(n_def + 1):
                        proba_outcome = pow(proba_p, k_surv) * pow((1 - proba_p), n_def - k_surv)
                        proba_outcome *= self.binomial_coefficient(k_surv, n_def)
                        if is_vamp:
                            possible_outcomes.append(((1 - proba_victory) * proba_outcome, (x, y, 0, 0, k_surv)))
                        else:
                            possible_outcomes.append(((1 - proba_victory) * proba_outcome, (x, y, 0, k_surv, 0)))

            battles_possible_outcomes[(x, y)] = possible_outcomes

        # Calcul des mises à jours de positions

        # On vide les cases de départ et on remplit les destinations sans conflits
        # Par défaut, peacedul_positions_update revoie le nombre de monstre présent initialement sur la case

        peaceful_positions_update = {}

        # case source à vider
        for move in moves:
            i, j, n_mons, x, y = move
            if (i, j) not in peaceful_positions_update:
                peaceful_positions_update[(i, j)] = np.sum(self.content[i, j])
            peaceful_positions_update[(i, j)] -= n_mons
        # case destination pacifique à remplir
        for move in peaceful_moves:
            i, j, n_mons, x, y = move
            if (x, y) not in peaceful_positions_update:
                peaceful_positions_update[(x, y)] = np.sum(self.content[x, y])
            peaceful_positions_update[(x, y)] += n_mons

        # Liste des mises à jour de position triviales
        trivial_positions_update = []

        for (i, j), n_mons in peaceful_positions_update.items():
            if is_vamp:
                trivial_positions_update.append((i, j, 0, n_mons, 0))
            else:
                trivial_positions_update.append((i, j, 0, 0, n_mons))

        # Notre liste en sortie
        # De la forme [(proba_outcome, [liste des positions (i,j,n_hum,n_vamp,n_lg)...]),...]
        possible_outcomes = []
        # On sélectionne des combinaisons possibles d'issues de chaque bataille
        for combined_battles_outcomes in product(*battles_possible_outcomes.values()):
            proba_conbined_battle = 1
            possible_outcome = list(trivial_positions_update)
            for proba_outcome, new_battle_positions in combined_battles_outcomes:
                proba_conbined_battle *= proba_outcome
                possible_outcome.append(new_battle_positions)
            if proba_conbined_battle:
                possible_outcomes.append((proba_conbined_battle, possible_outcome))

        return possible_outcomes

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
        n_hum, n_vamp, n_lg = self.populations
        print(
            "Vampires {} | Werewolves {} | Remaining Humans: {}".format(
                n_vamp, n_lg, n_hum))

if __name__ == "__main__":
    carte = NumpyMap()
    carte.print_map()
    for a in carte.next_ranked_moves(True):
        print(a)
    #carte.update_content(np.array([[0,0,5,0,0]]))
    #carte.print_map()
    #print(carte.content)
    #import pdb; pdb.set_trace()
    move = np.array([[0,1,1,1,1], [0,1,1,1,2]])
    carte.compute_moves(move)
    carte.print_map()
    print(carte.UPD)
    #print(move)
    #print(score)
    #print(move.T[3], move.T[4])
    #print(np.sum(score[move.T[3], move.T[4]]))