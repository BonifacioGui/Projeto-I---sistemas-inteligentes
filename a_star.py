# a_star.py

import heapq
import math

class Node:
    """
    Representa um nó na busca do A*. Cada nó tem uma posição,
    um custo para chegar até ele, e uma referência ao nó pai.
    """
    def __init__(self, position, parent=None):
        self.position = position  # Uma tupla (x, y)
        self.parent = parent      # O nó que veio antes deste

        self.g = 0  # Custo do caminho desde o início até este nó
        self.h = 0  # Custo da heurística (estimativa até o objetivo)
        self.f = 0  # Custo total (g + h)

    def __eq__(self, other):
        # Dois nós são considerados iguais se tiverem a mesma posição.
        return self.position == other.position
    
    def __lt__(self, other):
        # Usado para ordenar os nós na lista de prioridade (heapq).
        # Nós com menor custo F são considerados "menores".
        return self.f < other.f

def _reconstruct_path(end_node):
    """
    Função auxiliar para reconstruir o caminho a partir do nó final,
    seguindo os 'pais' de volta ao início.
    """
    path = []
    current = end_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Retorna o caminho do início ao fim

def a_star_search(board, start_pos, end_pos, heuristic_func):
    """
    Implementação do algoritmo A* para encontrar o caminho de menor custo.
    """
    
    # 1. Inicialização
    start_node = Node(start_pos)
    end_node = Node(end_pos)
    
    # A Lista Aberta (open_list) é uma fila de prioridade.
    # Armazenamos (f_cost, node) para que o heapq ordene pelo f_cost.
    open_list = []
    heapq.heappush(open_list, (start_node.f, start_node))
    
    # A Lista Fechada (closed_set) armazena apenas as posições (x, y)
    # que já foram totalmente exploradas, para checagem rápida.
    closed_set = set()
    
    # Um dicionário para rastrear o nó com o menor custo g para uma posição
    # Isso nos ajuda a saber se já encontramos um caminho melhor para um nó na open_list
    g_costs = {start_pos: 0}
    
    # Contator de nós expandidos para a análise de eficiência
    nodes_expanded = 0

    # 2. Loop de Busca
    while open_list:
        # Pega o nó com o menor custo F da fila de prioridade
        current_f, current_node = heapq.heappop(open_list)
        
        # Se já exploramos, pulamos
        if current_node.position in closed_set:
            continue
            
        # Marca o nó atual como explorado
        closed_set.add(current_node.position)
        nodes_expanded += 1
        
        # 3. Verificação de Objetivo
        if current_node == end_node:
            path = _reconstruct_path(current_node)
            return path, nodes_expanded

        # 4. Expansão de Vizinhos
        # Movimentos possíveis do cavalo (delta x, delta y)
        knight_moves = [
            (1, 2), (1, -2), (-1, 2), (-1, -2),
            (2, 1), (2, -1), (-2, 1), (-2, -1)
        ]
        
        for move in knight_moves:
            # Calcula a posição do vizinho
            neighbor_pos = (
                current_node.position[0] + move[0],
                current_node.position[1] + move[1]
            )
            
            # Verifica se o vizinho é válido (dentro do tabuleiro e não é barreira)
            if not board.is_valid(neighbor_pos):
                continue

            # Calcula o novo custo G (custo para chegar no vizinho)
            # Custo G = Custo G do nó atual + Custo para entrar na casa do vizinho
            new_g = current_node.g + board.get_cost(neighbor_pos)
            
            # Verifica se este é um caminho melhor do que um já existente
            # ou se é a primeira vez que visitamos este nó
            if neighbor_pos not in g_costs or new_g < g_costs[neighbor_pos]:
                
                # Atualiza o custo G para esta posição
                g_costs[neighbor_pos] = new_g
                
                # Calcula a heurística H
                h = heuristic_func(neighbor_pos, end_pos, board.min_cost)
                
                # Calcula o custo F
                f = new_g + h
                
                # Cria o nó vizinho
                neighbor_node = Node(neighbor_pos, parent=current_node)
                neighbor_node.g = new_g
                neighbor_node.h = h
                neighbor_node.f = f
                
                # Adiciona o vizinho na lista aberta para ser explorado
                heapq.heappush(open_list, (f, neighbor_node))

    # 5. Caminho não encontrado
    return None, nodes_expanded