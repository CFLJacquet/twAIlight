"""
Run it to see the graph.

CMD : python battle_winrate_plot.py
"""
import numpy as np
import matplotlib.pyplot as plot

def winrate(x):
    if x < 1:
        return x/2
    elif x == 1:
        return 0.5
    else:
        return min(1, x-0.5)

def intuitive(x):
    return x/2

x1 = np.arange(0.0, 2.0, 0.05)

winrate_x1 = [winrate(x) for x in x1]
intuitive_x1 = [intuitive(x) for x in x1]

plot.plot(x1, winrate_x1, 'r', x1, intuitive_x1, 'b--')
plot.xlabel('E1')
plot.ylabel('E2')
plot.title("Win rate (E1 = x * E2)")
plot.show()
