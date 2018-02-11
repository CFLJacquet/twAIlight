from Morpion.Map_Morpion import Morpion


class SommetDuJeu:

    def __init__(self, is_ami=True):
        self._children = list()
        self.etat = Morpion()
        self.is_ami = is_ami
        self._score = None


    @property
    def score(self):
        if self._score is None:
            self._score = self.etat.state_evaluation()
        return self._score

    @property
    def children(self):
        # Si la liste des enfants n'est pas vide, alors nul besoin de la recalculer !
        if self._children:
            return self._children
        # Si la liste est vide alors on la recalcule
        else:
            for move in self.etat.next_possible_moves():
                next_ami = not self.is_ami

                # Création du sommet fils
                new_child_vertice = self.__class__(next_ami)

                # On met la partie du sommet fils à jour
                moves = self.etat.previous_moves + [move]
                new_child_vertice.etat.add_moves(moves)

                # On ajoute ce fils complété dans la liste des fils du noeud actuel
                self._children.append(new_child_vertice)

            return self._children

    @classmethod
    def game_on(cls):
        """Lance le jeu de la classe"""
        sommet = cls()

        moves = []

        while not sommet.etat.game_over():
            print(sommet.etat)
            print("{} joue".format(sommet.is_ami))

            moves += [sommet.next_move()]

            sommet = cls(is_ami=not sommet.is_ami)
            sommet.etat.add_moves(moves)

        print(sommet.etat)
        print("Vainqueur : {}".format(sommet.etat.winner()))

        print("{} sommets ont été créés pour les besoins de cette simulation.".format(
            cls.nb_vertices_created()))

    def next_move(self):
        """Décision du prochain mouvement. Sera reecrit dans les classes filles"""
        pass