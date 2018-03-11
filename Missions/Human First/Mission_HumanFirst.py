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
                forbidden_places.add((i , j))
            elif 1.5*n_hum >=current_population:
                risky_humans[(i,j)]=n_hum
            elif n_hum>0:
                risk_free_humans[(i,j)]=n_hum

        distance_to_target = dict()
        # On attaque d'abord les humains faciles
        if risk_free_humans:
            for pos in risk_free_humans:
                distance_to_target[pos]= HumanFirst.distance(current_position, pos)


        # Cas que des humains nombreux, obligations de prendre des risques
        else:
            for pos in risky_humans:
                distance_to_target[pos] = HumanFirst.distance(current_position, pos)

        # Choix Glouton
        target = min(distance_to_target, key=distance_to_target.get)
        next_position=HumanFirst.next_position_to_target(current_position, target, forbidden_places=forbidden_places)

        return [(*current_position, current_population,*next_position)]



    @staticmethod
    def next_position_to_target(origin, destination,forbidden_places=set()):
        """Prochain mouvement vers une cible en utilisant l'algorithme A*"""
        visited=set()
        to_visit=set()
        distance_from_origin={origin:0}
        predecessor=dict()
        evaluations={origin:HumanFirst.distance(origin, destination)}
        current_position=origin

        while current_position != destination:
            visited.add(current_position)
            to_visit.discard(current_position)
            current_distance=distance_from_origin[current_position]
            i,j=current_position
            new_positions_to_explore=set([(i+i_0, j+j_0) for (i_0, j_0) in product((-1,0,1), repeat=2)])
            new_positions_to_explore-=visited
            new_positions_to_explore-=forbidden_places
            new_positions_to_explore-=to_visit
            to_visit|=new_positions_to_explore
            for pos in new_positions_to_explore:
                distance_from_origin[pos]=current_distance+1
                evaluations[pos]=HumanFirst.distance(pos,destination)
                predecessor[pos]=current_position
            current_position=min(to_visit, key=lambda x:distance_from_origin[x]+evaluations[x])

        while predecessor[current_position]!=origin:
            current_position=predecessor[current_position]

        return current_position

    @staticmethod
    def real_distance(origin, destination , forbidden_places=set()):
        """Distance entre origin et destination sans passer par les forbidden places en utilisant l'algorithme A*"""
        visited = set()
        to_visit = set()
        distance_from_origin = {origin: 0}
        evaluations = {origin: HumanFirst.distance(origin, destination)}
        current_position = origin

        while current_position != destination:
            visited.add(current_position)
            to_visit.discard(current_position)
            current_distance = distance_from_origin[current_position]
            i, j = current_position
            new_positions_to_explore = set([(i + i_0, j + j_0) for (i_0, j_0) in product((-1, 0, 1), repeat=2)])
            new_positions_to_explore -= visited
            new_positions_to_explore -= forbidden_places
            new_positions_to_explore -= to_visit
            to_visit |= new_positions_to_explore
            for pos in new_positions_to_explore:
                distance_from_origin[pos] = current_distance + 1
                evaluations[pos] = HumanFirst.distance(pos, destination)
            current_position = min(to_visit, key=lambda x: distance_from_origin[x] + evaluations[x])

        return distance_from_origin[destination]

    @staticmethod
    def distance(origin, destination):
        return max(abs(origin[0]-destination[0]), abs(origin[1]-destination[1]))




if __name__ == '__main__':

    current_position=(0,0)
    print(current_position)
    destination=(5,0)
    forbidden_places = set([(2, -1), (2, 0), (2, 1), (2, 2)])
    while current_position!=destination:
        current_position=HumanFirst.next_position_to_target(current_position,destination,forbidden_places)
        print(current_position)

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
