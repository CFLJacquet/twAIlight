from queue import Queue
from copy import deepcopy, copy

from Map import Map
from Cartes.Map_Map8 import Map8
from Cartes.Map_Ligne13 import MapLigne13

from Algorithmes.Sommet_du_jeu import SommetOutcome


class SommetDuJeu_Negascout(SommetOutcome):
    __vertices_created = 0
    __transposion_table = {}
    q_s_m = None
    q_m_s = None

    
    @classmethod
    def init_queues(cls, q_m_s, q_s_m):
        cls.q_m_s = q_m_s
        cls.q_s_m = q_s_m

    def __init__(self, is_vamp=None, depth=None, nb_group_max=None, stay_enabled=True, nb_cases=None, game_map=None, init_map=False):
        super().__init__(is_vamp, depth, game_map, init_map)
        self.nb_group_max = nb_group_max
        self.stay_enabled = stay_enabled
        self.nb_cases = nb_cases
        SommetDuJeu_Negascout.__vertices_created += 1
        if init_map:
            SommetDuJeu_Negascout.__transposion_table={}

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def transposition_table(cls):
        return cls.__transposion_table

    def get_score(self):
        if self.map.hash in SommetDuJeu_Negascout.__transposion_table:
            return SommetDuJeu_Negascout.__transposion_table[self.map.hash]
        else:
            return None, None

    def set_score(self, depth, score):
        SommetDuJeu_Negascout.__transposion_table[self.map.hash] = (depth, score)

    @property
    def i_children(self):
        for moves in self.map.i_next_relevant_moves(self.is_vamp, nb_group_max=self.nb_group_max, stay_enabled=self.stay_enabled, nb_cases=self.nb_cases[self.depth]):
            if not self.q_m_s is None and not self.q_m_s.empty(): break
            carte=copy(self.map)
            carte.most_probable_outcome(moves, self.is_vamp)
            child = SommetDuJeu_Negascout(
                is_vamp=not self.is_vamp,
                depth=self.depth-1,
                nb_group_max=self.nb_group_max,
                stay_enabled=self.stay_enabled,
                nb_cases=self.nb_cases,
                game_map=carte)
            child.previous_moves = moves
            yield child

    
    def negascout(self, alpha, beta):
        color = 1 if self.is_vamp else -1

        score_depth, score = self.get_score()
        if score is not None and score_depth <= self.depth:
            return score

        if self.map.game_over() or self.depth == 0:
            return color * self.evaluation

        is_first_child = True
        for child in self.i_children:
            if is_first_child:
                score = -1 * child.negascout(-1*beta, -1*alpha)
                is_first_child = False
            else:
                score = -1 * child.negascout(-1*alpha-1, -1*alpha)
                if alpha < score < beta:
                    score = -1 * child.negascout(-1*beta, -1*score)
            
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        
        self.set_score(self.depth, alpha)
        return alpha   

    def next_move(self):
        """
        :return: le prochain mouvement
        """
        color = 1 if self.is_vamp else -1
        alpha = -1000
        beta  =  1000 

        if self.map.game_over() or self.depth == 0:
            return color * self.evaluation, None

        is_first_child = True
        next_move = None
        for child in self.i_children:
            if is_first_child:
                score = -1 * child.negascout(-1*beta, -1*alpha)
                is_first_child = False
            else:
                score = -1 * child.negascout(-1*alpha-1, -1*alpha)
                if alpha < score < beta:
                    score = -1 * child.negascout(-1*beta, -1*score)
            
            #child.map.print_map()
            print(score, child.previous_moves, child.map.state_evaluation())
            if score > alpha:
                alpha = score
                next_move = child.previous_moves
            if alpha >= beta:
                break        
        
        if self.q_s_m is None:
            return next_move # For testing
        if self.q_m_s.empty():
            self.q_s_m.put(next_move)


if __name__ == '__main__':
    carte = Map8()

    next_move = next(carte.i_next_relevant_moves(
        False,
        stay_enabled=False,
        nb_group_max=4,
        nb_cases=8))

    carte.compute_moves(next_move)

    racine= SommetDuJeu_Negascout(
        depth=2,
        nb_group_max=2,
        stay_enabled=False,
        nb_cases=[None,2,4],#[None,1,3,2,4,3,4],
        game_map=carte,
        is_vamp=True,
        init_map=True)
    
    #carte.compute_moves(racine.next_move())
    carte.print_map()

    import cProfile
    cProfile.run('print(racine.next_move()); print(racine.nb_vertices_created())')