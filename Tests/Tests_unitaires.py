from unittest import TestCase
from copy import deepcopy
import random

from Map import Map
from Cartes.Map_Dust2 import MapDust2
from Cartes.Map_Ligne13 import MapLigne13
from Cartes.Map_Map8 import Map8
from Cartes.Map_Random import MapRandom
from Cartes.Map_TheTrap import MapTheTrap


class TestMap(TestCase):
    """Teste la carte et son bon comportement"""

    def test_hash(self):
        """On s'intéresse aux collisions éventuelles sur le hash de la carte
        """
        N_TEST = 10000  # Nombre de carte générée

        collision = False
        # Dictionnaire des hashs déjà vu, de la forme seen_hashes[hash]=carte
        seen_hashes = dict()

        # liste des cartes à visiter avec leur prochains mouvements
        # de la forme [(carte, next_move)..]
        to_visit = list()

        # instance de carte (par défaut)
        carte = Map()

        seen_hashes[carte.hash] = carte

        to_visit = [(carte, random.choice(carte.next_possible_moves(is_vamp=True)))]
        to_visit.append((carte, random.choice(carte.next_possible_moves(is_vamp=False))))
        n_test_performed = 0
        while to_visit and n_test_performed < N_TEST:
            n_test_performed += 1
            carte, next_moves = to_visit.pop()
            for move in next_moves:
                child = deepcopy(carte)
                child.compute_moves([move])
                if child.hash in seen_hashes:
                    if child.content != seen_hashes[child.hash].content:
                        collision = True
                        break
                if child.next_possible_moves(is_vamp=True):
                    to_visit.append((child, random.choice(child.next_possible_moves(is_vamp=True))))
                if child.next_possible_moves(is_vamp=False):
                    to_visit.append((child, random.choice(child.next_possible_moves(is_vamp=False))))

        self.assertTrue(not collision)

    def test_methods(self):
        """ Teste si toutes les méthodes se lancent bien, et ne donnent pas de messages d'erreur.

        """
        carte = Map()
        carte.next_possible_moves(is_vamp=True)
        carte.next_possible_moves(is_vamp=False)
        carte.update_positions([(0, 0, 0, 0, 0)])
        carte.next_possible_positions(is_vamp=True)
        carte.next_possible_positions(is_vamp=False)
        carte.winner()
        carte.game_over()
        carte.compute_moves([(0, 1, 1, 0, 0)])
        carte.populations()
        carte.print_map()
        _ = carte.hash
        _ = carte.content
        carte.state_evaluation()
        carte.is_valid_moves([(0, 0, 1, 0, 1)], is_vamp=True)

    def test_next_moves(self):
        """On s'intéresse à la méthode .next_possible_moves

        :return:
        """
        carte = Map()
        carte.update_positions([(0, 1, 0, 3, 0)])
        carte.update_positions([(0, 0, 0, 4, 0)])
        carte.print_map()
        for moves in carte.next_possible_moves(is_vamp=True):
            self.assertTrue(carte.is_valid_moves(moves, is_vamp=True))
        for moves in carte.next_possible_moves(is_vamp=False):
            self.assertTrue(carte.is_valid_moves(moves, is_vamp=False))


class TestDust2(TestCase):
    def test_methods(self):
        """ Teste si toutes les méthodes se lancent bien, et ne donnent pas de messages d'erreur.

        """
        carte = MapDust2()
        carte.next_possible_moves(is_vamp=True)
        carte.next_possible_moves(is_vamp=False)
        carte.update_positions([(0, 0, 0, 0, 0)])
        carte.next_possible_positions(is_vamp=True)
        carte.next_possible_positions(is_vamp=False)
        carte.winner()
        carte.game_over()
        carte.compute_moves([(0, 1, 1, 0, 0)])
        carte.populations()
        carte.print_map()
        _ = carte.hash
        _ = carte.content
        carte.state_evaluation()
        carte.is_valid_moves([(0, 0, 1, 0, 1)], is_vamp=True)


class TestLigne13(TestCase):
    def test_methods(self):
        """ Teste si toutes les méthodes se lancent bien, et ne donnent pas de messages d'erreur.

        """
        carte = MapLigne13()
        carte.next_possible_moves(is_vamp=True)
        carte.next_possible_moves(is_vamp=False)
        carte.update_positions([(0, 0, 0, 0, 0)])
        carte.next_possible_positions(is_vamp=True)
        carte.next_possible_positions(is_vamp=False)
        carte.winner()
        carte.game_over()
        carte.compute_moves([(0, 1, 1, 0, 0)])
        carte.populations()
        carte.print_map()
        _ = carte.hash
        _ = carte.content
        carte.state_evaluation()
        carte.is_valid_moves([(0, 0, 1, 0, 1)], is_vamp=True)


class TestMap8(TestCase):
    def test_methods(self):
        """ Teste si toutes les méthodes se lancent bien, et ne donnent pas de messages d'erreur.

        """
        carte = Map8()
        carte.next_possible_moves(is_vamp=True)
        carte.next_possible_moves(is_vamp=False)
        carte.update_positions([(0, 0, 0, 0, 0)])
        carte.next_possible_positions(is_vamp=True)
        carte.next_possible_positions(is_vamp=False)
        carte.winner()
        carte.game_over()
        carte.compute_moves([(0, 1, 1, 0, 0)])
        carte.populations()
        carte.print_map()
        _ = carte.hash
        _ = carte.content
        carte.state_evaluation()
        carte.is_valid_moves([(0, 0, 1, 0, 1)], is_vamp=True)


class TestMapRandom(TestCase):
    def test_methods(self):
        """ Teste si toutes les méthodes se lancent bien, et ne donnent pas de messages d'erreur.

        """
        carte = MapRandom()
        carte.next_possible_moves(is_vamp=True)
        carte.next_possible_moves(is_vamp=False)
        carte.update_positions([(0, 0, 0, 0, 0)])
        carte.next_possible_positions(is_vamp=True)
        carte.next_possible_positions(is_vamp=False)
        carte.winner()
        carte.game_over()
        carte.compute_moves([(0, 1, 1, 0, 0)])
        carte.populations()
        carte.print_map()
        _ = carte.hash
        _ = carte.content
        carte.state_evaluation()
        carte.is_valid_moves([(0, 0, 1, 0, 1)], is_vamp=True)


class TestMapTheTrap(TestCase):
    def test_methods(self):
        """ Teste si toutes les méthodes se lancent bien, et ne donnent pas de messages d'erreur.

        """
        carte = MapTheTrap()
        carte.next_possible_moves(is_vamp=True)
        carte.next_possible_moves(is_vamp=False)
        carte.update_positions([(0, 0, 0, 0, 0)])
        carte.next_possible_positions(is_vamp=True)
        carte.next_possible_positions(is_vamp=False)
        carte.winner()
        carte.game_over()
        carte.compute_moves([(0, 1, 1, 0, 0)])
        carte.populations()
        carte.print_map()
        _ = carte.hash
        _ = carte.content
        carte.state_evaluation()
        carte.is_valid_moves([(0, 0, 1, 0, 1)], is_vamp=True)


if __name__ == '__main__':
    unittest.main()