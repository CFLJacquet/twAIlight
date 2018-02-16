from Morpion.Sommet_du_Jeu import SommetDuJeu


class SommetDuJeuMinMax(SommetDuJeu):
    __vertices_created = 0

    def __init__(self, is_vamp=True):
        SommetDuJeu.__init__(self, is_vamp)
        SommetDuJeuMinMax.__vertices_created += 1

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    def MinValue(self, depth):
        if self.map.game_over()or depth==0:
            return self.score
        else:
            children_scores = [child.MaxValue(depth-1) for child in self.children]
            return min(children_scores)

    def MaxValue(self,depth):
        if self.map.game_over()or depth==0:
            return self.score
        else:
            children_scores = [child.MinValue(depth-1) for child in self.children]
            return max(children_scores)

    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        C'est la fonction Minimax-Decision du cours 4 s.54

        Parcourt le graphe en DFS

        :return: le prochain mouvement
        """

        # On sélectionne le noeud fils selon sa race
        if self.is_vamp:
            next_child = max(self.children, key=lambda x: x.MinValue(10))
        else:

            next_child = min(self.children, key=lambda x: x.MaxValue(10))

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.map.previous_moves[-1]


if __name__ == "__main__":
    SommetDuJeuMinMax.game_on()
