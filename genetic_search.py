from itertools import combinations
from collections import defaultdict
import copy,math

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
import random

# Dictionnaires des cartes : nom de la carte --> carte (classe)
# MAPS = {"Dust_2": MapDust2, "ligne13": MapLigne13, "TheTrap": MapTheTrap, "Map_8": Map8}

# Nombre de parties par carte
N_GAME = 1
POOL_SIZE = 5
N_SURVIVORS = 3
TIMER = 100

# Function to generate an algorithm  class

def main():
    range_parameters = {'depth_max': [1,2,3,4,5,6,7],'nb_group_max': [1],'nb_cases':[[i for i in range (0,10)]]}
    tuned_parameters = [{'depth_max':a, 'nb_group_max':b, 'nb_cases':d} for a in range_parameters['depth_max'] for b in range_parameters['nb_group_max'] for d in range_parameters['nb_cases']]
    # Generation de la population à explorer. Les individus sont numérotés de 1 à n
    population = [(i,tuned_parameters[i]) for i in range(0,len(tuned_parameters))]
    population_dic = {i:tuned_parameters[i] for i in range(0,len(tuned_parameters))}
    population_size = len(population)
    print("There are %i individuals " % population_size)
    pool =[]
    historical_presence={}
    # Iterations
    print("Nombre de combats à faire: %i " %(N_GAME*TIMER*math.factorial(POOL_SIZE)/(math.factorial(2)*math.factorial(POOL_SIZE-2))))

    for epoch in range(TIMER):
        if epoch==0:
        # Initialisation de la pool aléatoire
            for i in range(0, POOL_SIZE):
                rand = random.randint(0, population_size - 1)
                pool.append(population[rand])

        individual_survivors = tournoi(pool,population_dic,nb_survivors=N_SURVIVORS,pool_size=POOL_SIZE)

        pool=[]
        for s in individual_survivors:
            pool.append(population[s])
            if s not in historical_presence:
                historical_presence[s]=0
                historical_presence[s]+=1

        # On remplit les places restantes dans la pool aléatoirement
        for i in range (N_SURVIVORS,POOL_SIZE-N_SURVIVORS+1):
            rand = individual_survivors[0]
            while rand in individual_survivors:
                rand = random.randint(0, population_size - 1)
            pool.append(population[rand])

    print("Nombre de combats: %i \n" %(TIMER*math.factorial(POOL_SIZE)/(math.factorial(2)*math.factorial(POOL_SIZE-2))))
    print("\nClassement des top %i algorithmes sur %i\n" %(N_SURVIVORS,population_size))
    for surv in individual_survivors:
        print("\nL'algorithme %i (présent pendant %i tours (sur %i) dans les survivants (TOP %i d'une pool)" %(surv,history[surv],TIMER,N_SURVIVORS))
        print("\nSes caractéristiques sont:\n")
        print(population_dic[surv])

