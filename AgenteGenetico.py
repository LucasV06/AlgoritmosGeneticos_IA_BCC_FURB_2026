import math
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# MODELAGEM DO PROBLEMA
# ==============================================================================

class Cidade:
    """Representa uma cidade no plano 2D com coordenadas X, Y e identificador id."""
    def __init__(self, X: float, Y: float, id: int = 0):
        self.X = float(X)
        self.Y = float(Y)
        self.id = int(id)

    def __repr__(self):
        # Representa a cidade pelo seu número inteiro (1 a 20)
        return str(self.id)


def calcularAptidao(cromossomo):
    """
    Calcula a função de aptidão (fitness), que é a distância euclidiana total
    percorrida pelo caixeiro-viajante ao visitar todas as cidades na ordem do
    cromossomo e retornar à cidade inicial (circuito fechado).
    """
    distancia_total = 0
    n = len(cromossomo)

    for i in range(n):
        atual = cromossomo[i]
        proxima = cromossomo[(i + 1) % n]  # Retorna à primeira cidade ao final

        distancia_total += math.sqrt(
            math.pow(proxima.X - atual.X, 2) +
            math.pow(proxima.Y - atual.Y, 2)
        )

    return distancia_total


# ==============================================================================
# OPERADORES GENÉTICOS
# ==============================================================================

def roleta(melhores_10, pesos):
    """
    Realiza a seleção por roleta com pesos lineares (1º peso 10, 2º peso 9, ..., 10º peso 1).
    Retorna o cromossomo sorteado.
    """
    soma_pesos = sum(pesos)
    sorteio = np.random.uniform(0, soma_pesos)
    acumulado = 0

    for i, peso in enumerate(pesos):
        acumulado += peso
        if sorteio <= acumulado:
            return melhores_10[i][0]

    return melhores_10[-1][0]


def cycle_crossover(pai1, pai2):
    """
    Operador de Recombinação Cycle Crossover (CX):
    - Escolhe um local aleatório no cromossomo;
    - Passo 1: Troca os números inteiros nesse local entre os descendentes;
    - Passos 2 a 4: Enquanto houver números duplicados, localiza o número repetido
      e troca na mesma posição com o outro descendente até eliminar todas as duplicatas.
    """
    filho1 = list(pai1)
    filho2 = list(pai2)
    n = len(filho1)

    # Escolhe um índice/local aleatório dentro do cromossomo
    pos = np.random.randint(0, n)

    # Se nessa posição os valores forem iguais, não há troca para realizar
    if filho1[pos].id == filho2[pos].id:
        return filho1, filho2

    # Passo 1: Troca os genes na posição sorteada
    filho1[pos], filho2[pos] = filho2[pos], filho1[pos]

    # Resolve os ciclos de números duplicados
    while True:
        posicoes_vistas = {}
        pos_duplicada = None

        for idx, cidade in enumerate(filho1):
            if cidade.id in posicoes_vistas:
                # Duplicata encontrada: escolhe a posição que não foi a recém trocada
                pos_original = posicoes_vistas[cidade.id]
                pos_duplicada = pos_original if idx == pos else idx
                break
            posicoes_vistas[cidade.id] = idx

        # Se não há mais números duplicados, ambos os descendentes são permutações válidas
        if pos_duplicada is None:
            break

        # Troca os elementos na posição onde está o número duplicado
        pos = pos_duplicada
        filho1[pos], filho2[pos] = filho2[pos], filho1[pos]

    return filho1, filho2


def mutacao(cromossomo):
    """
    Operador de mutação por troca (swap):
    Escolhe aleatoriamente dois índices no cromossomo e troca suas cidades.
    Atua sobre cada membro da nova geração.
    """
    filho_mutado = list(cromossomo)
    n = len(filho_mutado)
    idx1, idx2 = np.random.choice(n, size=2, replace=False)
    filho_mutado[idx1], filho_mutado[idx2] = filho_mutado[idx2], filho_mutado[idx1]
    return filho_mutado


# ==============================================================================
# CARREGAMENTO DOS DADOS DAS CIDADES
# ==============================================================================

# Carrega as coordenadas x e y das 20 cidades do arquivo cidades.mat
x, y = np.loadtxt("cidades.mat")

cidades = []
for i in range(len(x)):
    # Cada cidade recebe suas coordenadas e seu número identificador (1 a 20)
    cidades.append(Cidade(x[i], y[i], id=i + 1))


# ==============================================================================
# INICIALIZAÇÃO DA POPULAÇÃO
# ==============================================================================

TAMANHO_POPULACAO = 20
NUM_GERACOES = 10000

populacao = []
for i in range(TAMANHO_POPULACAO):
    # Gera uma permutação aleatória dos números/cidades
    cromossomo = list(np.random.permutation(cidades))
    populacao.append(cromossomo)

# Salva a população inicial para exibição no relatório final
populacao_inicial = [list(c) for c in populacao]

# Pesos lineares para os 10 melhores: 1º peso 10, 2º peso 9, ..., 10º peso 1
pesos_lineares = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

# Variáveis para guardar o melhor custo e a melhor solução global
melhor_custo_global = float("inf")
melhor_solucao_global = None
historico_melhor_custo = []


# ==============================================================================
# LOOP GERACIONAL (20.000 ITERAÇÕES)
# ==============================================================================

print(f"Iniciando o Algoritmo Genético por {NUM_GERACOES} gerações...\n")

