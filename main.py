from collections import defaultdict, deque
import os
import re
import email

class Grafo:
    def __init__(self):
        self.vertices = defaultdict(list)
        self.rotulos = {}
        self.pesos = {}

    def ordem(self):
        return len(self.vertices)

    def tamanho(self):
        return sum(len(vizinhos) for vizinhos in self.vertices.values())

    def vertice_isolado(self):
        isolados = 0
        destino = {v for _, v in self.pesos.keys()}
        for v in self.vertices:
            tem_saida = len(self.vertices[v]) > 0
            tem_entrada = v in destino
            if not tem_saida and not tem_entrada:
                isolados += 1
        return isolados

    def maiores_graus_saida(self):
        maiores_graus = [(v, len(self.vertices[v])) for v in self.vertices]
        maiores_graus.sort(key=lambda x: x[1], reverse=True)
        return maiores_graus[:20]

    def maiores_graus_entrada(self):
        entradas = defaultdict(int)
        for u, v in self.pesos:
            entradas[v] += 1
        maiores_graus = sorted(entradas.items(), key=lambda x: x[1], reverse=True)
        return maiores_graus[:20]

    def adicionar_vertice(self, v, rotulo=None):
        if v not in self.vertices:
            self.vertices[v] = []
        if rotulo:
            self.rotulos[v] = rotulo

    def adicionar_aresta(self, u, v):
        if u not in self.vertices:
            self.vertices[u] = []
        if v not in self.vertices:
            self.vertices[v] = []
        aresta = (u, v)
        if v in self.vertices[u]:
            self.pesos[aresta] = self.pesos.get(aresta, 1) + 1
        else:
            self.vertices[u].append(v)
            self.pesos[aresta] = 1

    def salvar_lista_adjacencias(self, arquivo):
        with open(arquivo, 'w', encoding='utf-8') as f:
            for v in sorted(self.vertices.keys()):
                rotulo_v = self.rotulos.get(v, str(v))
                f.write(f"Vértice {v} ({rotulo_v}):\n")
                if not self.vertices[v]:
                    f.write("  Nenhuma conexão de saída\n")
                else:
                    for u in self.vertices[v]:
                        peso = self.pesos.get((v, u), 1)
                        rotulo_u = self.rotulos.get(u, str(u))
                        f.write(f"  -> {u} ({rotulo_u}), peso: {peso}\n")
                f.write("\n")

    def diametro(self):
        def bfs(origem):
            visitado = {origem: None}
            distancia = {origem: 0}
            fila = deque([origem])
            while fila:
                atual = fila.popleft()
                for vizinho in self.vertices[atual]:
                    if vizinho not in visitado:
                        visitado[vizinho] = atual
                        distancia[vizinho] = distancia[atual] + 1
                        fila.append(vizinho)
            return distancia, visitado

        max_distancia = -1
        caminho_max = []
        for vertice in self.vertices:
            distancias, anteriores = bfs(vertice)
            for destino, dist in distancias.items():
                if dist > max_distancia:
                    max_distancia = dist
                    caminho = []
                    atual = destino
                    while atual is not None:
                        caminho.append(atual)
                        atual = anteriores[atual]
                    caminho.reverse()
                    caminho_max = caminho
        return max_distancia, caminho_max

def processar_arquivo_email(caminho_arquivo, grafo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()
        msg = email.message_from_string(conteudo)
        remetente = msg.get('From', '').strip()
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', remetente)
        if not email_match:
            return
        remetente = email_match.group(0).lower()
        grafo.adicionar_vertice(remetente, remetente)
        for campo in ['To', 'Cc', 'Bcc']:
            destinatarios_str = msg.get(campo, '')
            if not destinatarios_str:
                continue
            destinatarios = re.findall(r'[\w\.-]+@[\w\.-]+', destinatarios_str)
            for dest in destinatarios:
                dest = dest.lower()
                grafo.adicionar_vertice(dest, dest)
                grafo.adicionar_aresta(remetente, dest)
    except Exception as e:
        print(f"Erro ao processar o arquivo {caminho_arquivo}: {e}")

def construir_grafo_emails(diretorio_base):
    grafo = Grafo()
    emails_processados = 0
    try:
        for raiz, dirs, arquivos in os.walk(diretorio_base):
            for arquivo in arquivos:
                if arquivo.startswith('.') or '.' in arquivo:
                    continue
                caminho_arquivo = os.path.join(raiz, arquivo)
                processar_arquivo_email(caminho_arquivo, grafo)
                emails_processados += 1
                if emails_processados % 1000 == 0:
                    print(f"Emails processados: {emails_processados}")
    except Exception as e:
        print(f"Erro ao construir o grafo: {e}")
    print(f"Total de emails processados: {emails_processados}")
    return grafo

def verificar_grafo_euleriano(grafo):
    grau_saida = defaultdict(int)
    grau_entrada = defaultdict(int)
    for u in grafo.vertices:
        for v in grafo.vertices[u]:
            grau_saida[u] += 1
            grau_entrada[v] += 1
    euleriano = True
    for v in grafo.vertices:
        entrada = grau_entrada.get(v, 0)
        saida = grau_saida.get(v, 0)
        if entrada != saida:
            print(f"Vértice '{grafo.rotulos.get(v, v)}' viola a condição: grau de entrada = {entrada}, grau de saída = {saida}")
            euleriano = False
    if euleriano:
        print("O grafo é Euleriano: todos os vértices têm grau de entrada igual ao grau de saída.")
    else:
        print("O grafo NÃO é Euleriano: existem vértices com grau de entrada diferente do grau de saída.")
    return euleriano

def main():
    diretorio_base = "Amostra Enron - 2016"
    print(f"Iniciando processamento da base Enron em '{diretorio_base}'...")
    grafo = construir_grafo_emails(diretorio_base)
    arquivo_saida = "grafo.txt"
    grafo.salvar_lista_adjacencias(arquivo_saida)
    print(f"Grafo construído com {grafo.ordem()} vértices e {grafo.tamanho()} arestas.")
    print(f"Lista de adjacências salva no arquivo '{arquivo_saida}'")
    print(f"Vértices isolados: {grafo.vertice_isolado()}")
    print("\nPrimeiros 20 indivíduos com maior grau de saída (número de destinatários distintos):")
    maiores_graus_saida = grafo.maiores_graus_saida()
    for i, (email, grau) in enumerate(maiores_graus_saida, start=1):
        rotulo = grafo.rotulos.get(email, email)
        print(f"{i}. {rotulo} - Grau de saída: {grau}")
    verificar_grafo_euleriano(grafo)
    diametro, caminho = grafo.diametro()
    print(f"\nDiâmetro do grafo: {diametro}")
    print("Caminho correspondente:")
    for i, v in enumerate(caminho):
        print(f"{i+1}. {grafo.rotulos.get(v, v)}")

if __name__ == "__main__":
    main()

