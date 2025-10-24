# a_star.py

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