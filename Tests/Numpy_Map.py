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
    Carte du jeu amélioré avec numpy v2: 
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
    
    GAUSS_K = np.array([[1,1,1],[1,2,1], [1,1,1]])
    AVG_K   = np.array([[1,1,1],[1,1,1], [1,1,1]])

    def __init__(self, map_size=None, initial_positions=list(), debug_mode=False):
        """
        Initialise la carte
        :param map_size: dimensions de la carte
        :param initial_positions: Contenu de la carte format dict[(i,j)]=(nombre_humains, nombre_vampires, nombre_loup-garous)
        :param debug_mode: mode debug (boolean)
        """
        # Par Défaut Carte The Trap
        if map_size is None:
            self.size = (3, 3)
        else:
            self.size = map_size
        self._content = np.zeros((self.size[0], self.size[1], 3), dtype='int32')
        self._populations = np.zeros(3, dtype='int32') # 0 Humains, 0 Vampires, 0 Werewolves
        self._hash = 0

        if initial_positions == [] and map_size is None:
            initial_positions = [(0, 1, 0, 2, 0), (1, 1, 1, 0, 0), (2, 1, 0, 0, 2)]  # 2 vampire, 1 humain, 2 loup-garou

        # On crée la table de hashage des mouvements et d'autres paramètres sur les effectifs de la carte
        Map.init_map_class(self.size, initial_positions)

        # On ajoute les cases non vides avec update pour bien hasher notre carte
        self.update_content(initial_positions)

        self.UPD = []  # Liste des changements lors d'un update de la carte
        self.debug_mode = debug_mode

    def update_content(self, positions):
        """
        Mise à jour simple de la carte
        :param positions: liste de quintuplets de la forme (i,j,n_hum, n_vampire, n_loup_garou) 
            avec i,j les coordonnées de la case,
            n_humain le nombre d'humains, n_vampire le nombre de vampires et n_loup_garou le nombre de loups garous
        :return: None
        """
        for i, j, n_hum, n_vamp, n_lg in positions:
            old_h, old_v, old_lg = self.content[i, j]
            # On déhash l'ancienne position
            self._hash ^= self.hash_position((i, j, old_h, old_v, old_lg))

            # On met à jour la carte
            self.content[i, j] = (n_hum, n_vamp, n_lg)

            # On met à jour la population (les 3 sommes semblent être le plus performants d'après stackoverflow)
            self._populations += (n_hum - old_h, n_vamp - old_v, n_lg - old_lg)

            # On hash la nouvelle position
            self._hash ^= self.hash_position((i, j, *self.content[i, j]))

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
        i_x, i_y = np.any(self.content != [0,0,0], axis=2).nonzero()
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
        NumpyMap.init_map_class(self.size, positions)
        self.update_content(positions)

    def next_possible_positions(self, is_vamp):
        """
        Une fonction qui génère toutes les positions possibles à partir d'une carte (8 mouvements pour chaque groupe)

        :return: new_positions : un dictionnaire dont les clefs sont (x_old,y_old) et les valeurs les nouvelles positions possibles
        """

        new_positions = defaultdict(list)

        a = 1 if is_vamp else 2
        # On récupère toutes les positions initiales possibles
        starting_x, starting_y = self.content[...,a].nonzero()

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

            moves = list()  # Liste des mouvements

            # Parcours de chaque groupe de monstre
            for starting_position, repartition in zip(group_repartitions.keys(), combined_repartitions):

                # Pour un groupe de monstre, où vont-ils partir ?
                for i, n_mons in enumerate(repartition):
                    # Au moins un monstre se déplace
                    if n_mons:
                        # Position d'arrivée de ce sous-groupe de monstre
                        new_position = next_possible_positions[starting_position][i]

                        # Respect de la règle 5
                        if new_position in [(x_old, y_old) for x_old, y_old, *_ in moves]:
                            continue  # On ne rajoute pas cet élément
                        if starting_position in [(new_x, new_y) for *_, new_x, new_y in moves]:
                            continue  # On ne rajoute pas cet élément

                        # On enregistre ce mouvement pour un groupe de monstre
                        moves.append((*starting_position, n_mons, *new_position))

            if moves not in next_possible_moves:
                next_possible_moves.append(moves)

        # Respect de la règle 1
        while [] in next_possible_moves:
            next_possible_moves.remove([])

        return next_possible_moves

    def compute_score_map(self, is_vamp):
        """Calcule les scores de chaque cases de la carte et renvoie un nparray

        :return: numpy array des scores de chaque case
        """
        # 1 noyau gaussien, 1 noyau moyenne
        a = 1 if is_vamp else 2
        d = 2 if is_vamp else 1

        hum_content = self.content[...,0]
        att_content = self.content[...,a]
        def_content = self.content[...,d]
        score_hum = signal.convolve2d(hum_content, self.GAUSS_K, mode="same")
        score_adv = (signal.convolve2d(att_content, self.AVG_K, mode="same") - def_content) * def_content
        score = np.maximum(8 * score_hum, score_adv)
        return score.tolist()

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
        random_moves=list()
        for (i,j,x,y),n in concat_moves.items():
            random_moves.append((i,j,n,x,y))

        return random_moves

    def compute_moves(self, moves):
        """
        Met à jour et traite les déplacements d'un joueur sur la carte
        :param moves: liste de quintuplets de la forme (i,j,n,x,y) pour un déplacement de n individus en (i,j) vers (x,y)
        :return: None
        """
        # Mise à zéro de la liste des modifications de la carte
        self.UPD = []
        # On enregistre la carte actuelle pour la comparer avec sa version à jour
        old_map_content = self.content.copy()

        # Race du joueur
        is_vamp = True if self.content[moves[0][0], moves[0][1], 1] else False

        # Emplacement des batailles, avec le nombre de représentants de notre espèce à cet endroit
        battles_to_run = defaultdict(int)
        for i, j, n, x, y in moves:
            # Libération des cases sources
            if is_vamp:  # le joueur est un vampire
                self.update_content([(i, j, 0,  self.content[i, j, 1] - n, 0)])
            else:  # le joueur est un loup-garou
                self.update_content([(i, j, 0, 0, self.content[i, j, 2] - n)])

            # Chargement des cases cibles
            # On enregistre les modifications sur les cases sans bataille
            # Population de la case cible
            n_hum, n_vamp, n_lg = self.content[x, y]
            # Si case cible est vide
            if np.all(self.content[x, y] == [0, 0, 0]):
                self.update_content([(x, y, 0, n * is_vamp, n * (not is_vamp))])

            # Case vide peuplée d'humains
            if n_hum:
                # On enregistre la bataille
                battles_to_run[(x, y)] += n

            # Case cible peuplée d'ami
            # On peuple ces cases
            if n_vamp and is_vamp:
                self.update_content([(x, y, 0, (n + n_vamp), 0)])
            elif n_lg and not is_vamp:
                self.update_content([(x, y, 0, 0, (n + n_lg))])

            # Case cible avec des ennemis
            if n_vamp and not is_vamp or n_lg and is_vamp:
                # On enregistre la bataille
                battles_to_run[(x, y)] += n

        # On traite les batailles enregistrées
        for x, y in battles_to_run:
            n_att = battles_to_run[(x, y)]  # Nombre d'attaquants
            n_hum, n_vamp, n_lg = self.content[x, y]  # Populations initiales de la case cible

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
                    self.update_content([(x, y, 0, is_vamp * (n_surv + n_conv), (not is_vamp) * (n_surv + n_conv))])
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
                        self.update_content([(x, y, 0, is_vamp * (n_surv + n_conv), (not is_vamp) * (n_surv + n_conv))])

                        if self.debug_mode:
                            print(
                                "Victoire de l'attaquant ({} survivants, {} humains convertis)".format(n_surv, n_conv))
                    else:  # défaite
                        n_surv = n_hum - sum(
                            self.tirage(n_att, n_hum) for _ in range(n_hum))  # Nombre d'humain survivant
                        # Enregistrement des humains survivants sur la carte
                        self.update_content([(x, y, n_surv, 0,0)])
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
                    self.update_content([(x, y, 0, is_vamp * n_surv, (not is_vamp) * n_surv)])

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
                        self.update_content([(x, y, 0, is_vamp * n_surv, (not is_vamp) * n_surv)])

                        if self.debug_mode:
                            print("Victoire de l'attaquant ! {} survivants".format(n_surv))

                    # Victoire du défenseur
                    else:
                        n_surv = n_def - sum(
                            self.tirage(n_att, n_def) for _ in range(n_def))  # Nombre de défenseur survivant
                        # Enregistrement sur la carte
                        self.update_content([(x, y, 0, (not is_vamp) * n_surv, is_vamp * n_surv)])

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

        :param moves: liste de mouvements de la forme [(i,j,n,x,y),...]
        :return: liste du type [(probabilité associée, liste des mises à jour de positions)...]
        """
        battles_to_run = defaultdict(int)

        # Race du joueur
        is_vamp = True if self.content[moves[0][0], moves[0][1], 1] else False

        peaceful_moves = []  # Liste des nouvelles positions sans bataille

        for move in moves:
            i, j, n_mons, x, y = move
            n_hum, n_vamp, n_lg = self.content[x, y]
            if is_vamp and n_hum == 0 and n_lg == 0:  # Cas mouvement amical vampire
                peaceful_moves.append(move)
            elif not is_vamp and n_hum == 0 and n_vamp == 0:  # Cas mouvement amical loup-garou
                peaceful_moves.append(move)
            else:
                battles_to_run[(x, y)] += n_mons

        # On parcourt les batailles possibles
        battles_possible_outcomes = {}  # Référence pour chaque bataille les issues possibles
        for (x, y), n_att in battles_to_run.items():
            n_hum, n_vamp, n_lg = self.content[x, y]
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


    def is_valid_moves(self, moves, is_vamp):
        """Vérifie les mouvements proposés par un joueur. Renvoie Vrai si les mouvements sont corrects, faux sinon.

        :param moves: nparray liste des mouvements proposés par un joueur
                                    [[old_x1, old_y1, n1, new_x1, new_x1]
                                     [old_x2, old_y2, n2, new_x2, new_x2]]
        :param is_vamp: Boolean Vrai si c'est le joueur 1/ Vampire qui propose ses mouvements, Faux sinon
        :return: Boolean
        """
        """Vérifie les mouvements proposés par un joueur. Renvoie Vrai si les mouvements sont corrects, faux sinon.

        :param moves: list liste des mouvements proposés par un joueur
        :param is_vamp: Boolean Vrai si c'est le joueur 1/ Vampire qui propose ses mouvements, Faux sinon
        :return: Boolean
        """
        moves_checked = []  # liste des mouvements vérifiés parmi ceux proposés

        a = 1 if is_vamp else 2

        # Règle 1 : Au moins un mouvement
        if len(moves) == 0:
            return False

        # Règle 6 : Au moins un pion qui bouge
        if all(n == 0 for _, _, n, _, _ in moves):
            return False

        for i, j, n, x, y in moves:
            # Règle 4 : 8 cases adjacentes
            if abs(i - x) > 1 or abs(j - y) > 1:
                return False

            n_initial = self.content[i, j, a]
            n_checked = sum([n_c for (i_c, j_c, n_c, _, _) in moves_checked if (i_c, j_c) == (i, j)])

            # Règle 3 : On ne peut pas bouger plus que nos pions
            if n_initial < n_checked + n:
                return False
            moves_checked.append((i, j, n, x, y))

            # Règle 3 et 2 : On ne bouge que nos pions
            if n_initial == 0:
                return False

        # Règle 5 : Une case ne pas se retrouver cible et source
        for move_1, move_2 in combinations(moves, 2):
            if (move_1[0], move_1[1]) == (move_2[3], move_2[4]):
                return False
            if (move_1[3], move_1[4]) == (move_2[0], move_2[1]):
                return False

        # Si toutes les règles sont respectées, on renvoie vrai
        return True

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
    carte.compute_score_map(True)
    #print(carte.hash)
    #carte.update_content(np.array([[0,1,2,0,0]]))
    #print(carte.hash)
    #carte.update_content(np.array([[0,0,5,0,0]]))
    #move = np.array([[0,1,1,1,1],[0,2,1,1,2]])
    #for i in carte.possible_outcomes(move):
    #    print(i)