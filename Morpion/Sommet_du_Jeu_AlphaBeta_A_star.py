from Morpion.Sommet_du_Jeu_general import SommetDuJeu


class SommetDuJeuAlphaBetaAstar(SommetDuJeu):
    """ Graphe de jeu proche du AlphaBeta
    On ordonne les noeuds qui sont visités pour commencer par les plus prometteurs
    (avec la fonction d'évaluation de la carte)
    On réduit le nombre de sommets créés de -34%,
    mais cela coute +44% en temps de calcul (heuristique d'évaluation est chère)
    On peut s'attendre à de meilleurs résultats sur le jeu des vampires vs loup-garous,
    car il existe des heuristiques assez simples.
    """
    __vertices_created = 0

    def __init__(self, is_vamp=True):
        super().__init__(is_vamp)
        SommetDuJeuAlphaBetaAstar.__vertices_created += 1
        self._alpha = None
        self._beta = None

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @property
    def children(self):

        children = super().children
        if self.is_vamp:
            # Pour les besoins du max des alphas, on ordonne la liste avec les noeuds les plus forts d'abord
            self._children = sorted(children, key=lambda child: child.score)
        else:
            # Pour les besoins du mix des alphas, on ordonne la liste avec les noeuds les pluus faible
            self._children = sorted(children, key=lambda child: -child.score)
        return self._children


    def alpha(self, depth):
        """ Récupère la valeur maximale des bornes inférieures (alpha) des noeuds fils.

        :return: float
        """
        if self.map.game_over() or depth==0:
            return self.score
        else:
            for child in self.children:

                child.alpha = self._alpha

                # On éxécute la méthode lecture de l'attribut alpha sur ce fils
                new_alpha = child.beta(depth-1)

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
        if self.map.game_over() or depth==0:
            return self.score
        else:
            for child in self.children:

                child.beta = self._beta
                # On éxécute la méthode lecture de l'attribut alpha sur ce fils
                new_beta = child.alpha(depth-1)

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
    SommetDuJeuAlphaBetaAstar.game_on()
