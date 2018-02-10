from Morpion.Map_Morpion import Morpion


class SommetDuJeuMinMaxTransposition:
    __vertices_created = 0
    __transposion_table = {}

    def __init__(self, is_ami=True):
        SommetDuJeuMinMaxTransposition.__vertices_created += 1
        self._children = list()
        self._score = None
        self.map = Morpion()
        self.is_ami = is_ami

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def transposition_table(cls):
        return cls.__transposion_table

    def get_score_tt(self):
        if self.map.hash in SommetDuJeuMinMaxTransposition.__transposion_table:
            return SommetDuJeuMinMaxTransposition.__transposion_table[self.map.hash]
        else:
            return None

    def set_score_tt(self, score):
        SommetDuJeuMinMaxTransposition.__transposion_table[self.map.hash] = score

    @property
    def score(self):
        if self._score is None:
            self._score = self.map.state_evaluation()
        return self._score

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children:
            return self._children
        # Si la liste est vide alors on la recalcule
        else:
            for move in self.map.next_possible_moves():
                next_ami = not self.is_ami

                # Création du sommet fils
                new_child_vertice = SommetDuJeuMinMaxTransposition(next_ami)  # Je dois avoir des fils de la même classe

                # On met la partie du sommet fils à jour
                moves = self.map.previous_moves + [move]
                new_child_vertice.map.add_moves(moves)

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

            return self._children

    # MaxValue et MinValue vont devoir utiliser un parcours de graph type DFS
    def MinValue(self):
        score_from_tt = self.get_score_tt()

        if score_from_tt is not None:
            return score_from_tt

        if self.map.game_over():
            self.set_score_tt(self.score)
            return self.score


        else:
            children_scores = [child.MaxValue() for child in self.children]
            min_value=min(children_scores)
            self.set_score_tt(min_value)
            return min_value

    def MaxValue(self):

        score_from_tt = self.get_score_tt()
        if score_from_tt is not None:
            return score_from_tt

        if self.map.game_over():
            self.set_score_tt(self.score)
            return self.score

        else:
            children_scores = [child.MinValue() for child in self.children]
            max_value=max(children_scores)
            self.set_score_tt(max_value)
            return max_value

    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        C'est la fonction Minimax-Decision du cours 4 s.54.
        On utilise un table de transposition (hashage) pour stocker les scores des plateaux avec un score

        Parcourt le graphe en DFS

        :return: le prochain mouvement
        """

        # On sélectionne le noeud fils selon sa race
        if self.is_ami:
            print([child.MinValue() for child in self.children])
            next_child = max(self.children, key=lambda x: x.MinValue())
        else:
            print([child.MaxValue() for child in self.children])
            next_child = min(self.children, key=lambda x: x.MaxValue())

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.map.previous_moves[-1]


if __name__ == "__main__":

    sommet = SommetDuJeuMinMaxTransposition()

    moves = []
    i=0
    while not sommet.map.game_over() and i<1:
        print(sommet.map)
        print("{} joue".format(sommet.is_ami))

        moves += [sommet.next_move()]

        sommet = SommetDuJeuMinMaxTransposition(is_ami=not sommet.is_ami)
        sommet.map.add_moves(moves)

        i+=1
    print(sommet.map)
    print("Vainqueur : {}".format(sommet.map.winner()))

    print("{} sommets ont été créés pour les besoins de cette simulation.".format(
        SommetDuJeuMinMaxTransposition.nb_vertices_created()))

    print(SommetDuJeuMinMaxTransposition.transposition_table())