# visualization.py

import pygame
import math

# --- Constantes de Visualização ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
GRID_SIZE = 8
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE

# Cores (RGB)
COLORS = {
    "Estrada": (200, 200, 200),  # Cinza claro
    "Terra": (139, 69, 19),    # Marrom
    "Lama": (88, 41, 0),       # Marrom escuro
    "Barreira": (40, 40, 40),      # Cinza escuro
    "BACKGROUND": (255, 255, 255), # Branco
    "GRID_LINES": (0, 0, 0),       # Preto
}

class Visualizer:
    def __init__(self, board):
        pygame.init()
        pygame.display.set_caption("A* - Caminho Tático do Cavalo")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.board = board
        self.clock = pygame.time.Clock()
        
        # Mapeia os custos do tabuleiro para as cores
        self.cost_to_color_map = {
            board.costs["Estrada"]: COLORS["Estrada"],
            board.costs["Terra"]: COLORS["Terra"],
            board.costs["Lama"]: COLORS["Lama"],
            board.costs["Barreira"]: COLORS["Barreira"],
        }

    def _draw_board(self):
        """ Desenha o mapa de terreno (tabuleiro estático). """
        self.screen.fill(COLORS["BACKGROUND"])
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                # Calcula a posição do retângulo na tela
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                # Pega o custo daquela célula
                cost = self.board.get_cost((x, y))
                
                # Pega a cor correspondente
                color = self.cost_to_color_map.get(cost, COLORS["BACKGROUND"])
                
                # Desenha a célula
                pygame.draw.rect(self.screen, color, rect)
                # Desenha a grade
                pygame.draw.rect(self.screen, COLORS["GRID_LINES"], rect, 1)

    def run(self):
        """ Loop principal da visualização. """
        running = True
        while running:
            # --- Tratamento de Eventos ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # --- Lógica de Desenho ---
            self._draw_board() # Por enquanto, só desenha o tabuleiro
            
            # --- Atualização da Tela ---
            pygame.display.flip()
            self.clock.tick(30) # Limita a 30 frames por segundo

        pygame.quit()