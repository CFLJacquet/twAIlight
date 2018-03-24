from copy import deepcopy
from collections import defaultdict
import random

from Algorithmes.Sommet_du_jeu import SommetOutcome, SommetChance
from Map import Map

from Cartes.Map_TheTrap import MapTheTrap
from Cartes.Map_Map8 import Map8
from Cartes.Map_Random import MapRandom


class SommetChance_TemporalDifference(SommetChance):
    __vertices_created = 0
    __map_values = defaultdict(float)

    def __init__(self, is_vamp=None, depth=None, game_map=None):
        super().__init__(is_vamp, depth, game_map)
        SommetChance_TemporalDifference.__vertices_created += 1

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def get_value(cls, map_hash):
        return cls.__map_values[map_hash]

    @classmethod
    def set_value(cls, map_hash, new_value):
        cls.__map_values[map_hash] = new_value

    @property
    def children(self):
        if self._children is None:
            self._children = list()
            is_vamp = not self.is_vamp
            for proba, positions in self.map.possible_outcomes(self.previous_moves):
                # Création du sommet fils
                carte=deepcopy(self.map)
                new_child_vertice = SommetOutcome_TemporalDifference(
                    is_vamp=is_vamp,
                    game_map=carte)

                # On met la partie du sommet fils à jour
                new_child_vertice.previous_moves = self.previous_moves
                new_child_vertice.map.update_content(positions)
                new_child_vertice.probability = proba

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

        return self._children

    @property
    def value(self):
        weighted_value=0
        for child in self.children:

            weighted_value+= child.probability*self.get_value(child.map.hash)

        return weighted_value


    def simulation(self):
        ALPHA, GAMMA = 0.8, 0.9
        carte = deepcopy(self.map)
        current_hash = carte.hash
        current_value = self.get_value(current_hash)
        player = self.is_vamp
        next_move = self.previous_moves
        carte.compute_moves(next_move)
        i_round = 1
        while not carte.game_over() and i_round < 200:
            next_hash = carte.hash
            next_value = self.get_value(next_hash)
            # TODO reward sur chaque changement de différence de populations
            self.set_value(current_hash, current_value + ALPHA * (GAMMA * next_value - current_value))

            current_hash = next_hash
            current_value = next_value

            # Algo de décision aléatoire
            player = not player
            next_move = carte.random_moves(is_vamp=player)

            carte.compute_moves(next_move)

            i_round += 1
        winner = carte.winner()

        if winner is None:
            self.set_value(current_hash, (1 - ALPHA) * current_value)

        # Cas Vampire
        if winner:
            self.set_value(current_hash, current_value + ALPHA * (1 - current_value))
        # Cas Loup-Garou
        else:
            self.set_value(current_hash, current_value + ALPHA * (-1 - current_value))


class SommetOutcome_TemporalDifference(SommetOutcome):
    __vertices_created = 0
    __simulations=0

    def __init__(self, is_vamp=None, depth=None, game_map=None):
        super().__init__(is_vamp, depth, game_map)
        SommetOutcome_TemporalDifference.__vertices_created += 1

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def nb_simulation(cls):
        return cls.__simulations

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children is None:
            self._children = list()
            for moves in self.map.i_next_possible_moves(self.is_vamp):
                child = SommetChance_TemporalDifference(is_vamp=self.is_vamp, game_map=self.map)
                child.previous_moves = moves
                self._children.append(child)
        return self._children

    def temporal_difference_0(self):
        """ Lance une simulation pour chaque mouvement possible à partir du noeud actuel

        :return:
        """
        child = random.choice(self.children)
        child.simulation()
        SommetOutcome_TemporalDifference.__simulations+=1



if __name__ == '__main__':
    carte = MapTheTrap()
    carte.print_map()
    racine = SommetOutcome_TemporalDifference(is_vamp=True, game_map=carte)

    from time import time

    start_time = time()
    while time() < start_time + 20:
        racine.temporal_difference_0()

    racine.temporal_difference_0()

    for child in racine.children:
        print(child.previous_moves, child.value)
    print()
    print("Mouvements sélectionnés")
    if racine.is_vamp:
        max_child=max(racine.children, key=lambda child: child.value)
        next_moves=max_child.previous_moves
        print(max_child.previous_moves,max_child.value )
    else:
        min_child=min(racine.children, key=lambda child: child.value)
        next_moves=min_child.previous_moves
        print(min_child.previous_moves,min_child.value)
    print()
    print("Sommets créés :")
    print(SommetChance_TemporalDifference.nb_vertices_created() + SommetOutcome_TemporalDifference.nb_vertices_created())
    print("Nombre de simulations :")
    print(SommetOutcome_TemporalDifference.nb_simulation())
    #carte.compute_moves(next_moves)
    #carte.print_map()


    racine.temporal_difference_0()
    from cProfile import run
    run("[racine.temporal_difference_0() for _ in range(100)]")

