from ag.algoritmo_genetico import ciclo_AG, MAX_ITERACOES
from utils.grafo import gera_caixeiro_viajante
from utils.salva_resultados import salva_resultado_ag

N_CIDADES_LISTA = [100]
SEEDS = [1]
CONFIGS_POPULACAO = [
    (10000, 0.25),
]


def main():
    total = len(N_CIDADES_LISTA) * len(SEEDS) * len(CONFIGS_POPULACAO)
    executado = 0

    for n_cidades in N_CIDADES_LISTA:
        for seed in SEEDS:
            # gera o grafo uma vez por (n_cidades, seed) e reaproveita
            # nas 3 combinações de população/mutação
            cidades, matriz_distancia = gera_caixeiro_viajante(num_cidades=n_cidades, seed=seed)

            for num_populacao, taxa_mutacao in CONFIGS_POPULACAO:
                executado += 1
                tag = f"ag_caixeiro_{n_cidades}_{seed}_{num_populacao}_{taxa_mutacao}"
                print(f"\n[{executado}/{total}] Rodando {tag}")

                try:
                    resultado = ciclo_AG(
                        tempo_maximo=MAX_ITERACOES,
                        qtde_nos=n_cidades,
                        max_populacao=num_populacao,
                        taxa_mutacao=taxa_mutacao,
                        matriz_distancia=matriz_distancia,
                        seed=seed,
                    )
                    salva_resultado_ag(tag, cidades, matriz_distancia, resultado)
                except Exception as e:
                    # não deixa uma combinação com erro derrubar a bateria inteira
                    print(f"[ERRO] Falhou em {tag}: {e}")

    print(f"\nBateria concluída: {executado}/{total} combinações processadas.")


if __name__ == "__main__":
    main()