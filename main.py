# main.py

from board import Board
from visualization import Visualizer
from a_star import a_star_search
# --- MUDANÇA: Importa apenas as 2 heurísticas ---
from heuristics import h1_chebyshev, h2_knight_distance

# --- Configuração Principal ---
START_POS = (1, 1)
END_POS = (6, 6)

def main():
    """
    Função principal que inicializa e executa o programa.
    """
    # 1. Cria o tabuleiro lógico
    board = Board()
    
    # --- MUDANÇA: Define as DUAS heurísticas ---
    heuristic_options = {
        "H1 (Chebyshev)": h1_chebyshev,
        "H2 (Cavalo)": h2_knight_distance,
    }
    
    # 3. Cria o visualizador
    visualizer = Visualizer(board)
    
    # 4. Inicia o loop principal
    visualizer.run(
        start_pos=START_POS,
        end_pos=END_POS,
        heuristic_options=heuristic_options,
        search_function=a_star_search
    )

if __name__ == "__main__":
    main()