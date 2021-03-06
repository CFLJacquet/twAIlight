from Map import Map


class Map8(Map):
    """

    Carte proposée sur le repo github avec le serveur du projet en Go

    ________________________________________
    | 5H | 14H| 14H| 7H | 6H |    | 3H |    |
    ________________________________________
    | 1H | 9H |    | 12H|    | 17H| 14H|    |
    ________________________________________
    | 14H|    | 5H |    | 13H| 14H|    |    |
    ________________________________________
    | 8H | 5W | 3H | 16H| 3H |    |    | 8H |
    ________________________________________
    | 8H |    |    | 3H | 16H| 3H | 5V | 8H |
    ________________________________________
    |    |    | 14H| 13H|    | 5H |    | 13H|
    ________________________________________
    |    | 14H| 17H|    | 12H|    | 9H | 1H |
    ________________________________________
    |    | 3H |    | 6H | 7H | 14H| 14H| 5H |
    ________________________________________

    """

    def __init__(self, debug_mode=False):
        map_size = (8, 8)
        initial_positions = [(0, 0, 5, 0, 0),
                             (0, 1, 1, 0, 0),
                             (0, 2, 14, 0, 0),
                             (0, 3, 8, 0, 0),
                             (0, 4, 8, 0, 0),
                             (1, 0, 14, 0, 0),
                             (1, 1, 9, 0, 0),
                             (1, 3, 0, 0, 5),
                             (1, 6, 14, 0, 0),
                             (1, 7, 3, 0, 0),
                             (2, 0, 14, 0, 0),
                             (2, 2, 5, 0, 0),
                             (2, 3, 3, 0, 0),
                             (2, 5, 14, 0, 0),
                             (2, 6, 17, 0, 0),
                             (3, 0, 7, 0, 0),
                             (3, 1, 12, 0, 0),
                             (3, 3, 16, 0, 0),
                             (3, 4, 3, 0, 0),
                             (3, 5, 13, 0, 0),
                             (3, 7, 6, 0, 0),
                             (4, 0, 6, 0, 0),
                             (4, 2, 13, 0, 0),
                             (4, 3, 3, 0, 0),
                             (4, 4, 16, 0, 0),
                             (4, 6, 12, 0, 0),
                             (4, 7, 7, 0, 0),
                             (5, 1, 17, 0, 0),
                             (5, 2, 14, 0, 0),
                             (5, 4, 3, 0, 0),
                             (5, 5, 5, 0, 0),
                             (5, 7, 14, 0, 0),
                             (6, 0, 3, 0, 0),
                             (6, 1, 14, 0, 0),
                             (6, 4, 0, 5, 0),
                             (6, 6, 9, 0, 0),
                             (6, 7, 14, 0, 0),
                             (7, 3, 8, 0, 0),
                             (7, 4, 8, 0, 0),
                             (7, 5, 13, 0, 0),
                             (7, 6, 1, 0, 0),
                             (7, 7, 5, 0, 0)]

        super().__init__(map_size=map_size, initial_positions=initial_positions, debug_mode=debug_mode)


if __name__ == "__main__":
    carte = Map8()
    carte.update_content([(5,3,0,100,0),(5,5,0,10,0)])
    carte.print_map()
    import cProfile
    cProfile.run("list(carte.i_next_relevant_moves_3(is_vamp=True))")
