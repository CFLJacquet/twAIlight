from collections import defaultdict
import random
from itertools import combinations, product
from operator import itemgetter
from copy import deepcopy
from math import log2, pow, floor
from scipy import signal
import numpy as np
from pprint import pprint

class Map:
    """
    Carte du jeu

    Par défaut : Dust_2

    _______________
    |    |    |    |
    _______________
    | 2V | 1H | 2W |
    _______________
    |    |    |    |
    _______________
    """

    __HASH_TABLE = None
    __N_MONSTER_MAX = None  # Nombre de monstres maximum possible

    @classmethod
    def init_map_class(cls, map_size, initial_positions):
        """Crée la table de hashage des mouvements possibles, et renseigne les attributs de populations maximales de la
        classe.

        Méthode de hashage d'un élément de la carte en s'inspirant du hashage de Zobrist.
        https://en.wikipedia.org/wiki/Zobrist_hashing

        :param map_size: taille de la carte (x_max, y_max)
        :param initial_positions: contenu de la carte
        :return: None
        """

        # On cherche à connaitre nos constantes sur les effectifs des espèces en présence
        x_max, y_max = map_size

        sum_human_pop = 0  # Somme des populations d'humains sur la carte
        n_monster_max = 0  # Population maximale d'une espèce de monstre

        for i, j, n_hum, n_vamp, n_lg in initial_positions:
            sum_human_pop += n_hum
            n_monster_max = max(n_vamp, n_lg, n_monster_max)

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
    def N_MONSTER_MAX(cls):
        return cls.__N_MONSTER_MAX

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
        void_content = defaultdict(tuple)
        for i, j in product(range(self.size[0]), range(self.size[1])):
            void_content[(i, j)] = (0, 0, 0)
        self._content = void_content
        self._populations = (0, 0, 0) # 0 Humains, 0 Vampires, 0 Werewolves
        self._hash = 0

        if initial_positions == [] and map_size is None:
            initial_positions = [(0, 1, 0, 2, 0), (1, 1, 1, 0, 0), (2, 1, 0, 0, 2)]  # 2 vampire, 1 humain, 2 loup-garou

        # On crée la table de hashage des mouvements et d'autres paramètres sur les effectifs de la carte
        Map.init_map_class(self.size, initial_positions)

        # On ajoute les cases non vides avec update pour bien hasher notre carte
        self.update_content(initial_positions)

        self.UPD = []  # Liste des changements lors d'un update de la carte
        self.debug_mode = debug_mode

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        setattr(result, '_content', self.content.copy())
        return result

    @property
    def hash(self):
        return self._hash

    @property
    def content(self):
        return self._content

    @property
    def populations(self):
        return self._populations

    @classmethod
    def hash_position(cls, position):
        return cls.__HASH_TABLE[position]

    def home_vampire(self):
        """
        Renvoie les coordonnées de la case de départ des vampires
        :return: (i,j)
        """
        for x_y in self.content:
            if self.content[x_y][1]:  # case avec des vampires
                return x_y

    def home_werewolf(self):
        """
        Renvoie les coordonnées de la case de départ des loups-garous
        :return: (i,j)
        """
        for x_y in self.content:
            if self.content[x_y][2]:  # case avec des loups-garous
                return x_y

    def MAP_command(self):
        """
        Renvoie les nombres de cases peuplés et leurs quintuplets (coordonées, population).
        Le quintuplet a pour format (i,j,n_hum, n_vampire, n_loup_garou) avec i,j les coordonnées de la case
        n_humain le nombre d'humains, n_vampire le nombre de vampires et n_loup_garou le nombre de loups garous
        Utilisé par l'envoi des informations de la carte aux joueurs par le serveur
        :return: n (int), elements (list quintuplets)
        """
        elements = []
        n = 0
        for x_y in self.content:  # Parcours des éléments de la carte
            if sum(self.content[x_y]):  # Cette case est peuplée !
                elements.append((*x_y, *self.content[x_y]))  # On crée le quintuplet
                n += 1
        return n, elements

    def create_positions(self, positions):
        """ Crée la carte à partir de la commande MAP reçu par le joueur

        :param positions: liste de quintuplets de la forme (i,j,n_hum, h_vampire, n_loup_garou)
        avec i,j les coordonnées de la case
        :return: None
        """

        Map.init_map_class(self.size, positions)
        self.update_content(positions)


    def update_content(self, positions):
        """
        Mise à jour de la carte
        :param positions: liste de quintuplets de la forme (i,j,n_hum, n_vampire, n_loup_garou) avec i,j les coordonnées de la case
        n_humain le nombre d'humains, n_vampire le nombre de vampires et n_loup_garou le nombre de loups garous
        :return: None
        """
        for i, j, n_hum, n_vamp, n_lg in positions:
            old_h, old_v, old_lg = self.content[i, j]
            self.simple_update_content(i, j, n_hum, n_vamp, n_lg, old_h, old_v, old_lg)
    
    def simple_update_content(self, i, j, n_hum, n_vamp, n_lg, old_h, old_v, old_lg):
        """
        Mise à jour simple de la carte
        :param positions: 1 quintuplet de la forme (i,j,n_hum, n_vampire, n_loup_garou) avec i,j les coordonnées de la case
        n_humain le nombre d'humains, n_vampire le nombre de vampires et n_loup_garou le nombre de loups garous
        :return: None
        """
        # On déhash l'ancienne position
        self._hash ^= self.hash_position((i, j, old_h, old_v, old_lg))

        # On met à jour la carte
        self._content[i, j] = (n_hum, n_vamp, n_lg)

        # On met à jour la population (les 3 sommes semblent être le plus performants d'après stackoverflow)
        tot_h, tot_v, tot_lg = self._populations
        
        self._populations = (
            tot_h  + (n_hum - old_h),
            tot_v  + (n_vamp - old_v),
            tot_lg + (n_lg - old_lg))

        # On hash la nouvelle position
        self._hash ^= self.hash_position((i, j, n_hum, n_vamp, n_lg))


    @staticmethod
    def relevant_repartitions(pop_of_monster, n_case, split_enabled=True, stay_enabled=True):
        """ Renvoie les répartitions pertinentes d'au plus pop_of_monster dans n_case :
            - max 2 sous-groupes à la fin
            - pas de sous-groupe de moins de pop_of_monster // 3

        :param pop_of_monster: int
        :param n_case: int
        :return: list : liste des répartitions possibles
        """

        pop_combinaisons = list()
        min_size = max(pop_of_monster // 3, 2) if pop_of_monster > 1 else 0
        for pop_1 in range(pop_of_monster if split_enabled else 1):
            pop_2 = pop_of_monster - pop_1
            if  0 < pop_1 < min_size or 0 < pop_2 < min_size:
                continue
            pop_combinaisons.append((pop_1, pop_2))
        
        repartitions = list()
        if stay_enabled:repartitions.append([0] * n_case) # cas trivial
        
        for pop_1, pop_2 in pop_combinaisons:
            if pop_1 == 0 or stay_enabled:
                for j in range(n_case): # Le groupe 1 reste sur la case de départ
                    l = [0] * n_case
                    l[j] = pop_2
                    repartitions.append(l)

            if pop_1 == 0: continue # On évite n_case - 1 doublons 
            for i in range(n_case-1):
                for j in range(i+1, n_case):
                    l = [0] * n_case
                    l[i] = pop_1
                    l[j] = pop_2
                    repartitions.append(l)
        return repartitions


    def next_possible_positions_2(self, is_vamp, nb_group_max=None):
        """
        Une fonction qui génère un ensemble de positions possibles à partir d'une carte.
        Au lieu de renvoyer toutes les cases autour de chaque groupe, on ne considère que 
        les :param: nb_group_max groupes ayant le plus de monstres 

        :param: nb_group_max : nombre de groupes (maximum) considéré (le reste est ignoré)

        :return: next_posible_positions : un dictionnaire dont les clefs sont ((x_old,y_old), pop_old) 
                                 et les valeurs les nouvelles positions possibles
        """
        new_positions = defaultdict(list)
        # Race du joueur
        race = 1 if is_vamp else 2

        # On récupère toutes les positions initiales possibles
        starting_positions = []
        for (x, y), content in self.content.items():
            if content[race] != 0:
                starting_positions.append(((x, y), content[race]))
        
        if not nb_group_max is None:
            if len(starting_positions) > nb_group_max:
                starting_positions = sorted(starting_positions, key=itemgetter(1), reverse=True)
                starting_positions = starting_positions[:nb_group_max]

        x_max, y_max = self.size

        for starting_pos in starting_positions:
            (x_old, y_old), _ = starting_pos

            available_positions = [(x_old + i, y_old + j) for i, j in product((-1, 0, 1), repeat=2) \
                                   if (i, j) != (0, 0) \
                                   and 0 <= (x_old + i) < x_max \
                                   and 0 <= (y_old + j) < y_max
                                   ]  # pas de condition sur la règle 5 ici, pour ne pas être trop restrictif
            for new_pos in available_positions:
                new_positions[starting_pos].append(new_pos)
        return new_positions


    def next_relevant_positions(self, is_vamp, nb_group_max=None, nb_cases=None):
        """
        Une fonction qui genere un ensemble de positions pertinentes à partir d'une carte.
        
        Au lieu de renvoyer toutes les cases autour de chaque groupe, on ne considere que 
        les :param: nb_group_max groupes ayant le plus de monstres 

        De plus on ne renvoie que :param: nb_cases cases pour chaque groupes (ELAGAGE).

        On choisit ces cases en fonctions du nombre d'humains mangeables présents sur chaque case.

        :param: nb_group_max : nombre de groupes (maximum) considéré (le reste est ignoré).
        :param:  nb_cases : nombre de cases renvoyées par groupes

        :return: next_relevant_positions : un dictionnaire dont les clefs sont ((x_old,y_old), pop_old) 
                                 et les valeurs les nouvelles positions possibles
        """
        next_possible_positions = self.next_possible_positions_2(is_vamp, nb_group_max)
        next_relevant_positions = {}
    
        for starting_config in next_possible_positions:
            _, n_mob = starting_config
            
            def sort_function(pos):
                n_hum, _, _ = self.content[pos]
                return n_hum if 1.5*n_hum <= n_mob else -n_hum 

            relevant_positions = sorted(
                next_possible_positions[starting_config],
                key=sort_function,
                reverse=True)

            if not nb_cases is None:
                relevant_positions = relevant_positions[:nb_cases]
            
            next_relevant_positions[starting_config] = relevant_positions
        return next_relevant_positions 


    def next_relevant_moves(self, is_vamp, nb_group_max=None, stay_enabled=None, nb_cases=None):
        """
        Renvoie une liste des mouvements pertinents possibles pour un joueur

        :param: is_vamp: race du joueur
        :param: nb_group_max : nombre de groupes (maximum) considéré (le reste est ignoré).
        :param: stay_enabled : si True, autorise les groupes à ne pas bouger (au moins 1 mouvement est conservé)
        :param: nb_cases : nombre de cases renvoyées par groupes

        :return: liste des mouvements possibles
        """
        next_possible_positions = self.next_relevant_positions(is_vamp, nb_group_max, nb_cases)
        nb_group = len(next_possible_positions)

        group_repartitions = {}  # pour chaque groupe, on regarde la répartition de monstres autour de la case de départ

        for starting_config, next_positions in next_possible_positions.items():
            _, n_mob = starting_config
            n_case = len(next_positions)  # Nombre de nouvelles positions possibles

            pop_of_monsters = n_mob

            # Toutes les possibilités de répartitions à pop_of_monstres monstres sur n_case cases
            split_enabled = True if nb_group_max is None else nb_group < nb_group_max
            repartitions = Map.relevant_repartitions(pop_of_monsters, n_case, split_enabled, stay_enabled)
            nb_group += 1

            group_repartitions[starting_config] = repartitions

        # liste des mouvements possibles par le joueur
        next_possible_moves = list()

        # On s'intéresse à toutes les combinaisons possibles de mouvements sur chaque groupe
        for combined_repartitions in product(*group_repartitions.values()):

            moves = list()  # Liste des mouvements

            # Parcours de chaque groupe de monstre
            for starting_config, repartition in zip(group_repartitions.keys(), combined_repartitions):
                
                starting_position, _ = starting_config
                # Pour un groupe de monstre, où vont-ils partir ?
                for i, n_mons in enumerate(repartition):
                    # Au moins un monstre se déplace
                    if n_mons:
                        # Position d'arrivée de ce sous-groupe de monstre
                        new_position = next_possible_positions[starting_config][i]

                        # On enregistre ce mouvement pour un groupe de monstre
                        moves.append((*starting_position, n_mons, *new_position))

            if moves not in next_possible_moves:
                next_possible_moves.append(moves)

        # Respect de la règle 1
        while [] in next_possible_moves:
            next_possible_moves.remove([])

        return next_possible_moves

    def i_relevant_possible_moves(self, is_vamp, nb_group_max=None, stay_enabled=None, nb_cases=None):
        """
        Renvoie (genere) les mouvements pertinents possibles pour un joueur

        :param: is_vamp: race du joueur
        :param: nb_group_max : nombre de groupes (maximum) considéré (le reste est ignoré).
        :param: stay_enabled : si True, autorise les groupes à ne pas bouger (au moins 1 mouvement est conservé)
        :param: nb_cases : nombre de cases renvoyées par groupes

        :return: liste des mouvements possibles
        """
        next_possible_positions = self.next_relevant_positions(is_vamp, nb_group_max, nb_cases)
        nb_group = len(next_possible_positions)

        group_repartitions = {}  # pour chaque groupe, on regarde la répartition de monstres autour de la case de départ

        for starting_config, next_positions in next_possible_positions.items():
            _, n_mob = starting_config
            n_case = len(next_positions)  # Nombre de nouvelles positions possibles

            pop_of_monsters = n_mob

            # Toutes les possibilités de répartitions à pop_of_monstres monstres sur n_case cases
            split_enabled = True if nb_group_max is None else nb_group < nb_group_max
            repartitions = Map.relevant_repartitions(pop_of_monsters, n_case, split_enabled, stay_enabled)
            nb_group += 1

            group_repartitions[starting_config] = repartitions

        # liste des mouvements possibles par le joueur
        #next_possible_moves = list()

        # On s'intéresse à toutes les combinaisons possibles de mouvements sur chaque groupe
        for combined_repartitions in product(*group_repartitions.values()):

            moves = list()  # Liste des mouvements

            # Parcours de chaque groupe de monstre
            for starting_config, repartition in zip(group_repartitions.keys(), combined_repartitions):
                
                starting_position, _ = starting_config
                # Pour un groupe de monstre, où vont-ils partir ?
                for i, n_mons in enumerate(repartition):
                    # Au moins un monstre se déplace
                    if n_mons:
                        # Position d'arrivée de ce sous-groupe de monstre
                        new_position = next_possible_positions[starting_config][i]

                        # On enregistre ce mouvement pour un groupe de monstre
                        moves.append((*starting_position, n_mons, *new_position))

            if moves == []:
                continue

            yield(moves)


    def random_moves(self, is_vamp):
        """ Renvoie un mouvement aléatoirement choisi

        :param is_vamp: race du joueur
        :return: liste de mouvements de la forme [(i,j,n,x,y),...]
        """
        # Dictionnaires des mouvements rassemblés, en valeur le nombre de monstres
        concat_moves = defaultdict(int)

        next_possible_positions = self.next_relevant_positions(is_vamp)
        # On souhaite avoir au moins un mouvement
        while not concat_moves:
            for starting_config, next_positions in next_possible_positions.items():
                starting_position, n_mob = starting_config
                
                pop_of_monsters = n_mob
                # On choisit le nombre de monstres à déplacer un à un.
                n_moving_monsters= random.randint(0,pop_of_monsters)

                for _ in range(n_moving_monsters):
                    concat_moves[(*starting_position, *random.choice(next_positions))]+=1

        # On ecrit au bon format notre liste de mouvements attendue
        random_moves=list()
        for (i,j,x,y),n in concat_moves.items():
            random_moves.append((i,j,n,x,y))

        return random_moves


    def most_probable_outcome_2(self, moves, is_vamp):
        """
        Met à jour et traite les déplacements d'un joueur sur la carte en considérant uniquement le cas le plus probable dans chaque configuration de bataille
        :param moves: liste de quintuplets de la forme (i,j,n,x,y) pour un déplacement de n individus en (i,j) vers (x,y)
        :return: None
        """
        # Emplacement des batailles, avec le nombre de représentants de notre espèce à cet endroit
        battles_to_run = defaultdict(int)
        for i, j, n, x, y in moves:
            # Libération des cases sources
            old_h, old_v, old_lg = self.content[i,j]
            if is_vamp:  # le joueur est un vampire
                self.simple_update_content(i, j, 0,  old_v-n, 0, old_h, old_v, old_lg)
            else:  # le joueur est un loup-garou
                self.simple_update_content(i, j, 0, 0, old_lg - n, old_h, old_v, old_lg)

            # Chargement des cases cibles
            # On enregistre les modifications sur les cases sans bataille
            # Population de la case cible
            n_hum, n_vamp, n_lg = self.content[(x, y)]
            # Si case cible est vide
            if (n_hum, n_vamp, n_lg) == (0, 0, 0):
                self.simple_update_content(x, y, 0, n * is_vamp, n * (not is_vamp), 0, 0, 0)

            # Case vide peuplée d'humains
            if n_hum:
                # On enregistre la bataille
                battles_to_run[(x, y)] += n

            # Case cible peuplée d'ami
            # On peuple ces cases
            if n_vamp and is_vamp:
                self.simple_update_content(x, y, 0, (n + n_vamp), 0, n_hum, n_vamp, n_lg)
            elif n_lg and not is_vamp:
                self.simple_update_content(x, y, 0, 0, (n + n_lg), n_hum, n_vamp, n_lg)

            # Case cible avec des ennemis
            if n_vamp and not is_vamp or n_lg and is_vamp:
                # On enregistre la bataille
                battles_to_run[(x, y)] += n

        # On traite les batailles enregistrées
        for x, y in battles_to_run:
            n_att = battles_to_run[(x, y)]  # Nombre d'attaquants
            n_hum, n_vamp, n_lg = self.content[(x, y)]  # Populations initiales de la case cible

            ######################## Bataille Humain vs Monstre ##################

            if n_hum:
                if self.debug_mode:
                    print("Bataille contre humains en ({},{})".format(x, y))

                # cas victoire assurée
                if n_hum < n_att:
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} humains vs {} attaquants".format(n_att, n_hum))
                    n_total = n_att+n_hum
                    # Enregistrement des nouvelles populations sur la carte
                    self.simple_update_content(
                        x, y, 
                        0, is_vamp * (n_total), (not is_vamp) * (n_total),
                        n_hum, n_vamp, n_lg)
                    if self.debug_mode:
                        print("Victoire de l'attaquant ({} survivants, {} humains convertis)".format(0, 0))

                # cas victoire non sure
                else:
                    # Victoire de l'attaquant ?
                    if self.debug_mode:
                        print("Probabilité de victoire : {:.2f}% ({} humains vs {} attaquants)".format(
                            Map.proba_p(n_att, n_hum), n_hum, n_att))
                    # Victoire des monstres

                    n_surv = round(n_hum * (1-self.proba_p(n_att,n_hum)) ) # Nombre d'humain survivant
                    # Enregistrement des humains survivants sur la carte
                    self.simple_update_content(
                        x, y, 
                        n_surv, 0, 0,
                        n_hum, n_vamp, n_lg)
                    if self.debug_mode:
                        print("Défaite de l'attaquant ({} humains survivants)".format(n_surv))

            ###################### Bataille Vampires vs Loups-Garous ########################

            else:
                if self.debug_mode:
                    print("Bataille entres monstres en ({},{})".format(x, y))

                n_def = n_lg if is_vamp else n_vamp  # Nombre de défenseurs

                # Victoire sure
                if n_def < n_att:
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} attaquants vs {} défenseurs".format(n_att, n_def))

                    n_surv =round(n_att*self.proba_p(n_att,n_def))  # Nombre d'attaquants survivants

                    # Enregistrement des attaquants survivants
                    self.simple_update_content(
                        x, y, 
                        0, is_vamp * n_surv, (not is_vamp) * n_surv,
                        n_hum, n_vamp, n_lg)

                    if self.debug_mode:
                        print("Victoire de l'attaquant ! {} survivants".format(n_surv))

                # Victoire non sure
                else:
                    # Victoire de l'attaquant
                    if self.debug_mode:
                        print("Probabilité de victoire : {:.2f}% ({} défenseurs vs {} attaquants)".format(
                            Map.proba_p(n_att, n_def), n_def, n_att))

                    # Victoire du défenseur
                    n_surv = round(n_def - (1-self.proba_p(n_att,n_def)))  # Nombre de défenseur survivant
                    # Enregistrement sur la carte
                    self.simple_update_content(
                        x, y, 
                        0, (not is_vamp) * n_surv, is_vamp * n_surv,
                        n_hum, n_vamp, n_lg)

                    if self.debug_mode:
                        print("Défaite de l'attaquant ({} défenseurs survivants)".format(n_surv))

    def compute_moves(self, moves):
        """
        Met à jour et traite les déplacements d'un joueur sur la carte
        :param moves: liste de quintuplets de la forme (i,j,n,x,y) pour un déplacement de n individus en (i,j) vers (x,y)
        :return: None
        """
        # Mise à zéro de la liste des modifications de la carte
        self.UPD = []
        # On enregistre la carte actuelle pour la comparer avec sa version à jour
        old_map_content = dict(self.content)

        # Race du joueur
        is_vamp = True if self.content[(moves[0][0], moves[0][1])][1] else False

        # Emplacement des batailles, avec le nombre de représentants de notre espèce à cet endroit
        battles_to_run = defaultdict(int)
        for i, j, n, x, y in moves:
            # Libération des cases sources
            if is_vamp:  # le joueur est un vampire
                self.update_content([(i, j, 0,  self.content[(i, j)][1] - n, 0)])
            else:  # le joueur est un loup-garou
                self.update_content([(i, j, 0, 0, self.content[(i, j)][2] - n)])

            # Chargement des cases cibles
            # On enregistre les modifications sur les cases sans bataille
            # Population de la case cible
            n_hum, n_vamp, n_lg = self.content[(x, y)]
            # Si case cible est vide
            if self.content[(x, y)] == (0, 0, 0):
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
            n_hum, n_vamp, n_lg = self.content[(x, y)]  # Populations initiales de la case cible

            ######################## Bataille Humain vs Monstre ##################

            if n_hum:
                if self.debug_mode:
                    print("Bataille contre humains en ({},{})".format(x, y))

                # cas victoire assurée
                if n_hum <= n_att:
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} humains vs {} attaquants".format(n_att, n_hum))
                    n_conv = n_hum  # Nombre d'humains convertis
                    n_surv = n_att  # Nombre de survivants de l'espèce attaquante
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
        for (i, j), (n_hum, n_vamp, n_lg) in self.content.items():  # Parcours de la carte
            if old_map_content[(i, j)] != (n_hum, n_vamp, n_lg):  # Différence avec la vieille carte détectée
                self.UPD.append((i, j, n_hum, n_vamp, n_lg))  # Enregistrement dans la liste UPD


    @staticmethod
    def binomial_coefficient(k, n):
        """ Renvoie la valeur de k parmi n (coefficient binomial)

        :param k: int
        :param n: int
        :return: k parmi n
        """
        if 0 <= k <= n:
            n_prod = 1
            k_prod = 1
            for t in range(1, min(k, n - k) + 1):
                n_prod *= n
                k_prod *= t
                n -= 1
            return n_prod // k_prod
        else:
            return 0

    @staticmethod
    def proba_p(n_att, n_def):
        """ Calcule et renvoie la probabilité P définie dans le sujet du Projet \n\n
 
        :param n_att: nombre d'attaquant \n
        :param n_def: nombre de défenseur \n
        :return: probabilite P (float)
        """
        ratio_att_def = n_att / n_def

        if ratio_att_def < 1:
            return ratio_att_def / 2
        else:
            return min(1, ratio_att_def - 0.5)

    @staticmethod
    def tirage(n_att, n_def):
        """Renvoie un tirage aléatoire de probabilité P

        :param n_att: nombre d'attaquants
        :param n_def: nombre de défenseur
        :return: résultat du tirage de probabilité P (boolean)
        """
        probabilite = Map.proba_p(n_att, n_def)
        if probabilite:  # Si la probabilité est non nulle
            return (random.random() / probabilite) <= 1
        else:  # Si la probabilité est nulle (cas dégénéré, impossible en temps normal)
            return False

    def is_valid_moves(self, moves, is_vamp):
        """Vérifie les mouvements proposés par un joueur. Renvoie Vrai si les mouvements sont corrects, faux sinon.

        :param moves: list liste des mouvements proposés par un joueur
        :param is_vamp: Boolean Vrai si c'est le joueur 1/ Vampire qui propose ses mouvements, Faux sinon
        :return: Boolean
        """
        moves_checked = []  # liste des mouvements vérifiés parmi ceux proposés

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

            n_initial = self.content[(i, j)][1 if is_vamp else 2]
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


    def state_evaluation(self):
        if self.game_over():  # Si la partie est terminée
            if self.winner() is None:  # Match nul
                return 0
            elif self.winner():  # Vampire gagne
                return Map.__N_MONSTER_MAX
            else:  # Loup-garou gagne
                return -1*Map.__N_MONSTER_MAX

        _, n_vamp, n_lg = self.populations

        return n_vamp - n_lg  # Score pour une partie en cours

    def game_over(self):
        """ Renvoie si la partie est terminée

        :return: Vrai si la partie est terminée, faux sinon (boolean)
        """
        _, n_vamp, n_lg = self.populations
        if n_vamp == 0 or n_lg == 0:  # Plus de monstres
            return True
        return False  # Il reste des monstres

    def winner(self):
        """ Renvoie la race de l'espèce gagnante ou None si match nul

        :return: True pour vampires ont gagné, False pour loups-garous ont gagnés, None pour match nul
        """
        _, n_vamp, n_lg = self.populations
        if n_vamp > n_lg:  # Il reste de vampires
            return True
        elif n_lg > n_vamp:  # Il reste des loups-garous
            return False
        else:  # Autant de loups-garous ni de vampires ==> Match Nul
            return None

    def print_map(self):
        """ Affiche la carte et des scores
        :return: None
        """
        RACE = ("H", "V", "W")

        # Carte
        for j in range(self.size[1]):  # Parcours des lignes
            print("_" * (self.size[0] * 5))
            for i in range(self.size[0]):  # Parcours des colonnes
                cell_text = "|" + " " * 4
                if (i, j) in self.content:
                    for pos, n_esp in enumerate(self.content[(i, j)]):
                        if n_esp:  # Effectif d'une espèce
                            if n_esp < 10:
                                cell_text = cell_text.replace(" " * 3, " {}{}".format(n_esp, RACE[pos]))
                            else:
                                cell_text = cell_text.replace(" " * 4, " {}{}".format(n_esp, RACE[pos]))
                print(cell_text, end='')  # Affichage de la cellule
            print("|")
        print("_" * (self.size[0] * 5))

        self.print_score()

    def print_score(self):
        # Score
        n_hum, n_vamp, n_lg = self.populations
        print(
            "Vampires {} | Werewolves {} | Remaining Humans: {}".format(
                n_vamp, n_lg, n_hum))


if __name__ == "__main__":
    carte = Map()
    carte.print_map()
    #print(len(carte.next_possible_moves(True, nb_group_max=1)))

    #print(carte.next_possible_relevant_moves(True, 3))

    # moves = [(0, 1, 1, 1, 1)]
    
    # print(carte.possible_outcomes(moves))
