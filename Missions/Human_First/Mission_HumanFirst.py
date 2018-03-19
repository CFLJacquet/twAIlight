from itertools import product

from Cartes.Map_Ligne13 import MapLigne13
from Algorithmes.Algo_Aleatoire import AlgoAleatoireInterne
from Serveur_Interne import ServeurInterne
from Joueur import Joueur


class HumanFirst(Joueur):
    
    def next_moves(self, nb_moves=1):
        """ Renvoie les combinaisons de mouvements pertinentes pour un joueur. \n\n

            Hypotheses: \n
            - on ne considère que les groupes d'humains convertible a 100% => risque de ne pas
            pouvoir bouger si y a que des gros \n
            - demi-dist de l'ennemi => risque immobilisation si ennemi a cote \n
            - si il y a rien d'interessant prendre une direction rapprochant d'un groupe humain
            convertible    ________________ A IMPLEMENTER AVEC UN ALGO A* ________________

            :return: liste ordonnée des meilleurs mouvements possibles
        """
        next_possible_positions = self.map.next_possible_positions(self.is_vamp)
        next_best_moves = []
        x_max, y_max = self.map.size
        

        if self.is_vamp: all_ennemis = [x_y for x_y in self.map.content if self.map.content[x_y][2]]
        else : all_ennemis = [x_y for x_y in self.map.content if self.map.content[x_y][1]]

        all_humains = [x_y for x_y in self.map.content if self.map.content[x_y][0]]

        for starting_position, moves in next_possible_positions.items():
            # Prendre l'ennemi "dangereux" le plus proche et calculer la moitié de la distance ...
            # ... afin de régler la taille du kernel pour le produit de convolution. On considère
            # ... que l'ennemi aura mangé tous les humains dans sa zone (dist/2)
            gp_num = sum(self.map.content[starting_position])

            dangerous_enn = [x_y for x_y in all_ennemis if sum(self.map.content[x_y]) >  gp_num ] 

            if dangerous_enn :
                # on prend la distance du groupe le plus proche et on le divise par 2, et on soustrait 1
                dist_min = min( [ int(max(abs(group_enn[0]-starting_position[0]),abs(group_enn[1]-starting_position[1]))/2)-1 \
                                    for group_enn in dangerous_enn ] )
                if dist_min < 0:
                    print("ATTENTION ennemi a cote")
                    """ prevoir le passage au mode defensif si ennemi trop gros une case a cote
                    de nous """

            else : #distance par défaut
                if self.map.debug_mode:
                    print("\nPas d'ennemi dangereux -> dist_min = 1/2 * taille carte ")
                dist_min = min(x_max//2, y_max//2)
            
            # on calcule le produit de convolution de noyau de taille (2*dist_min+1) pour chaque case autour de notre groupe 
            valeur = []
            for direction in moves:
                grad = 0
                for i in range(-dist_min, dist_min+1):
                    for j in range(-dist_min, dist_min+1):
                        try :
                            # on récupère les groupes d'humains suffisamment petits (<= taille)
                            hum = self.map.content[(direction[0] + i, direction[1] + j)][0]
                            if hum <= gp_num :
                                grad += hum
                        except:
                            pass
                valeur.append( (grad, sum(self.map.content[direction]), direction) )
            
            """if not all(v == 0 for v in [x[0] for x in valeur]): """
            valeur.sort(key=lambda x: (-x[1], -x[0]))
            temp = 0
            while len(next_best_moves) < nb_moves and temp < len(valeur):
                if valeur[temp][1] <= gp_num:
                    next_best_moves.append( (starting_position[0],starting_position[1], gp_num, valeur[temp][2][0], valeur[temp][2][1]) )
                temp += 1

            if self.map.debug_mode:
                    print("Demi-distance a l'adversaire le plus proche :", dist_min+1)
                    print("Produit de convolution (gradient, nb_humains dans la cellule, coord) :\n", valeur,"\n")

        return next_best_moves

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