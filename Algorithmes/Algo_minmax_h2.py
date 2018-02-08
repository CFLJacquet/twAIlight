# -*- coding: utf-8 -*-

from Joueur import Joueur
from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Map import Map
from Sommet_du_jeu import SommetDuJeu

class AlgoMinMaxH2(Joueur):

    def next_moves(self, show_map=True):
        """ Fonction pour faire bouger nos armées qui utile le meilleur coup à horizon 2

        :param show_map: permet d'afficher la carte comprise pour un joueur. Très utile pour les parties avec le serveur du
        projet
        """


        moves = []
        if self.is_vamp:  # Le joueur est un loup-garou
            starting_positions = [x_y for x_y in self.map.content if self.map.content[x_y][1] != 0]
        else:  # Le joueur est un loup-garou
            starting_positions = [x_y for x_y in self.map.content if self.map.content[x_y][2] != 0]
        if self.debug_mode: print(self.name + '/next_moves Map : ' + str(self.map.content))
        if show_map: self.map.print_map()
        # On prend une décision pour chaque case occupée par nos armées

        # On commence par générer un graph dont la racine est l'état actuel du jeu, les enfants nos mouvements possibles
        # Les feuilles du graph sont les réactions du joueur contre nos avancées

        for x_y in starting_positions:
            x_old, y_old = x_y

            # Scission du groupe ou non
            if self.is_vamp:
                pop_of_monsters = self.map.content[x_y][1]  # Nombre de vampires sur la case
            else:
                pop_of_monsters = self.map.content[x_y][2]  # Nombre de loup-garous sur la case

            # On peut scinder en deux les groupes de monstres
            n_1 = random.randint(0, pop_of_monsters)  # Nombre d'individus dans le premier groupe de monstres
            n_2 = pop_of_monsters - n_1  # Nombre d'individus dans le deuxième groupe de monstres

            def new_position(x_old, y_old, x_max, y_max, starting_positions):
                """ Renvoie une nouvelle position pour nos monstres, aléatoirement choisie

                :param x_old: Abscisse de départ
                :param y_old: Ordonnée de départ
                :param x_max: taille maximale de x
                :param y_max: taille maximale de y
                :param starting_positions: Positions des cases contenant notre joueur
                :return: une nouvelle position
                """

                available_positions = [(x_old + i, y_old + j) for i in (-1, 0, 1) \
                                       for j in (-1, 0, 1) \
                                       if (x_old + i, y_old + j) != (x_old, y_old) \
                                       and 0 <= (x_old + i) < x_max \
                                       and 0 <= (y_old + j) < y_max
                                       and (x_old + i, y_old + j) not in starting_positions  # Règle 5
                                       ]
                new_pos = random.choice(available_positions)

                return new_pos

            if n_1:  # Si on a des individus dans le groupe 1, on rajoute un mouvement dans la liste moves
                new_move = new_position(x_old, y_old, self.map.size[0], self.map.size[1], starting_positions)
                moves.append((x_old, y_old, n_1, new_move[0], new_move[1]))
            if n_2:  # Idem pour le groupe 2
                new_move = new_position(x_old, y_old, self.map.size[0], self.map.size[1], starting_positions)
                moves.append((x_old, y_old, n_2, new_move[0], new_move[1]))

        return moves

class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """

if __name__=="__main__":
    Joueur1=AlgoAleatoireInterne
    Joueur2 =AlgoAleatoireInterne
    Serveur=ServeurInterne(Map(),Joueur1,Joueur2)
    Serveur.start()
