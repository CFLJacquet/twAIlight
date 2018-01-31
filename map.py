from collections import defaultdict
import random

class Map(object):

    
    def __init__(self, size):
        self.content = defaultdict(tuple) # Exemple : {(0, 0): (4, 'W')} ,ie en 0,0 il y a 4 Werewolves.
        self.size = size
    
    def move(self, list_coordinates, is_vamp=True):
        """ Fonction pour faire bouger nos armées. Il y une probabilité aléatoire uniforme de se déplacer
        sur les cases adjascentes, et une probabilité aléatoire de casser le groupe en 2 s'il y a suffisamment
        de membres """

        end_position = []
        if is_vamp:
            members = [elt for elt in list_coordinates if elt[3] != 0]
        else:
            members = [elt for elt in list_coordinates if elt[4] != 0]
        
        # On prend une décision pour chaque case occupée par nos armées
        for elt in members:
            x_old = elt[0]
            y_old = elt[1]

            # Scission du groupe ou non
            if is_vamp:
                number = elt[3]
            else :
                number = elt[4]
            if number > 1 :
                groupe_1 = random.randint(0, number)
                groupe_2 = number - groupe_1

            for groupe in [groupe for groupe in [groupe_1, groupe_2] if groupe != 0 ] :
                # Elimine les cases hors de la carte
                available_positions = [ (x_old + i, y_old + j) for i in (-1, 0, 1) \
                                                    for j in (-1, 0, 1) \
                                                    if (x_old + i, y_old + j) != (x_old, y_old) \
                                                    and (x_old + i) in range(self.size[0]) \
                                                    and (y_old + j) in range(self.size[1])]
                # Choix de la nouvelle position
                new_position = available_positions[random.randint(0, len(available_positions)-1)]
                end_position.append( (x_old, y_old, groupe, new_position[0], new_position[1]) )

        return end_position

if __name__ == "__main__":
    m = Map((5,6))
    UDP = [(3, 3, 0, 4, 0), (3, 4, 0, 0, 0), (4, 3, 0, 0, 0), (2, 2, 0, 0, 4), (2, 3, 0, 0, 0)]
    new = m.move(UDP)
    print(new)