import random

from Map import Map
from Cartes.Map_TheTrap import MapTheTrap
from Cartes.Map_Map8 import Map8

def old_way_random_moves(carte, is_vamp):
    return random.choice(carte.next_possible_moves(is_vamp=is_vamp))


def new_way_random_moves(carte, is_vamp):
    return carte.random_moves(is_vamp=is_vamp)


if __name__ == '__main__':
    carte = Map8()
    print(new_way_random_moves(carte, is_vamp=True))
    print(old_way_random_moves(carte, is_vamp=True))
    from cProfile import run as profile_run

    profile_run("old_way_random_moves(carte, is_vamp=True)")
    profile_run("new_way_random_moves(carte, is_vamp=True)")
