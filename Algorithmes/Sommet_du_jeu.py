from copy import deepcopy

from twAIlight.Map import Map


class SommetChance:
    def __init__(self, is_vamp=None, depth=None, game_map=None):
        self.map = game_map
        self.previous_moves = None
        self._children = None
        self.is_vamp = is_vamp
        self.depth = depth
        self._evaluation = None

    @property
    def children(self):
        if self._children is None:
            self._children = list()
            is_vamp = not self.is_vamp
            for proba, positions in self.map.possible_outcomes(self.previous_moves):
                # Création du sommet fils
                new_child_vertice = SommetOutcome(is_vamp=is_vamp, game_map=self.map.__copy__(self.map),
                                                  depth=self.depth - 1)

                # On met la partie du sommet fils à jour
                new_child_vertice.previous_moves = self.previous_moves
                new_child_vertice.map.update_positions(positions)
                new_child_vertice.probability = proba

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

        return self._children

    @property
    def evaluation(self):
        if self._evaluation is None:
            evaluation = 0
            for child in self.children:
                evaluation += child.probability * child.evaluation
            self._evaluation = evaluation
            return evaluation
        else:
            return self._evaluation


class SommetOutcome:
    __vertices_created = 0

    def __init__(self, is_vamp=None, depth=None, game_map=None, init_map=False):
        self._children = None
        self._evaluation = None
        self.map = game_map
        self.is_vamp = is_vamp
        self.depth = depth
        self.previous_moves = None
        self.probability = 1
        if init_map:
            SommetOutcome.__transposion_table={}

    def __copy__(self, objet):
        t = deepcopy(objet)
        return t

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @property
    def evaluation(self):
        if self._evaluation is None:
            self._evaluation = self.map.state_evaluation()
        return self._evaluation

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children is None:
            self._children = list()
            for moves in self.map.next_possible_moves(self.is_vamp):
                child = SommetChance(is_vamp=self.is_vamp, depth=self.depth, game_map=self.map.__copy__(self.map))
                child.previous_moves = moves
                self._children.append(child)
        return self._children
