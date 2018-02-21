from itertools import product
from cProfile import run as run_profile


def repartition_produit_cartesien(pop_of_monsters, n_case):

    repartitions=set()
    for repartition in product(range(pop_of_monsters + 1), repeat=n_case):
        # Si on a réparti au plus le nombre de monstres de la case initiale
        if sum(repartition) <= pop_of_monsters:
            repartitions.add(repartition)
    return repartitions

def repartitions_recursive(pop_of_monster, n_case):
    repartitions=list()

    if pop_of_monster ==0:
        return [[0]*n_case]
    if n_case==1:
        for i in range(pop_of_monster+1):
            repartitions.append([i])
        return repartitions
    for pop_first_case in range(pop_of_monster+1):
        for rep in repartitions_recursive(pop_of_monster-pop_first_case, n_case-1):
            new_rep=[pop_first_case]+rep
            repartitions.append(new_rep)
    return repartitions

if __name__ == '__main__':
    run_profile("repartition_produit_cartesien(6, 8)")
    run_profile("repartitions_recursive(6, 8)")
    print(repartition_produit_cartesien(2,3))
    print(repartitions_recursive(2,3))
    print(len(repartition_produit_cartesien(6, 8)))
    print(len(repartitions_recursive(6, 8)))
