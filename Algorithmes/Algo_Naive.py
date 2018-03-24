
from Joueur import Joueur
from Joueur_Interne import JoueurInterne


class AlgoNaive(JoueurInterne):
    """
    Joueur allant sur la case adjacente comptant le plus d'humains mangeables.
    Si pas de groupe d'humains mangeables à porté, il fait tourner le groupe en sens trigo autour du
    milieu de la carte, sans jamais se suicider.
    """
    def next_moves(self, show_map=True):
        next_move =  next(self.map.i_next_relevant_moves(
            self.is_vamp,
            nb_group_max=4))
        print("Naive: ", next_move)
        return next_move


if __name__ == "__main__":
    pass
    """Joueur_1=AlgoNaive()
    Joueur_1.start()
    Joueur_1.join()"""
