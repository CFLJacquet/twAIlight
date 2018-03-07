from twAIlight.Map import Map


class MapTheTrap(Map):
    """

    Carte the Trap (donnée par le projet)
    __________________________________________________
    |    |    |    |    |    |    |    |    |    | 2H |
    __________________________________________________
    |    |    |    |    | 4W |    |    |    |    |    |
    __________________________________________________
    |    |    | 4H |    |    |    |    |    |    | 1H |
    __________________________________________________
    |    |    |    |    | 4V |    |    |    |    |    |
    __________________________________________________
    |    |    |    |    |    |    |    |    |    | 2H |
    __________________________________________________
    """

    def __init__(self, debug_mode=False):
        map_size = (10, 5)
        initial_positions = [(2, 2, 4, 0, 0),
                             (4, 1, 0, 0, 4),
                             (4, 3, 0, 4, 0),
                             (9, 0, 2, 0, 0),
                             (9, 2, 1, 0, 0),
                             (9, 4, 2, 0, 0)]

        super().__init__(map_size=map_size, initial_positions=initial_positions, debug_mode=debug_mode)


if __name__ == "__main__":
    carte = MapTheTrap()
    carte.print_map()
