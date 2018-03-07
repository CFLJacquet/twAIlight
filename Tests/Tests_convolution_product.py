import time
from itertools import product
import numpy as np
from scipy import signal

from twAIlight.Map import Map
from twAIlight.Cartes.Map_Ligne13 import MapLigne13

carte = MapLigne13()

# Création de matrice 1 : Pure Python
start_time = time.time()
for _ in range(1000):
    matrix1 = [[carte.content[i,j][0] for j in range(carte.size[1])] for i in range(carte.size[0])]
end_time = time.time()
print(end_time - start_time)


# Création de matrice 2 : Pure Numpy
start_time = time.time()
for _ in range(1000):
    matrix2 = np.reshape(np.array(list(carte.content.values()))[:,0], carte.size)
end_time = time.time()
print(end_time - start_time)


# Création de matrice 3 : Mix
start_time = time.time()
for _ in range(1000):
    matrix3 = np.array([[carte.content[i,j][0] for j in range(carte.size[1])] for i in range(carte.size[0])])
end_time = time.time()
print(end_time - start_time)

# La création 1 Pur Python gagne de 20% environ


kernel = [[1,1,1], [1,2,1], [1,1,1]]
# Produit de convolution 1: Full Python
start_time = time.time()
for _ in range(1000):
    conv1 = [[0 for _ in range(carte.size[1])] for _ in range(carte.size[0])]
    for i,j in product(range(len(matrix1)), range(len(matrix1[0]))):
        for x in range(len(kernel)):
            for y in range(len(kernel[0])):
                if 0 <= i+(x-1) < len(matrix1) and 0 <= j+(y-1) < len(matrix1[0]):
                    conv1[i][j] += kernel[x][y] * matrix1[i+(x-1)][j+(y-1)]
end_time = time.time()
print(end_time - start_time)

# Produit de convolution 2: Full numpy
start_time = time.time()
for _ in range(1000):
    conv2 = signal.convolve2d(matrix2, kernel, mode="same")
end_time = time.time()
print(end_time - start_time)

# Produit de convolution 3: Full numpy
start_time = time.time()
for _ in range(1000):
    conv2 = signal.convolve2d(matrix3, kernel, mode="same")
end_time = time.time()
print(end_time - start_time)