"""Bateria de experimentos.

Roda a Tempera Simulada em varios tamanhos de instancia e sementes,
comparando as duas estruturas de vizinhanca (2-opt vs swap), e salva
tudo em um CSV

python run_experimentos.py
"""

from __future__ import annotations

import csv
import os

from utils.grafo import gera_caixeiro_viajante
from sa_tsp import SAConfig, resolver

DIR_SAIDA = os.path.join(os.path.dirname(__file__), "resultados")

TAMANHOS = [10, 20, 50, 100]
SEEDS = [1, 2, 3, 4, 5]
VIZINHANCAS = ["2opt", "swap"]


def main():
    os.makedirs(DIR_SAIDA, exist_ok=True)
    caminho_csv = os.path.join(DIR_SAIDA, "resumo_experimentos.csv")

    linhas = []
    for n in TAMANHOS:
        for seed in SEEDS:
            cidades, matriz_dist = gera_caixeiro_viajante(
                num_cidades=n, tam_grade=100, seed=seed
            )
            for vizinhanca in VIZINHANCAS:
                config = SAConfig(vizinhanca=vizinhanca, seed=seed)
                resultado = resolver(matriz_dist, config)
                linhas.append({
                    "n_cidades": n,
                    "seed": seed,
                    "vizinhanca": vizinhanca,
                    "melhor_custo": resultado.melhor_custo,
                    "n_iteracoes": resultado.n_iteracoes,
                    "n_avaliacoes_vizinho": resultado.n_avaliacoes_vizinho,
                    "tempo_execucao_s": resultado.tempo_execucao_s,
                    "temp_inicial_usada": resultado.config.temp_inicial,
                })
                print(f"n={n:4d} seed={seed} vizinhanca={vizinhanca:5s} "
                      f"-> custo={resultado.melhor_custo:9.3f} "
                      f"tempo={resultado.tempo_execucao_s:6.3f}s")

    with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
        campos = list(linhas[0].keys())
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)

    print(f"\n[OK] Resumo salvo em {caminho_csv}")


if __name__ == "__main__":
    main()
