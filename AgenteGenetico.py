import math
import numpy as np

class Cidade:
    def __init__(self, X: float, Y: float):
        self.X = X
        self.Y = Y


def calcularAptidao(cromossomo):
    distancia_total = 0
    n = len(cromossomo)

    for i in range(n):
        atual = cromossomo[i]
        proxima = cromossomo[(i + 1) % n]

        distancia_total += math.sqrt(
            math.pow(proxima.X - atual.X, 2) +
            math.pow(proxima.Y - atual.Y, 2)
        )

    return distancia_total


x, y = np.loadtxt("cidades.mat")

cidades = []
for i in range(len(x)):
    cidades.append(Cidade(x[i], y[i]))


populacao = []
for i in range(20):
    cromossomo = np.random.permutation(cidades)
    populacao.append(cromossomo)

avaliados = []
for cromossomo in (populacao):
    avaliados.append(cromossomo, calcularAptidao(cromossomo))

ordenados = avaliados.sort()