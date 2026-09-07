import numpy as np

"""GERADOR DE GRAFO PRO CAIXEIRO VIAJANTE"""

def gera_caixeiro_viajante(num_cidades, tam_grade=100, seed=None):
    if seed is not None:
        np.random.seed(seed)
        
    coordenadas = np.random.uniform(0, tam_grade, size=(num_cidades, 2))

    diff = coordenadas[:, np.newaxis, :] - coordenadas[np.newaxis, :, :]
    matriz_dist = np.sqrt(np.sum(diff ** 2, axis=-1))
    
    return coordenadas, matriz_dist

# Exemplo
cidades, matriz = gera_caixeiro_viajante(num_cidades=5, tam_grade=100, seed=42)

print("Coordenadas:\n", cidades)
print("\nDistancias:\n", matriz)