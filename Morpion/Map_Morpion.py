import random
import math

class Morpion:
    """
    Equivalent de la classe Map sur le jeu des Vampires vs Loups-garous.

    Les joueurs sont soit True soit False.

    Par défaut, True commence"""
    __HASH_TABLE = None

    def __init__(self):
        self.previous_moves = list()  # contenu du plateau, dans l'ordre dans lequel les pions sont joués
        if Morpion.__HASH_TABLE is None:
            Morpion.init_hash_table()
        self._hash=0

    @classmethod
    def init_hash_table(cls):
        """ Méthode de hashage d'un élément de la carte en s'inspirant du hashage de Zobrist.
        https://en.wikipedia.org/wiki/Zobrist_hashing

        :return:
        """
        table = {}
        x_max = 3 # Nombre de colonnes
        y_max = 3 # Nombre de lignes
        n_race =2 # Nombre de type de pions
        N_max=1 # Effectif maximal d'une case

        # On calcule le nombre de cartes différentes possibles
        N_cartes_possible=1*1 # case vide avec une population possibles
        N_cartes_possible+=n_race*N
        n_bit = math.floor(math.log(((n_race+1)*N_max)**(x_max*y_max))/math.log(2))# Nombre de bit sur lequel coder au minimum les positions
        m_bit =5 # Marge sur la taille de l'entier pour éviter les collisions

        nombre_max_hashage = math.pow(2,n_bit+m_bit)
        for i in range(x_max):
            table[i] = {}
            for j in range(y_max):
                table[i][j] = {1: random.randint(0, nombre_max_hashage),
                               0: random.randint(0, nombre_max_hashage)
                               }
        Morpion.__HASH_TABLE = table

    @staticmethod
    def hash_move(move):
        i,j,race=move
        return Morpion.__HASH_TABLE[i][j][race]

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
        self._hash^=Morpion.__HASH_TABLE[i][j][player]

    def state_evaluation(self):
        """ Renvoie l'évaluation d'une carte Morpion pour le joueur actuel

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
        # print([state for state in self.map if state[2]!=other_player])
        for i in [state for state in self.previous_moves if state[2] != other_player]:
            # si une ligne n'est occupée que par nos pions, c'est une victoire potentielle
            # print([k[0] for k in self.map if k!=i and k[2]==other_player])
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

    @property
    def hash(self):
        return self._hash

    def __repr__(self):
        """ Représente le plateau du Morpion

        :return:
        """
        res = "\n-------\n"
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


if __name__ == "__main__":
    a = Morpion()
    a.add_move((1,1,True))
    a.add_move((1,2,False))
    print(a.hash)
    print(a.hash_move((1,1,True))^a.hash_move((1,2,False)))

    # Test collision
    table={}
    morpion=Morpion()
    table[morpion.hash]=morpion
    to_visit=[(morpion, morpion.next_possible_moves())]
    count=1
    different_set=set()
    different_set.add(morpion.__repr__())
    while to_visit:
        carte, next_moves=to_visit.pop()
        for next_move in next_moves:
            next_carte = Morpion()
            moves=carte.previous_moves+[next_move]
            next_carte.add_moves(moves)
            if next_carte.hash in table:
                if table[next_carte.hash].__repr__() != next_carte.__repr__():
                    print("collisions !")
                    print(table[next_carte.hash])
                    print(next_carte)
            table[next_carte.hash]=next_carte
            count+=1
            different_set.add(next_carte.__repr__())
            if next_carte.next_possible_moves():
                to_visit.append((next_carte, next_carte.next_possible_moves()))
    print(count)
    print(len(different_set))

