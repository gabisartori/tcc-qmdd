# Defesa do Trabalho de Conclusão de Curso

Boa tarde à banca e a todos que estão assistindo. Agradeço pela presença e vou começar agora a defesa do meu Trabalho de Conclusão de Curso.

O tema do trabalho é a simulação de circuitos quânticos por meio de diagramas de decisão, com o objetivo de implementar um simulador para a plataforma de desenvolvimento quântico Ket.

## Motivação

Primeiramente, é importante ressaltar como o desenvolvimento de algoritmos quânticos impacta a área da computação. Sabe-se que é possível utilizar fenômenos quânticos para executar algoritmos mais eficientes que algoritmos clássicos.

Por exemplo, o algoritmo de Grover permite encontrar um elemento em uma lista desordenada com complexidade $O(\sqrt{n})$, onde $n$ é o tamanho da lista. O melhor algoritmo clássico conhecido possui complexidade linear, $O(n)$.

Apesar desse ganho de desempenho, computação quântica e computação clássica são formalmente equivalentes em termos de capacidade computacional. Isso significa que todo algoritmo quântico pode ser executado em um computador clássico e vice-versa.

Essa equivalência é relevante porque o desenvolvimento de algoritmos quânticos é afetado pela escassez de hardware quântico capaz de executá-los. Os dispositivos disponíveis são caros e possuem baixa capacidade. Assim, surge a necessidade de simular algoritmos quânticos por meio de computadores clássicos.

## Computação Quântica Circuital

Uma das formas de representar um algoritmo quântico é por meio de circuitos compostos por qubits e portas lógicas quânticas.

O menor elemento dessa representação é o qubit, representado por um vetor em $\mathbb{C}^2$:

$$
\ket{\psi} = \alpha\ket{0} + \beta\ket{1},
$$

tal que

$$
|\alpha|^2 + |\beta|^2 = 1.
$$

Os valores $\alpha$ e $\beta$ são amplitudes complexas. Seus módulos ao quadrado representam as probabilidades de obtenção dos estados $\ket{0}$ e $\ket{1}$ em uma medição.

Como qubits são representados por vetores, operações sobre eles são representadas por matrizes unitárias. Para um circuito com múltiplos qubits, o estado é representado pelo produto tensorial dos estados individuais. Da mesma forma, uma porta aplicada sobre um único qubit deve ser combinada por meio do produto tensorial com matrizes identidade para representar sua ação sobre o circuito completo.

Esse processo faz com que vetores cresçam de forma exponencial em relação ao número de qubits. Um circuito com $n$ qubits possui $2^n$ estados possíveis. Portas que atuam sobre vários qubits produzem matrizes com $2^n \times 2^n$ posições.

Consequentemente, armazenar e multiplicar matrizes densas torna-se inviável para circuitos maiores. Por isso, são necessários métodos especializados de simulação.

## QMDD

Para lidar com esse problema, foi utilizado o QMDD — *Quantum Multiple-Valued Decision Diagram*, ou diagrama de decisão múltipla para sistemas quânticos.

O QMDD é uma estrutura de dados baseada em grafos dirigidos acíclicos e ponderados. Os vértices representam seções da matriz ou do vetor. Cada vértice está associado a um qubit. Já as arestas armazenam pesos complexos utilizados para reconstruir os valores representados pelo diagrama.

A principal vantagem dessa estrutura é explorar a redundância presente em matrizes quânticas. Muitas matrizes são compostas por padrões repetidos. Em vez de armazenar individualmente todas as posições da matriz, o QMDD reutiliza vértices equivalentes.

Além disso, o QMDD possui regras de normalização e eliminação de redundâncias. Valores comuns às arestas podem ser fatorados e armazenados em uma única aresta superior. Vértices equivalentes são compartilhados e vértices com todas as arestas iguais podem ser eliminados.

### Representação de Matriz

Uma matriz que atua sobre um único qubit é representada por um vértice com quatro arestas. Essas arestas correspondem às posições da matriz:

$$
[M_{00}, M_{01}, M_{10}, M_{11}].
$$

A aresta inicial contém um fator de normalização comum às outras arestas.

Como exemplo, considere a porta Y:

$$
Y =
\begin{bmatrix}
0 & -i \\
i & 0
\end{bmatrix}.
$$

No QMDD, o peso de entrada é $i$. As quatro arestas do vértice possuem os valores $0$, $-1$, $1$ e $0$, nessa ordem.

Agora vamos considerar uma porta atuando sobre dois qubits, representada por $X \otimes H$. Matematicamente, essa matriz possui 16 posições:

$$
X \otimes H =
\frac{1}{\sqrt{2}}
\begin{bmatrix}
0 & 0 & 1 & 1 \\
0 & 0 & 1 & -1 \\
1 & 1 & 0 & 0 \\
1 & -1 & 0 & 0
\end{bmatrix}.
$$

No entanto, o QMDD representa essa operação com apenas dois vértices e oito arestas. A repetição dos padrões da porta H é compartilhada pelo diagrama.

Nesse exemplo, o fator $\frac{1}{\sqrt{2}}$ é fatorado sucessivamente até chegar à aresta inicial.

Os vértices do QMDD são organizados de acordo com a significância dos qubits. O vértice mais próximo da aresta inicial representa o qubit mais significativo. À medida que o diagrama avança em direção ao vértice terminal, são encontrados os qubits menos significativos.

Para recuperar um valor da matriz, são escolhidas arestas de acordo com os índices da posição desejada. Os pesos encontrados no caminho são multiplicados. O produto corresponde ao valor armazenado na matriz original.

