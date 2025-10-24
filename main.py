# main.py

from board import Board
from visualization import Visualizer

def main():
    """
    Função principal que inicializa e executa o programa.
    """
    # 1. Cria o tabuleiro lógico
    board = Board()
    
    # 2. Cria o visualizador, passando o tabuleiro para ele
    visualizer = Visualizer(board)
    
    # 3. Inicia o loop principal da aplicação
    visualizer.run()

if __name__ == "__main__":
    main()