"""Roda a Tempera Simulada em uma instancia do TSP,
salva metricas e graficos em resultados/.

python main.py --n-cidades 50 --seed 42 --alpha 0.995 --vizinhanca 2opt
"""

import argparse

import numpy as np

from utils.grafo import gera_caixeiro_viajante
from utils.salva_resultados import salva_resultado
from sa_tsp import SAConfig, resolver, custo_rota


def parse_args():
    p = argparse.ArgumentParser(description="Tempera Simulada para o Caixeiro Viajante")
    p.add_argument("--n-cidades", type=int, default=50)
    p.add_argument("--tam-grade", type=float, default=100)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--temp-inicial", type=float, default=None)
    p.add_argument("--temp-minima", type=float, default=1e-3)
    p.add_argument("--alpha", type=float, default=0.995)
    p.add_argument("--iters-por-temp", type=int, default=None)
    p.add_argument("--max-patamares-sem-melhora", type=int, default=None)
    p.add_argument("--vizinhanca", choices=["2opt", "swap"], default="2opt")
    p.add_argument("--tag", type=str, default="execucao")
    return p.parse_args()


def main():
    args = parse_args()

    cidades, matriz_dist = gera_caixeiro_viajante(
        num_cidades=args.n_cidades, tam_grade=args.tam_grade, seed=args.seed
    )

    config = SAConfig(
        temp_inicial=args.temp_inicial,
        temp_minima=args.temp_minima,
        alpha=args.alpha,
        iters_por_temp=args.iters_por_temp,
        max_patamares_sem_melhora=args.max_patamares_sem_melhora,
        vizinhanca=args.vizinhanca,
        seed=args.seed,
    )

    resultado = resolver(matriz_dist, config)

    rota_ordenada_por_indice = np.sort(resultado.melhor_rota)
    assert np.array_equal(rota_ordenada_por_indice, np.arange(args.n_cidades)), \
        "A rota final nao e uma permutacao valida das cidades"
    custo_conferido = custo_rota(resultado.melhor_rota, matriz_dist)
    assert abs(custo_conferido - resultado.melhor_custo) < 1e-6, \
        "Custo incremental divergiu do custo recomputado do zero"

    print(f"Cidades: {args.n_cidades} | Vizinhanca: {args.vizinhanca} | Seed: {args.seed}")
    print(f"Melhor custo encontrado: {resultado.melhor_custo:.4f}")
    print(f"Iteracoes: {resultado.n_iteracoes} | Tempo: {resultado.tempo_execucao_s:.3f}s")

    salva_resultado(args.tag, cidades, matriz_dist, resultado)


if __name__ == "__main__":
    main()
