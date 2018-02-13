from itertools import product

"""
On cherche à vérifier si on compte bien le nombre de façon de répartir au plus a chaussettes dans b tiroirs.
"""


def count_set(a, b):
    """ FOnction naïve, qui donne le bon résutat pour exactement a chaussettes

    :param a: nombre de chaussette
    :param b: nombre de tiroirs
    :return: Nombre de configurations possibles
    """
    pos_set = set()
    for tuple in product(range(a + 1), repeat=b):
        if sum(tuple) == a:
            pos_set.add(tuple)
    return len(pos_set)

def sum_count_set(a,b):
    """ Fonction naïve qui donne le bon résultat pour au plus a chaussettes

    :param a: nombre de chaussette
    :param b: nombre de tiroirs
    :return: Nombre de configurations possibles
    """
    sum_count=0
    for a_ in range(1, a+1):
        sum_count+=count_set(a_,b)
    return sum_count

def count_conj(a, b):
    """ Fonction conjecturée, récursive, pour exactement a chaussettes

    :param a: nombre de chaussette
    :param b: nombre de tiroirs
    :return: Nombre de configurations possibles
    """
    if a == 1:
        return b
    elif b == 1:
        return 1
    else:
        return count_conj(a - 1, b) + count_conj(a, b - 1)


def sum_count(a, b):
    """ Somme à partir de la fonction récursive, pour au plus a chaussettes

    :param a: nombre de chaussette
    :param b: nombre de tiroirs
    :return: Nombre de configurations possibles
    """
    sum_c = 0

    for a_ in range(1, a + 1):
        sum_c += count_conj(a_, b)
    return sum_c


def dynamic_count(a, b):
    """ Fonction conjecturée, en programmation dynamique, pour au plus a chaussettes

    :param a: nombre de chaussette
    :param b: nombre de tiroirs
    :return: Nombre de configurations possibles
    """
    dict_res = {}
    for i in range(1, a+ 1):
        dict_res[(i, 1)] = 1
    for j in range(2, b + 1):
        dict_res[(1, j)] = j

    for b_ in range(2, b + 1):
        for a_ in range(2, a + 1):
            dict_res[(a_, b_)] = dict_res[(a_ - 1, b_)] + dict_res[(a_, b_ - 1)]
    sum_c=0
    for a_ in range(1,a+1):
        sum_c+=dict_res[(a_,b)]

    return sum_c


def main():
    equality=True
    for a, b in product(range(2, 5), repeat=2):

        if dynamic_count(a, b)!=sum_count_set(a,b) or dynamic_count(a, b)!=sum_count(a, b):
            print("Problem !")
            print(a, b, sum_count_set(a,b), sum_count(a, b),dynamic_count(a, b))
            equality=False
            break
    if equality:
        print("Test passed !")
if __name__ == "__main__":
    main()
    import cProfile
    cProfile.run("sum_count(10,18)")
    cProfile.run("dynamic_count(10,18)")
