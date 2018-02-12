from itertools import combinations
from Serveur_Interne import ServeurInterne

# Importation des algorithmes de décision
from Algorithmes.Algo_Aleatoire import AlgoAleatoireInterne
from Algorithmes.Algo_minmax import AlgoMinMaxH2

# Importation des des cartes du tournoi
from Cartes.Map_Ligne13 import MapLigne13
from Cartes.Map_Dust2 import MapDust2
from Cartes.Map_TheTrap import MapTheTrap
from Cartes.Map_Map8 import Map8

# Dictionnaires des cartes : nom de la carte --> carte (classe)
# MAPS = {"Dust_2": MapDust2, "ligne13": MapLigne13, "TheTrap": MapTheTrap, "Map_8": Map8}
MAPS = {"Dust2": MapDust2}

# Dictionnaires des algorithmes de décision : nom de l'algo --> algo (classe)
ALGOS = {"AlgoAleatoire": AlgoAleatoireInterne, "AlgoMinMax": AlgoMinMaxH2}

# Nombre de parties par carte
N_GAME = 1


def main():
    """
    A partir des cartes définies plus haut, on effectue tous les duels possibles, et on les joue N_GAME fois

    :return: dictionnaire des scores
    """
    # Dictionnaire de scores
    # de la forme result[1er_joueur][2eme_joueur][carte]=[nombre partie gagnée attaquant, nombre partie gagné défenseur]
    result = {}

    # Parcours de toutes les paires possibles de joueurs
    for (algo_1_name, algo_1), (algo_2_name, algo_2) in combinations(ALGOS.items(), 2):
        result[algo_1_name] = {algo_2_name: {}}

        # Parcours de toutes les cartes du tournois
        for game_map_name, game_map in MAPS.items():
            result[algo_1_name][algo_2_name][game_map_name] = [0, 0]

            # On joue les N_GAME /2 parties
            for _ in range(N_GAME - (N_GAME // 2)):
                server_game = ServeurInterne(game_map, algo_1, algo_2, name1=algo_1_name, name2=algo_2_name,
                                             print_map=True)
                server_game.start()
                server_game.join()

                # Enregistrement des scores
                if server_game.winner:  # Si le joueur attaquant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][0] += 1
                else:  # Si le joueur défendant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][1] += 1

            # On joue les N_GAME /2 parties en inversant l'ordre des joueurs
            for _ in range(N_GAME // 2):
                server_game = ServeurInterne(game_map, algo_2, algo_1, name1=algo_2_name, name2=algo_1_name,
                                             print_map=True)
                server_game.start()
                server_game.join()

                # Enregistrement des scores
                if server_game.winner:  # Si le joueur attaquant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][1] += 1
                else:  # Si le joueur défendant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][0] += 1

        # Affichage des résultats du tournoi
        for algo_att_name in result:
            for algo_def_name in result[algo_att_name]:
                for carte in result[algo_att_name][algo_def_name]:
                    print("Match {0} vs {1} sur {2}: score {3}".format(algo_att_name,
                                                                       algo_def_name,
                                                                       carte,
                                                                       result[algo_att_name][algo_def_name][carte])
                          )


if __name__ == "__main__":
    main()
