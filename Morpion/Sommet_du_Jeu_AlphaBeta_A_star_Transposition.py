from Morpion.Map_Morpion import Morpion


class SommetDuJeuAlphaBetaAstarTransposition:
    """ Graphe de jeu proche du AlphaBeta
    On ordonne les noeuds qui sont visités pour commencer par les plus prometteurs
    (avec la fonction d'évaluation de la carte)
    On réduit le nombre de sommets créés de -34%,
    mais cela coute +44% en temps de calcul (heuristique d'évaluation est chère)
    On peut s'attendre à de meilleurs résultats sur le jeu des vampires vs loup-garous,
    car il existe des heuristiques assez simples.
    """
    __vertices_created = 0
    __transposion_table = {}
    def __init__(self, is_ami=True):
        SommetDuJeuAlphaBetaAstarTransposition.__vertices_created += 1
        self._children = list()
        self._alpha = None
        self._beta = None
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
        if self.map.hash in SommetDuJeuAlphaBetaAstarTransposition.__transposion_table:
            return SommetDuJeuAlphaBetaAstarTransposition.__transposion_table[self.map.hash]
        else:
            return None

    def set_score_tt(self, score):
        SommetDuJeuAlphaBetaAstarTransposition.__transposion_table[self.map.hash] = score

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
                new_child_vertice = SommetDuJeuAlphaBetaAstarTransposition(next_ami)  # Je dois avoir des fils de la même classe

                # On met la partie du sommet fils à jour
                moves = self.map.previous_moves + [move]
                new_child_vertice.map.add_moves(moves)

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)


            if self.is_ami:
                # Pour les besoins du max des alphas, on ordonne la liste avec les noeuds les plus forts d'abord
                self._children=sorted(self._children, key=lambda child: child.score)
            else:
                # Pour les besoins du mix des alphas, on ordonne la liste avec les noeuds les pluus faible
                self._children=sorted(self._children, key=lambda child: -child.score)
            return self._children

    @property
    def alpha(self):
        """ Récupère la valeur maximale des bornes inférieures (alpha) des noeuds fils.

        :return: float
        """
        score_from_tt = self.get_score_tt()

        if score_from_tt is not None:
            return score_from_tt

        if self.map.game_over():
            return self.score
        else:
            for child in self.children:

                child.alpha = self._alpha

                # On éxécute la méthode lecture de l'attribut alpha sur ce fils
                new_alpha = child.beta

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
        score_from_tt = self.get_score_tt()

        if score_from_tt is not None:
            return score_from_tt

        if self.map.game_over():
            return self.score
        else:
            for child in self.children:

                child.beta = self._beta
                # On éxécute la méthode lecture de l'attribut alpha sur ce fils
                new_beta = child.alpha

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
        return next_child.map.previous_moves[-1]


if __name__ == "__main__":

    sommet = SommetDuJeuAlphaBetaAstarTransposition()

    moves = []

    while not sommet.map.game_over():
        print(sommet.map)
        print("{} joue".format(sommet.is_ami))

        moves += [sommet.next_move()]

        sommet = SommetDuJeuAlphaBetaAstarTransposition(is_ami=not sommet.is_ami)
        sommet.map.add_moves(moves)

    print(sommet.map)
    print("Vainqueur : {}".format(sommet.map.winner()))

    print("{} sommets ont été créés pour les besoins de cette simulation.".format(
        SommetDuJeuAlphaBetaAstarTransposition.nb_vertices_created()))
