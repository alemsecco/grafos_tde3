O grafo é construído a partir da base de dados "Amostra Enron - 2016", considerando o remetente e o(s) destinatários de cada mensagem. 
O grafo é ponderado, considerando a frequência com que um remetente envia uma mensagem para um destinatário. 
O grafo também é rotulado, considerando como rótulo de cada vértice, o endereço de e-mail do usuário.
Para demonstrar a criação do grafo, a lista de adjacências é salva em um arquivo texto.


Métodos/funções para extrair as seguintes informações gerais do grafo construído:
'''
  a. O número de vértices do grafo (ordem);
  b. O número de arestas do grafo (tamanho);
  c. O número de vértices isolados;
  d. Os 20 indivíduos que possuem maior grau de saída e os valores correspondentes (de maneira ordenada e decrescente de acordo com o grau);
  e. Os 20 indivíduos que possuem maior grau de entrada e os valores correspondentes (de maneira ordenada e decrescente de acordo com o grau).
'''

Função que verifica se o grafo é Euleriano (ou seja, que possui um ciclo Euleriano), retornando true ou false. 
Caso a resposta seja false, a função informa ao usuário todas as condições que não foram satisfeitas.

Método que retorna uma lista com todos os vértices que estão localizados até uma distância D de um vértice N, em que D é a soma dos pesos ao longo do caminho mais curto entre dois vértices. 
A implementação é eficiente o suficiente para lidar com grafos com milhares de vértices e arestas sem exceder limites razoáveis de tempo e memória.

Método que calcula o diâmetro de um grafo, ou seja, o maior caminho mínimo entre qualquer par de vértices.
O algoritmo retorna o valor desse maior caminho mínimo (diâmetro) e o caminho correspondente encontrado.
Por simplicidade, é desconsiderado que o caminho mínimo entre dois vértices de componentes diferentes é infinito.
