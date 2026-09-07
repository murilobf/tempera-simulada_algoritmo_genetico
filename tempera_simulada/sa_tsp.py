"""Tempera Simulada aplicada ao Caixeiro Viajante.

Este modulo contem a modelagem/algoritmo
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import numpy as np


@dataclass
class SAConfig:
    temp_inicial: float = None  # se None, estimada automaticamente
    temp_minima: float = 1e-3
    alpha: float = 0.995          # fator de resfriamento (0<alpha<1)
    iters_por_temp: int = None    # se None, usa max(50, n_cidades * 2)
    max_patamares_sem_melhora: int | None = None
    vizinhanca: str = "2opt"      # "2opt" | "swap" | "or_opt"
    seed: int | None = None


@dataclass
class SAHistorico:
    """Series temporais registradas durante a execucao, para analise."""

    iteracao: list = field(default_factory=list)
    temperatura: list = field(default_factory=list)
    custo_atual: list = field(default_factory=list)
    melhor_custo: list = field(default_factory=list)
    aceitou: list = field(default_factory=list)  # bool: aceitou o vizinho?
    piora_aceita: list = field(default_factory=list)  # bool: aceitou piora?


@dataclass
class SAResultado:
    melhor_rota: np.ndarray
    melhor_custo: float
    historico: SAHistorico
    tempo_execucao_s: float
    n_iteracoes: int
    n_avaliacoes_vizinho: int
    config: SAConfig


def custo_rota(rota: np.ndarray, matriz_dist: np.ndarray) -> float:
    """Custo total do ciclo fechado (soma das arestas + retorno ao inicio)."""
    idx_atual = rota
    idx_prox = np.roll(rota, -1)
    return float(matriz_dist[idx_atual, idx_prox].sum())


def _delta_2opt(rota, matriz_dist, i, j):
    """Delta de custo ao reverter o segmento rota[i+1:j+1] (2-opt)"""
    n = len(rota)
    a, b = rota[i], rota[(i + 1) % n]
    c, d = rota[j], rota[(j + 1) % n]
    antes = matriz_dist[a, b] + matriz_dist[c, d]
    depois = matriz_dist[a, c] + matriz_dist[b, d]
    return depois - antes


def _delta_swap(rota, matriz_dist, i, j):
    """Delta de custo ao trocar as cidades nas posicoes i e j"""
    n = len(rota)
    if j == i + 1 or (i == 0 and j == n - 1):
        # posicoes adjacentes no ciclo
        rota_tmp = rota.copy()
        antes = custo_rota(rota_tmp, matriz_dist)
        rota_tmp[i], rota_tmp[j] = rota_tmp[j], rota_tmp[i]
        depois = custo_rota(rota_tmp, matriz_dist)
        return depois - antes

    ant_i, ci, pos_i = rota[i - 1], rota[i], rota[(i + 1) % n]
    ant_j, cj, pos_j = rota[j - 1], rota[j], rota[(j + 1) % n]
    antes = (matriz_dist[ant_i, ci] + matriz_dist[ci, pos_i] +
             matriz_dist[ant_j, cj] + matriz_dist[cj, pos_j])
    depois = (matriz_dist[ant_i, cj] + matriz_dist[cj, pos_i] +
              matriz_dist[ant_j, ci] + matriz_dist[ci, pos_j])
    return depois - antes


def _estima_temp_inicial(matriz_dist: np.ndarray, rng: np.random.Generator, n_amostras: int = 200) -> float:
    """Estima T0 a partir da variacao media de custo entre vizinhos aleatorios"""
    n = matriz_dist.shape[0]
    deltas = []
    rota = np.arange(n)
    for _ in range(n_amostras):
        i, j = sorted(rng.choice(n, size=2, replace=False))
        d = _delta_2opt(rota, matriz_dist, i, j)
        if d > 0:
            deltas.append(d)
    if not deltas:
        return 1.0
    delta_medio = float(np.mean(deltas))
    p_aceite_alvo = 0.8
    return -delta_medio / math.log(p_aceite_alvo)


def resolver(matriz_dist: np.ndarray, config: SAConfig | None = None) -> SAResultado:
    """Executa a Tempera Simulada para o TSP dado pela matriz de distancias"""
    if config is None:
        config = SAConfig()

    n = matriz_dist.shape[0]
    rng = np.random.default_rng(config.seed)

    iters_por_temp = config.iters_por_temp or max(50, n * 2)
    temp_inicial = config.temp_inicial or _estima_temp_inicial(matriz_dist, rng)

    if config.max_patamares_sem_melhora is not None:
        max_patamares_sem_melhora = config.max_patamares_sem_melhora
    else:
        total_patamares_estimado = math.ceil(
            math.log(config.temp_minima / temp_inicial) / math.log(config.alpha)
        )
        max_patamares_sem_melhora = max(50, total_patamares_estimado // 4)

    rota_atual = rng.permutation(n)
    custo_atual = custo_rota(rota_atual, matriz_dist)

    melhor_rota = rota_atual.copy()
    melhor_custo = custo_atual

    hist = SAHistorico()

    T = temp_inicial
    iteracao = 0
    n_avaliacoes = 0
    patamares_sem_melhora = 0
    t0 = time.perf_counter()

    while T > config.temp_minima and patamares_sem_melhora < max_patamares_sem_melhora:
        melhor_custo_no_inicio_do_patamar = melhor_custo

        for _ in range(iters_por_temp):
            i, j = sorted(rng.choice(n, size=2, replace=False))

            if config.vizinhanca == "2opt":
                delta = _delta_2opt(rota_atual, matriz_dist, i, j)
            elif config.vizinhanca == "swap":
                delta = _delta_swap(rota_atual, matriz_dist, i, j)
            else:
                raise ValueError(f"vizinhanca desconhecida: {config.vizinhanca}")

            n_avaliacoes += 1
            aceitou = False
            piora_aceita = False

            if delta <= 0:
                aceitou = True
            else:
                p = math.exp(-delta / T)
                if rng.random() < p:
                    aceitou = True
                    piora_aceita = True

            if aceitou:
                if config.vizinhanca == "2opt":
                    rota_atual[i + 1:j + 1] = rota_atual[i + 1:j + 1][::-1]
                else:
                    rota_atual[i], rota_atual[j] = rota_atual[j], rota_atual[i]
                custo_atual += delta

                if custo_atual < melhor_custo - 1e-9:
                    melhor_custo = custo_atual
                    melhor_rota = rota_atual.copy()

            iteracao += 1
            hist.iteracao.append(iteracao)
            hist.temperatura.append(T)
            hist.custo_atual.append(custo_atual)
            hist.melhor_custo.append(melhor_custo)
            hist.aceitou.append(aceitou)
            hist.piora_aceita.append(piora_aceita)

        if melhor_custo < melhor_custo_no_inicio_do_patamar - 1e-9:
            patamares_sem_melhora = 0
        else:
            patamares_sem_melhora += 1

        T *= config.alpha

    tempo_execucao = time.perf_counter() - t0

    return SAResultado(
        melhor_rota=melhor_rota,
        melhor_custo=melhor_custo,
        historico=hist,
        tempo_execucao_s=tempo_execucao,
        n_iteracoes=iteracao,
        n_avaliacoes_vizinho=n_avaliacoes,
        config=config,
    )
