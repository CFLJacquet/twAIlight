from Cartes.Map_Random import MapRandom
from Cartes.Map_Map8 import Map8

carte = Map8()

turn = 0
while carte.game_over() == False and turn < 200:
    print("ok")
    moves = carte.next_possible_relevant_moves(True, 1)
    # mettre au format liste de quintuplet next_possible_moves[0]

    carte.compute_moves(moves)
    carte.print_map()

    moves = carte.random_moves(False)
    carte.compute_moves(moves)
    carte.print_map()

    turn += 1


# carte.print_map()
# print(carte.next_possible_relevant_moves(True, 3))
