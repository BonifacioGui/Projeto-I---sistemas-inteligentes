# board.py

import math

class Board:
    def __init__(self):
        # Define os custos de terreno. Usamos 'inf' (infinito) para barreiras.
        self.costs = {
            "Estrada": 0.5,
            "Terra": 1.0,
            "Lama": 5.0,
            "Barreira": math.inf
        }
        
        # Um exemplo de tabuleiro 8x8.
        # 0: Estrada, 1: Terra, 2: Lama, 3: Barreira
        terrain_map = self._generate_default_map()
        
        # Converte o mapa de terrenos para um mapa de custos reais
        terrain_types = list(self.costs.keys())
        self.grid = [
            [self.costs[terrain_types[terrain_map[y][x]]] for x in range(8)]
            for y in range(8)
        ]
        
        # O menor custo possível em uma casa transitável (será útil para a heurística)
        self.min_cost = min(c for c in self.costs.values() if c != math.inf)

    def _generate_default_map(self):
        terrain_map = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 2, 2, 1, 0, 1],
            [1, 0, 1, 3, 3, 1, 0, 1],
            [1, 0, 1, 3, 3, 1, 0, 1],
            [1, 0, 1, 2, 2, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]
        return terrain_map

    def get_cost(self, position):
        """ Retorna o custo para entrar em uma determinada posição (x, y). """
        x, y = position
        return self.grid[y][x]

    def is_valid(self, position):
        """ Verifica se uma posição (x, y) está dentro do tabuleiro e não é uma barreira. """
        x, y = position
        # Verifica se está dentro dos limites (0 a 7)
        if not (0 <= x < 8 and 0 <= y < 8):
            return False
        # Verifica se não é uma barreira
        if self.grid[y][x] == math.inf:
            return False
        return True