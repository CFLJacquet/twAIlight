import unittest
from copy import deepcopy
import random

import numpy as np

from twAIlight.Numpy_Map import NumpyMap


class TestNumpyMap(unittest.TestCase):
    """Teste la carte et son bon comportement"""

    def test_hash(self):
        """On s'intéresse aux collisions éventuelles sur le hash de la carte
        """
        N_TEST = 10000  # Nombre de cartes générées pour le test

        collision = False
        # Dictionnaire des hashs déjà vu, de la forme seen_hashes[hash]=carte
        seen_hashes = dict()

        # liste des cartes à visiter avec leur prochains mouvements
        # de la forme [(carte, next_move)..]
        to_visit = list()

        # instance de carte (par défaut)
        carte = NumpyMap()

        seen_hashes[carte.hash] = carte

        to_visit = [(carte, random.choice(carte.next_possible_moves(is_vamp=True)))]
        to_visit.append((carte, random.choice(carte.next_possible_moves(is_vamp=False))))
        n_test_performed = 0
        while to_visit and n_test_performed < N_TEST:
            n_test_performed += 1
            carte, next_moves = to_visit.pop()
            child = deepcopy(carte)
            child.compute_moves(next_moves)
            if child.hash in seen_hashes:
                if np.any(child.content != seen_hashes[child.hash].content):
                    collision = True
                    break
            if child.next_ranked_moves(is_vamp=True):
                to_visit.append((child, random.choice(child.next_ranked_moves(is_vamp=True))))
            if child.next_ranked_moves(is_vamp=False):
                to_visit.append((child, random.choice(child.next_ranked_moves(is_vamp=False))))

        self.assertTrue(not collision)

    def test_methods(self):
        """ Teste si toutes les méthodes se lancent bien, et ne donnent pas de messages d'erreur.

        """
        carte = NumpyMap()
        carte.next_possible_moves(is_vamp=True)
        carte.next_possible_moves(is_vamp=False)
        carte.update_content([(0, 0, 0, 0, 0)])
        carte.next_possible_positions(is_vamp=True)
        carte.next_possible_positions(is_vamp=False)
        carte.winner()
        carte.game_over()
        carte.compute_moves([(0, 1, 1, 0, 0)])
        carte.populations
        carte.print_map()
        _ = carte.hash
        _ = carte.content
        carte.state_evaluation()
        carte.is_valid_moves([(0, 1, 1, 0, 0)], is_vamp=True)
        carte.possible_outcomes(carte.next_possible_moves(is_vamp=True)[0])

    def test_next_moves(self):
        """On s'intéresse à la méthode .next_possible_moves

        :return:
        """
        carte = NumpyMap()
        carte.update_content([(0, 1, 0, 3, 0)])
        carte.update_content([(0, 0, 0, 4, 0)])
        carte.print_map()
        for moves in carte.next_possible_moves(is_vamp=True):
            self.assertTrue(carte.is_valid_moves(moves, is_vamp=True))
        for moves in carte.next_possible_moves(is_vamp=False):
            self.assertTrue(carte.is_valid_moves(moves, is_vamp=False))

    def test_binomial(self):
        self.assertEqual(NumpyMap.binomial_coefficient(10, 15), 3003)
        self.assertEqual(NumpyMap.binomial_coefficient(-1, 2), 0)
        self.assertEqual(NumpyMap.binomial_coefficient(29, 60), 114449595062769120)

    def test_possible_outcomes(self):
        """ On teste si la somme des probabilités des conséquences d'un mouvement est bien égale à 1.

        """
        carte = NumpyMap()
        moves = [(0, 1, 1, 1, 1),(0, 2, 1, 2, 2)]
        sum_proba = sum(proba for proba, _ in carte.possible_outcomes(moves))
        self.assertEqual(sum_proba, 1)
        moves = [(0, 1, 2, 1, 1)]
        sum_proba = sum(proba for proba, _ in carte.possible_outcomes(moves))
        self.assertEqual(sum_proba, 1)

if __name__ == '__main__':
    test = TestNumpyMap()
    import cProfile
    cProfile.run("test.test_hash()")
    #unittest.main()
