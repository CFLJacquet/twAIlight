from Map import Map
from copy import deepcopy


class SommetDuJeu:
    def __init__(self, is_vamp=None, depth=None, game_map=None):
        self._children = list()
        self._score = None
        self.map = game_map
        self.is_vamp = is_vamp
        self.depth = depth
        self.played_moves = list()

    def __copy__(self, objet):
        t = deepcopy(objet)
        return t

    # MaxValue et MinValue vont devoir utiliser un parcours de graph type DFS
    def MinValue(self):
        if self.map.game_over() or self.depth == 0:
            return self.score
        else:
            children_scores = [child.MaxValue() for child in self.children]
            return min(children_scores)

    def MaxValue(self):
        if self.map.game_over() or self.depth == 0:
            return self.score
        else:
            children_scores = [child.MinValue() for child in self.children]
            return max(children_scores)

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
            dic_moves = self.map.next_possible_moves(self.is_vamp)
            for old_positions in dic_moves:
                # On parcourt la liste des anciennes Positions
                for move in dic_moves[old_positions]:
                    is_vamp = not self.is_vamp

                    # Création du sommet fils
                    new_child_vertice = SommetDuJeu(is_vamp=is_vamp, game_map=self.map.__copy__(self.map), depth=self.depth-1)

                    # On met la partie du sommet fils à jour
                    new_child_vertice.played_moves = self.played_moves + [move]
                    new_child_vertice.map.compute_moves([move])
                    new_child_vertice.depth = self.depth - 1

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
        if self.is_vamp:
            next_child = max(self.children, key=lambda x: x.MinValue())
        else:
            next_child = min(self.children, key=lambda x: x.MaxValue())

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        best_choice = next_child.played_moves[-1]
        return best_choice
