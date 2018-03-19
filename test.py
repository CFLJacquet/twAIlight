from Missions.Human_First.Alt_HumanFirst import *
from Missions.Human_First.Mission_HumanFirst import *

from Cartes.Map_TheTrap import MapTheTrap

# starving_player=A_HumanFirst()
P1 = A_HumanFirst()
P2 = HumanFirst()
carte=MapTheTrap(True)

carte.print_map()
P1.is_vamp=True
P1.map=carte
P2.is_vamp=False
P2.map=carte

turn = 0
while not carte.game_over() and turn < 50:
    carte.compute_moves(P1.next_moves())
    carte.print_map()
    # On fait jouer l'adversaire
    carte.compute_moves(carte.random_moves(is_vamp=False))
    turn += 1
carte.print_map()







# from Cartes.Map_Random import MapRandom
# from Cartes.Map_Map8 import Map8

# carte = Map8()

# turn = 0
# while carte.game_over() == False and turn < 200:
#     print("ok")
#     moves = carte.next_possible_relevant_moves(True, 1)
#     # mettre au format liste de quintuplet next_possible_moves[0]

#     carte.compute_moves(moves)
#     carte.print_map()

#     moves = carte.random_moves(False)
#     carte.compute_moves(moves)
#     carte.print_map()

#     turn += 1


# # carte.print_map()
# # print(carte.next_possible_relevant_moves(True, 3))
