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

    def __init__(self, debug_mode=False):
        map_size = (3, 3)
        map_content = {}
        for i, j in product(range(map_size[0]), range(map_size[1])):
            map_content[(i, j)] = (0, 0, 0)
        map_content[(0, 1)] = (0, 1, 0)  # 1 vampire
        map_content[(2, 1)] = (0, 0, 1)  # 1 loup-garou
        super().__init__(map_size=map_size, initial_positions=map_content, debug_mode=debug_mode)


if __name__ == "__main__":
    carte = MapDust2()
    carte.print_map()
