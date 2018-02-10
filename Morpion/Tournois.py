from itertools import combinations
import time
from collections import defaultdict

# Nos algorithmes
from Morpion.Sommet_du_jeu_Aleatoire import SommetDuJeuAleatoire
from Morpion.Sommet_du_Jeu_MinMax import SommetDuJeuMinMax
from Morpion.Sommet_du_Jeu_AlphaBeta import SommetDuJeuAlphaBeta
from Morpion.Sommet_du_Jeu_AlphaBeta_A_star import SommetDuJeuAlphaBetaAstar
from Morpion.Sommet_du_Jeu_MinMax_Tranposition import SommetDuJeuMinMaxTransposition

ALGOS = {'Aleatoire': SommetDuJeuAleatoire,
         'MinMax': SommetDuJeuMinMax,
         'AlphaBeta': SommetDuJeuAlphaBeta,
         'AlphaBetaAstar':SommetDuJeuAlphaBetaAstar,
         'MinMax_Transposition':SommetDuJeuMinMaxTransposition
         }

# Nombre de parties à jouer par duel
N_GAME = 4


def run_a_game(classe_sommet_1, classe_sommet_2, debug_mode=False):
    """ Joue une partie entre une instance de class_sommet_1 et class_sommet_2.
    Donne le vainqueur entre les deux joueurs et le temps d'éxécution des deux joueurs;

    :param classe_sommet_1: classe de graphe de jeu
    :param classe_sommet_2: classe de graphe de jeu
    :return: Vrai si le premier joueur gagne, faux s'il perd et None si match nul
    """

    sommet_1 = classe_sommet_1(is_ami=True)
    sommet_2 = classe_sommet_2(is_ami=False)

    duration_play_1 = 0  # Temps de jeu du joueur 1
    duration_play_2 = 0  # Temps de jeu du joueur 2

    updated_moves = []  # historique des coups joués

    while not sommet_1.map.game_over():
        if debug_mode: print(sommet_1.map)
        if debug_mode: print("{} joue".format(sommet_1.is_ami))

        start_play = time.time()
        updated_moves += [sommet_1.next_move()]  # Mise à jour de l'historique des coups
        end_play = time.time()

        duration_play_1 += end_play - start_play  # Temps de jeu du joueur 1 incrémenté

        sommet_2 = classe_sommet_2(is_ami=False)  # (re)Création du graphe du joueur 2
        sommet_2.map.add_moves(updated_moves)  # Mise à jour avec l'historique des coups joués pour le joueur 2

        if sommet_2.map.game_over():
            break

        if debug_mode: print(sommet_2.map)
        if debug_mode: print("{} joue".format(sommet_2.is_ami))

        start_play = time.time()
        updated_moves += [sommet_2.next_move()]  # Mise à jour de l'historique des coups
        end_play = time.time()

        duration_play_2 += end_play - start_play  # Temps de jeu du joueur 2 incrémenté

        sommet_1 = classe_sommet_1(is_ami=True)  # (re)Création du graphe du  joueur 1
        sommet_1.map.add_moves(updated_moves)  # Mise à jour avec l'historique des coups joués pour le joueur 1

    if sommet_1.map.game_over():
        if debug_mode: print(sommet_1.map)
        if debug_mode: print("Vainqueur : {}".format(sommet_1.map.winner()))
        return sommet_1.map.winner(), duration_play_1, duration_play_2

    if sommet_2.map.game_over():
        if debug_mode: print(sommet_2.map)
        if debug_mode: print("Vainqueur : {}".format(sommet_2.map.winner()))
        return sommet_2.map.winner(), duration_play_1, duration_play_2


def main():
    """ Effectue un tournoi entre les algos donnés sur la carte Morpion().

    :return: score en print
    """
    result = {}  # Compte les scores (victoire, nul et défaite) pour chaque duel joué
    time_played = defaultdict(float)
    # Parcours de toutes les paires possibles de joueurs
    for (algo_1_name, algo_1), (algo_2_name, algo_2) in combinations(ALGOS.items(), 2):

        if not algo_1_name in result:
            result[algo_1_name] = {}

        if not algo_2_name in result[algo_1_name]:
            result[algo_1_name][algo_2_name] = {'V': 0, 'N': 0, 'D': 0}

            # On joue les N_GAME/2 parties
            for _ in range(N_GAME//2):
                game_winner, duration_1, duration_2 = run_a_game(algo_1, algo_2)

                # on enregistre les temps d'éxécution des joueurs
                time_played[algo_1_name] += duration_1
                time_played[algo_2_name] += duration_2

                if game_winner is None:
                    result[algo_1_name][algo_2_name]['N'] += 1
                elif game_winner:
                    result[algo_1_name][algo_2_name]['V'] += 1
                else:
                    result[algo_1_name][algo_2_name]['D'] += 1

            # N_GAME /2 parties en inversant les joueurs
            for _ in range(N_GAME//2):
                game_winner, duration_2, duration_1 = run_a_game(algo_2, algo_1)

                # on enregistre les temps d'éxécution des joueurs
                time_played[algo_1_name] += duration_1
                time_played[algo_2_name] += duration_2

                if game_winner is None:
                    result[algo_1_name][algo_2_name]['N'] += 1
                elif game_winner:
                    result[algo_1_name][algo_2_name]['D'] += 1
                else:
                    result[algo_1_name][algo_2_name]['V'] += 1

    # Affichage des résultats du tournoi
    for algo_1 in result:
        for algo_2 in result[algo_1]:
            vic = result[algo_1][algo_2]["V"]
            draw = result[algo_1][algo_2]["N"]
            los = result[algo_1][algo_2]["D"]
            print(f"Match {algo_1} vs {algo_2}: score {vic}V {draw}N {los}D")

    # Affichage du nombre de sommets créés pour chaque algorithme
    print()
    for algo_name, algo_class in ALGOS.items():
        print(f"{algo_class.nb_vertices_created()} sommets ont été créés pour la classe {algo_name}")

    # Affichage du temps de jeu par équipe
    print()
    for algo_name, duration in time_played.items():
        print(f"{algo_name} a joué durant {duration:.2f} s.")


if __name__ == "__main__":
    main()
