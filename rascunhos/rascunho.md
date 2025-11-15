# Resumo
Atualmente, o desenvolvimento de algoritmos quânticos é limitado pela falta de formas eficazes e acessíveis de executá-los na prática. Hardware quântico moderno ainda apresenta baixa capacidade de processamento e seu uso é caro demais. Dessa forma, é adequada a simulação do algoritmo em hardware clássico para auxiliar e reduzir o custo do desenvolvimento dos algoritmos.
Por sua vez, a simulação clássica também traz desafios: o consumo de memória cresce exponencialmente em relação ao número de qubits do circuito a ser simulado, tornando-a inviável para circuitos maiores. Neste trabalho, será apresentado o QMDD (Quantum Multiple-valued Decision Diagram), uma estrutura de dados capaz de representar e executar circuitos quânticos de forma a mitigar o consumo exponencial previamente mencionado.


# Introdução
- Importância da simulação clássica de sistemas quânticos
- Complexidade da simulação
- Diferentes formas de realizar essa simulação incluem a representação de um circuito por meio de sucessivas multiplicações de matrizes.
- QMDD serve para representar matrizes e operá-las da forma mais sucinta possível de acordo com a redundância nas matrizes. (Decidir se eu vou tratar o qmdd como representação da matriz final do circuito ou se vou representar o vetor do estado do sistema como uma matriz 2^n x 1 e usar o qmdd pra isso)

# Fundamentação Teórica (Pessoal da física precisa entender)
## Sistema Quântico
## Grafos
## Qubit
## Porta Lógica Quântica
### Porta Lógica Quântica Controlada (Explicar que outras portas de múltiplos qubits podem ser decompostas em portas aplicadas separadamente em cada qubit)
## Circuito Quântico
## Produto Tensorial, Demonstrar que o produto tensorial de n qubits resulta em um vetor de 2^n dimensões.

# Simulação Clássica de um Sistema Quântico
## Evolução temporal do sistema como passos discretos em um circuito.
## Representação do Circuito como sucessivas multiplicações de matrizes representando a aplicação de cada porta lógica
## Construção da matriz que representa uma porta lógica aplicada a um certo qubit
### Construção da martiz que representa uma porta lógica controlada.

