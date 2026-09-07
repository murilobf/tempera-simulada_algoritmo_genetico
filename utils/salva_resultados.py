import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DIR_SAIDA = os.path.join(os.path.dirname(__file__), "resultados")

def salva_resultado(tag, cidades, matriz_dist, resultado):
    os.makedirs(DIR_SAIDA, exist_ok=True)

    # metricas em JSON
    metricas = {
        "tag": tag,
        "n_cidades": len(cidades),
        "melhor_custo": resultado.melhor_custo,
        "melhor_rota": resultado.melhor_rota.tolist(),
        "tempo_execucao_s": resultado.tempo_execucao_s,
        "n_iteracoes": resultado.n_iteracoes,
        "n_avaliacoes_vizinho": resultado.n_avaliacoes_vizinho,
        "config": {
            "temp_inicial": resultado.config.temp_inicial,
            "temp_minima": resultado.config.temp_minima,
            "alpha": resultado.config.alpha,
            "iters_por_temp": resultado.config.iters_por_temp,
            "max_patamares_sem_melhora": resultado.config.max_patamares_sem_melhora,
            "vizinhanca": resultado.config.vizinhanca,
            "seed": resultado.config.seed,
        },
    }
    caminho_json = os.path.join(DIR_SAIDA, f"{tag}_metricas.json")
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(metricas, f, indent=2, ensure_ascii=False)

    # grafico de convergencia (custo atual vs melhor custo)
    hist = resultado.historico
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(hist.iteracao, hist.custo_atual, color="tab:blue", alpha=0.4, label="Custo atual")
    ax1.plot(hist.iteracao, hist.melhor_custo, color="tab:red", linewidth=2, label="Melhor custo")
    ax1.set_xlabel("Iteracao")
    ax1.set_ylabel("Custo da rota")
    ax1.set_title(f"Convergencia da Tempera Simulada ({tag})")
    ax1.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(DIR_SAIDA, f"{tag}_convergencia.png"), dpi=150)
    plt.close(fig)

    # grafico de resfriamento (temperatura vs iteracao)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(hist.iteracao, hist.temperatura, color="tab:orange")
    ax.set_xlabel("Iteracao")
    ax.set_ylabel("Temperatura")
    ax.set_yscale("log")
    ax.set_title(f"Resfriamento geometrico ({tag})")
    fig.tight_layout()
    fig.savefig(os.path.join(DIR_SAIDA, f"{tag}_temperatura.png"), dpi=150)
    plt.close(fig)

    # rota final no plano 
    rota = resultado.melhor_rota
    pontos = cidades[rota]
    pontos_fechado = np.vstack([pontos, pontos[0]])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(pontos_fechado[:, 0], pontos_fechado[:, 1], "-o", color="tab:green", markersize=4)
    ax.scatter(cidades[:, 0], cidades[:, 1], color="black", zorder=3, s=10)
    ax.set_title(f"Melhor rota encontrada ({tag}) - custo={resultado.melhor_custo:.2f}")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(os.path.join(DIR_SAIDA, f"{tag}_rota.png"), dpi=150)
    plt.close(fig)

    print(f"[OK] Resultados salvos em {DIR_SAIDA}/{tag}_*")
    return caminho_json