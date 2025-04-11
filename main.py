from collections import defaultdict
import os
import re
import email


class Grafo:
    def __init__(self):
        self.vertices = defaultdict(list)
        self.rotulos = {}  # Armazena os rótulos dos vértices (endereços de email)
        self.pesos = {}    # Armazena os pesos das arestas (frequência de emails)

    def ordem(self):
        return len(self.vertices)
    
    def tamanho(self):
        return sum(len(vizinhos) for vizinhos in self.vertices.values())
    
    #um vertice é isolado se não tiver nenhuma saida e não tiver nenhuma entrada
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
        """
        Retorna os 20 indivíduos que possuem maior grau de saída e os valores
        correspondentes (de maneira ordenada e decrescente de acordo com o grau)

        Saída:
        - Lista de tuplas (vértice, grau de saída), ordenada.
        """
        # aqui vai calcular o grau de saida de cada vertice
        maiores_graus = [(v, len(self.vertices[v])) for v in self.vertices]

        #  ordena decrescentemente de acordp com grau saida
        maiores_graus.sort(key=lambda x: x[1], reverse=True)

         # retorna os 20 primeiros :))
        return maiores_graus[:20]
    
    def maiores_graus_entrada(self):
        """
        Os 20 indivíduos que possuem maior grau de entrada e os valores
        correspondentes (de maneira ordenada e decrescente de acordo com o grau).

        Saída:
        - Lista de tuplas (vértice, grau de entrada), ordenada.
        """
        # utiliza defaultdict para contar o grau de entrada
        entradas = defaultdict(int)
        for u, v in self.pesos:
            entradas[v] += 1
        maiores_graus = sorted(entradas.items(), key=lambda x: x[1], reverse=True)# tranforma em uma lista de tuplas 
        return maiores_graus[:20] #retorna os 20 primeiros :))
        
    def adicionar_vertice(self, v, rotulo=None):
        # Adiciona um vértice ao grafo com um rótulo opcional
        if v not in self.vertices:
            self.vertices[v] = []
        if rotulo:
            self.rotulos[v] = rotulo
            
    def adicionar_aresta(self, u, v):
        # Adiciona uma aresta direcionada de u para v ou incrementa seu peso
        # Garante que os vértices existam
        if u not in self.vertices:
            self.vertices[u] = []
        if v not in self.vertices:
            self.vertices[v] = []
            
        # Chave para armazenar o peso da aresta (u,v)
        aresta = (u, v)
        
        # Se v já está na lista de adjacência de u, incrementamos o peso
        if v in self.vertices[u]:
            self.pesos[aresta] = self.pesos.get(aresta, 1) + 1
        else:
            # Caso contrário, adicionamos v à lista de adjacência de u e definimos o peso como 1
            self.vertices[u].append(v)
            self.pesos[aresta] = 1
            
    def salvar_lista_adjacencias(self, arquivo):
        # Salva a lista de adjacências em um arquivo texto.
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


