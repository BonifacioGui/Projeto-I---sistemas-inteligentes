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
    Implementação do algoritmo A* (como um GERADOR) para 
    encontrar o caminho de menor custo, retornando o estado a cada passo.
    """
    
    # 1. Inicialização
    start_node = Node(start_pos)
    end_node = Node(end_pos)
    
    open_list = []
    heapq.heappush(open_list, (start_node.f, start_node))
    
    closed_set = set()
    g_costs = {start_pos: 0}
    nodes_expanded = 0

    # 2. Loop de Busca
    while open_list:
        # Pega o nó com o menor custo F da fila
        current_f, current_node = heapq.heappop(open_list)
        
        if current_node.position in closed_set:
            continue
            
        closed_set.add(current_node.position)
        nodes_expanded += 1
        
        # "Pausa" a função e entrega o estado atual para o visualizador desenhar
        yield {
            'open': {node.position for f, node in open_list}, 
            'closed': closed_set,
            'current': current_node.position
        }
        
        # 3. Verificação de Objetivo
        if current_node == end_node:
            path = _reconstruct_path(current_node)
            # --- CORRIGIDO ---
            return path, nodes_expanded, g_costs

        # 4. Expansão de Vizinhos
        knight_moves = [
            (1, 2), (1, -2), (-1, 2), (-1, -2),
            (2, 1), (2, -1), (-2, 1), (-2, -1)
        ]
        
        for move in knight_moves:
            neighbor_pos = (
                current_node.position[0] + move[0],
                current_node.position[1] + move[1]
            )
            
            if not board.is_valid(neighbor_pos):
                continue

            new_g = current_node.g + board.get_cost(neighbor_pos)
            
            if neighbor_pos not in g_costs or new_g < g_costs[neighbor_pos]:
                
                g_costs[neighbor_pos] = new_g
                h = heuristic_func(neighbor_pos, end_pos, board.min_cost)
                f = new_g + h
                
                neighbor_node = Node(neighbor_pos, parent=current_node)
                neighbor_node.g = new_g
                neighbor_node.h = h
                neighbor_node.f = f
                
                heapq.heappush(open_list, (f, neighbor_node))

    # 5. Caminho não encontrado
    # --- CORRIGIDO ---
    return None, nodes_expanded, g_costs