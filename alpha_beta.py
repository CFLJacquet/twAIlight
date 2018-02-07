from copy import deepcopy

class Morpion:
    """Par défaut, True commence"""

    def __init__(self):
        self.etat = list()

    def whos_turn(self):
        if len(self.etat)%2:
            return False
        else:
            return True

    def add_moves(self, moves):
        for move in moves:
            self.add_move(move)

    def add_move(self, move):

        if len(move) == 3:
            i, j, player = move
        else:
            i, j = move
            player = self.whos_turn()
        self.etat.append((i, j, player))

    def __copy__(self, objet):
        t = deepcopy(objet)
        return t


    def state_evaluation(self,curr_player):
        other_player = not curr_player
        if self.winner()==curr_player:
            return 10000
        elif self.winner()==other_player:
            return -10000
        else:
            op_c = self.open_positions(curr_player)
            op_o = self.open_positions(other_player)
        return op_c - op_o

    def open_positions(self,curr_player):
        count=0
        row_line_blanks=[]
        other_player = not curr_player
        for i in range(3):
            # Quoiqu'il arrive on ajoute toutes les lignes blanches ou colonnes blanche
            if i not in [k[0] for k in self.etat]:
                count=count+1
            if i not in [k[1] for k in self.etat]:
                count=count+1
            # On parcourt ensuite les état qui pourraient donner lieu à une victoire
        for i in self.etat:
            # si une ligne n'est occupée que par nos pions, c'est une victoire potentielle
            if i[0] not in [k[0] for k in self.etat if k!=i and k[2]==other_player]:
                count=count+1
            # Si une colonne n'est occupée que par nos pions c'est aussi une victoire potentielle
            if i[1] not in [k[1] for k in self.etat if k!=i and k[2]==other_player]:
                count=count+1

        # Cas particulier des diagonales
        if (1,1,other_player) in self.etat:
            # Si l'autre n'occupe pas le centre (donc soit nous l'occupons, soit il est vide), on regarde qui occupe les coins
            if other_player not in [k[2] for k in self.etat if k[0:2]==(0,1) or k[0:2]==(0,2) or k[0:2]==(2,0) or k[0:2]==(2,2)]:
                count=count+1

        return count

    def winner(self):
        for i in range(3):
            if (i, 0, True) in self.etat:
                current_player = True
            elif (i, 0, False) in self.etat:
                current_player = False
            else:
                break
            if (i, 1, current_player) in self.etat and (i, 2, current_player) in self.etat:
                return current_player

        for j in range(3):
            if (0, j, True) in self.etat:
                current_player = True
            elif (0, j, False) in self.etat:
                current_player = False
            else:
                break
            if (1, j, current_player) in self.etat and (2, j, current_player) in self.etat:
                return current_player

        if (1, 1, True) in self.etat:
            current_player = True
        elif (1, 1, False) in self.etat:
            current_player = False
        else:
            return None
        if (0, 0, current_player) in self.etat and (2, 2, current_player) in self.etat:
            return current_player
        if (2, 0, current_player) in self.etat and (0, 2, current_player) in self.etat:
            return current_player

        return None

    def next_possible_moves(self):
        possible_moves = set((i, j) for i in range(3) for j in range(3))
        possible_moves -= set((i, j) for i, j, _ in self.etat)
        next_player = self.whos_turn()
        return set((i, j, next_player) for (i, j) in possible_moves)

    def game_over(self):
        for i in range(3):
            if (i, 0, True) in self.etat:
                current_player = True
            elif (i, 0, False) in self.etat:
                current_player = False
            else:
                break
            if (i, 1, current_player) in self.etat and (i, 2, current_player) in self.etat:
                return True

        for j in range(3):
            if (0, j, True) in self.etat:
                current_player = True
            elif (0, j, False) in self.etat:
                current_player = False
            else:
                break
            if (1, j, current_player) in self.etat and (2, j, current_player) in self.etat:
                return True

        if (1, 1, True) in self.etat:
            current_player = True
        elif (1, 1, False) in self.etat:
            current_player = False
        else:
            return False
        if (0, 0, current_player) in self.etat and (2, 2, current_player) in self.etat:
            return True
        if (2, 0, current_player) in self.etat and (0, 2, current_player) in self.etat:
            return True

        return False

    def __repr__(self):
        res = "-------\n"
        for j in range(3):
            for i in range(3):
                res+='|'
                if (i, j, True) in self.etat:
                    res += "X"
                elif (i, j, False) in self.etat:
                    res += "O"
                else:
                    res += " "
            res += '|\n-------\n'
        return res


class GrapheDeJeu:
    def __init__(self):
        self.noeuds = []

    def add_vertice(self, vertice):
        if isinstance(vertice, SommetDuJeu):
            self.noeuds.append(vertice)

    def add_vertices(self, vertices):
        for vert in vertices:
            self.add_vertice(vert)


class SommetDuJeu:
    def __init__(self, is_ami):
        self.children = list()
        self.alpha = None
        self.beta = None
        self.etat = Morpion()
        self.is_ami = is_ami

    def __copy__(self, objet):
        t = deepcopy(objet)
        return t

    def MinValue(self):
        pass

    def MaxValue(self):
        self.max_val=-10
        for possibility in self.children:
            val = possibility.etat.state_evaluation(self.is_ami)
            if val > self.max_val:
                self.max_val=val
                self.best_scenario = possibility.etat.etat[-1]




def alpha_beta_morpion(morpion_state,is_ami):
    """
    cette fonction doit retourner le meilleur mouvement étant donné un état du jeu à horizon 1

    """
    graphe_du_jeu=GrapheDeJeu()
    cur_vertice=SommetDuJeu(is_ami)
    cur_vertice.etat=cur_vertice.etat.__copy__(morpion_state)


    graphe_du_jeu.add_vertice(cur_vertice)

    is_ami=not is_ami
    i=0
    child_vertice={}
    for move in cur_vertice.etat.next_possible_moves():
        # La copy d'une classe en python se fait :
        child_vertice[i]=SommetDuJeu(is_ami)
        child_vertice[i]=child_vertice[i].__copy__(cur_vertice)

        child_vertice[i].etat.add_move(move)

        cur_vertice.children.append(child_vertice[i])
        graphe_du_jeu.add_vertice(child_vertice[i])
        i=i+1

    #print(cur_vertice.children[1].etat)

    cur_vertice.MaxValue()
    return cur_vertice.best_scenario



if __name__ == "__main__":
    morpion = Morpion()
    print(morpion.game_over())
    print(morpion.next_possible_moves())
    morpion.add_moves([(0, 1),(1,0)])
    print(morpion)
    best_next_move = alpha_beta_morpion(morpion,False)
    morpion.add_move(best_next_move)
    print(morpion)

    #print(morpion.game_over())
    #print(morpion.winner())
