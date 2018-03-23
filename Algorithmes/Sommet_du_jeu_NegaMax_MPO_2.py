from queue import Queue
from copy import deepcopy, copy

from twAIlight.Map import Map
from twAIlight.Cartes.Map_Map8 import Map8
from twAIlight.Cartes.Map_Ligne13 import MapLigne13

from twAIlight.Algorithmes.Sommet_du_jeu import SommetOutcome

class SommetDuJeu_NegaMax_MPOO(SommetOutcome):
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
        SommetDuJeu_NegaMax_MPOO.__vertices_created += 1
        if init_map:
            SommetDuJeu_NegaMax_MPOO.__transposion_table={}

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

    @classmethod
    def transposition_table(cls):
        return cls.__transposion_table

    def get_score(self):
        if self.map.hash in SommetDuJeu_NegaMax_MPOO.__transposion_table:
            return SommetDuJeu_NegaMax_MPOO.__transposion_table[self.map.hash]
        else:
            return None, None, None

    def set_score_tt(self, flag, depth, score):
        SommetDuJeu_NegaMax_MPOO.__transposion_table[self.map.hash] = (flag, depth, score)

    @property
    def i_children(self):
        for moves in self.map.i_next_relevant_moves_3(self.is_vamp):
            # Vérification du timeout
            if not self.q_m_s is None and not self.q_m_s.empty(): break
            
            # Création du sommet fils
            carte=copy(self.map)
            carte.most_probable_outcome(moves, self.is_vamp)
            
            child = SommetDuJeu_NegaMax_MPOO(
                is_vamp=not self.is_vamp,
                depth=self.depth-1,
                game_map=carte)
            child.previous_moves = moves
            yield child

    def negamax(self, alpha, beta):
        alphaOrig = alpha
        color = 1 if self.is_vamp else -1
        flag, depth, score = self.get_score()

        if flag is not None:

            if depth >= self.depth:
                if flag == "exact":
                    return score
                elif flag == "lowerbound":
                    if alpha is not None:
                        if score > alpha:
                            alpha = score
                    else:
                        alpha = score
                elif flag == "upperbound":
                    if beta is not None:
                        if score < beta:
                            beta = score
                    else:
                        beta = score
                if alpha is not None and beta is not None:
                    if alpha >= beta:
                        return score

        if self.map.game_over() or self.depth == 0:
            return color * self.evaluation

        bestvalue = None
        for child in self.i_children:
            if alpha is None and beta is None:
                v = - child.negamax(None, None)
            elif beta is None:
                v = - child.negamax(None, -1*alpha)
            elif alpha is None:
                v = - child.negamax(-1*beta, None)
            else:
                v = - child.negamax(-1*beta, -1*alpha)

            # On prend le max entre bestvalue et v
            if bestvalue is None:
                bestvalue = v
            elif bestvalue < v:
                bestvalue = v

            if alpha is None:
                alpha = v
            elif alpha < v:
                alpha = v

            if beta is not None:
                if alpha >= beta:
                    break

        if bestvalue is None: return None

        flag = None
        if alphaOrig is not None:
            if bestvalue <= alphaOrig:
                flag = "upperbound"
        if beta is not None:
            if bestvalue >= beta:
                flag = "lowerbound"
        if flag is None:
            flag = "exact"

        self.set_score_tt(flag, self.depth, bestvalue)

        return bestvalue

    def next_move(self):
        """ Renvoie le meilleur mouvement à faire.
        C'est la fonction Minimax-Decision du cours 4 s.54

        Parcourt le graphe en DFS

        :return: le prochain mouvement
        """
        alpha = None
        beta = None
        color = 1 if self.is_vamp else -1

        if self.map.game_over() or self.depth == 0:
            return color * self.evaluation

        bestvalue = None
        next_move = None
        for child in self.i_children:
            if alpha is None and beta is None:
                v = - child.negamax(None, None)
            elif beta is None:
                v = - child.negamax(None, -1*alpha)
            elif alpha is None:
                v = - child.negamax(-1*beta, None)
            else:
                v = - child.negamax(-1*beta, -1*alpha)

            # On prend le max entre bestvalue et v
            if bestvalue is None:
                bestvalue = v
                next_move = child.previous_moves
            elif bestvalue < v:
                bestvalue = v
                next_move = child.previous_moves

            
            #print(v, child.previous_moves, child.map.state_evaluation())
            if alpha is None:
                alpha = v
            elif alpha < v:
                alpha = v

            if beta is not None:
                if alpha >= beta:
                    break

        if self.q_s_m is None:
            return next_move # For testing
        if self.q_m_s.empty():
            self.q_s_m.put(next_move)

    def next_move_old(self):
        """ Renvoie le meilleur mouvement à faire.
        C'est la fonction Minimax-Decision du cours 4 s.54

        Parcourt le graphe en DFS

        :return: le prochain mouvement
        """
        # On sélectione le noeud fils selon sa race

        next_child = min(self.children,
                         key=lambda child: child.negamax(alpha=None, beta=None))
        # On retourne le dernier mouvement pour arriver à ce sommet fils
        #if not self.is_vamp:
        #    for child in self._children: print(child.previous_moves,child.map.state_evaluation(), child.negamax(None, None))
        next_move = next_child.previous_moves
        

        if self.q_s_m is None:
            return next_move # For testing
        if self.q_m_s.empty():
            self.q_s_m.put(next_move)

if __name__ == '__main__':
    carte = MapLigne13()

    next_moves = [
        [(0,20,10,1,19)],
        [(20,20,10,19,19)],
        [(1,19,5,2,19),(1,19,6,2,18)],
        [(19,19,5,20,18),(19,19,6,18,18)]
    ]
    for next_move in next_moves:
        carte.compute_moves(next_move)
    
    racine= SommetDuJeu_NegaMax_MPOO(
        depth=6,
        game_map=carte,
        is_vamp=True,
        init_map=True)
    
    #carte.compute_moves(racine.next_move())
    carte.print_map()

    import cProfile
    cProfile.run('print(racine.next_move()); print(racine.nb_vertices_created())')