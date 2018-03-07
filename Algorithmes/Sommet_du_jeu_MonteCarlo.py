from copy import deepcopy
import random
from math import sqrt, log

from twAIlight.Algorithmes.Sommet_du_jeu import SommetOutcome, SommetChance
from twAIlight.Map import Map
from twAIlight.Cartes.Map_TheTrap import MapTheTrap
from twAIlight.Cartes.Map_Map8 import Map8
from twAIlight.Cartes.Map_Random import MapRandom
from twAIlight.Cartes.Map_Ligne13 import MapLigne13


class SommetChance_MonteCarlo(SommetChance):
    __vertices_created = 0
    __simulation = {}

    def __init__(self, is_vamp=None, depth=None, game_map=None):
        super().__init__(is_vamp, depth, game_map)
        SommetChance_MonteCarlo.__vertices_created += 1
        self.n_wins = 0
        self.n_games = 0

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def get_simulation(cls, map_hash):
        if map_hash in cls.__simulation:
            return cls.__simulation[map_hash]
        else:
            return None, None

    @classmethod
    def add_simulation_result(cls, map_hash, is_vamp_winner):
        if map_hash in cls.__simulation:
            old_n_game, old_n_vamp_win = cls.__simulation[map_hash]
            cls.__simulation[map_hash] = (old_n_game + 1, old_n_vamp_win + is_vamp_winner)
        else:
            cls.__simulation[map_hash] = (1, is_vamp_winner)

    @property
    def children(self):
        if self._children is None:
            self._children = list()
            is_vamp = not self.is_vamp
            for proba, positions in self.map.possible_outcomes(self.previous_moves):
                # Création du sommet fils
                carte=deepcopy(self.map)
                new_child_vertice = SommetOutcome_MonteCarlo(is_vamp=is_vamp, game_map=carte)

                # On met la partie du sommet fils à jour
                new_child_vertice.previous_moves = self.previous_moves
                new_child_vertice.map.update_content(positions)
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
            next_move = carte.random_moves(is_vamp=player)
            carte.compute_moves(next_move)
            i_round += 1
        winner = carte.winner()

        if winner is None:
            if random.random() < 0.5:
                winner = True
            else:
                winner = False

        SommetChance_MonteCarlo.add_simulation_result(self.map.hash, is_vamp_winner=winner)

        n_game, n_win_vamp = SommetChance_MonteCarlo.get_simulation(self.map.hash)

        # Cas Vampire
        if self.is_vamp:
            self.n_games, self.n_wins = n_game, n_win_vamp
        # Cas Loup-Garou
        else:
            self.n_games, self.n_wins = n_game, n_game - n_win_vamp


class SommetOutcome_MonteCarlo(SommetOutcome):
    __vertices_created = 0

    def __init__(self, is_vamp=None, depth=None, game_map=None):
        super().__init__(is_vamp, depth, game_map)
        SommetOutcome_MonteCarlo.__vertices_created += 1
        self.n_wins = 0
        self.n_games = 0

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

            winner = self.map.winner()
            if winner is None:
                if random.random() < 0.5:
                    winner = True
                else:
                    winner = False

            SommetChance_MonteCarlo.add_simulation_result(self.map.hash, is_vamp_winner=winner)

            n_game, n_win_vamp = SommetChance_MonteCarlo.get_simulation(self.map.hash)

            # Cas Vampire
            if self.is_vamp:
                self.n_games, self.n_wins = n_game, n_win_vamp
            # Cas Loup-Garou
            else:

                self.n_games, self.n_wins = n_game, n_game - n_win_vamp

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
            previous_n_games = next_child.n_games
            # Simulation
            if max_UCB is None:
                next_child.simulation()

            # Selection (toujours en cours)
            else:
                next_child.MCTS()

            # Back Propagation
            self.n_games += next_child.n_games - previous_n_games
            self.n_wins += next_child.n_wins - previous_n_wins


if __name__ == '__main__':
    carte = MapRandom()
    carte.print_map()
    racine = SommetOutcome_MonteCarlo(is_vamp=True, game_map=carte)

    from time import time

    start_time = time()
    while time() < start_time + 2:
        racine.MCTS()

    for child in racine.children:
        if child.n_games:
            print(child.previous_moves, child.n_wins / child.n_games, child.n_games)
        else:
            print(child.previous_moves, None)
    max_child = max(racine.children, key=lambda child: child.n_wins / child.n_games if child.n_games != 0 else 0)
    robust_child = max(racine.children, key=lambda child: child.n_games)

    print()

    if max_child == robust_child:
        print(max_child.previous_moves)
    else:
        n_threshold = max_child.n_games / 4
        selected_children = filter(lambda child: child.n_games > n_threshold, racine.children)
        print(max(selected_children,
                  key=lambda child: child.n_wins / child.n_games if child.n_games != 0 else 0).previous_moves)
    print()
    print("Sommets créés :")
    print(SommetChance_MonteCarlo.nb_vertices_created() + SommetOutcome_MonteCarlo.nb_vertices_created())
    print("Nombre de simulations :")
    print(racine.n_games)
"""
    carte=MapLigne13()
    racine = SommetOutcome_MonteCarlo(is_vamp=True, game_map=carte)
    import cProfile
    cProfile.run("[racine.MCTS() for _ in range(20)]")"""