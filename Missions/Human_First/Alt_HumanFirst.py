"""
designed by Mathieu
PB: si tous les groupes d'humains autour sont plus gros, l'algo plante
next_position=self.map.next_position_to_target(current_position, target, forbidden_places=forbidden_places)
-> target est vide

"""


from itertools import product

from Cartes.Map_Ligne13 import MapLigne13
from Algorithmes.Algo_Aleatoire import AlgoAleatoireInterne
from Serveur_Interne import ServeurInterne
from Joueur import Joueur


class A_HumanFirst(Joueur):

    def next_moves(self, last_resort=False):
        possible_position=self.map.next_possible_positions(self.is_vamp)
        forbidden_places=set()
        risky_humans=dict()
        risk_free_humans=dict()
        pop_hum, pop_vamp, pop_lg=self.map.populations
        current_population = pop_vamp if self.is_vamp else pop_lg

        for (i,j), (n_hum,n_vamp,n_lg) in self.map.content.items():
            if self.is_vamp and n_vamp!=0 or not self.is_vamp and n_lg!=0:
                current_position=(i,j)
            if self.is_vamp and 0 < n_lg < current_population  or not self.is_vamp and 0 < n_vamp  < current_population:
                forbidden_places|=set([(i+i_0, j+j_0) for (i_0,j_0) in product((-1,0,1),repeat=2)])
            
            if n_hum > current_population:
                forbidden_places.add((i , j))
                risky_humans[(i,j)]=n_hum
            elif n_hum>0:
                risk_free_humans[(i,j)]=n_hum

        distance_to_target = dict()
        # On attaque d'abord les humains faciles
        if risk_free_humans:
            for pos in risk_free_humans:
                distance_to_target[pos]= self.map.distance(current_position, pos)

        # Cas que des humains nombreux, obligations de prendre des risques
        if last_resort:
            for pos in risky_humans:
                distance_to_target[pos] = self.map.distance(current_position, pos)

        # Si aucune des cases n'est satisfaisante, prendre la 1e case neutre
        print(distance_to_target)
        if not distance_to_target:
            next_position = [pos for pos in possible_position[current_position] if pos not in forbidden_places][0]
        else:
            # Choix Glouton
            target = min(distance_to_target, key=distance_to_target.get)
            print(forbidden_places)
            next_position=self.map.next_position_to_target(current_position, target, forbidden_places=forbidden_places)

        return [(*current_position, current_population,*next_position)]



if __name__ == '__main__':


    starving_player=A_HumanFirst()
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
