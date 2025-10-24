# heuristics.py
from collections import deque

# heuristics.py
# (No final do arquivo, depois da h2_knight_distance)

def h0_dijkstra(current_pos, end_pos, min_cost):
    """
    H0: Heurística Zero (Equivalente ao Dijkstra).
    A heurística mais fraca possível, mas perfeitamente admissível.
    h(n) = 0.
    """
    return 0
    
def h1_manhattan(current_pos, end_pos, min_cost):
    """
    H1: Heurística Fraca (Distância de Manhattan).
    Não considera o movimento do cavalo, apenas a distância no grid.
    É admissível pois é multiplicada pelo menor custo de terreno.
    """
    dx = abs(current_pos[0] - end_pos[0])
    dy = abs(current_pos[1] - end_pos[1])
    distance = dx + dy
    return distance * min_cost

# --- Início da lógica para H2 ---

# Usamos um "cache" para armazenar as distâncias do cavalo
# Assim, só calculamos a distância entre dois pontos uma única vez.
_knight_dist_cache = {}

def _get_min_knight_moves(start_pos, end_pos):
    """
    Calcula o número MÍNIMO de movimentos de cavalo entre dois pontos
    em um tabuleiro VAZIO usando Busca em Largura (BFS).
    """
    # Checa se já calculamos isso
    if (start_pos, end_pos) in _knight_dist_cache:
        return _knight_dist_cache[(start_pos, end_pos)]

    # Fila para o BFS: (posição, distância)
    queue = deque([(start_pos, 0)])
    # Set de posições já visitadas
    visited = {start_pos}
    
    knight_moves = [
        (1, 2), (1, -2), (-1, 2), (-1, -2),
        (2, 1), (2, -1), (-2, 1), (-2, -1)
    ]

    while queue:
        current_pos, dist = queue.popleft()

        if current_pos == end_pos:
            # Achamos! Salva no cache e retorna
            _knight_dist_cache[(start_pos, end_pos)] = dist
            return dist

        for move in knight_moves:
            next_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
            
            # Verifica se está dentro do tabuleiro 8x8 e se não foi visitado
            if (0 <= next_pos[0] < 8 and 
                0 <= next_pos[1] < 8 and 
                next_pos not in visited):
                
                visited.add(next_pos)
                queue.append((next_pos, dist + 1))
    
    return float('inf') # Caso não encontre (não deve acontecer em 8x8)


def h2_knight_distance(current_pos, end_pos, min_cost):
    """
    H2: Heurística Forte (Distância Real do Cavalo).
    Calcula o número mínimo de movimentos de cavalo em um tabuleiro
    vazio e multiplica pelo menor custo de terreno para ser admissível.
    """
    # Pega o número de "passos" do cavalo
    knight_steps = _get_min_knight_moves(current_pos, end_pos)
    
    return knight_steps * min_cost