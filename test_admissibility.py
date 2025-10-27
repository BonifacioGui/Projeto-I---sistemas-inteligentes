import random
import math

from board import Board
from a_star import a_star_search
from heuristics import h1_chebyshev, h2_knight_distance

# Heurística nula (equivalente ao Dijkstra)
def h_zero(_current, _goal, _min_cost_ignored=None):
    return 0

def run_dijkstra_like(board, start, goal):
    """
    Roda o A* com heurística 0 para obter:
    - custo real ótimo (menor custo total)
    - número de nós expandidos
    """
    def h_zero(_a, _b, _min_cost=None):
        return 0

    gen = a_star_search(board, start, goal, h_zero)

    while True:
        try:
            next(gen)
        except StopIteration as e:
            final_value = e.value
            if final_value is None:
                return math.inf, 0
            path, nodes_expanded, g_costs, initial_h = final_value
            if not path:
                return math.inf, nodes_expanded
            end_pos = path[-1]
            real_cost = g_costs.get(end_pos, math.inf)
            return real_cost, nodes_expanded



def test_admissibility(num_tests=10):
    """
    Sorteia pares (start, goal) válidos no tabuleiro e testa:
    - admissibilidade de h1 (Chebyshev)
    - admissibilidade de h2 (Distância do cavalo)
    """

    board = Board()

    results = []

    for i in range(num_tests):
        # Sorteia posições válidas (não-barreira e diferentes)
        while True:
            start = (random.randint(0, 7), random.randint(0, 7))
            goal  = (random.randint(0, 7), random.randint(0, 7))
            if start != goal and board.is_valid(start) and board.is_valid(goal):
                break

        # Custo real ótimo usando A* com h=0 (equivalente a Dijkstra)
        real_cost, nodes_expanded = run_dijkstra_like(board, start, goal)

        # Avalia as heurísticas passando board.min_cost
        h1_val = h1_chebyshev(start, goal, board.min_cost)
        h2_val = h2_knight_distance(start, goal, board.min_cost)

        # Checa admissibilidade:
        # Uma heurística h é admissível se h(n) <= custo real mínimo do n até o objetivo.
        # Aqui estamos testando isso no nó inicial "start".
        h1_adm = h1_val <= real_cost + 1e-9
        h2_adm = h2_val <= real_cost + 1e-9

        results.append({
            "start": start,
            "goal": goal,
            "real_cost": real_cost,
            "h1": h1_val,
            "h2": h2_val,
            "h1_adm": h1_adm,
            "h2_adm": h2_adm,
            "nodes_expanded": nodes_expanded,
        })

    # -------- Saída detalhada por par --------
    print("=================================================================")
    print("TESTE DE ADMISSIBILIDADE DAS HEURÍSTICAS")
    print("=================================================================\n")
    for r in results:
        print(f"Start {r['start']} -> Goal {r['goal']}")
        if r["real_cost"] == math.inf:
            print("  Caminho real: INATINGÍVEL (barreiras bloqueando)")
            print(f"  h1 = {r['h1']:.4f} | admissível?  -- (ignorar caso)")
            print(f"  h2 = {r['h2']:.4f} | admissível?  -- (ignorar caso)")
        else:
            print(f"  Custo real ótimo: {r['real_cost']:.4f}")
            print(f"  h1 (chebyshev):  {r['h1']:.4f}  -> admissível? {r['h1_adm']}")
            print(f"  h2 (knightdist): {r['h2']:.4f}  -> admissível? {r['h2_adm']}")
            print(f"  Nós expandidos p/ achar custo real: {r['nodes_expanded']}")
        print()

    # -------- Resumo agregado --------
    total_valid = [r for r in results if r["real_cost"] != math.inf]
    if total_valid:
        h1_ok = sum(1 for r in total_valid if r["h1_adm"])
        h2_ok = sum(1 for r in total_valid if r["h2_adm"])
        print("=================================================================")
        print("RESUMO")
        print("=================================================================")
        print(f"H1 admissível em {h1_ok}/{len(total_valid)} casos ({100*h1_ok/len(total_valid):.1f}%)")
        print(f"H2 admissível em {h2_ok}/{len(total_valid)} casos ({100*h2_ok/len(total_valid):.1f}%)")
        print("=================================================================")


if __name__ == "__main__":
    test_admissibility(num_tests=10)
