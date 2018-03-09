from itertools import product

from Cartes.Map_Ligne13 import MapLigne13
from Algorithmes.Algo_Aleatoire import AlgoAleatoireInterne
from Serveur_Interne import ServeurInterne
from Joueur import Joueur


class HumanFirst(Joueur):

    def next_moves(self):
        forbidden_places=set()
        risky_humans=dict()
        risk_free_humans=dict()
        pop_hum, pop_vamp, pop_lg=self.map.populations()
        current_population = pop_vamp if self.is_vamp else pop_lg
        for (i,j), (n_hum,n_vamp,n_lg) in self.map.content.items():
            if self.is_vamp and n_vamp!=0 or not self.is_vamp and n_lg!=0:
                current_position=(i,j)
            if self.is_vamp and n_lg!=0 or not self.is_vamp and n_vamp!=0:
                forbidden_places|=set([(i+i_0, j+j_0) for (i_0,j_0) in product((-1,0,1),repeat=2)])
            if n_hum>=current_population:
                forbidden_places |= set([(i + i_0, j + j_0) for (i_0, j_0) in product((-1, 0, 1), repeat=2)])
            elif 1.5*n_hum >=current_population:
                risky_humans[(i,j)]=n_hum
            elif n_hum>0:
                risk_free_humans[(i,j)]=n_hum

        # On attaque d'abord les humains faciles
        if risk_free_humans:
            distance_to_target=dict()
            for (i,j) in risk_free_humans:
                distance_to_target[(i,j)]=max(abs(i-current_position[0]), abs(j-current_position[1]))


        # Cas que des humains nombreux, obligations de prendre des risques
        else:
            distance_to_target = dict()
            for (i, j) in risky_humans:
                distance_to_target[(i, j)] = max(abs(i - current_position[0]), abs(j - current_position[1]))

        # Choix Glouton
        target = min(distance_to_target, key=distance_to_target.get)
        if target[0] > current_position[0]:
            move_x = 1
        elif target[0] < current_position[0]:
            move_x = -1
        else:
            move_x = 0

        if target[1] > current_position[1]:
            move_y = 1
        elif target[1] < current_position[1]:
            move_y = -1
        else:
            move_y = 0

        return [
            (*current_position, current_population, current_position[0] + move_x, current_position[1] + move_y)]

    @staticmethod
    def distance_A_star(origin, destination,forbidden_places):
        visited=set()
        next_possible_path = []
        distance_from_origin={origin:0}
        evaluations={origin:HumanFirst.distance(origin, destination)}
        current_position=origin

        while current_position != destination:
            visited.add(current_position)
            i,j=current_position
            next_possible_moves=[(i+i_0, j+j_0) for (i_0, j_0) in product((-1,0,1), repeat=2) if (i_0,j_0)!= (0,0) ]

    @staticmethod
    def distance(origin, destination):
        return max(abs(origin[0]-destination[0]), abs(origin[1]-destination[1]))



if __name__ == '__main__':
    starving_player=HumanFirst()
    carte=MapLigne13()
    carte.print_map()
    starving_player.is_vamp=True
    starving_player.map=carte
    while not carte.game_over():
        carte.compute_moves(starving_player.next_moves())
        carte.print_map()
        # On fait jouer l'adversaire
        carte.compute_moves(carte.random_moves(is_vamp=False))
        carte.print_map()
