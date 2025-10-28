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

    # Verifica se já existe o resultado armazenado em cache.
    # Isso evita recalcular a mesma distância entre dois pontos.
    if (start_pos, end_pos) in _knight_dist_cache:
        return _knight_dist_cache[(start_pos, end_pos)]

    # Cria uma fila (queue) para armazenar as posições a explorar.
    # Cada elemento contém: (posição_atual, distância_em_movimentos)
    queue = deque([(start_pos, 0)])

    # Conjunto de posições já visitadas, evitando revisitar casas do tabuleiro.
    visited = {start_pos}

    # Define todos os movimentos possíveis do cavalo no xadrez.
    # Cada tupla representa o deslocamento (dx, dy).
    knight_moves = [
        (1, 2), (1, -2), (-1, 2), (-1, -2),
        (2, 1), (2, -1), (-2, 1), (-2, -1)
    ]

    # Enquanto ainda existirem posições a explorar na fila...
    while queue:
        # Retira a próxima posição (FIFO) para explorar.
        current_pos, dist = queue.popleft()

        # Se a posição atual for o destino, encontramos o número mínimo de saltos.
        # Armazena o resultado em cache e o retorna.
        if current_pos == end_pos:
            _knight_dist_cache[(start_pos, end_pos)] = dist
            return dist

        # Explora todos os possíveis movimentos do cavalo a partir da posição atual.
        for move in knight_moves:
            # Calcula a próxima posição aplicando o deslocamento.
            next_pos = (current_pos[0] + move[0], current_pos[1] + move[1])

            # Verifica se a nova posição está dentro dos limites do tabuleiro (8x8)
            # e se ainda não foi visitada.
            if (0 <= next_pos[0] < 8 and 
                0 <= next_pos[1] < 8 and 
                next_pos not in visited):

                # Marca a posição como visitada para evitar ciclos.
                visited.add(next_pos)

                # Adiciona a nova posição à fila com +1 no número de movimentos.
                queue.append((next_pos, dist + 1))

    # Caso o destino não seja alcançável (não deveria ocorrer num tabuleiro 8x8),
    # retorna infinito como fallback de segurança.
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