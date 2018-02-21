from Map import Map
from Cartes.Map_Map8 import Map8

if __name__ == '__main__':
    import cProfile
    carte=Map8()
    next_moves=carte.random_moves(is_vamp=True)
    carte.compute_moves(next_moves)
    cProfile.run("carte.compute_moves(next_moves)")