# -*- coding: utf-8 -*-
from copy import deepcopy

from twAIlight.Joueur_Interne import JoueurInterne
from twAIlight.Algorithmes.Algo_Aleatoire import AlgoAleatoireInterne
from twAIlight.Algorithmes.Algo_NegaMax import AlgoNegaMax
from twAIlight.Cartes.Map_Dust2 import MapDust2
from twAIlight.Cartes.Map_TheTrap import MapTheTrap
from twAIlight.Cartes.Map_Map8 import Map8
from twAIlight.Serveur_Interne import ServeurInterne


class AlgoCustomizedEvaluation(JoueurInterne):
    """
    Une réécriture de la classe JoueurInterne, qui suit une fonction d'évaluation personnalisée

    """
    __map_evaluated = {}

    @classmethod
    def add_map_evaluation(cls, map_hash, evaluation):
        cls.__map_evaluated[map_hash] = evaluation

    @classmethod
    def get_map_evaluation(cls, map_hash):
        if map_hash in cls.__map_evaluated:
            return cls.__map_evaluated[map_hash]
        else:
            return None

    @staticmethod
    def customized_evaluation(game_map):
        """Renvoie une évaluation personnalisée d'une carte

        :return: cus_eval
        """
        cus_eval = AlgoCustomizedEvaluation.get_map_evaluation(game_map.hash)
        if cus_eval is None:
            if game_map.game_over():
                return game_map.state_evaluation()

            pop_hum, pop_vamp, pop_lg = game_map.populations

            cus_eval = pop_vamp - pop_lg  # Evaluation classique

            # Recherche du nombre de sous-groupes
            n_ss_vamp = 0
            n_ss_lg = 0
            for i_j in game_map.content:
                _, n_vamp, n_lg = game_map.content[i_j]
                if n_vamp:
                    n_ss_vamp += 1
                if n_lg:
                    n_ss_lg += 1
            cus_eval += -0.5 * (n_ss_vamp - n_ss_lg)

            # Distance des plus proches humains
            d_hum_vamp = 0
            d_hum_lg = 0

            if pop_hum:
                for i, j in game_map.content:
                    _, n_vamp, n_lg = game_map.content[(i, j)]

                    # Si la case est peuplée de monstres, on cherche les humains les plus proches
                    if n_vamp:
                        for x, y in game_map.content:
                            n_hum, _, _ = game_map.content[(x, y)]
                            if 0 < n_hum <= n_vamp:
                                current_distance = max(abs(i - x), abs(j - y))
                                if d_hum_vamp == 0:
                                    d_hum_vamp = current_distance
                                elif d_hum_vamp > current_distance:
                                    d_hum_vamp = current_distance
                                if d_hum_vamp == 1:
                                    break

                    if n_lg:
                        for x, y in game_map.content:
                            n_hum, _, _ = game_map.content[(x, y)]
                            if 0 < n_hum <= n_lg:
                                current_distance = max(abs(i - x), abs(j - y))
                                if d_hum_lg == 0:
                                    d_hum_lg = current_distance
                                elif d_hum_lg > current_distance:
                                    d_hum_lg = current_distance
                                if d_hum_lg == 1:
                                    break
                cus_eval += -0.1 * (d_hum_vamp - d_hum_lg)

            # On enregistre cus_eval
            AlgoCustomizedEvaluation.add_map_evaluation(map_hash=game_map.hash, evaluation=cus_eval)

        return cus_eval

    def evaluate_moves(self, moves):
        """ Renvoie l'évaluation de mouvements sur une carte

        :param moves: mouvements proposés
        :return: évaluation
        """
        cur_evaluation = 0
        for proba, updated_positions in self.map.possible_outcomes(moves):
            carte = deepcopy(self.map)
            carte.update_content(updated_positions)
            move_evaluation = AlgoCustomizedEvaluation.customized_evaluation(carte)
            cur_evaluation += proba * move_evaluation
        return cur_evaluation

    def next_moves(self, show_map=True):
        """ Renvoie le prochain mouvement prometteur avec l'évaluation personnalisée

        :param show_map: (boolean) Affichage de la carte
        :return: list
        """
        if show_map: self.map.print_map()

        # Evaluation actuelle de la carte
        current_evaluation = AlgoCustomizedEvaluation.customized_evaluation(self.map)

        better_moves = None
        better_evaluation = None

        for moves in self.map.next_possible_moves(self.is_vamp):
            if self.is_vamp:
                # Si le mouvement est intéressant pour les vampires
                # (Pour des raisons de performances, on accepte la première situation légèrement meilleure)
                # if self.evaluate_moves(moves) > current_evaluation:
                #    return moves

                if better_moves is None:
                    better_moves = moves
                    better_evaluation = self.evaluate_moves(moves)
                elif better_evaluation < self.evaluate_moves(moves):
                    better_moves = moves
                    better_evaluation = self.evaluate_moves(moves)
            else:
                # Si le mouvement est intéressant pour les loup-garous
                # (Pour des raisons de performances, on accepte la première situation légèrement meilleure)
                # if self.evaluate_moves(moves) < current_evaluation:
                #    return moves

                if better_moves is None:
                    better_moves = moves
                    better_evaluation = self.evaluate_moves(moves)
                elif better_evaluation > self.evaluate_moves(moves):
                    better_moves = moves
                    better_evaluation = self.evaluate_moves(moves)

        else:
            # On ne trouve pas de mouvement améliorant la situation du joueur,
            # On renvoie le moins pire des mouvements trouvés
            return better_moves

    @classmethod
    def nb_vertices_created(cls):
        return 0


if __name__ == '__main__':
    Joueur1 = AlgoCustomizedEvaluation
    Joueur2 = AlgoAleatoireInterne
    MapDust2 = MapTheTrap
    Serveur = ServeurInterne(MapDust2, Joueur1, Joueur2, name1="Evaluation", name2="Aléatoire", print_map=True)
    Serveur.start()
