import random
from itertools import product

from Map import Map


class MapRandom(Map):
    """

    Carte Aléatoire #MagieNoire
    """

    __SIZE_MAX = 20
    __HUM_MAX = 10
    __MONSTER_MAX = 10

    def __init__(self, debug_mode=False):
        x_max = random.randint(1, MapRandom.__SIZE_MAX)
        y_max = random.randint(1, MapRandom.__SIZE_MAX)
        map_size = (x_max, y_max)

        initial_positions = []

        free_case = set(product(range(x_max), range(y_max)))

        for _ in range(random.randint(1, x_max * y_max // 2 + 1)):
            i_j = random.choice([*product(range(x_max), range(y_max))])
            free_case.discard((i_j))
            n_hum = random.randint(1, MapRandom.__MONSTER_MAX)
            initial_positions.append((*i_j, n_hum, 0, 0))

        n_monsters = random.randint(1, MapRandom.__MONSTER_MAX)

        vamp_home = random.choice(list(free_case))
        initial_positions.append((*vamp_home, 0, n_monsters, 0))
        free_case.discard(vamp_home)

        lg_home = random.choice(list(free_case))
        initial_positions.append((*lg_home, 0, 0, n_monsters))

        super().__init__(map_size=map_size, initial_positions=initial_positions, debug_mode=debug_mode)


if __name__ == "__main__":
    carte = MapRandom()
    carte.print_map()
