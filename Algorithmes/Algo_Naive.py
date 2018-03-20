
from twAIlight.Joueur import Joueur


class AlgoNaive(Joueur):

    #def create_map(self, map_size):
    #    """ Crée une carte à la taille map_size et l'enregistre dans l'attribut map
    #
    #    :param map_size: (n,m) dimension de la carte
    #    :return: None
    #    """
    #    self.map = Map(map_size=map_size) # Map_Silv

    def next_moves(self, show_map=True):
        next_move =  self.map.next_relevant_moves(
            self.is_vamp,
            stay_enabled=False,
            nb_group_max=4,
            nb_cases=8)[0]
        print("Naive: ", next_move)
        return next_move



if __name__ == "__main__":
  Joueur_1=AlgoNaive()
  Joueur_1.start()
  Joueur_1.join()
