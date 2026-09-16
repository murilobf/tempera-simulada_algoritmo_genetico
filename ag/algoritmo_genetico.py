import random
import time
from dataclasses import dataclass, field
from typing import List

import numpy as np

from utils.grafo import gera_caixeiro_viajante
from utils.salva_resultados import salva_resultado_ag

NUM_CIDADES = 10
MAX_ITERACOES = 1500
MAX_ESTAGNADO = MAX_ITERACOES*0.2 #define quanto tempo ele pode ficar sem nenhuma modificação pra evitar processamento adicional
TAXA_MUTACAO = 0
NUM_POPULACAO = 1000
SEED = 1

cidades, matriz_distancia = gera_caixeiro_viajante(num_cidades=NUM_CIDADES, seed=SEED)


class Individuo:
    def __init__(self, rota=None, custo=0, aptidao=0):
        # evita o problema clássico de valor default mutável (rota=[])
        self.rota = rota if rota is not None else []
        self.custo = custo
        self.aptidao = aptidao


@dataclass
class ConfigAG:
    tempo_maximo: int
    qtde_nos: int
    max_populacao: int
    taxa_mutacao: float
    seed: int = SEED


@dataclass
class Historico:
    iteracao: List[int] = field(default_factory=list)
    custo_medio: List[float] = field(default_factory=list)
    melhor_custo: List[float] = field(default_factory=list)


@dataclass
class ResultadoAG:
    melhor_custo: float
    melhor_rota: np.ndarray
    tempo_execucao_s: float
    n_iteracoes: int
    n_avaliacoes: int
    config: ConfigAG
    historico: Historico


def ciclo_AG(tempo_maximo, qtde_nos, max_populacao, taxa_mutacao, matriz_distancia, seed=SEED):
    random.seed(seed)
    inicio = time.time()
    tempo_atual = 0
    tempo_estagnado = 0

    populacao = inicia_populacao(qtde_nos, max_populacao)
    avalia(populacao, matriz_distancia)
    n_avaliacoes = len(populacao)

    melhor_custo_global = populacao[0].custo
    melhor_rota_global = populacao[0].rota.copy()

    historico = Historico()

    while tempo_atual < tempo_maximo:
        pais = seleciona_pais(populacao, int(len(populacao) / 2))
        mistura(pais, qtde_nos, populacao)
        muta(populacao, taxa_mutacao)
        avalia(populacao, matriz_distancia)
        n_avaliacoes += len(populacao)
        genocidio(populacao, max_populacao)

        custos = [individuo.custo for individuo in populacao]
        melhor_da_geracao = populacao[0]
        #print(melhor_da_geracao.custo)

        if melhor_da_geracao.custo < melhor_custo_global:
            melhor_custo_global = melhor_da_geracao.custo
            melhor_rota_global = melhor_da_geracao.rota.copy()
            tempo_estagnado = 0

        else:
            tempo_estagnado += 1

        historico.iteracao.append(tempo_atual)
        historico.custo_medio.append(float(np.mean(custos)))
        historico.melhor_custo.append(melhor_custo_global)
        tempo_atual += 1

        if(tempo_estagnado >= MAX_ESTAGNADO):
            print('Execução interrompida por estagnação')
            break

    tempo_execucao_s = time.time() - inicio

    config = ConfigAG(
        tempo_maximo=tempo_maximo,
        qtde_nos=qtde_nos,
        max_populacao=max_populacao,
        taxa_mutacao=taxa_mutacao,
        seed=seed,
    )

    return ResultadoAG(
        melhor_custo=melhor_custo_global,
        melhor_rota=np.array(melhor_rota_global),
        tempo_execucao_s=tempo_execucao_s,
        n_iteracoes=tempo_atual,
        n_avaliacoes=n_avaliacoes,
        config=config,
        historico=historico,
    )


def inicia_populacao(qtde_nos, max_populacao):
    populacao_inicial = []
    nodos = [i for i in range(1, qtde_nos)]  # ',1' pois a cidade inicial não faz parte da rota chutada exceto ao começo e fim

    for _ in range(max_populacao):
        random.shuffle(nodos)
        rota = [0] + nodos.copy()
        individuo = Individuo(rota=rota)
        populacao_inicial.append(individuo)

    return populacao_inicial


# A nota é o custo total da rota
def avalia(populacao, matriz_distancia):
    for individuo in populacao:
        custo = 0.0
        rota = individuo.rota
        n = len(rota)

        # O '% n' faz voltar pra cidade incial
        for i in range(n):
            cidade_atual = rota[i]
            cidade_prox = rota[(i + 1) % n]
            custo += matriz_distancia[cidade_atual, cidade_prox]
        individuo.custo = custo

    populacao.sort(key=lambda individuo: individuo.custo)

    # aptidão definida por ranking já que pode ser que a variação de custo não seja grande
    n = len(populacao)
    for posicao, individuo in enumerate(populacao):
        individuo.aptidao = n - posicao


def torna_par(n):
    return int(n) if (n % 2 == 0) else int(n + 1)


# A seleção antes era pegando a metade melhor, mas isso convergia muito rápido no mesmo ponto e não melhorava muito mesmo com tempo e mutação grandes
def seleciona_pais(populacao, n_pares, k=3):
    def torneio():
        candidatos = random.sample(populacao, k)
        return min(candidatos, key=lambda ind: ind.custo)
    return [(torneio(), torneio()) for _ in range(n_pares)]


def ordem_crossover(pai1_rota, pai2_rota):
    n = len(pai1_rota)
    segmento_pai1 = pai1_rota[1:]
    segmento_pai2 = pai2_rota[1:]
    tam = len(segmento_pai1)

    ponto1 = random.randint(0, tam - 2)
    ponto2 = random.randint(ponto1 + 1, tam - 1)

    filho_segmento = [None] * tam
    filho_segmento[ponto1:ponto2 + 1] = segmento_pai1[ponto1:ponto2 + 1]

    usados = set(filho_segmento[ponto1:ponto2 + 1])

    pos_filho = (ponto2 + 1) % tam
    pos_pai2 = (ponto2 + 1) % tam

    while None in filho_segmento:
        cidade = segmento_pai2[pos_pai2]
        if cidade not in usados:
            filho_segmento[pos_filho] = cidade
            usados.add(cidade)
            pos_filho = (pos_filho + 1) % tam
        pos_pai2 = (pos_pai2 + 1) % tam

    return [0] + filho_segmento


def mistura(pares, qtde_nos, populacao):
    filhos = []
    for pai1, pai2 in pares:
        filho1_rota = ordem_crossover(pai1.rota, pai2.rota)
        filho2_rota = ordem_crossover(pai2.rota, pai1.rota)
        filhos.append(Individuo(rota=filho1_rota))
        filhos.append(Individuo(rota=filho2_rota))
    populacao.extend(filhos)


def muta(populacao, taxa_mutacao=0.1):
    for individuo in populacao[1:]:  # protege o melhor
        if random.random() < taxa_mutacao:
            rota = individuo.rota

            # mutação por inversão 
            i, j = sorted(random.sample(range(1, len(rota)), 2))
            rota[i:j + 1] = rota[i:j + 1][::-1]


def genocidio(populacao, max_populacao):
    populacao[:] = populacao[:max_populacao]


if __name__ == "__main__":
    resultado = ciclo_AG(MAX_ITERACOES, NUM_CIDADES, NUM_POPULACAO, TAXA_MUTACAO, matriz_distancia, seed=SEED)
    salva_resultado_ag("ag_caixeiro", cidades, matriz_distancia, resultado)