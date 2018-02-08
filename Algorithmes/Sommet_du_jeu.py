class SommetDuJeu:
    def __init__(self, is_ami=True):
        self.parent = None
        self._children = list()
        self.alpha = None
        self.beta = None
        self._score = None
        self.etat = Morpion()
        self.is_ami = is_ami

    def __copy__(self, objet):
        t = deepcopy(objet)
        return t

    # MaxValue et MinValue vont devoir utiliser un parcours de graph type DFS
    def MinValue(self):
        if self.etat.game_over():
            return self.score
        else:
            children_scores = [child.MaxValue() for child in self.children]
            return min(children_scores)

    def MaxValue(self):
        if self.etat.game_over():
            return self.score
        else:
            children_scores = [child.MinValue() for child in self.children]
            return max(children_scores)

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
                new_child_vertice = SommetDuJeu(next_ami)

                # On met la partie du sommet fils à jour
                moves = self.etat.previous_moves + [move]
                new_child_vertice.etat.add_moves(moves)

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

            return self._children

    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        C'est la fonction Minimax-Decision du cours 4 s.54

        Parcourt le graphe en DFS

        :return: le prochain mouvement
        """

        # On sélectione le noeud fils selon sa race
        if self.is_ami:
            next_child = max(self.children, key=lambda x: x.MinValue())
        else:
            next_child = min(self.children, key=lambda x: x.MaxValue())

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.etat.previous_moves[-1]
