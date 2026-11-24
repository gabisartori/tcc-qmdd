# Defesa do Trabalho de Conclusão de Curso

Boa tarde à banca e a todos que estão assistindo. Agradeço pela presença e vou começar agora a defesa do meu Trabalho de Conclusão de Curso.

O tema do trabalho é a simulação de circuitos quânticos por meio de diagramas de decisão com o objetivo de implementar um simulador para a plataforma de desenvolvimento quântico Ket.

## Motivação

Primeiramente, é importante ressaltar como o desenvolvimento de algoritmos quânticos impacta a área da computação. Sabe-se que é possível utilizar fenômenos quânticos para executar algoritmos mais eficientes que algoritmos clássicos. Por exemplo, o algoritmo de Grover, que permite encontrar um item numa lista desordenada com complexidade $O(\sqrt{n})$ em relação ao tamanho da lista enquanto o melhor algoritmo clássico conhecido possui complexidade linear ($O(n)$).

Porém, apesar do ganho de desempenho, a computação quântica ainda é computacionalmente equivalente à computação clássica. Ou seja, todo algoritmo quântico pode ser executado em um computador clássico e vice-versa.

Isso é importante pois o desenvolvimento de algoritmos quânticos é, atualmente, significativamente impactado pela escassez de hardware quântico capaz de executá-los. Então, nota-se a utilidade da simulação por meios clássicos de algoritmos quânticos.

## Computação Quântica Circuital

Uma das formas de representar um algoritmo quântico é por meio de circuitos compostos de portas lógicas quânticas. Nela, a menor unidade de informação, o qubit, é representado por meio de um vetor em C² tal que |\alpha|² + |\beta|² = 1.

Sendo a menor unidade de informação um vetor, operações sobre qubits podem ser codificadas utilizando matrizes unitárias.

Por sua vez, circuitos com múltiplos qubits são representados utilizando o produto vetorial entre os vetores de cada qubit e as matrizes. Cada porta aplicada sobre um único qubit é representada como o produto tensorial entre a matriz que representa o comportamento da porta e várias matrizes identidades para cada qubit não afetado.

A dimensão do resultado de um produto tensorial é o produto das dimensões das entradas. Isso faz com que tanto os vetores quanto as matrizes utilizados para representar um circuito crescem exponencialmente em relação ao número de qubits do circuito. Isso faz com que a simulação por meio de operações da álgebra linear seja não trivial, demandando métodos especializados para realizá-la de forma eficiente.

## QMDD

<!-- TODO: Arranjar outra palavra pra tensor -->
Para isso, existe o QMDD: Quantum Multiple-Valued Decision Diagram. Essa é uma estrutura de dados capaz de compactar matrizes e vetores a partir da repetição de padrões em seções do tensor. Essa repetição é particularmente frequente em tensores resultantes de produtos tensoriais, uma operação que permeia a simulação de circuitos quânticos.

O QMDD faz uso de grafos dirigidos acíclicos e ponderados para representar tensores. Nele os pesos das arestas são fatores utilizados para reconstruir os valores do tensor enquanto os vértices representam seções do tensor ---na computação quântica, cada vértice representa um qubit.

### Representação de Matriz

O passo inicial do QMDD é representar matrizes que operam sobre um único qubit. Assim, a matriz 2x2 é representada por um grafo com 2 vértices: um inicial e um final. Do vértice inicial, saem 4 arestas em direção ao vértice final. Cada aresta representa uma das posições da matriz. Por fim, uma aresta inicial aponta para o vértice inicial, carregando um fator de normalização para as 4 arestas do vértice raiz.

Por exemplo, a porta Y, a seguir, é representada por meio de um QMDD com arestas 0, -1, 1, 0 e aresta raiz com peso $i$

Note que o QMDD ordena as posições da matriz como M_00, M_01, M_10 e M_11. Então a primeira coluna da matriz é representada pela primeira e pela terceira aresta do vértice.

A seguir, temos um exemplo de uma porta agindo sobre 2 qubits, a porta X \otimes H. Note que o fator \frac{1}{\sqrt{2}} foi fatorado sucessivamente do vértice que representa a porta H até a aresta inicial do QMDD. <!-- TODO: decidir se vou explicar os algoritmos ou não -->

Esse processo de concatenação dos grafos permite representar uma matriz 4x4, de 16 posições, usando apenas 8 arestas. Nota-se que, enquanto o tamanho da matriz cresce exponencialmente em relação ao número de qubits, o tamanho do grafo cresce linearmente.

Um detalhe importante é que, no QMDD, os vértices mais próximos da aresta raiz representam qubits mais significativos, enquanto vértices mais pertos do terminal representam qubits menos significativos.

<!-- TODO: Explicar como ler o QMDD de duas portas -->

### Construção de Porta Controlada

<!-- TODO: Explicar portas controladas somewhere -->
Para construir um diagrama que utiliza qubits de controle, é preciso duplicar vértices para representar os dois cenários possíveis do qubit de controle. Se o qubit está em 0, ele precisa apontar para matriz identidade, enquanto se está em 1, precisa apontar para matriz da porta desejada.

Por exemplo, o QMDD a seguir representa a porta CNOT tendo como qubit de controle o mais significativo e como alvo o menos significativo. Note como o vértice que representa o qubit de controle tem suas arestas levando a diferentes vértices. O vértice esquerdo representa a aplicação da matriz identidade sobre o segundo qubit, enquanto o vértice direito representa a matriz X.

Aqui é onde a complexidade da simulação clássica aparece. Para cada qubit de controle no circuito, é preciso fazer essa duplicação de vértices, fazendo com que o grafo cresça exponencialmente. Logo, espera-se que o QMDD tenha melhor desempenho em circuitos com poucos qubits de controle.

## Implementação Integração com o Ket

Dito isso, os algoritmos para criação e multiplicação de QMDDs foram implementados em Rust diretamente no código fonte do simulador do Ket.

### Aplicação de Porta Genérica

### Medição e Simulação Forte

## Experimentos

### Algoritmos

### Variando Número de Qubits

### Variando Camadas no FALQON

### Resultados

## Limitações e Trabalhos Futuros

### Circuitos com Muitos Qubits de Controle

### LIMDD

### Comparar Diferentes Métodos de Representação de Números Complexos

## Conclusão e Objetivos Concluídos

## Referências e Agradecimentos
