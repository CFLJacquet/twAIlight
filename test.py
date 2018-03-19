from Cartes.Map_Ligne13 import MapLigne13

carte = MapLigne13(True)
carte.print_map()
print(len(carte.next_possible_moves(True)))

print(carte.next_possible_relevant_moves(True, 3))