### Construção de Porta Controlada

Portas controladas exigem uma representação diferente porque a operação aplicada no qubit alvo depende do estado do qubit de controle.

Se o controle estiver em $\ket{0}$, o alvo deve permanecer inalterado e será aplicada a matriz identidade.

Se o controle estiver em $\ket{1}$, será aplicada a matriz da porta desejada.

Um exemplo é a porta CNOT. O vértice que representa o qubit de controle possui arestas apontando para diferentes caminhos. Uma dessas arestas representa a identidade aplicada ao qubit alvo. Outra representa a porta X.

A combinação desses caminhos permite representar a aplicação condicional da porta.

Esse comportamento gera um problema relevante para a estrutura. Cada qubit de controle pode exigir vértices adicionais para representar os cenários possíveis. Por isso, circuitos com muitos controles podem fazer o tamanho do QMDD crescer rapidamente.

Espera-se, portanto, que o método tenha melhor desempenho em circuitos nos quais as matrizes possuam padrões repetidos e poucos qubits sejam utilizados como controle.

## Implementação e Integração com o Ket

Os algoritmos necessários para criação, normalização, adição e multiplicação de QMDDs foram implementados em Rust. A implementação foi integrada diretamente ao código-fonte da plataforma Ket.

### Aplicação de Porta Genérica

Para criar um QMDD correspondente a uma porta, a implementação recebe a matriz da operação e a lista de qubits de controle e alvo.

Primeiramente, os vértices correspondentes ao circuito completo são construídos. Os cenários controlados são representados pela combinação da matriz identidade e da matriz da porta desejada.

A aplicação da porta ao estado é realizada pela multiplicação entre o QMDD que representa o estado atual e o QMDD que representa a operação.

Durante essa multiplicação, dois tipos de mecanismos foram utilizados para melhorar o desempenho:

- Identificação de vértices duplicados, evitando a criação de estruturas equivalentes.
- Memoização das operações entre arestas, armazenando resultados já calculados em uma tabela hash.

Essas otimizações são importantes porque as operações de adição e multiplicação são recursivas e podem visitar várias vezes os mesmos pares de arestas.

Atualmente, o Ket decompõe portas arbitrárias em um conjunto fundamental composto por portas de Pauli, Hadamard, fase e rotações. Após a decomposição, as portas fundamentais são enviadas ao simulador, que cria e aplica seus QMDDs.

### Medição e Simulação Forte

O Ket exige que um simulador seja capaz de realizar dois tipos de operação sobre os estados:

- Medição destrutiva de qubits.
- Recuperação completa do vetor de amplitudes.

Por isso, o simulador implementado suporta simulação forte.

Para recuperar o vetor de amplitudes, o algoritmo percorre todos os caminhos possíveis entre a aresta inicial e o vértice terminal. Para cada caminho, os pesos das arestas são multiplicados.

O resultado é a amplitude correspondente ao estado associado a esse caminho.

A medição de um qubit é realizada percorrendo o QMDD e somando as probabilidades dos caminhos nos quais o qubit pode assumir o valor $\ket{0}$ ou o valor $\ket{1}$.

A probabilidade de cada resultado é utilizada para escolher aleatoriamente o resultado da medição, de acordo com a regra de Born.

Após o resultado ser escolhido, o estado é atualizado de modo que a superposição seja colapsada. Se o qubit é medido em $\ket{0}$, os caminhos associados a $\ket{1}$ são eliminados. Caso contrário, os caminhos associados a $\ket{0}$ são eliminados.

Esse procedimento também permite que o Ket realize medições sucessivas sobre o mesmo circuito. O mesmo qubit retornará sempre o resultado compatível com o estado colapsado.

## Experimentos

Os experimentos foram realizados para analisar o comportamento do simulador em diferentes tipos de circuitos.

O simulador QMDD foi comparado com o simulador denso e com o simulador esparso já disponíveis no Ket.

### Algoritmos

Os algoritmos utilizados foram o algoritmo de Grover, o FALQON e o algoritmo de Estimação de Fase Quântica.

O algoritmo de Grover utiliza repetidamente portas controladas. Isso faz com que o número de qubits de controle possa crescer junto com o tamanho do circuito.

O FALQON é um algoritmo de otimização composto por portas controladas em menor quantidade que o algoritmo de Grover. Foi utilizado o problema Max-Cut sobre um grafo.

Por fim, o algoritmo de Estimação de Fase Quântica combina portas controladas com operações da Transformada Quântica de Fourier.

Esses três algoritmos permitem analisar o desempenho em circuitos com diferentes graus de controle e entrelaçamento.

### Variando o Número de Qubits

No primeiro tipo de experimento, o número de qubits foi aumentado progressivamente para cada combinação de simulador e algoritmo.

Em cada combinação, iniciam-se as execuções em uma quantidade mínima de qubits. Quando a simulação termina dentro do limite estabelecido, o número de qubits é aumentado.

Caso o tempo máximo seja ultrapassado, a combinação deixa de ser executada naquele cenário.

Essa estratégia permite observar como o tempo de simulação cresce em relação ao tamanho do circuito.

### Variando as Camadas no FALQON

Um segundo experimento manteve o número de qubits fixo e variou o número de camadas do FALQON.

Nesse caso, o número de qubits foi fixado em 18. O número de camadas variou de 250 até 1500.

O objetivo desse experimento foi observar o custo causado por aumentar a quantidade de operações, mantendo a largura do circuito constante.

### Resultados

Esta seção será preenchida após a conclusão da coleta e análise dos resultados.