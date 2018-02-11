import random

from Morpion.Map_Morpion import Morpion


class SommetDuJeuAleatoire:
    __vertices_created = 0

    def __init__(self, is_ami=True):
        SommetDuJeuAleatoire.__vertices_created += 1
        self._children = list()
        self.map = Morpion()
        self.is_ami = is_ami

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @property
    def score(self):
        if self._score is None:
            self._score = self.map.state_evaluation()
        return self._score

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children:
            return self._children
        # Si la liste est vide alors on la recalcule
        else:
            for move in self.map.next_possible_moves():
                next_ami = not self.is_ami

                # Création du sommet fils
                new_child_vertice = SommetDuJeuAleatoire(next_ami)

                # On met la partie du sommet fils à jour
                moves = self.map.previous_moves + [move]
                new_child_vertice.map.add_moves(moves)

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

            return self._children

    def next_move(self):
        """ Renvoie un mouvement aléatoire.

        :return: le prochain mouvement
        """

        return random.choice(list(self.map.next_possible_moves()))


if __name__ == "__main__":
    sommet = SommetDuJeuAleatoire()

    while not sommet.map.game_over():
        print(sommet.map)
        print("{} joue".format(sommet.is_ami))

        previous_moves = list(sommet.map.previous_moves)
        previous_ami = sommet.is_ami

        updated_moves = previous_moves + [sommet.next_move()]

        sommet = SommetDuJeuAleatoire(not previous_ami)
        sommet.map.add_moves(updated_moves)

    print(sommet.map)
    print("Vainqueur : {}".format(sommet.map.winner()))
