from Morpion.Sommet_du_Jeu import SommetDuJeu


class SommetDuJeuAlphaBeta(SommetDuJeu):
    __vertices_created = 0

    def __init__(self, is_vamp=True):
        SommetDuJeu.__init__(self, is_vamp)
        SommetDuJeuAlphaBeta.__vertices_created += 1
        self._alpha = None
        self._beta = None

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created


    def alpha(self, depth):
        """ Récupère la valeur maximale des bornes inférieures (alpha) des noeuds fils.

        :return: float
        """
        if self.map.game_over() or depth==0:
            return self.score
        else:
            for move in self.map.next_possible_moves():

                # Création du sommet fils
                new_child_vertice = SommetDuJeuAlphaBeta(not self.is_vamp)  # Je dois avoir des fils de la même classe

                # On met la partie du sommet fils à jour
                moves = self.map.previous_moves + [move]
                new_child_vertice.map.add_moves(moves)
                new_child_vertice.alpha = self._alpha

                # On éxécute la méthode lecture de l'attribut alpha sur ce fils
                new_alpha = new_child_vertice.beta(depth-1)

                if self._alpha is None:
                    self._alpha = new_alpha

                if self._beta is not None:
                    if self._beta < new_alpha:
                        self._alpha = new_alpha
                        break  # élagage
                # Choix de l'alpha le plus grand
                if new_alpha > self._alpha:
                    self._alpha = new_alpha

            return self._alpha


    def beta(self, depth):
        """ Récupère la valeur minimale des bornes supérieures des noeuds fils.

        :return: float
        """
        if self.map.game_over()or depth==0:
            return self.score
        else:
            for move in self.map.next_possible_moves():

                # Création du sommet fils
                new_child_vertice = SommetDuJeuAlphaBeta(not self.is_vamp)  # Je dois avoir des fils de la même classe

                # On met la partie du sommet fils à jour
                moves = self.map.previous_moves + [move]
                new_child_vertice.map.add_moves(moves)
                new_child_vertice.beta = self._beta
                # On éxécute la méthode lecture de l'attribut alpha sur ce fils
                new_beta = new_child_vertice.alpha(depth-1)

                if self._beta is None:
                    self._beta = new_beta

                if self._alpha is not None:
                    if self._alpha > new_beta:
                        self._beta = new_beta
                        break  # élagage

                if new_beta < self._beta:
                    self._beta = new_beta

            return self._beta


    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        Algorithme du AlphaBeta (parcours en profondeur)

        :return: le prochain mouvement
        """

        # On sélectionne le noeud fils selon sa race
        if self.is_vamp:
            next_child = max(self.children, key=lambda child: child.beta(10))
        else:
            next_child = min(self.children, key=lambda child: child.alpha(10))

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.map.previous_moves[-1]


if __name__ == "__main__":
    SommetDuJeuAlphaBeta.game_on()
