from itertools import product


def count_set(a, b):
    pos_set = set()
    for tuple in product(range(a + 1), repeat=b):
        if sum(tuple) == a:
            pos_set.add(tuple)
    return len(pos_set)


def count_conj(a, b):
    if a == 1:
        return b
    elif b == 1:
        return 1
    else:
        return count_conj(a - 1, b) + count_conj(a, b - 1)


def sum_count(a, b):
    sum_c = 0

    for a_ in range(1, a + 1):
        sum_c += count_conj(a_, b)
    return sum_c


def new_sum_count(a, b):
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
    for a, b in product(range(1, 10), repeat=2):

        if new_sum_count(a,b)!=sum_count(a,b):
            print(a,b,new_sum_count(a,b),count_conj(a,b))
            break



if __name__ == "__main__":
    main()
    import cProfile
    cProfile.run("sum_count(10,18)")
    cProfile.run("new_sum_count(10,18)")
