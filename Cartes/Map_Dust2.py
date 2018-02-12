from itertools import product
from Map import Map


class MapDust2(Map):
    """

    Carte simple avec 1 vampire et 1 loup garou, carte par défaut dans Maps
    _______________
    |    |    |    |
    _______________
    | 1V |    | 1W |
    _______________
    |    |    |    |
    _______________
    """




if __name__ == "__main__":
    carte = MapDust2()
    carte.print_map()
