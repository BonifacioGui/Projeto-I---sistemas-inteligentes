# main.py

from board import Board
from visualization import Visualizer
from a_star import a_star_search
from heuristics import h0_dijkstra, h2_knight_distance

# --- Configuração Principal ---
START_POS = (1, 1)
END_POS = (6, 6)

def main():
    """
    Função principal que inicializa e executa o programa.
    """
    # 1. Cria o tabuleiro lógico
    board = Board()
    
    # 2. Define as heurísticas que o visualizador pode usar
    heuristic_options = {
        "H0 (Dijkstra)": h0_dijkstra,
        "H2 (Cavalo)": h2_knight_distance
    }
    
    # 3. Cria o visualizador, passando o tabuleiro para ele
    visualizer = Visualizer(board)
    
    # 4. Inicia o loop principal da aplicação, injetando
    #    as posições, as heurísticas e a função de busca.
    visualizer.run(
        start_pos=START_POS,
        end_pos=END_POS,
        heuristic_options=heuristic_options,
        search_function=a_star_search
    )

if __name__ == "__main__":
    main()