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


class Attack(Joueur):

    def next_moves(self, aggressivity = 1.5, last_resort=False):
        """ 
        :param aggressivity: sets the factor above which our group would attack 
        (e.g nb_allies >= 1.5*nb_enemies) \n
        :param last_resort: if True the algo will consider enemies even if they are more numerous
        """
        forbidden_places=set()
        risk_free_enemies=dict()
        risky_enemies=dict()
        pop_hum, pop_vamp, pop_lg=self.map.populations
        current_population = pop_vamp if self.is_vamp else pop_lg

        for (i,j), (n_hum,n_vamp,n_lg) in self.map.content.items():
            if self.is_vamp and n_vamp!=0 or not self.is_vamp and n_lg!=0:
                current_position=(i,j)

            if self.is_vamp and n_lg>current_population or not self.is_vamp and n_vamp>current_population:
                risky_enemies[(i,j)] = n_lg if self.is_vamp else n_vamp
                forbidden_places|=set([(i+i_0, j+j_0) for (i_0,j_0) in product((-1,0,1),repeat=2)])
            elif self.is_vamp and 0 < n_lg*aggressivity <= current_population:
                risk_free_enemies[(i,j)] = n_lg
            elif not self.is_vamp and 0 < n_vamp*aggressivity <= current_population:
                risk_free_enemies[(i,j)] = n_vamp

        distance_to_target = dict()
        # On attaque d'abord les ennemis faciles
        if risk_free_enemies:
            for pos in risk_free_enemies:
                distance_to_target[pos]= self.map.distance(current_position, pos)

        # Si tous les ennemis sont trop nombreux, obligation de prendre des risques
        if last_resort:
            for pos in risky_enemies:
                distance_to_target[pos] = self.map.distance(current_position, pos)

        # Choix Glouton
        target = min(distance_to_target, key=distance_to_target.get)
        print(target)
        next_position=self.map.next_position_to_target(current_position, target, forbidden_places=forbidden_places)

        return [(*current_position, current_population,*next_position)]



if __name__ == '__main__':


    starving_player=Attack()
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
