from collections import defaultdict
import random
import operator

class Map:
    def __init__(self,map_size=None, map_content=None,debug_mode=False):
        # Part Défaut Carte The Trap
        if map_size is None:
            map_size = (10, 5)
        self.size = map_size
        if map_content is None:
            map_content = {(0, 0): (0, 0, 0), (0, 1): (0, 0, 0), (0, 2): (0, 0, 0), (0, 3): (0, 0, 0),
                           (0, 4): (0, 0, 0), (1, 0): (0, 0, 0), (1, 1): (0, 0, 0), (1, 2): (0, 0, 0),
                           (1, 3): (0, 0, 0), (1, 4): (0, 0, 0), (2, 0): (0, 0, 0), (2, 1): (0, 0, 0),
                           (2, 2): (4, 0, 0), (2, 3): (0, 0, 0), (2, 4): (0, 0, 0), (3, 0): (0, 0, 0),
                           (3, 1): (0, 0, 0), (3, 2): (0, 0, 0), (3, 3): (0, 0, 0), (3, 4): (0, 0, 0),
                           (4, 0): (0, 0, 0), (4, 1): (0, 0, 4), (4, 2): (0, 0, 0), (4, 3): (0, 4, 0),
                           (4, 4): (0, 0, 0), (5, 0): (0, 0, 0), (5, 1): (0, 0, 0), (5, 2): (0, 0, 0),
                           (5, 3): (0, 0, 0), (5, 4): (0, 0, 0), (6, 0): (0, 0, 0), (6, 1): (0, 0, 0),
                           (6, 2): (0, 0, 0), (6, 3): (0, 0, 0), (6, 4): (0, 0, 0), (7, 0): (0, 0, 0),
                           (7, 1): (0, 0, 0), (7, 2): (0, 0, 0), (7, 3): (0, 0, 0), (7, 4): (0, 0, 0),
                           (8, 0): (0, 0, 0), (8, 1): (0, 0, 0), (8, 2): (0, 0, 0), (8, 3): (0, 0, 0),
                           (8, 4): (0, 0, 0), (9, 0): (2, 0, 0), (9, 1): (0, 0, 0), (9, 2): (1, 0, 0),
                           (9, 3): (0, 0, 0), (9, 4): (2, 0, 0)}
        self.content = map_content
        self.UPD = [] # Liste des changements lors d'un update de la carte
        self.debug_mode = debug_mode

    def home_vampire(self): # Case de départ des Vampires
        for x_y in self.content:
            if self.content[x_y][1]:
                return x_y

    def home_werewolf(self):# Case de départ des Loups-Garous
        for x_y in self.content:
            if self.content[x_y][2]:
                return x_y

    def MAP_command(self):
        elements = []
        n = 0
        for x_y in self.content:
            if sum(self.content[x_y]):
                elements.append((*x_y, *self.content[x_y]))
                n += 1
        return n, elements

    def update(self, positions):
        for i, j, n_hum, n_vamp, n_lg in positions:
            self.content[(i, j)] = (n_hum, n_vamp, n_lg)

    def update_and_compute(self, moves):
        self.UPD = []
        old_map_content = dict(self.content)
        is_vamp = True if self.content[(moves[0][0], moves[0][1])][1] else False
        # Emplacement des batailles, avec le nombre de représentants de notre espèce à cet endroit
        battles_to_run = defaultdict(int)
        for i, j, n, x, y in moves:
            # Free initial position
            if is_vamp:
                self.content[(i, j)] = (0, self.content[(i, j)][1] - n, 0)

            else:
                self.content[(i, j)] = (0, 0, self.content[(i, j)][2] - n)

            # Then move :
            # On enregistre les modifications sur les cases sans bataille

            n_hum, n_vamp, n_lg = self.content[(x, y)]
            # Empty cases
            if self.content[(x, y)] == (0, 0, 0):
                self.content[(x, y)] = (0, n * is_vamp, n * (not is_vamp))

            # Human cases
            if n_hum:
                battles_to_run[(x, y)] += n

            # Friend cases
            if n_vamp and is_vamp:
                self.content[(x, y)] = (0, (n + n_vamp), 0)
            elif n_lg and not is_vamp:
                self.content[(x, y)] = (0, 0, (n + n_lg))
            # Enemy cases
            if n_vamp and not is_vamp or n_lg and is_vamp:
                battles_to_run[(x, y)] += n

        for x, y in battles_to_run:
            n_att = battles_to_run[(x, y)]  # Nombre d'attaquants
            n_hum, n_vamp, n_lg = self.content[(x, y)]
            if n_hum:
                if self.debug_mode:
                    print("Bataille contre humains en ({},{})".format(x, y))
                if n_hum < n_att:  # victoire assurée
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} humains vs {} attaquants".format(n_att, n_hum))
                    n_conv = sum(self.tirage(n_att, n_hum) for _ in range(n_hum))
                    n_surv = sum(self.tirage(n_att, n_hum) for _ in range(n_att))
                    self.content[(x, y)] = (0, is_vamp * (n_surv + n_conv), (not is_vamp) * (n_surv + n_conv))
                    if self.debug_mode:
                        print("Victoire de l'attaquant ({} survivants, {} humains convertis)".format(n_surv, n_conv))
                else:
                    victory = self.tirage(n_att, n_hum)
                    if self.debug_mode:
                        print("Probabilité de victoire : {:.2f}% ({} humains vs {} attaquants)".format(
                            Map.proba_p(n_att, n_hum), n_hum, n_att))
                    if victory:
                        n_conv = sum(self.tirage(n_att, n_hum) for _ in range(n_hum))
                        n_surv = sum(self.tirage(n_att, n_hum) for _ in range(n_att))
                        self.content[(x, y)] = (0, is_vamp * (n_surv + n_conv), (not is_vamp) * (n_surv + n_conv))
                        if self.debug_mode:
                            print("Victoire de l'attaquant ({} survivants, {} humains convertis)".format(n_surv, n_conv))
                    else:  # défaite
                        n_surv = n_hum - sum(self.tirage(n_att, n_hum) for _ in range(n_hum))
                        self.content[(x, y)] = (n_surv, 0, 0)
                        if self.debug_mode:
                            print("Défaite de l'attaquant ({} humains survivants)".format(n_surv))
            else:
                if self.debug_mode:
                    print("Bataille entres monstres en ({},{})".format(x, y))
                n_def = n_lg if is_vamp else n_vamp
                if n_def * 1.5 < n_att:
                    if self.debug_mode:
                        print("Victoire assurée de l'attaquant ! {} attaquants vs {} défenseurs".format(n_att, n_def))
                    n_surv = sum(self.tirage(n_att, n_def) for _ in range(n_att))
                    self.content[(x, y)] = (0, is_vamp * n_surv, (not is_vamp) * n_surv)
                    if self.debug_mode:
                        print("Victoire de l'attaquant ! {} survivants".format(n_surv))
                else:
                    victory = self.tirage(n_att, n_def)

                    if self.debug_mode:
                        print("Probabilité de victoire : {:.2f}% ({} défenseurs vs {} attaquants)".format(
                            Map.proba_p(n_att, n_def), n_def, n_att))

                    if victory:
                        n_surv = sum(self.tirage(n_att, n_def) for _ in range(n_att))
                        self.content[(x, y)] = (0, is_vamp * (n_att + n_surv), (not is_vamp) * (n_att + n_surv))
                        if self.debug_mode:
                            print("Victoire de l'attaquant ! {} survivants".format(n_surv))
                    else:  # défaite
                        n_surv = n_def - sum(self.tirage(n_att, n_def) for _ in range(n_def))
                        self.content[(x, y)] = (0, (not is_vamp) * n_surv, is_vamp * n_surv)
                        if self.debug_mode:
                            print("Défaite de l'attaquant ({} défenseurs survivants)".format(n_surv))

        for (i, j), (n_hum, n_vamp, n_lg) in self.content.items():
            if old_map_content[(i, j)] != (n_hum, n_vamp, n_lg):
                self.UPD.append((i, j, n_hum, n_vamp, n_lg))

    @staticmethod
    def proba_p(n_att, n_def):
        x = n_att / n_def
        if x < 1:
            return x / 2
        elif x == 1:
            return 0.5
        else:
            return min(1, x - 0.5)
    @staticmethod
    def tirage(n_att, n_def):
        probabilite = Map.proba_p(n_att, n_def)
        return (random.random() / probabilite) <= 1

    def populations(self):
        n_hum, n_vamp, n_lg = 0, 0, 0
        for i_hum, i_vamp, i_lg in self.content.values():
            n_hum += i_hum
            n_vamp += i_vamp
            n_lg += i_lg
        return n_hum, n_vamp, n_lg

    def game_over(self):
        _, n_vamp, n_lg = self.populations()
        if n_vamp == 0 or n_lg == 0:
            return True
        return False

    def winner(self):
        _, n_vamp, n_lg = self.populations()
        if n_vamp:
            return True
        elif n_lg:
            return False
        else:  # Egalité
            return None

    def print_map(self):
        race = ("H", "V", "W")
        for j in range(self.size[1]): # For each row
            print("_" * (self.size[0] * 5))
            for i in range(self.size[0]): # For each cell
                cell_text = "|" + " "*4
                if (i, j) in self.content:
                    for r, k in enumerate(self.content[(i, j)]):
                        if k:
                            cell_text = cell_text.replace(" "*3, " {}{}".format(k, race[r]))
                print(cell_text, end='')
            print("|")
        print("_" * (self.size[0] * 5))

        # Score
        total_races = tuple(map(sum, zip(*list(self.content.values()))))
        print(
            "Scores:\t\tVampires {} | {} Werewolves\n\tRemaining Humans: {}".format(
                total_races[1], total_races[2], total_races[0]))


if __name__ == "__main__":
    carte = Map()
    carte.print_map()
    carte.update_and_compute([(4, 1, 3, 3, 2), (4, 1, 1, 3, 2)])
    carte.print_map()
