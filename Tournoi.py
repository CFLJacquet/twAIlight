from itertools import combinations
from collections import defaultdict

from twAIlight.Serveur_Interne import ServeurInterne

# Importation des algorithmes de décision
from twAIlight.Algorithmes.Algo_Aleatoire import AlgoAleatoireInterne
from twAIlight.Algorithmes.Algo_MinMax import AlgoMinMax
from twAIlight.Algorithmes.Algo_NegaMax import AlgoNegaMax
from twAIlight.Algorithmes.Algo_NegaMax_Oriente import AlgoNegMaxOriente
from twAIlight.Algorithmes.Algo_NegaMax_MPOO import AlgoNegMax_MPOO
from twAIlight.Algorithmes.Algo_Customized_Evaluation import AlgoCustomizedEvaluation
from twAIlight.Algorithmes.Algo_MonteCarloTreeSearch import AlgoMonteCarlo
from twAIlight.Algorithmes.Algo_Temporal_Difference_0 import AlgoTemporalDifference0


# Importation des des cartes du tournoi
from twAIlight.Cartes.Map_Ligne13 import MapLigne13
from twAIlight.Cartes.Map_Dust2 import MapDust2
from twAIlight.Cartes.Map_TheTrap import MapTheTrap
from twAIlight.Cartes.Map_Map8 import Map8
from twAIlight.Cartes.Map_Random import MapRandom

# Dictionnaires des cartes : nom de la carte --> carte (classe)
# MAPS = {"Dust_2": MapDust2, "ligne13": MapLigne13, "TheTrap": MapTheTrap, "Map_8": Map8}
MAPS = {#"Dust2": MapDust2,
        "Map8":Map8,
        #"TheTrap":MapTheTrap,
        #"CarteAléatoire":MapRandom
        }

# Dictionnaires des algorithmes de décision : nom de l'algo --> algo (classe)
ALGOS = {"Aleatoire": AlgoAleatoireInterne,
        "Aleatoire2": AlgoAleatoireInterne,
         #"MinMax": AlgoMinMax,
         #"NegaMax": AlgoNegaMax,
        # "NegaMax_MPOO" : AlgoNegMax_MPOO
         #"NegaMaxOriente": AlgoNegMaxOriente,
         #"Evaluation": AlgoCustomizedEvaluation,
         #"MonteCarlo": AlgoMonteCarlo
         }

# Nombre de parties par carte
N_GAME = 10


