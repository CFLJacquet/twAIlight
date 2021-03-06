from Map import Map
from copy import deepcopy

from Algorithmes.Sommet_du_jeu import SommetOutcome, SommetChance


class SommetChance_NegaMax_Oriente(SommetChance):
    __vertices_created = 0

    def __init__(self, is_vamp=None, depth=None, game_map=None):
        super().__init__(is_vamp, depth, game_map)
        SommetChance_NegaMax_Oriente.__vertices_created += 1

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @property
    def children(self):
        if self._children is None:
            self._children = list()
            for proba, positions in self.map.possible_outcomes(self.previous_moves):
                # Création du sommet fils
                carte=deepcopy(self.map)
                new_child_vertice = SommetDuJeu_NegaMax_Oriente(
                    is_vamp=self.is_vamp, 
                    game_map=carte,
                    depth=self.depth)

                # On met la partie du sommet fils à jour
                new_child_vertice.previous_moves = self.previous_moves
                new_child_vertice.map.update_content(positions)
                new_child_vertice.probability = proba

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

        return self._children

    def negamax(self, alpha, beta):
        sum_expected = 0
        for child in self.children:
            sum_expected += child.negamax(alpha, beta) * child.probability
        return sum_expected


class SommetDuJeu_NegaMax_Oriente(SommetOutcome):
    __vertices_created = 0
    __transposion_table = {}

    def __init__(self, is_vamp=None, depth=None, game_map=None, init_map=False):
        super().__init__(is_vamp, depth, game_map, init_map)
        SommetDuJeu_NegaMax_Oriente.__vertices_created += 1
        if init_map:
            SommetDuJeu_NegaMax_Oriente.__transposion_table = {}

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def transposition_table(cls):
        return cls.__transposion_table

    def get_score(self):
        if self.map.hash in SommetDuJeu_NegaMax_Oriente.__transposion_table:
            return SommetDuJeu_NegaMax_Oriente.__transposion_table[self.map.hash]
        else:
            return None, None, None

    def set_score_tt(self, flag, depth, score):
        SommetDuJeu_NegaMax_Oriente.__transposion_table[self.map.hash] = (flag, depth, score)

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children is None:
            self._children = list()
            for moves in self.map.i_next_possible_moves(self.is_vamp):
                child = SommetChance_NegaMax_Oriente(is_vamp=not self.is_vamp, depth=self.depth - 1, game_map=self.map)
                child.previous_moves = moves
                self._children.append(child)
            self._children.sort(key=lambda x: x.evaluation, reverse=self.is_vamp)
        return self._children

    def negamax(self, alpha, beta):
        alphaOrig = alpha
        color = 1 if self.is_vamp else -1
        flag, depth, score = self.get_score()

        if flag is not None:

            if depth >= self.depth:
                if flag == "exact":
                    return score
                elif flag == "lowerbound":
                    if alpha is not None:
                        if score > alpha:
                            alpha = score
                    else:
                        alpha = score
                elif flag == "upperbound":
                    if beta is not None:
                        if score < beta:
                            beta = score
                    else:
                        beta = score
                if alpha is not None and beta is not None:
                    if alpha >= beta:
                        return score

        if self.map.game_over() or self.depth == 0:
            return color * self.evaluation

        bestvalue = None
        for child in self.children:
            if alpha is None and beta is None:
                v = - child.negamax(None, None)
            elif beta is None:
                v = - child.negamax(None, -1*alpha)
            elif alpha is None:
                v = - child.negamax(-1*beta, None)
            else:
                v = - child.negamax(-1*beta, -1*alpha)

            # On prend le max entre bestvalue et v
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

        self.set_score_tt(flag, self.depth, bestvalue)

        return bestvalue

    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        C'est la fonction Minimax-Decision du cours 4 s.54

        Parcourt le graphe en DFS

        :return: le prochain mouvement
        """
        # On sélectione le noeud fils selon sa race
        next_child = min(self.children,
                         key=lambda child: child.negamax(alpha=None, beta=None))

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.previous_moves


if __name__ == '__main__':
    carte = Map()
