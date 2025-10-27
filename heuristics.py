# heuristics.py
import math
from collections import deque

def h1_chebyshev(current, goal, min_cost):
    """
    Heurística nula (ou quase nula) — garante admissibilidade universal.
    Usa uma leve aproximação só para guiar melhor a busca.
    """
    dx = abs(current[0] - goal[0])
    dy = abs(current[1] - goal[1])
    # heurística extremamente conservadora: subestima sempre
    return min(dx, dy) * (min_cost * 0.1)

# --- Início da lógica para H2 ---
_knight_dist_cache = {}

def _get_min_knight_moves(start_pos, end_pos):
    """
    Calcula o número MÍNIMO de movimentos de cavalo entre dois pontos
    em um tabuleiro VAZIO usando Busca em Largura (BFS).
    """
    if (start_pos, end_pos) in _knight_dist_cache:
        return _knight_dist_cache[(start_pos, end_pos)]

    queue = deque([(start_pos, 0)])
    visited = {start_pos}
    
    knight_moves = [
        (1, 2), (1, -2), (-1, 2), (-1, -2),
        (2, 1), (2, -1), (-2, 1), (-2, -1)
    ]

    while queue:
        current_pos, dist = queue.popleft()

        if current_pos == end_pos:
            _knight_dist_cache[(start_pos, end_pos)] = dist
            return dist

        for move in knight_moves:
            next_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
            
            if (0 <= next_pos[0] < 8 and 
                0 <= next_pos[1] < 8 and 
                next_pos not in visited):
                
                visited.add(next_pos)
                queue.append((next_pos, dist + 1))
    
    return float('inf') 


def h2_knight_distance(current_pos, end_pos, min_cost):
    """
    H2 (Cavalo): Heurística Forte e Admissível.
    Calcula o número mínimo de movimentos de cavalo em um tabuleiro
    vazio e multiplica pelo menor custo de terreno para ser admissível.
    """
    knight_steps = _get_min_knight_moves(current_pos, end_pos)
    return knight_steps * min_cost

# --- Funções não utilizadas (mantidas para referência) ---

def h0_dijkstra(current_pos, end_pos, min_cost):
    """
    H0 (Dijkstra): A Heurística Admissível mais fraca.
    h(n) = 0.
    """
    return 0

def h1_manhattan(current_pos, end_pos, min_cost):
    """
    H_M (Manhattan): Heurística Não-Admissível.
    Implementação baseada na Dica do projeto.
    NOTA: Esta heurística provou ser NÃO-ADMISSÍVEL nos testes,
    pois superestimou o custo real (ex: estimou 5.0 para um custo real de 4.50).
    """
    dx = abs(current_pos[0] - end_pos[0])
    dy = abs(current_pos[1] - end_pos[1])
    distance = dx + dy
    return distance * min_cost