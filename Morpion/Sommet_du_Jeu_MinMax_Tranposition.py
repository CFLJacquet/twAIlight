from Morpion.Sommet_du_Jeu import SommetDuJeu


class SommetDuJeuMinMaxTransposition(SommetDuJeu):
    __vertices_created = 0
    __transposion_table = {}

    def __init__(self, is_vamp=True):
        super().__init__(is_vamp)
        SommetDuJeuMinMaxTransposition.__vertices_created += 1

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def transposition_table(cls):
        return cls.__transposion_table

    def get_score_tt(self):
        if self.map.hash in SommetDuJeuMinMaxTransposition.__transposion_table:
            return SommetDuJeuMinMaxTransposition.__transposion_table[self.map.hash]
        else:
            return None

    def set_score_tt(self, score):
        SommetDuJeuMinMaxTransposition.__transposion_table[self.map.hash] = score

    # MaxValue et MinValue vont devoir utiliser un parcours de graph type DFS
    def MinValue(self, depth):
        score_from_tt = self.get_score_tt()

        if score_from_tt is not None:
            return score_from_tt

        if self.map.game_over() or depth==0:
            self.set_score_tt(self.score)
            return self.score

        else:
            children_scores = [child.MaxValue(depth-1) for child in self.children]
            min_value = min(children_scores)
            self.set_score_tt(min_value)
            return min_value

    def MaxValue(self, depth):

        score_from_tt = self.get_score_tt()
        if score_from_tt is not None:
            return score_from_tt

        if self.map.game_over() or depth ==0:
            self.set_score_tt(self.score)
            return self.score

        else:
            children_scores = [child.MinValue(depth-1) for child in self.children]
            max_value = max(children_scores)
            self.set_score_tt(max_value)
            return max_value

    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        C'est la fonction Minimax-Decision du cours 4 s.54.
        On utilise un table de transposition (hashage) pour stocker les scores des plateaux avec un score

        Parcourt le graphe en DFS

        :return: le prochain mouvement
        """

        # On sélectionne le noeud fils selon sa race
        if self.is_vamp:
            next_child = max(self.children, key=lambda x: x.MinValue(3))
        else:
            next_child = min(self.children, key=lambda x: x.MaxValue(3))

        # On retourne le dernier mouvement pour arriver à ce sommet fils
        return next_child.map.previous_moves[-1]


if __name__ == "__main__":
    SommetDuJeuMinMaxTransposition.game_on()
