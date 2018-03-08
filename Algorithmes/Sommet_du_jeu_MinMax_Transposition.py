from copy import deepcopy

from twAIlight.Map import Map
from twAIlight.Algorithmes.Sommet_du_jeu import SommetOutcome, SommetChance


class SommetChance_MinMax(SommetChance):
    __vertices_created = 0

    def __init__(self, is_vamp=None, depth=None, game_map=None):
        super().__init__(is_vamp, depth, game_map)
        SommetChance_MinMax.__vertices_created += 1

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    def MaxValue(self):
        sum_expected = 0
        for child in self.children:
            sum_expected += child.MinValue() * child.probability
        return sum_expected

    def MinValue(self):
        sum_expected = 0
        for child in self.children:
            sum_expected += child.MaxValue() * child.probability
        return sum_expected

    @property
    def children(self):
        if self._children is None:
            self._children = list()
            is_vamp = not self.is_vamp
            for proba, positions in self.map.possible_outcomes(self.previous_moves):
                # Création du sommet fils
                carte=deepcopy(self.map)
                new_child_vertice = SommetOutcome_MinMax(
                    is_vamp=is_vamp,
                    game_map=carte,
                    depth=self.depth - 1)

                # On met la partie du sommet fils à jour
                new_child_vertice.previous_moves = self.previous_moves
                new_child_vertice.map.update_content(positions)
                new_child_vertice.probability = proba

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

        return self._children


class SommetOutcome_MinMax(SommetOutcome):
    __vertices_created = 0
    __transposion_table = {}

    def __init__(self, is_vamp=None, depth=None, game_map=None, init_map=False):
        super().__init__(is_vamp, depth, game_map)
        SommetOutcome_MinMax.__vertices_created+=1
        if init_map:
            SommetOutcome_MinMax.__transposion_table={}

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def transposition_table(cls):
        return cls.__transposion_table

    def get_score(self):
        if self.map.hash in SommetOutcome_MinMax.__transposion_table:
            return SommetOutcome_MinMax.__transposion_table[self.map.hash]
        else:
            return None, None

    def set_score_tt(self, depth, score):
        SommetOutcome_MinMax.__transposion_table[self.map.hash] = (depth, score)

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children is None:
            self._children = list()
            for moves in self.map.next_ranked_moves(self.is_vamp)[:4]:
                child = SommetChance_MinMax(is_vamp=self.is_vamp, depth=self.depth, game_map=self.map)
                child.previous_moves = moves
                self._children.append(child)
        return self._children

    # MaxValue et MinValue vont devoir utiliser un parcours de graph type DFS
    def MinValue(self):
        depth_tt, score = self.get_score()

        if score is not None:
            if depth_tt >= self.depth:
                return score

        if self.map.game_over() or self.depth == 0:
            self.set_score_tt(self.depth, self.evaluation)
            return self.evaluation
        else:
            children_scores = [child.MinValue() for child in self.children]
            min_value = min(children_scores)
            self.set_score_tt(self.depth, min_value)
            return min_value

    def MaxValue(self):
        depth_tt, score = self.get_score()

        if score is not None:
            if depth_tt >= self.depth:
                return score

        if self.map.game_over() or self.depth == 0:
            self.set_score_tt(self.depth, self.evaluation)
            return self.evaluation
        else:
            children_scores = [child.MaxValue() for child in self.children]
            max_value = max(children_scores)
            self.set_score_tt(self.depth, max_value)
            return max_value

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
            #print([(child.MaxValue(), child.previous_moves) for child in self.children])
            next_child = min(self.children, key=lambda x: x.MaxValue())

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.previous_moves


if __name__ == '__main__':
    carte = Map()
    racine=SommetOutcome_MinMax(is_vamp=True, depth=3, game_map=carte, init_map=True)
    print(racine.next_move())