from Map import Map
from copy import deepcopy


class SommetDuJeu:
    __vertices_created = 0
    __transposion_table = {}
    
    def __init__(self, is_vamp=None, depth=None, game_map=None):
        self._children = list()
        self._score = None
        self.map = game_map
        self.is_vamp = is_vamp
        self.depth = depth
        self.last_moves = list()
        self.probabilite = 1
        SommetDuJeu.__vertices_created+=1


    def __copy__(self, objet):
        t = deepcopy(objet)
        return t

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def transposition_table(cls):
        return cls.__transposion_table

    def get_score_tt(self):
        if self.map.hash in SommetDuJeu.__transposion_table:
            return SommetDuJeu.__transposion_table[self.map.hash]
        else:
            return None

    def set_score_tt(self, score):
        SommetDuJeu.__transposion_table[self.map.hash] = score


    # MaxValue et MinValue vont devoir utiliser un parcours de graph type DFS
    def MinValue(self):
        score_from_tt = self.get_score_tt()

        if score_from_tt is not None:
            return score_from_tt

        if self.map.game_over() or self.depth == 0:
            return self.score
        else:
            children_scores = [child.MaxValue() for child in self.children]
            min_value = min(children_scores)
            self.set_score_tt(min_value)
            return min_value

    def MaxValue(self):
        score_from_tt = self.get_score_tt()

        if score_from_tt is not None:
            return score_from_tt

        if self.map.game_over() or self.depth == 0:
            self.set_score_tt(self.score)
            return self.score
        else:
            children_scores = [child.MinValue() for child in self.children]
            max_value = max(children_scores)
            self.set_score_tt(max_value)
            return max_value

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
            moves = self.map.next_possible_moves(self.is_vamp)
            for move in moves:
                is_vamp = not self.is_vamp

                # Création du sommet fils
                new_child_vertice = SommetDuJeu(is_vamp=is_vamp, game_map=self.map.__copy__(self.map),
                                                depth=self.depth - 1)

                # On met la partie du sommet fils à jour
                new_child_vertice.last_moves = move
                new_child_vertice.map.compute_moves(move)
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
        return next_child.last_moves
