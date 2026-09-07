def ciclo_AG(tempo_maximo):
    tempo_atual = 0
    inicia_populacao()
    avalia()

    while(tempo_atual < tempo_maximo):
        seleciona_pais()
        mistura()
        muta()
        avalia()
        genocidio()
        tempo_atual += 1

def inicia_populacao():
    "TODO"

def avalia():
    "TODO"

def seleciona_pais():
    "TODO"

def mistura():
    "TODO"

def muta():
    "TODO"

def genocidio():
    "TODO"