from Morpion.Map_Morpion import Morpion


class SommetDuJeuAlphaBeta:
    __vertices_created = 0

    def __init__(self, is_ami=True):
        SommetDuJeuAlphaBeta.__vertices_created += 1
        self._children = list()
        self._alpha = None
        self._beta = None
        self._score = None
        self.etat = Morpion()
        self.is_ami = is_ami

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @property
    def score(self):
        if self._score is None:
            self._score = self.etat.state_evaluation()
        return self._score

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children:
            return self._children
        # Si la liste est vide alors on la recalcule
        else:
            for move in self.etat.next_possible_moves():
                next_ami = not self.is_ami

                # Création du sommet fils
                new_child_vertice = SommetDuJeuAlphaBeta(next_ami)  # Je dois avoir des fils de la même classe

                # On met la partie du sommet fils à jour
                moves = self.etat.previous_moves + [move]
                new_child_vertice.etat.add_moves(moves)

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

            return self._children

    @property
    def alpha(self):
        """ Récupère la valeur maximale des bornes inférieures (alpha) des noeuds fils.

        :return: float
        """
        if self.etat.game_over():
            return self.score
        else:
            for move in self.etat.next_possible_moves():

                # Création du sommet fils
                new_child_vertice = SommetDuJeuAlphaBeta(not self.is_ami)  # Je dois avoir des fils de la même classe

                # On met la partie du sommet fils à jour
                moves = self.etat.previous_moves + [move]
                new_child_vertice.etat.add_moves(moves)
                new_child_vertice.alpha = self._alpha

                # On éxécute la méthode lecture de l'attribut alpha sur ce fils
                new_alpha = new_child_vertice.beta

                if self._alpha is None:
                    self._alpha = new_alpha

                if self._beta is not None:
                    if self._beta < new_alpha:
                        self._alpha = new_alpha
                        break  # élagage
                # Choix de l'alpha le plus grand
                if new_alpha > self._alpha:
                    self._alpha = new_alpha

            return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value

    @property
    def beta(self):
        """ Récupère la valeur minimale des bornes supérieures des noeuds fils.

        :return: float
        """
        if self.etat.game_over():
            return self.score
        else:
            for move in self.etat.next_possible_moves():

                # Création du sommet fils
                new_child_vertice = SommetDuJeuAlphaBeta(not self.is_ami)  # Je dois avoir des fils de la même classe

                # On met la partie du sommet fils à jour
                moves = self.etat.previous_moves + [move]
                new_child_vertice.etat.add_moves(moves)
                new_child_vertice.beta = self._beta
                # On éxécute la méthode lecture de l'attribut alpha sur ce fils
                new_beta = new_child_vertice.alpha

                if self._beta is None:
                    self._beta = new_beta

                if self._alpha is not None:
                    if self._alpha > new_beta:
                        self._beta = new_beta
                        break  # élagage

                if new_beta < self._beta:
                    self._beta = new_beta

            return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = value

    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        Algorithme du AlphaBeta (parcours en profondeur)

        :return: le prochain mouvement
        """

        # On sélectionne le noeud fils selon sa race
        if self.is_ami:
            next_child = max(self.children, key=lambda child: child.beta)
        else:
            next_child = min(self.children, key=lambda child: child.alpha)

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.etat.previous_moves[-1]


if __name__ == "__main__":

    sommet = SommetDuJeuAlphaBeta()

    moves = []

    while not sommet.etat.game_over():
        print(sommet.etat)
        print("{} joue".format(sommet.is_ami))

        moves += [sommet.next_move()]

        sommet = SommetDuJeuAlphaBeta(is_ami=not sommet.is_ami)
        sommet.etat.add_moves(moves)

    print(sommet.etat)
    print("Vainqueur : {}".format(sommet.etat.winner()))

    print("{} sommets ont été créés pour les besoins de cette simulation.".format(
        SommetDuJeuAlphaBeta.nb_vertices_created()))