def tournoi(pool,population_dic,nb_survivors=10,pool_size=20):
    """
    A partir des cartes définies plus haut, on effectue tous les duels possibles, et on les joue N_GAME fois et on renvoie les N_SURVIVORS

    :return: ranking des N_SURVIVORS
    """
    # Dictionnaire de scores
    # de la forme result[1er_joueur][2eme_joueur][carte]=[nombre partie gagnée attaquant, nombre partie gagné défenseur]
    result = {}
    # Dictionnaire des statistiques, enregistre le temps maximal d'un tour, le nombre de tours joués, le nombre de partie jouée
    # la durée totale de jeu, le nombre de victoires et de défaites
    stats = {}
    # Parcours de toutes les paires possibles de joueurs

    MAPS = {  # "Dust2": MapDust2,
        "Map8": Map8,
        # "TheTrap":MapTheTrap,
        # "CarteAléatoire":MapRandom
    }

    # Dictionnaires des algorithmes de décision : nom de l'algo --> algo (classe)

    print(pool)
    print(population_dic)


    for (individual_1,individual_2) in combinations(pool, 2):

        individual_1_name = individual_1[0]
        individual_1_properties = individual_1[1]

        individual_2_name = individual_2[0]
        individual_2_properties = individual_2[1]

        if individual_1_name not in result:
            result[individual_1_name] = {individual_2_name: {}}
        else:
            result[individual_1_name][individual_2_name] = {}

        if individual_1_name not in stats:
            stats[individual_1_name] = {"total_play_duration": 0,
                                  "max_play_duration": 0,
                                  "nb_play": 0,
                                  "nb_victories": 0,
                                  "nb_defeats": 0,
                                  "nb_vertices": 0
                                  }
        if individual_2_name not in stats:
            stats[individual_2_name] = {"total_play_duration": 0,
                                  "max_play_duration": 0,
                                  "nb_play": 0,
                                  "nb_victories": 0,
                                  "nb_defeats": 0,
                                  "nb_vertices": 0
                                  }
        # Parcours de toutes les cartes du tournois
        for game_map_name, game_map in MAPS.items():
            result[individual_1_name][individual_2_name][game_map_name] = [0, 0]

            # On joue les N_GAME parties
            for _ in range (0,N_GAME):

                # On créé les algo à partir des caractéristiques individuelles
                class algo_individual_1(AlgoNegMax_MPOO):
                    def __init__(self,q_p_s, q_s_p, name=None, debug_mode=False):
                        """ On ajoute des hyper paramètres qui permettent de différencier différents individus parmi ces algos
                        """
                        super().__init__(q_p_s, q_s_p, name=None, debug_mode=False)
                        self.depth_max =  individual_1_properties['depth_max']
                        self.nb_group_max = individual_1_properties['nb_group_max']
                        self.nb_cases = individual_1_properties['nb_cases']

                class algo_individual_2(AlgoNegMax_MPOO):
                    def __init__(self,q_p_s, q_s_p, name=None, debug_mode=False):
                        """ On ajoute des hyper paramètres qui permettent de différencier différents individus parmi ces algos
                        """
                        super().__init__(q_p_s, q_s_p, name=None, debug_mode=False)
                        self.depth_max =  individual_2_properties['depth_max']
                        self.nb_group_max = individual_2_properties['nb_group_max']
                        self.nb_cases = individual_2_properties['nb_cases']

                server_game = ServeurInterne(game_map, algo_individual_1, algo_individual_2, name1=individual_1_name, name2=individual_2_name,print_map=False)
                server_game.start()
                server_game.join()

                # Enregistrement des scores et des statistiques de la partie
                if server_game.winner:  # Si le joueur attaquant en premier gagne
                    result[individual_1_name][individual_2_name][game_map_name][0] += 1
                    stats[individual_1_name]["nb_victories"] += 1
                    stats[individual_2_name]["nb_defeats"] += 1
                else:  # Si le joueur défendant en premier gagne
                    result[individual_1_name][individual_2_name][game_map_name][1] += 1
                    stats[individual_1_name]["nb_defeats"] += 1
                    stats[individual_2_name]["nb_victories"] += 1

                stats[individual_1_name]["total_play_duration"] += server_game.total_play_duration_1
                stats[individual_2_name]["total_play_duration"] += server_game.total_play_duration_2
                stats[individual_1_name]["max_play_duration"] = max(stats[individual_1_name]["max_play_duration"],
                                                              server_game.max_play_duration_1)
                stats[individual_2_name]["max_play_duration"] = max(stats[individual_2_name]["max_play_duration"],
                                                              server_game.max_play_duration_2)
                stats[individual_1_name]["nb_play"] += server_game.nb_play_1
                stats[individual_2_name]["nb_play"] += server_game.nb_play_2

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
        print(f"\tDictionnaire de caractéristiques individuelles :")
        print(population_dic[algo_name])
        print(f"\tAverage play duration : \t\t\t\t{average_play_duration:.2f}s")
        print(f"\tMaximum duration of a play : \t\t\t{max_play_duration:.2f}s")
        print(f"\tNumber of vertices created per play : \t{vertices_created_per_round:.0f} vertices")

    return ranking[:nb_survivors]

if __name__ == "__main__":
    main()