for geracao in range(NUM_GERACOES):
    # Avaliação da população atual
    avaliados = []
    for cromossomo in populacao:
        custo = calcularAptidao(cromossomo)
        avaliados.append((cromossomo, custo))

    # Ordena do mais apto ao menos apto (menor distância é o mais apto)
    avaliados.sort(key=lambda ind: ind[1]) # ARRUMAR

    # Guarda o melhor custo desta geração
    melhor_da_geracao, custo_da_geracao = avaliados[0]
    historico_melhor_custo.append(custo_da_geracao)

    if custo_da_geracao < melhor_custo_global:
        melhor_custo_global = custo_da_geracao
        melhor_solucao_global = list(melhor_da_geracao)

    # Exibe o progresso periodicamente no console
    if (geracao + 1) % 2000 == 0 or geracao == 0:
        print(f"Geração {geracao + 1:5d}/{NUM_GERACOES} | Custo Atual: {custo_da_geracao:.5f} | Melhor Global: {melhor_custo_global:.5f}")

    # Mantém os 10 melhores da população atual (50% de renovação)
    dez_melhores = avaliados[:10]

    # Roleta dos 10 melhores com pesos lineares e sorteio de 5 pares ordenados de pais
    novos_filhos = []
    for _ in range(5):
        pai1 = roleta(dez_melhores, pesos_lineares)
        pai2 = roleta(dez_melhores, pesos_lineares)

        # Procura pais distintos se possível
        tentativas = 0
        while pai1 is pai2 and tentativas < 10:
            pai2 = roleta(dez_melhores, pesos_lineares)
            tentativas += 1

        # Cycle Crossover: gera dois filhos para cada par de pais
        filho1, filho2 = cycle_crossover(pai1, pai2)

        # Mutação aleatória de dois espaços em cada membro da nova geração
        filho1_mutado = mutacao(filho1)
        filho2_mutado = mutacao(filho2)

        novos_filhos.append(filho1_mutado)
        novos_filhos.append(filho2_mutado)

    # Insere os 10 novos filhos junto aos 10 pais mantidos e recomeça a geração
    populacao = [ind[0] for ind in dez_melhores] + novos_filhos


# Avaliação final da população após 10.000 gerações
avaliados_final = []
for cromossomo in populacao:
    avaliados_final.append((cromossomo, calcularAptidao(cromossomo)))
avaliados_final.sort(key=lambda ind: ind[1])


# ==============================================================================
# EXIBIÇÃO DOS RESULTADOS NA JANELA DE COMANDO
# ==============================================================================

print("\n" + "=" * 70)
print("                   RESULTADOS DO ALGORITMO GENÉTICO")
print("=" * 70)
print(f"• Tamanho da População : {TAMANHO_POPULACAO}")
print(f"• Número de Cidades    : {len(cidades)}")
print(f"• Melhor Custo         : {melhor_custo_global:.5f}")
print(f"• Melhor Solução       : {[c.id for c in melhor_solucao_global]}")

print("\n• População Inicial (Amostra dos 20 cromossomos da Geração 0):")
for i, ind in enumerate(populacao_inicial):
    print(f"  Indivíduo {i + 1:02d}: {[c.id for c in ind]}")

print("\n• População Final (20 cromossomos e custos após 10.000 gerações):")
for i, (ind, custo) in enumerate(avaliados_final):
    print(f"  Indivíduo {i + 1:02d} (Custo: {custo:.5f}): {[c.id for c in ind]}")
print("=" * 70)


# ==============================================================================
# MÉTODO MATPLOTLIB PARA APRESENTAR O GRÁFICO
# ==============================================================================

def plotar_resultados(melhor_solucao, melhor_custo, historico):
    """
    Plota as cidades como pontos, o circuito fechado da melhor solução encontrada
    e a curva de convergência da distância ao longo das gerações.
    """
    # Adiciona a cidade inicial ao final para fechar o ciclo
    caminho = list(melhor_solucao) + [melhor_solucao[0]]
    xs = [c.X for c in caminho]
    ys = [c.Y for c in caminho]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Gráfico 1: Rota das Cidades no Plano 1x1
    ax1.plot(xs, ys, color='royalblue', linestyle='-', linewidth=2, label='Trajeto Fechado', zorder=1)
    ax1.scatter([c.X for c in melhor_solucao], [c.Y for c in melhor_solucao], 
                color='crimson', s=90, edgecolors='black', label='Cidades', zorder=2)
    ax1.scatter(melhor_solucao[0].X, melhor_solucao[0].Y, 
                color='limegreen', s=140, edgecolors='black', label=f'Início (Cidade {melhor_solucao[0].id})', zorder=3)

    # Identificação numérica de cada cidade
    for c in melhor_solucao:
        ax1.annotate(f" {c.id}", (c.X, c.Y), fontsize=10, fontweight='bold', color='navy')

    ax1.set_title(f"Melhor Caminho do Caixeiro Viajante (TSP)\nDistância Total: {melhor_custo:.5f}", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Coordenada X")
    ax1.set_ylabel("Coordenada Y")
    ax1.set_xlim(-0.05, 1.05)
    ax1.set_ylim(-0.05, 1.05)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper right')

    # Gráfico 2: Curva de Convergência (Evolução da Aptidão)
    ax2.plot(historico, color='darkgreen', linewidth=1.5)
    ax2.set_title("Evolução da Aptidão ao Longo das Gerações", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Geração")
    ax2.set_ylabel("Distância Total (Custo)")
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig("melhor_caminho.png", dpi=300)
    print("\nGráfico salvo como 'melhor_caminho.png'.")
    plt.show()


plotar_resultados(melhor_solucao_global, melhor_custo_global, historico_melhor_custo)
