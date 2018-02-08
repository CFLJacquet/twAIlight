from itertools import combinations_with_replacement
from Serveur_Interne import ServeurInterne

# Importation des algorithmes de décision
from Algorithmes.Algo_Aléatoire import AlgoAleatoireInterne

# Importation des des cartes du tournoi
from Cartes.Map_Ligne13 import MapLigne13
from Cartes.Map_Dust2 import MapDust2
from Cartes.Map_TheTrap import MapTheTrap
from Cartes.Map_Map8 import Map8

# Dictionnaires des cartes : nom de la carte --> carte (classe)
MAPS = {"Dust_2": MapDust2, "ligne13": MapLigne13, "TheTrap": MapTheTrap, "Map_8": Map8}

# Dictionnaires des algorithmes de décision : nom de l'algo --> algo (classe)
ALGOS = {"aléatoire": AlgoAleatoireInterne}

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

    # Parcours de toutes les paires possibles de joueurs
    for (algo_1_name, algo_1), (algo_2_name, algo_2) in combinations_with_replacement(ALGOS.items(), 2):
        result[algo_1_name] = {algo_2_name: {}}

        # Parcours de toutes les cartes du tournois
        for game_map_name, game_map in MAPS.items():
            result[algo_1_name][algo_2_name][game_map_name] = [0, 0]

            # On joue les N_GAME parties
            for _ in range(N_GAME):
                server_game = ServeurInterne(game_map, algo_1, algo_2, name1=algo_1_name, name2=algo_2_name, print_map= False)
                server_game.start()
                server_game.join()

                # Enregistrement des scores
                if server_game.winner:  # Si le joueur attaquant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][0] += 1
                else:  # Si le joueur défendant en premier gagne
                    result[algo_1_name][algo_2_name][game_map_name][1] += 1

        # Affichage des résultats du tournoi
        print(result)


if __name__ == "__main__":
    main()
