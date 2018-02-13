from collections import defaultdict
import random
from itertools import combinations, product
from copy import deepcopy
from math import log, pow, floor


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

        N_possible_map_hum = 1  # Le nombre de cartes possibles uniquement avec des humains (1 comme neutre multiplicatif)

        for i, j, n_hum, n_vamp, n_lg in initial_positions:
            sum_human_pop += n_hum
            n_monster_max = max(n_vamp, n_lg, n_monster_max)
            if n_hum:
                N_possible_map_hum *= n_hum

        cls.__N_MONSTER_MAX = n_monster_max + sum_human_pop

        # On calcule le nombre de cartes différentes possibles

        # avec 2 types de joueurs différents avec (n_monster_max+sum_human_pop) effectifs sur cette case
        N_possible_maps = 2 * Map.count_cartes_possibles(n_monster_max + sum_human_pop, x_max * y_max)

        # ... + les cartes possibles grâce aux humains
        N_possible_maps += N_possible_map_hum

        # Nombre de bit sur lequel coder au minimum les positions
        n_bit = floor(log(N_possible_maps) / log(2))
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

    @staticmethod
    def count_cartes_possibles(n_monstres, n_cases):
        """ Renvoie le nombre de répartitions possibles sur une carte de n_cases avec n_monstres

        :param n_monstres: nombre de monstres à répartir
        :param n_cases: nombre de cases sur la carte
        :return: compte de cartes
        """
        dict_res = {}
        for i in range(1, n_monstres + 1):
            dict_res[(i, 1)] = 1
        for j in range(2, n_cases + 1):
            dict_res[(1, j)] = j

        for n_case in range(2, n_cases + 1):
            for n_mons in range(2, n_monstres + 1):
                dict_res[(n_mons, n_case)] = dict_res[(n_mons - 1, n_case)] + dict_res[(n_mons, n_case - 1)]
        sum_cartes = 0
        for n_mons in range(1, n_monstres + 1):
            sum_cartes += dict_res[(n_mons, n_cases)]

        return sum_cartes

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
        void_content = {}
        for i, j in product(range(self.size[0]), range(self.size[1])):
            void_content[(i, j)] = (0, 0, 0)
        self._content = void_content
        self._hash = 0

        if initial_positions == [] and map_size is None:
            initial_positions = [(0, 1, 0, 2, 0), (1, 1, 1, 0, 0),(2, 1, 0, 0, 2)]  # 2 vampire, 1 humain, 2 loup-garou

        # On crée la table de hashage des mouvements et d'autres paramètres sur les effectifs de la carte
        Map.init_map_class(self.size, initial_positions)

        # On ajoute les cases non vides avec update pour bien hasher notre carte
        self.update_positions(initial_positions)

        self.UPD = []  # Liste des changements lors d'un update de la carte
        self.debug_mode = debug_mode

    @property
    def hash(self):
        return self._hash

    @property
    def content(self):
        return self._content

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
        Le quintuplet a pour format (i,j,n_hum, h_vampire, n_loup_garou) avec i,j les coordonnées de la case
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

        :param liste de quintuplets de la forme (i,j,n_hum, h_vampire, n_loup_garou) avec i,j les coordonnées de la case
        :return: None
        """

        Map.init_map_class(self.size, positions)
        self.update_positions(positions)

    def update_positions(self, positions):
        """
        Mise à jour simple de la carte
        :param positions: liste de quintuplets de la forme (i,j,n_hum, h_vampire, n_loup_garou) avec i,j les coordonnées de la case
        n_humain le nombre d'humains, n_vampire le nombre de vampires et n_loup_garou le nombre de loups garous
        :return: None
        """
        for i, j, n_hum, n_vamp, n_lg in positions:
            # On déhash l'ancienne position
            self._hash ^= self.hash_position((i, j, *self.content[(i, j)]))

            # On met à jour la carte
            self.content[(i, j)] = (n_hum, n_vamp, n_lg)

            # On hash la nouvelle position
            self._hash ^= self.hash_position((i, j, *self.content[(i, j)]))

    def __copy__(self, objet):
        t = deepcopy(objet)
        return t

    def next_possible_positions(self, is_vamp):
        """
        Une fonction qui génère toutes les positions possibles à partir d'une carte (8 mouvements pour chaque groupe)

        :return: new_positions : un dictionnaire dont les clefs sont (x_old,y_old) et les valeurs les nouvelles positions possibles
        """

        new_positions = defaultdict(list)

        # On récupère toutes les positions initiales possibles
        if is_vamp:  # Le joueur est un loup-garou
            starting_positions = [x_y for x_y in self.content if self.content[x_y][1] != 0]
        else:  # Le joueur est un loup-garou
            starting_positions = [x_y for x_y in self.content if self.content[x_y][2] != 0]

        x_max, y_max = self.size

        for starting_pos in starting_positions:
            x_old, y_old = starting_pos

            available_positions = [(x_old + i, y_old + j) for i, j in product((-1, 0, 1), repeat=2) \
                                   if (i, j) != (0, 0) \
                                   and 0 <= (x_old + i) < x_max \
                                   and 0 <= (y_old + j) < y_max \
                                   and (x_old + i, y_old + j) not in starting_positions  # Règle 5
                                   ]
            for new_pos in available_positions:
                new_positions[starting_pos].append(new_pos)
        return new_positions

    def next_possible_moves(self, is_vamp):
        """ Renvoie toutes les combinaisons possibles de mouvements possibles par un joueur

        :param is_vamp: race du joueur
        :return: liste des mouvements possibles
        """
        next_possible_positions = self.next_possible_positions(is_vamp)

        group_repartitions = {}  # pour chaque groupe, on regarde la répartition de monstres autour de la case de départ

        for starting_position, next_positions in next_possible_positions.items():

            n_case = len(next_positions)  # Nombre de nouvelles positions possibles

            if is_vamp:
                pop_of_monsters = self.content[starting_position][1]  # Nombre de vampires sur la case
            else:
                pop_of_monsters = self.content[starting_position][2]  # Nombre de loup-garous sur la case

            repartitions = set()  # Ensemble de toutes les répartitions de monstres possibles parmi les cases disponibles

            # Toutes les possibilités de répartitions à pop_of_monstres monstres sur n_case cases
            for repartition in product(range(pop_of_monsters + 1), repeat=n_case):
                if sum(
                        repartition) <= pop_of_monsters:  # Si on a réparti au plus le nombre de mosntres de la case initiale
                    repartitions.add(repartition)

            group_repartitions[starting_position] = repartitions

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
                        # On enregistre ce mouvement pour un groupe de monstre
                        moves.append((*starting_position, n_mons, *new_position))

            next_possible_moves.append(moves)

        # Respect de la règle 1
        while [] in next_possible_moves:
            next_possible_moves.remove([])

        return next_possible_moves

    def state_evaluation(self):

        if self.game_over():  # Si la partie est terminée
            if self.winner() is None:  # Match nul
                return 0
            elif self.winner():  # Vampire gagne
                return Map.__N_MONSTER_MAX
            else:  # Loup-garou gagne
                return - Map.__N_MONSTER_MAX

        n_hum, n_vamp, n_lg = self.populations()

        return n_vamp - n_lg  # Score pour une partie en cours

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

            # On déhash l'ancienne position
            self._hash ^= self.hash_position((i, j, *self.content[(i, j)]))

            if is_vamp:  # le joueur est un vampire
                self.content[(i, j)] = (0, self.content[(i, j)][1] - n, 0)

            else:  # le joueur est un loup-garou
                self.content[(i, j)] = (0, 0, self.content[(i, j)][2] - n)

            # Chargement des cases cibles
            # On enregistre les modifications sur les cases sans bataille
            # Population de la case cible
            n_hum, n_vamp, n_lg = self.content[(x, y)]
            # Si case cible est vide
            if self.content[(x, y)] == (0, 0, 0):
                self.content[(x, y)] = (0, n * is_vamp, n * (not is_vamp))

            # Case vide peuplée d'humains
            if n_hum:
                # On enregistre la bataille
                battles_to_run[(x, y)] += n

            # Case cible peuplée d'ami
            # On peuple ces cases
            if n_vamp and is_vamp:
                self.content[(x, y)] = (0, (n + n_vamp), 0)
            elif n_lg and not is_vamp:
                self.content[(x, y)] = (0, 0, (n + n_lg))

            # Case cible avec des ennemis
            if n_vamp and not is_vamp or n_lg and is_vamp:
                # On enregistre la bataille
                battles_to_run[(x, y)] += n

            # On hash la nouvelle position à jour
            self._hash ^= self.hash_position((x, y, *self.content[(x, y)]))

        # On traite les batailles enregistrées
        for x, y in battles_to_run:
            n_att = battles_to_run[(x, y)]  # Nombre d'attaquants
            n_hum, n_vamp, n_lg = self.content[(x, y)]  # Populations initiales de la case cible

            # On déhash l'ancienne position
            self._hash ^= self.hash_position((x, y, *self.content[(x, y)]))

            ######################## Bataille Humain vs Monstre ##################

            if n_hum:
                if self.debug_mode:
                    print("Bataille contre humains en ({},{})".format(x, y))

                # cas victoire assurée
                if n_hum < n_att:
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} humains vs {} attaquants".format(n_att, n_hum))
                    n_conv = sum(self.tirage(n_att, n_hum) for _ in range(n_hum))  # Nombre d'humains convertis
                    n_surv = sum(
                        self.tirage(n_att, n_hum) for _ in range(n_att))  # Nombre de survivants de l'espèce attaquante
                    # Enregistrement des nouvelles populations sur la carte
                    self.content[(x, y)] = (0, is_vamp * (n_surv + n_conv), (not is_vamp) * (n_surv + n_conv))
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
                        self.content[(x, y)] = (0, is_vamp * (n_surv + n_conv), (not is_vamp) * (n_surv + n_conv))

                        if self.debug_mode:
                            print(
                                "Victoire de l'attaquant ({} survivants, {} humains convertis)".format(n_surv, n_conv))
                    else:  # défaite
                        n_surv = n_hum - sum(
                            self.tirage(n_att, n_hum) for _ in range(n_hum))  # Nombre d'humain survivant
                        # Enregistrement des humains survivants sur la carte
                        self.content[(x, y)] = (n_surv, 0, 0)
                        if self.debug_mode:
                            print("Défaite de l'attaquant ({} humains survivants)".format(n_surv))


            ###################### Bataille Vampires vs Loups-Garous ########################

            else:
                if self.debug_mode:
                    print("Bataille entres monstres en ({},{})".format(x, y))

                n_def = n_lg if is_vamp else n_vamp  # Nombre de défenseurs

                # Victoire sure
                if n_def * 1.5 < n_att:
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} attaquants vs {} défenseurs".format(n_att, n_def))

                    n_surv = sum(self.tirage(n_att, n_def) for _ in range(n_att))  # Nombre d'attaquants survivants

                    # Enregistrement des attaquants survivants
                    self.content[(x, y)] = (0, is_vamp * n_surv, (not is_vamp) * n_surv)

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
                        self.content[(x, y)] = (0, is_vamp * n_surv, (not is_vamp) * n_surv)

                        if self.debug_mode:
                            print("Victoire de l'attaquant ! {} survivants".format(n_surv))

                    # Victoire du défenseur
                    else:
                        n_surv = n_def - sum(
                            self.tirage(n_att, n_def) for _ in range(n_def))  # Nombre de défenseur survivant
                        # Enregistrement sur la carte
                        self.content[(x, y)] = (0, (not is_vamp) * n_surv, is_vamp * n_surv)

                        if self.debug_mode:
                            print("Défaite de l'attaquant ({} défenseurs survivants)".format(n_surv))

            # On hash la nouvelle position à jour
            self._hash ^= self.hash_position((x, y * self.content[(x, y)]))

        # Remplissage de la liste UPD à partir des modifications de la carte
        for (i, j), (n_hum, n_vamp, n_lg) in self.content.items():  # Parcours de la carte
            if old_map_content[(i, j)] != (n_hum, n_vamp, n_lg):  # Différence avec la vieille carte détectée
                self.UPD.append((i, j, n_hum, n_vamp, n_lg))  # Enregistrement dans la liste UPD

    @staticmethod
    def proba_p(n_att, n_def):
        """ Calcule et renvoie la probabilité P définie dans le sujet du Projet

        :param n_att: nombre d'attaquant
        :param n_def: nombre de défenseur
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

    def populations(self):
        """Renvoie les populations des différentes espèces sur la carte

        :return: n_hum, n_vamp, n_lg les populations respectives des humains, vampires et loups-garous
        """
        n_hum, n_vamp, n_lg = 0, 0, 0
        for i_hum, i_vamp, i_lg in self.content.values():
            n_hum += i_hum
            n_vamp += i_vamp
            n_lg += i_lg
        return n_hum, n_vamp, n_lg

    def game_over(self):
        """ Renvoie si la partie est terminée

        :return: Vrai si la partie est terminée, faux sinon (boolean)
        """
        _, n_vamp, n_lg = self.populations()
        if n_vamp == 0 or n_lg == 0:  # Plus de monstres
            return True
        return False  # Il reste des monstres

    def winner(self):
        """ Renvoie la race de l'espèce gagnante ou None si match nul

        :return: True pour vampires ont gagné, False pour loups-garous ont gagnés, None pour match nul
        """
        _, n_vamp, n_lg = self.populations()
        if n_vamp > n_lg:  # Il reste de vampires
            return True
        elif n_lg < n_vamp:  # Il reste des loups-garous
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

        # Score


        n_hum, n_vamp, n_lg = self.populations()
        print(
            "Scores:\t\tVampires {} | {} Werewolves\n\tRemaining Humans: {}".format(
                n_vamp, n_lg, n_hum))


if __name__ == "__main__":
    carte = Map()
    carte.print_map()
    print(carte.hash)
    print(carte.next_possible_moves(is_vamp=True))
    print(carte.next_possible_moves(is_vamp=False))
    carte.update_positions([(0, 1, 0, 3, 0)])
    carte.print_map()
    print(len(carte.next_possible_moves(is_vamp=True)))
