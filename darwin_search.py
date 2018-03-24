from itertools import combinations
import math
import operator
import random

from Serveur_Interne import ServeurInterne

from Algorithmes.Algo_NegaMax_MPOO import AlgoNegMax_MPOO

from Cartes.Map_Ligne13 import MapLigne13
from Cartes.Map_Dust2 import MapDust2
from Cartes.Map_TheTrap import MapTheTrap
from Cartes.Map_Map8 import Map8
from Cartes.Map_Random import MapRandom

N_GAME = 1 # nombre de parties par carte (chaque carte est appelée dans une pool)
POOL_SIZE = 20 # Taille des pools de combats
N_SURVIVORS = 5 # Nombre de survivants que l'on garde dans chaque pool à la suite des combats (on garde Top N_SURVIVORS sur POOL_SIZE individus)
TIMER = 200 # Nombre d'itérations

def main():
    # Declaration des caractéristiques possibles de la population
    range_parameters = {'depth_max': [3,5,7,9],'nb_group_max': [2,3,4,5],'nb_cases':[[1,1,1,1,1,1],[1,2,1,5,1,1]]}

    # Produit cartésien pour générer tous les individus possibles
    tuned_parameters = [{'depth_max':a, 'nb_group_max':b, 'nb_cases':d} for a in range_parameters['depth_max'] for b in range_parameters['nb_group_max'] for d in range_parameters['nb_cases']]
    # Generation de la population à explorer. Les individus sont numérotés de 1 à n
    population = [(i,tuned_parameters[i]) for i in range(0,len(tuned_parameters))]
    population_dic = {i:tuned_parameters[i] for i in range(0,len(tuned_parameters))}

    population_size = len(population)
    print("There are %i individuals " % population_size)
    pool =[]

    # Initialisation du decompte du nombre de victoire en pool
    historical_presence={}
    for s in range(0,population_size):
        historical_presence[s] = 0

    # Initialisation du decompte d'ajout à la pool
    ajout={}
    for s in range(0,population_size):
        ajout[s] = 0

    # Iterations
    print("Nombre de combats à faire: %i " %(N_GAME*TIMER*math.factorial(POOL_SIZE)/(math.factorial(2)*math.factorial(POOL_SIZE-2))))

    for epoch in range(TIMER):
        print("This is epoch %i" %epoch)

        if epoch==0:
        # Initialisation de la pool aléatoire
            for i in range(0, POOL_SIZE):
                rand = random.randint(0, population_size - 1)
                pool.append(population[rand])
                ajout[rand] += 1

        # On ne garde que les individus qui survivent au tournoi (cf fonction tournoi en dessous)
        individual_survivors = tournoi(pool,population_dic,nb_survivors=N_SURVIVORS)
        pool=[]
        for s in individual_survivors:
            pool.append(population[s])
            historical_presence[s]+=1

        # On remplit les places restantes dans la pool aléatoirement pour challenger les vainqueurs
        for i in range (N_SURVIVORS,POOL_SIZE-N_SURVIVORS+1):
            rand = individual_survivors[0]
            while rand in individual_survivors:
                rand = random.randint(0, population_size - 1)
            pool.append(population[rand])
            ajout[rand] += 1


    # On peut aussi choisir de regarder les algos restés le plus longtemps
    print("\n########  Algorithmes le plus vus en pool (normalisation par le nombre d'ajout au pool)")
    sorted_hist_presence = sorted(historical_presence.items(), key=operator.itemgetter(1),reverse=True)
    for elem in sorted_hist_presence[:5]:
        if ajout[elem[0]]!=0:
            print("\nAlgo numero %i : vu %i en pool pour %i ajouts " %(elem[0],elem[1],ajout[elem[0]]))
        else:
            print("%i n'a jamais été tiré et ajouté à la pool ! " %elem[0])

    # On peut choisir de regarder les algos survivants
    print("\n######## Nombre de combats: %i" %(TIMER*math.factorial(POOL_SIZE)/(math.factorial(2)*math.factorial(POOL_SIZE-2))))
    print("Classement des top %i algorithmes sur %i" %(N_SURVIVORS,population_size))
    for surv in individual_survivors:
        print("L'algorithme %i (présent pendant %i tours (sur %i) dans les survivants (TOP %i d'une pool)" %(surv,historical_presence[surv],TIMER,N_SURVIVORS))
        print("Ses caractéristiques sont:")
        print(population_dic[surv])

def tournoi(pool,population_dic,nb_survivors=10):
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
        #"Map8": Map8,
        # "TheTrap":MapTheTrap,
        "CarteAléatoire":MapRandom}

    # Dictionnaires des algorithmes de décision : nom de l'algo --> algo (classe)

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

                stats[individual_1_name]["nb_vertices"] += algo_individual_1.nb_vertices_created()
                stats[individual_2_name]["nb_vertices"] += algo_individual_2.nb_vertices_created()

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