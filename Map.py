from collections import defaultdict
import random
from itertools import combinations


class Map:
    """
    Carte du jeu

    Par défaut : The Trap
    __________________________________________________
    |    |    |    |    |    |    |    |    |    | 2H |
    __________________________________________________
    |    |    |    |    | 4W |    |    |    |    |    |
    __________________________________________________
    |    |    | 4H |    |    |    |    |    |    | 1H |
    __________________________________________________
    |    |    |    |    | 4V |    |    |    |    |    |
    __________________________________________________
    |    |    |    |    |    |    |    |    |    | 2H |
    __________________________________________________
    """

    def __init__(self, map_size=None, map_content=None, debug_mode=False):
        """
        Initialise la carte
        :param map_size: dimensions de la carte
        :param map_content: Contenu de la carte format dict[(i,j)]=(nombre_humains, nombre_vampires, nombre_loup-garous)
        :param debug_mode: mode debug (boolean)
        """
        # Par Défaut Carte The Trap
        if map_size is None:
            map_size = (10, 5)
        self.size = map_size
        if map_content is None:
            map_content = {(0, 0): (0, 0, 0), (0, 1): (0, 0, 0), (0, 2): (0, 0, 0), (0, 3): (0, 0, 0),
                           (0, 4): (0, 0, 0), (1, 0): (0, 0, 0), (1, 1): (0, 0, 0), (1, 2): (0, 0, 0),
                           (1, 3): (0, 0, 0), (1, 4): (0, 0, 0), (2, 0): (0, 0, 0), (2, 1): (0, 0, 0),
                           (2, 2): (4, 0, 0), (2, 3): (0, 0, 0), (2, 4): (0, 0, 0), (3, 0): (0, 0, 0),
                           (3, 1): (0, 0, 0), (3, 2): (0, 0, 0), (3, 3): (0, 0, 0), (3, 4): (0, 0, 0),
                           (4, 0): (0, 0, 0), (4, 1): (0, 0, 4), (4, 2): (0, 0, 0), (4, 3): (0, 4, 0),
                           (4, 4): (0, 0, 0), (5, 0): (0, 0, 0), (5, 1): (0, 0, 0), (5, 2): (0, 0, 0),
                           (5, 3): (0, 0, 0), (5, 4): (0, 0, 0), (6, 0): (0, 0, 0), (6, 1): (0, 0, 0),
                           (6, 2): (0, 0, 0), (6, 3): (0, 0, 0), (6, 4): (0, 0, 0), (7, 0): (0, 0, 0),
                           (7, 1): (0, 0, 0), (7, 2): (0, 0, 0), (7, 3): (0, 0, 0), (7, 4): (0, 0, 0),
                           (8, 0): (0, 0, 0), (8, 1): (0, 0, 0), (8, 2): (0, 0, 0), (8, 3): (0, 0, 0),
                           (8, 4): (0, 0, 0), (9, 0): (2, 0, 0), (9, 1): (0, 0, 0), (9, 2): (1, 0, 0),
                           (9, 3): (0, 0, 0), (9, 4): (2, 0, 0)}
        self.content = map_content
        self.UPD = []  # Liste des changements lors d'un update de la carte
        self.debug_mode = debug_mode

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

    def update(self, positions):
        """
        Mise à jour simple de la carte
        :param positions: liste de quintuplets de la forme (i,j,n_hum, h_vampire, n_loup_garou) avec i,j les coordonnées de la case
        n_humain le nombre d'humains, n_vampire le nombre de vampires et n_loup_garou le nombre de loups garous
        :return: None
        """
        for i, j, n_hum, n_vamp, n_lg in positions:
            self.content[(i, j)] = (n_hum, n_vamp, n_lg)


    def next_possible_moves(self):
        """
        Une fonction qi génère automatiquement tous les états potentiels du tour n+1

        """
        possible_moves=[]


        return possible_moves


    def state_evaluation(self):
        """
        Une fonction qui évalue la qualité des états

        """
        evaluation=0


        return evaluation



    def update_and_compute(self, moves):
        """
        Met à jour et traite les déplacements d'un joueur sur la carte
        :param moves: liste de quintuplets de la forme (i,j,n_hum, h_vampire, n_loup_garou) avec i,j les coordonnées de la case
        n_humain le nombre d'humains, n_vampire le nombre de vampires et n_loup_garou le nombre de loups garous
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
        if n_vamp:  # Il reste de vampires
            return True
        elif n_lg:  # Il reste des loups-garous
            return False
        else:  # Plus de loups-garous ni de vampires ==> Match Nul
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
                            if n_esp <10:
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
    carte.update_and_compute([(4, 1, 3, 3, 2), (4, 1, 1, 3, 2)])
    carte.print_map()