def main():
    """
    A partir des cartes définies plus haut, on effectue tous les duels possibles, et on les joue N_GAME fois

    :return: dictionnaire des scores
    """
    # Dictionnaire de scores
    # de la forme result[1er_joueur][2eme_joueur][carte]=[nombre partie gagnée attaquant, nombre partie gagné défenseur]
    result = {}
    # Dictionnaire des statistiques, enregistre le temps maximal d'un tour, le nombre de tours joués, le nombre de partie jouée
    # la durée totale de jeu, le nombre de victoires et de défaites
    stats = {}
    # Parcours de toutes les paires possibles de joueurs
    for (algo_1_name, algo_1), (algo_2_name, algo_2) in combinations(ALGOS.items(), 2):

        if algo_1_name not in result:
            result[algo_1_name] = {algo_2_name: {}}
        else:
            result[algo_1_name][algo_2_name] = {}

        if algo_1_name not in stats:
            stats[algo_1_name] = {"total_play_duration": 0,
                                  "max_play_duration": 0,
                                  "nb_play": 0,
                                  "nb_victories": 0,
                                  "nb_defeats": 0,
                                  "nb_vertices": 0
                                  }
        if algo_2_name not in stats:
            stats[algo_2_name] = {"total_play_duration": 0,
                                  "max_play_duration": 0,
                                  "nb_play": 0,
                                  "nb_victories": 0,
                                  "nb_defeats": 0,
                                  "nb_vertices": 0
                                  }
        # Parcours de toutes les cartes du tournois
        for game_map_name, game_map in MAPS.items():
            result[algo_1_name][algo_2_name][game_map_name] = [0, 0]

            # On joue les N_GAME /2 parties
            for _ in range(N_GAME - (N_GAME // 2)):
                server_game = ServeurInterne(game_map, algo_1, algo_2, name1=algo_1_name, name2=algo_2_name,
                                             print_map=False)
                server_game.start()
                server_game.join()

                # Enregistrement des scores et des statistiques de la partie
                if server_game.winner:  # Si le joueur attaquant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][0] += 1
                    stats[algo_1_name]["nb_victories"] += 1
                    stats[algo_2_name]["nb_defeats"] += 1
                else:  # Si le joueur défendant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][1] += 1
                    stats[algo_1_name]["nb_defeats"] += 1
                    stats[algo_2_name]["nb_victories"] += 1

                stats[algo_1_name]["total_play_duration"] += server_game.total_play_duration_1
                stats[algo_2_name]["total_play_duration"] += server_game.total_play_duration_2
                stats[algo_1_name]["max_play_duration"] = max(stats[algo_1_name]["max_play_duration"],
                                                              server_game.max_play_duration_1)
                stats[algo_2_name]["max_play_duration"] = max(stats[algo_2_name]["max_play_duration"],
                                                              server_game.max_play_duration_2)
                stats[algo_1_name]["nb_play"] += server_game.nb_play_1
                stats[algo_2_name]["nb_play"] += server_game.nb_play_2

            # On joue les N_GAME /2 parties en inversant l'ordre des joueurs
            for _ in range(N_GAME // 2):
                server_game = ServeurInterne(game_map, algo_2, algo_1, name1=algo_2_name, name2=algo_1_name,
                                             print_map=False)
                server_game.start()
                server_game.join()

                # Enregistrement des scores
                if server_game.winner:  # Si le joueur attaquant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][1] += 1
                    stats[algo_1_name]["nb_defeats"] += 1
                    stats[algo_2_name]["nb_victories"] += 1
                else:  # Si le joueur défendant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][0] += 1
                    stats[algo_1_name]["nb_victories"] += 1
                    stats[algo_2_name]["nb_defeats"] += 1

                stats[algo_1_name]["total_play_duration"] += server_game.total_play_duration_2
                stats[algo_2_name]["total_play_duration"] += server_game.total_play_duration_1
                stats[algo_1_name]["max_play_duration"] = max(stats[algo_1_name]["max_play_duration"],
                                                              server_game.max_play_duration_2)
                stats[algo_2_name]["max_play_duration"] = max(stats[algo_2_name]["max_play_duration"],
                                                              server_game.max_play_duration_1)
                stats[algo_1_name]["nb_play"] += server_game.nb_play_2
                stats[algo_2_name]["nb_play"] += server_game.nb_play_1

    for algo_name, algo_class in ALGOS.items():
        stats[algo_name]["nb_vertices"] = algo_class.nb_vertices_created()

    # Affichage des résultats du tournoi
    print()
    for algo_1_name in result:
        for algo_2_name in result[algo_1_name]:
            for game_map_name in MAPS:
                score = result[algo_1_name][algo_2_name][game_map_name]
                print(f"Match sur {game_map_name} {algo_1_name} {score[0]}:{score[1]} {algo_2_name}")

    # Classement
    print()
    ranking = sorted((algo_name for algo_name in stats), key=lambda algo: stats[algo]["nb_victories"] / (
        stats[algo]["nb_victories"] + stats[algo]["nb_defeats"]),
                     reverse=True)
    for i, algo_name in enumerate(ranking):
        n_game = stats[algo_name]['nb_victories'] + stats[algo_name]['nb_defeats']
        win_rate = stats[algo_name]['nb_victories'] / n_game
        average_play_duration = stats[algo_name]['total_play_duration'] / stats[algo_name]['nb_play']
        max_play_duration = stats[algo_name]['max_play_duration']
        vertices_created_per_round = stats[algo_name]['nb_vertices'] / stats[algo_name]['nb_play']
        print(f"{i+1}. {algo_name} : win ratio {win_rate:.2%}")
        print(f"\tAverage play duration : \t\t\t\t{average_play_duration:.2f}s")
        print(f"\tMaximum duration of a play : \t\t\t{max_play_duration:.2f}s")
        print(f"\tNumber of vertices created per play : \t{vertices_created_per_round:.0f} vertices")

if __name__ == "__main__":
    main()
