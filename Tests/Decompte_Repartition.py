from itertools import product


def count_set(a,b):
    pos_set=set()
    for tuple in product(range(a+1),repeat=b):
        if sum(tuple)==a:
            pos_set.add(tuple)
    return len(pos_set)

def count_conj(a,b):
    if a==1:
        return b
    elif b==1:
        return 1
    else:
        return count_conj(a-1, b)+count_conj(a,b-1)

def main():
    for a,b in product(range(1,10),repeat=2):
        print(count_set(a,b))
        print(count_conj(a,b))

if __name__=="__main__":
    #main()
    import cProfile
    cProfile.run("count_set(3,8)")
    cProfile.run("count_conj(3,8)")
