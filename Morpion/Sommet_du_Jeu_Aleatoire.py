import random
from Morpion.Sommet_du_Jeu_general import SommetDuJeu


class SommetDuJeuAleatoire(SommetDuJeu):
    __vertices_created = 0

    def __init__(self, is_ami=True):
        SommetDuJeu.__init__(self, is_ami)
        SommetDuJeuAleatoire.__vertices_created += 1

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    def next_move(self):
        """ Renvoie un mouvement aléatoire.

        :return: le prochain mouvement
        """

        return random.choice(list(self.map.next_possible_moves()))


if __name__ == "__main__":
    SommetDuJeuAleatoire.game_on()
