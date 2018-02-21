"""
Run it to see the graph.

CMD : python battle_winrate_plot.py
"""
import numpy as np
import matplotlib.pyplot as plot

from Map import Map

tirage_battle=Map.tirage


def winrate(x):
    if x < 1:
        return x / 2
    elif x == 1:
        return 0.5
    else:
        return min(1, x - 0.5)


def intuitive(x):
    return x / 2


x1 = np.arange(0.0, 2.0, 0.05)

winrate_x1 = [winrate(x) for x in x1]
intuitive_x1 = [intuitive(x) for x in x1]

N_tirage=1000
test_battle_x1=[sum(tirage_battle(x,1) for _ in range(N_tirage))/N_tirage for x in x1]
error_95=[1.96*np.sqrt(test_battle_x1[i]*(1-test_battle_x1[i])/N_tirage) for i in range(len(x1))]

error_sup_95=[tirage+error for (tirage, error) in zip(test_battle_x1,error_95)]
error_inf_95=[tirage-error for (tirage, error) in zip(test_battle_x1,error_95)]
plot.plot(x1, winrate_x1, 'k', x1, intuitive_x1, 'b--')
plot.scatter(x1,test_battle_x1)
plot.plot(x1,error_sup_95,'g',x1,error_inf_95,'r')
plot.xlabel('E1/E2')
plot.ylabel('P : Probabilité de Gagner')
plot.title("Win rate (E1 = x * E2)")
plot.show()
