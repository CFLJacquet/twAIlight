from collections import defaultdict
import random

class MapInterne:
    def __init__(self):
        # Carte The Trap
        self.map_size = (5, 10)
        self.map_content = {(0, 0): (0, 0, 0), (0, 1): (0, 0, 0), (0, 2): (0, 0, 0), (0, 3): (0, 0, 0),
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
        self.UDP = []
        self.home_1 = self.home_1()
        self.home_2 = self.home_2()

    def home_1(self):
        # Par défaut, le premier joueur est un vampire
        for x_y in self.map_content:
            if self.map_content[x_y][1]:
                return x_y

    def home_2(self):
        # Par défaut, le deuxième joueur est un loup-garou
        for x_y in self.map_content:
            if self.map_content[x_y][2]:
                return x_y

    def MAP_command(self):
        elements = []
        n = 0
        for x_y in self.map_content:
            if sum(self.map_content[x_y]):
                elements.append((*x_y, *self.map_content[x_y]))
                n += 1
        return n, elements

    def update(self, moves):
        self.UDP = []
        is_vamp = True if self.map_content[(moves[0][0], moves[0][1])][1] else False
        battles_to_run = defaultdict(
            int)  # Emplacement des batailles, avec le nombre de représentants de notre espèce à cet endroit
        for i, j, n, x, y in moves:
            # Free initial position
            if is_vamp:
                self.map_content[(i, j)] = (0, self.map_content[(i, j)][1] - n, 0)

            else:
                self.map_content[(x, y)] = (0, 0, self.map_content[(i, j)][2] - n)
            self.UDP.append((i, j, *self.map_content[(i, j)]))

            # Then move :
            # On enregistre les modifications sur les cases sans bataille
            # Empty cases
            if self.map_content[(x, y)] == (0, 0, 0):
                self.map_content[(x, y)] = (0, n * is_vamp, n * (not is_vamp))
                self.UDP.append((x, y, *self.map_content[(x, y)]))
            # Human cases
            n_hum, n_vamp, n_lg = self.map_content[(x, y)]
            if n_hum:
                battles_to_run[(x, y)] += n

            # Friend cases
            if n_vamp and is_vamp:
                self.map_content[(i, j)] = (0, (n + n_vamp), 0)
                self.UDP.append((x, y, *self.map_content[(x, y)]))
            elif n_lg and not is_vamp:
                self.map_content[(i, j)] = (0, 0, (n + n_lg))
                self.UDP.append((x, y, *self.map_content[(x, y)]))
            # Enemy cases
            if n_vamp and not is_vamp or n_lg and is_vamp:
                battles_to_run[(x, y)] += n

        for x, y in battles_to_run:
            n_att = battles_to_run[(x, y)]
            n_hum, n_vamp, n_lg = self.map_content[(x, y)]
            if n_hum:
                if n_hum < n_att:
                    self.map_content[(x, y)] = (0, is_vamp * (n_att + n_hum), (not is_vamp) * (n_att + n_hum))
                else:
                    victory = self.tirage(n_att, n_hum)
                    if victory:
                        n_surv = sum(self.tirage(n_att, n_hum) for _ in range(n_hum))
                        self.map_content[(x, y)] = (0, is_vamp * (n_att + n_surv), (not is_vamp) * (n_att + n_surv))
                    else:  # défaite
                        n_surv = n_hum - sum(self.tirage(n_att, n_hum) for _ in range(n_hum))
                        self.map_content[(x, y)] = (n_surv, 0, 0)
            else:
                n_def = n_lg if is_vamp else n_vamp
                if n_def * 1.5 < n_att:
                    self.map_content[(x, y)] = (0, is_vamp * (n_att + n_def), (not is_vamp) * (n_att + n_def))
                else:
                    victory = self.tirage(n_att, n_def)
                    if victory:
                        n_surv = sum(self.tirage(n_att, n_def) for _ in range(n_def))
                        self.map_content[(x, y)] = (0, is_vamp * (n_att + n_surv), (not is_vamp) * (n_att + n_surv))
                    else:  # défaite
                        n_surv = n_hum - sum(self.tirage(n_att, n_def) for _ in range(n_def))
                        self.map_content[(x, y)] = (0, (not is_vamp) * n_surv, is_vamp * n_surv)
            self.UDP.append((x, y, *self.map_content[(x, y)]))

    @staticmethod
    def proba_p(n_att, n_def):
        x = n_att / n_def
        if x < 1:
            return x / 2
        elif x == 1:
            return 0.5
        else:
            return min(1, x - 0.5)

    def tirage(self, n_att, n_def):
        probabilite = Map.proba_p(n_att, n_def)
        return (random.random() / probabilite) <= 1

    def populations(self):
        n_hum, n_vamp, n_lg = 0, 0, 0
        for i_hum, i_vamp, i_lg in self.map_content.values():
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
        if n_lg:
            return True
        elif n_vamp:
            return False
        else:  # Egalité
            return None

if __name__=="__main__":
    pass