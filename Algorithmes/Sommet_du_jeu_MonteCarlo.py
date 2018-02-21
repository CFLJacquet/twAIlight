from Map import Map
from Cartes.Map_TheTrap import MapTheTrap
from copy import deepcopy
import random
from math import sqrt, log

from Algorithmes.Sommet_du_jeu import SommetOutcome, SommetChance


class SommetChance_MonteCarlo(SommetChance):
    __vertices_created = 0

    def __init__(self, is_vamp=None, depth=None, game_map=None):
        super().__init__(is_vamp, depth, game_map)
        SommetChance_MonteCarlo.__vertices_created += 1
        self.n_wins = 0
        self.n_games = 0
        self.visited = False

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @property
    def children(self):
        if self._children is None:
            self._children = list()
            is_vamp = not self.is_vamp
            for proba, positions in self.map.possible_outcomes(self.previous_moves):
                # Création du sommet fils
                new_child_vertice = SommetOutcome_MonteCarlo(is_vamp=is_vamp, game_map=self.map.__copy__(self.map))

                # On met la partie du sommet fils à jour
                new_child_vertice.previous_moves = self.previous_moves
                new_child_vertice.map.update_positions(positions)
                new_child_vertice.probability = proba

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

        return self._children

    def UCB(self, N=0):
        """ Upper Confidence Border calculé pour ce noeud
        (avec les notations du cours 4 s97)

        :param N: Nombre de parties jouées en tout
        :return: UCB
        """
        C = 2
        if self.n_games == 0:
            return None
        else:
            average = self.n_wins / self.n_games
            confidence = C * sqrt(log(N) / self.n_games)
            return average + confidence

    def MCTS(self):

        self.visited = True

        for child in self.children:
            child.MCTS()

        self.n_games = 0
        self.n_wins = 0
        for child in self.children:
            self.n_games += child.n_games
            self.n_wins += child.n_games - child.n_wins

    def simulation(self):
        carte = deepcopy(self.map)
        player = self.is_vamp
        next_move = self.previous_moves
        carte.compute_moves(next_move)
        i_round = 1
        while not carte.game_over() and i_round < 200:
            player = not player
            next_move = random.choice(carte.next_possible_moves(is_vamp=player))
            carte.compute_moves(next_move)
            i_round += 1
        winner = carte.winner()

        self.n_games += 1
        if winner is None:
            if random.random() < 0.5:
                self.n_wins += 1
        elif winner == self.is_vamp:
            self.n_wins += 1


class SommetOutcome_MonteCarlo(SommetOutcome):
    __vertices_created = 0

    def __init__(self, is_vamp=None, depth=None, game_map=None):
        super().__init__(is_vamp, depth, game_map)
        SommetOutcome_MonteCarlo.__vertices_created += 1
        self.n_wins = 0
        self.n_games = 0
        self.visited = False

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children is None:
            self._children = list()
            for moves in self.map.next_possible_moves(self.is_vamp):
                child = SommetChance_MonteCarlo(is_vamp=self.is_vamp, game_map=self.map)
                child.previous_moves = moves
                self._children.append(child)
        return self._children

    def MCTS(self):
        if self.map.game_over():
            self.n_games += 1
            if self.map.winner() is not None:
                if self.map.winner() != self.is_vamp:
                    self.n_wins += 1
            else:
                if random.random() < 0.5:
                    self.n_wins += 1

        else:
            # Selection
            max_UCB = None
            next_child = None
            for child in self.children:
                child_UCB = child.UCB(self.n_games)
                if child_UCB is None:
                    next_child = child
                    max_UCB = None
                    break
                if max_UCB is None:
                    max_UCB = child_UCB
                    next_child = child
                elif max_UCB < child_UCB:
                    max_UCB = child_UCB
                    next_child = child

            previous_n_wins = next_child.n_wins

            # Simulation
            if max_UCB is None:
                next_child.simulation()

            # Selection (toujours en cours)
            else:
                next_child.MCTS()

            # Back Propagation
            self.n_games += 1
            self.n_wins += next_child.n_wins - previous_n_wins


if __name__ == '__main__':
    carte = MapTheTrap()
    racine = SommetOutcome_MonteCarlo(is_vamp=True, game_map=carte)
    import cProfile

    cProfile.run("racine.MCTS()")

    for child in racine.children:
        if child.n_games:
            print(child.previous_moves, child.n_wins / child.n_games)
        else:
            print(child.previous_moves, None)
    print()
    print("Sommets créés :")
    print(SommetChance_MonteCarlo.nb_vertices_created() + SommetOutcome_MonteCarlo.nb_vertices_created())
