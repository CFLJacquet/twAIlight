class Morpion:
    """
    Equivalent de la classe Map sur le jeu des Vampires vs Loups-garous.

    Les joueurs sont soit True soit False.

    Par défaut, True commence"""

    def __init__(self):
        self.previous_moves = list()  # contenu du plateau, dans l'ordre dans lequel les pions sont joués

    def whos_turn(self):
        """ Renvoie le joueur qui a la main.

        :return: boolean: nom du joueur
        """
        if len(self.previous_moves) % 2:
            return False
        else:
            return True

    def add_moves(self, moves):
        """ Rajoute une liste de mouvements au jeu Morpion

        :param moves: liste de mouvements
        :return: None
        """
        for move in moves:
            self.add_move(move)

    def add_move(self, move):
        """ Rajoute un mouvement à la carte.
        :param move: (i,j,player) avec i,j coordonnées et player le nom du joueur
        :return : None
        """

        if len(move) == 3:
            i, j, player = move
        else:
            i, j = move
            player = self.whos_turn()

        self.previous_moves.append((i, j, player))

    def state_evaluation(self):
        """ Renvoie l'évaluation d'une carte Morpion pour le joueur actuel

        :param curr_player: race du joueur actuel (boolean)
        :return: score de l'évaluation
        """

        # Cas victoire
        if self.winner():
            return 10

        # Cas défaite
        elif self.winner() == False:
            return -10

        # Cas Partie en cours
        else:
            op_c = self.open_positions(True)
            op_o = self.open_positions(False)
        return op_o - op_c

    def open_positions(self, player):
        count = 0
        other_player = not player

        for i in range(3):
            # Quoiqu'il arrive on ajoute toutes les lignes blanches ou colonnes blanche
            if i not in [k[0] for k in self.previous_moves]:
                count = count + 1
            if i not in [k[1] for k in self.previous_moves]:
                count = count + 1
                # On parcourt ensuite les état qui pourraient donner lieu à une victoire

        # print("Je ne garde que mes états")
        # print([state for state in self.etat if state[2]!=other_player])
        for i in [state for state in self.previous_moves if state[2] != other_player]:
            # si une ligne n'est occupée que par nos pions, c'est une victoire potentielle
            # print([k[0] for k in self.etat if k!=i and k[2]==other_player])
            if i[0] not in [k[0] for k in self.previous_moves if k != i and k[2] == other_player]:
                count = count + 1
            # Si une colonne n'est occupée que par nos pions c'est aussi une victoire potentielle
            if i[1] not in [k[1] for k in self.previous_moves if k != i and k[2] == other_player]:
                count = count + 1

        # Cas particulier des diagonales
        # On vérifie la non présence d'une case détenue par l'ennemi sur chacune des diagonales

        # Diagonale descendante
        if not ((1, 1, other_player) in self.previous_moves or (0, 0, other_player) in self.previous_moves or (
                2, 2, other_player) in self.previous_moves):
            count += 1

        # Diagonale montante
        if not ((1, 1, other_player) in self.previous_moves or (2, 0, other_player) in self.previous_moves or (
                0, 2, other_player) in self.previous_moves):
            count += 1

        return count

    def winner(self):
        """ Renvoie la race du joueur gagnant

        :return: True, False ou None si Partie encore en cours
        """

        # Parcours de la première ligne pour observer les colonnes
        for i in range(3):

            # Pour la ligne i, on cherche le joueur qui l'occupe
            if (i, 0, True) in self.previous_moves:
                current_player = True
            elif (i, 0, False) in self.previous_moves:
                current_player = False
            else:
                break

            # On regarde les deux autres éléments de la colonne pour vérifier si elle est occupée par le même joueur
            if (i, 1, current_player) in self.previous_moves and (i, 2, current_player) in self.previous_moves:
                return current_player

        # Parcours de la première colonne pour observer les lignes
        for j in range(3):

            # Pour la colonne j, on cherche le joueur qui l'occupe
            if (0, j, True) in self.previous_moves:
                current_player = True
            elif (0, j, False) in self.previous_moves:
                current_player = False
            else:
                break

            # On regarde les deux autres éléments de la ligne pour vérifier si elle est occupée par le même joueur
            if (1, j, current_player) in self.previous_moves and (2, j, current_player) in self.previous_moves:
                return current_player

        # Cas des diagonales

        # Joueur pouvant avoir une diagonale
        if (1, 1, True) in self.previous_moves:
            current_player = True
        elif (1, 1, False) in self.previous_moves:
            current_player = False
        else:
            return None

        # Parcours des deux diagonales avec l'information du joueur qui a le centre
        if (0, 0, current_player) in self.previous_moves and (2, 2, current_player) in self.previous_moves:
            return current_player
        if (2, 0, current_player) in self.previous_moves and (0, 2, current_player) in self.previous_moves:
            return current_player

        return None

    def next_possible_moves(self):
        """ Renvoie l'ensemble des positions possibles sur la carte pour un prochain mouvement.
        Pas besoin de préciser le joueur qui va jouer !

        :return: set
        """
        # Toutes les cases de la carte...
        possible_moves = set((i, j) for i in range(3) for j in range(3))

        # Auxquelles on supprime les cases déjà occupées
        possible_moves -= set((i, j) for i, j, _ in self.previous_moves)

        # Race du joueur qui va jouer
        next_player = self.whos_turn()

        return set((i, j, next_player) for (i, j) in possible_moves)

    def game_over(self):
        """ Renvoie Vrai si le jeu est terminé, Faux sinon

        :return: boolean
        """

        # Parcours des colonnes

        # Sélection du potentiel vainqueur avec le parcours de la première ligne
        for i in range(3):
            if (i, 0, True) in self.previous_moves:
                current_player = True
            elif (i, 0, False) in self.previous_moves:
                current_player = False
            else:
                break
            # Parcours de la colonne
            if (i, 1, current_player) in self.previous_moves and (i, 2, current_player) in self.previous_moves:
                return True

        # Idem avec les lignes en parcourant la première colonne
        for j in range(3):
            if (0, j, True) in self.previous_moves:
                current_player = True
            elif (0, j, False) in self.previous_moves:
                current_player = False
            else:
                break
            if (1, j, current_player) in self.previous_moves and (2, j, current_player) in self.previous_moves:
                return True

        # Cas des diagonales

        # Qui controle le centre ?
        if (1, 1, True) in self.previous_moves:
            current_player = True
        elif (1, 1, False) in self.previous_moves:
            current_player = False
        else:
            return False  # Partie non terminée

        # Le joueur occupant le centre, détient la diagonale descendante ?
        if (0, 0, current_player) in self.previous_moves and (2, 2, current_player) in self.previous_moves:
            return True

        # Le joueur occupant le centre, détient la diagonale montante ?
        if (2, 0, current_player) in self.previous_moves and (0, 2, current_player) in self.previous_moves:
            return True

        # Si la grille est complète
        if len(self.previous_moves) == 9:
            return True

        return False

    def __repr__(self):
        """ Représente le plateau du Morpion

        :return:
        """
        res = "-------\n"
        for j in range(3):
            for i in range(3):
                res += '|'
                if (i, j, True) in self.previous_moves:
                    res += "X"
                elif (i, j, False) in self.previous_moves:
                    res += "O"
                else:
                    res += " "
            res += '|\n-------\n'
        return res
