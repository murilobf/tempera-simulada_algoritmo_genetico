import random
from utils.grafo import gera_caixeiro_viajante

NUM_CIDADES = 50

cidades,matriz_distancia = gera_caixeiro_viajante(num_cidades = 50, seed=10)

class Individuo:
    def __init__(self, rota = [], custo = 0, aptidao = 0):
        self.rota = rota
        self.custo = custo
        self.aptidao = aptidao

def ciclo_AG(tempo_maximo, qtde_nos, max_populacao, taxa_mutacao):
    tempo_atual = 0
    populacao = inicia_populacao(qtde_nos,max_populacao)
    avalia(populacao)
    '''for individuo in populacao:
            print(individuo.custo, individuo.aptidao)'''

    while(tempo_atual < tempo_maximo):
        pais = seleciona_pais(populacao, int(len(populacao)/2))
        mistura(pais, qtde_nos, populacao)
        muta(populacao, taxa_mutacao)
        avalia(populacao)
        genocidio(populacao, max_populacao)
        individuo = populacao[0]
        print(individuo.custo, individuo.aptidao)
        tempo_atual += 1

def inicia_populacao(qtde_nos, max_populacao):

    populacao_inicial = []
    nodos = [i for i in range(1, qtde_nos)] # ',1' pois a cidade inicial não faz parte da rota chutada exceto ao começo e fim 

    for _ in range(max_populacao):
        random.shuffle(nodos)
        rota = [0] + nodos.copy()
        individuo = Individuo(rota=rota)
        populacao_inicial.append(individuo)

    return populacao_inicial

#A nota é o custo total da rota
def avalia(populacao):
    for individuo in populacao:
        custo = 0.0
        rota = individuo.rota
        n = len(rota)

        # O '% n' faz voltar pra cidade incial
        for i in range(n):
            cidade_atual = rota[i]
            cidade_prox = rota[(i+1) % n]
            custo += matriz_distancia[cidade_atual, cidade_prox]
        individuo.custo = custo

    populacao.sort(key = lambda individuo: individuo.custo)

    # aptidão definida por ranking já que pode ser que a variação de custo não seja grande
    n = len(populacao)
    for posicao, individuo in enumerate(populacao):
        individuo.aptidao = n - posicao

def torna_par(n):
    return int(n) if (n % 2 == 0) else int(n+1)

#A seleção antes era pegando a metade melhor, mas isso convergia muito rápido no mesmo ponto e não melhorava muito mesmo com tempo e mutação grandes
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
    for individuo in populacao[1:]: #protege o melhor
        if random.random() < taxa_mutacao:
            rota = individuo.rota
            i, j = random.sample(range(1, len(rota)), 2)
            rota[i], rota[j] = rota[j], rota[i]
    

def genocidio(populacao, max_populacao):
    populacao[:] = populacao[:max_populacao]

if __name__ == "__main__":
    ciclo_AG(1000,NUM_CIDADES,10000,0.5)