from Morpion.Sommet_du_Jeu import SommetDuJeu


class NegaMaxAstar(SommetDuJeu):
    __vertices_created = 0
    __transposion_table = {}

    def __init__(self, is_vamp=True):
        super().__init__(is_vamp)
        NegaMaxAstar.__vertices_created += 1

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def transposition_table(cls):
        return cls.__transposion_table

    def get_transposition_table(self):
        if self.map.hash in NegaMaxAstar.__transposion_table:
            return NegaMaxAstar.__transposion_table[self.map.hash]
        else:
            return None, None, None

    def set_transposition_table(self, flag, value, depth):
        NegaMaxAstar.__transposion_table[self.map.hash] = (flag, value, depth)

    @property
    def children(self):

        children = super().children
        if self.is_vamp:
            # Pour les besoins du max des alphas, on ordonne la liste avec les noeuds les plus forts d'abord
            self._children = sorted(children, key=lambda child: child.evaluation)
        else:
            # Pour les besoins du mix des alphas, on ordonne la liste avec les noeuds les pluus faible
            self._children = sorted(children, key=lambda child: -child.evaluation)
        return self._children

    def negamax(self, depth, alpha, beta):
        alphaOrig = alpha
        color = 1 if self.is_vamp else -1

        flag, value, depth_tt = self.get_transposition_table()

        if flag is not None:

            if depth_tt >= depth:
                if flag == "exact":
                    return value
                elif flag == "lowerbound":
                    if alpha is not None:
                        if value > alpha:
                            alpha = value
                    else:
                        alpha = value
                elif flag == "upperbound":
                    if beta is not None:
                        if value < beta:
                            beta = value
                    else:
                        beta = value
                if alpha is not None and beta is not None:
                    if alpha >= beta:
                        return value

        if self.map.game_over() or depth == 0:
            # self.set_score_tt(self.score)
            return color * self.score
        bestvalue = None
        for child in self.children:
            if alpha is None and beta is None:
                v = - child.negamax(depth - 1, None, None)
            elif beta is None:
                v = - child.negamax(depth - 1, None, -alpha)
            elif alpha is None:
                v = - child.negamax(depth - 1, -beta, None)
            else:
                v = - child.negamax(depth - 1, -beta, -alpha)

            if bestvalue is None:
                bestvalue = v
            elif bestvalue < v:
                bestvalue = v

            if alpha is None:
                alpha = v
            elif alpha < v:
                alpha = v

            if beta is not None:
                if alpha >= beta:
                    break

        flag = None
        if alphaOrig is not None:
            if bestvalue <= alphaOrig:
                flag = "upperbound"
        if beta is not None:
            if bestvalue >= beta:
                flag = "lowerbound"
        if flag is None:
            flag = "exact"

        self.set_transposition_table(flag, bestvalue, depth)

        return bestvalue


    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        Algorithme du AlphaBeta (parcours en profondeur)

        :return: le prochain mouvement
        """

        # On sélectionne le noeud fils
        next_child = min(self.children,
                         key=lambda child: child.negamax(depth=10, alpha=None, beta=None))

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.map.previous_moves[-1]


if __name__ == "__main__":
    NegaMaxAstar.game_on()