def processar_arquivo_email(caminho_arquivo, grafo):
    """
    Processa um único arquivo de email no formato da base Enron
    e atualiza o grafo com as informações de remetente e destinatários.
    
    Parâmetros:
    - caminho_arquivo: caminho do arquivo de email
    - grafo: objeto Grafo a ser atualizado
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()
            
        # Usa a biblioteca email para processar o email
        msg = email.message_from_string(conteudo)
        
        # Extrai remetente
        remetente = msg.get('From', '')
        if not remetente:
            return
            
        # Limpa o endereço de email do remetente
        remetente = remetente.strip()
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', remetente)
        if email_match:
            remetente = email_match.group(0).lower()
        else:
            return
        
        # Adiciona o vértice remetente
        grafo.adicionar_vertice(remetente, remetente)
        
        # Processa todos os destinatários (To, Cc, Bcc)
        for campo in ['To', 'Cc', 'Bcc']:
            destinatarios_str = msg.get(campo, '')
            if not destinatarios_str:
                continue
                
            # Extrai os endereços de email dos destinatários
            destinatarios = re.findall(r'[\w\.-]+@[\w\.-]+', destinatarios_str)
            
            for dest in destinatarios:
                dest = dest.lower()
                grafo.adicionar_vertice(dest, dest)
                grafo.adicionar_aresta(remetente, dest)
                
    except Exception as e:
        print(f"Erro ao processar o arquivo {caminho_arquivo}: {e}")


def construir_grafo_emails(diretorio_base):
    """
    Constrói um grafo direcionado percorrendo recursivamente os diretórios
    da base Enron e processando todos os arquivos de email encontrados.
    
    Parâmetros:
    - diretorio_base: diretório raiz contendo as pastas dos usuários
    
    Retorna:
    - Um objeto Grafo representando o grafo construído
    """
    grafo = Grafo()
    emails_processados = 0
    
    try:
        # Percorre todos os diretórios e subdiretórios
        for raiz, dirs, arquivos in os.walk(diretorio_base):
            for arquivo in arquivos:
                # Ignora arquivos ocultos e outros que não sejam emails
                if arquivo.startswith('.') or '.' in arquivo:
                    continue
                    
                caminho_arquivo = os.path.join(raiz, arquivo)
                processar_arquivo_email(caminho_arquivo, grafo)
                emails_processados += 1
                
                # Exibe progresso a cada 1000 emails processados
                if emails_processados % 1000 == 0:
                    print(f"Emails processados: {emails_processados}")
                
    except Exception as e:
        print(f"Erro ao construir o grafo: {e}")
    
    print(f"Total de emails processados: {emails_processados}")
    return grafo


def verificar_grafo_euleriano(grafo):
    """
    Verifica se o grafo direcionado é Euleriano.
    Um grafo direcionado possui um ciclo Euleriano se:
    - Todos os vértices com grau de entrada ou saída maior que 0 pertencem ao mesmo componente fortemente conexo (não verificado aqui)
    - O grau de entrada é igual ao grau de saída para todos os vértices

    Retorna:
    - True se o grafo é Euleriano
    - False se não for, mostrando os motivos
    """


    grau_saida = defaultdict(int)
    grau_entrada = defaultdict(int)

    # Calcula graus de entrada e saída
    for u in grafo.vertices:
        for v in grafo.vertices[u]:
            grau_saida[u] += 1
            grau_entrada[v] += 1

    # Verifica se todos os vértices têm grau de entrada igual ao de saída
    euleriano = True
    for v in grafo.vertices:
        entrada = grau_entrada.get(v, 0)
        saida = grau_saida.get(v, 0)
        if entrada != saida:
            print(f"Vértice '{grafo.rotulos.get(v, v)}' viola a condição: grau de entrada = {entrada}, grau de saída = {saida}")
            euleriano = False

    if euleriano:
        print("O grafo é Euleriano: todos os vértices têm grau de entrada igual ao grau de saída.")
        return True
    else:
        print("O grafo NÃO é Euleriano: existem vértices com grau de entrada diferente do grau de saída.")
        return False   


def main():
    # Diretório base da amostra Enron
    diretorio_base = "Amostra Enron - 2016"
    
    print(f"Iniciando processamento da base Enron em '{diretorio_base}'...")
    grafo = construir_grafo_emails(diretorio_base)
    
    # Salva a lista de adjacências em um arquivo
    arquivo_saida = "grafo.txt"
    grafo.salvar_lista_adjacencias(arquivo_saida)
    
    print(f"Grafo construído com {grafo.ordem()} vértices e {grafo.tamanho()} arestas.")
    print(f"Lista de adjacências salva no arquivo '{arquivo_saida}'")

    #vertices isolados 
    print(f"Vértices isolados: {grafo.vertice_isolado()}")

    # 20 maiores graus de saida de forma descrescente 
    print("\nPrimeiros 20 indivíduos com maior grau de saída (número de destinatários distintos):")
    maiores_graus_saida = grafo.maiores_graus_saida()
    for i, (email, grau) in enumerate(maiores_graus_saida, start=1):
        rotulo = grafo.rotulos.get(email, email)
        print(f"{i}. {rotulo} - Grau de saída: {grau}")

    # 20 maiores graus de entrada de forma descrescente
    """
    print("\nPrimeiros 20 indivíduos com maior grau de entrada (número de remetentes distintos):")
    maiores_graus = grafo.maiores_graus_entrada()
    for i, (email, grau) in enumerate(maiores_graus, start=1):
        rotulo = grafo.rotulos.get(email, email)
        print(f"{i}. {rotulo} - Grau de entrada: {grau}")
    """

    # verificando if grafo = euleriano (vai printar todos os vertices discrepantes)
    #verificar_grafo_euleriano(grafo)


if __name__ == "__main__":
    main()
