"""Geracao de instancias do Problema do Caixeiro Viajante."""

import numpy as np

def gera_caixeiro_viajante(num_cidades, tam_grade=100, seed=None):

    rng = np.random.default_rng(seed)
    coordenadas = rng.uniform(0, tam_grade, size=(num_cidades, 2))

    diff = coordenadas[:, np.newaxis, :] - coordenadas[np.newaxis, :, :]
    matriz_dist = np.sqrt(np.sum(diff ** 2, axis=-1))

    return coordenadas, matriz_dist


if __name__ == "__main__":
    cidades, matriz = gera_caixeiro_viajante(num_cidades=5, tam_grade=100, seed=42)
    print("Coordenadas:\n", cidades)
    print("\nDistancias:\n", matriz)