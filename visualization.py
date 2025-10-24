# visualization.py

import pygame
import math

# --- Constantes de Visualização ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 700  # Altura para o tabuleiro + área de texto
GRID_SIZE = 8
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE

# --- Cores (Paleta Preto e Branco) ---
COLORS = {
    # Cores do Tabuleiro (Tradicional)
    "BOARD_LIGHT": (255, 255, 255), # Branco
    "BOARD_DARK": (0, 0, 0),        # Preto
    "TERRAIN_BARREIRA": (60, 0, 0), # Vermelho-sangue (para destacar no preto/branco)
    
    # Marcadores
    "START_BORDER": (0, 180, 0),       # Verde Escuro
    "END_BORDER": (220, 0, 0),         # Vermelho Brilhante
    "PATH": (70, 0, 130),          # Roxo "Deep Purple"
    
    # Indicadores da Busca
    # --- MUDANÇA: Cor do ponto para VERDE ---
    "CLOSED_DOT": (0, 200, 0),       # Verde vivo 
    
    # UI
    "GRID_LINES": (128, 128, 128),   # Cinza médio
    "TEXT": (0, 0, 0),           # Preto
    "BACKGROUND_UI": (245, 245, 245) # Fundo da UI
}

class Visualizer:
    def __init__(self, board):
        pygame.init()
        pygame.font.init() 
        
        pygame.display.set_caption("A* - Caminho Tático do Cavalo")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.board = board
        self.clock = pygame.time.Clock()
        
        # Fontes
        self.font_main = pygame.font.SysFont('Arial', 22) # Fonte um pouco menor para caber
        self.font_stats = pygame.font.SysFont('Arial', 18)
        self.font_small = pygame.font.SysFont('Arial', 14) # Para o mapa de custo
        
        # Carregar imagem do cavalo
        try:
            self.knight_image = pygame.image.load('knight.png').convert_alpha()
            self.knight_image = pygame.transform.scale(self.knight_image, (CELL_SIZE - 10, CELL_SIZE - 10))
            self.knight_image_offset = (CELL_SIZE - self.knight_image.get_width()) // 2
        except pygame.error:
            print("Erro: Imagem 'knight.png' não encontrada. O cavalo não será desenhado.")
            self.knight_image = None
        
        # Mapeia custos de terreno para as cores de fundo
        self.cost_to_color_map = {
            board.costs["Estrada"]: None, # 'None' usa o padrão xadrez
            board.costs["Terra"]: None, # 'None' usa o padrão xadrez
            board.costs["Lama"]: None, # 'None' usa o padrão xadrez
            board.costs["Barreira"]: COLORS["TERRAIN_BARREIRA"],
        }
    
    def _get_chess_color(self, x, y):
        """ Retorna a cor base (clara/escura) do xadrez. """
        if (x + y) % 2 == 0:
            return COLORS["BOARD_LIGHT"]
        else:
            return COLORS["BOARD_DARK"]

    def _draw_text(self, text, position, font, color=COLORS["TEXT"], center=False):
        """ Helper para desenhar texto na tela. """
        text_surface = font.render(text, True, color)
        if center:
            rect = text_surface.get_rect(center=position)
            self.screen.blit(text_surface, rect)
        else:
            self.screen.blit(text_surface, position)

    def _draw_board(self):
        """ Desenha o mapa de terreno (camada base). """
        # Limpa a tela inteira com a cor de fundo da UI
        self.screen.fill(COLORS["BACKGROUND_UI"]) 
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cost = self.board.get_cost((x, y))
                
                # Define a cor base da célula
                color = self.cost_to_color_map.get(cost)
                if color is None: # Se for 'None', usa o padrão xadrez
                    color = self._get_chess_color(x, y)
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLORS["GRID_LINES"], rect, 1)

    def _draw_search_state(self, search_state):
        """ Desenha os indicadores da busca (pontos verdes da lista fechada). """
        
        dot_radius = CELL_SIZE // 10
        for pos in search_state['closed']:
            center_x = pos[0] * CELL_SIZE + CELL_SIZE // 2
            center_y = pos[1] * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, COLORS["CLOSED_DOT"], (center_x, center_y), dot_radius)

    def _draw_g_cost_map(self, g_costs, path):
        """ Desenha o mapa de calor dos custos G sobre o caminho. """
        if not path:
            return

        path_g_costs = [g_costs.get(pos, 0) for pos in path]
        max_g = max(path_g_costs)
        if max_g == 0: max_g = 1 
        
        for pos in path:
            g = g_costs.get(pos, 0)
            heat_ratio = g / max_g
            
            heat_color = (255, 255 - int(255 * heat_ratio), 0)
            
            rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            s.fill((*heat_color, 120)) 
            self.screen.blit(s, rect.topleft)
            
            self._draw_text(f"{g:.1f}", rect.center, self.font_small, (0,0,0), center=True)

    def _draw_path(self, path):
        """ Desenha o caminho final encontrado. """
        if not path or len(path) < 2:
            return
            
        points = []
        for pos in path:
            center_x = pos[0] * CELL_SIZE + CELL_SIZE // 2
            center_y = pos[1] * CELL_SIZE + CELL_SIZE // 2
            points.append((center_x, center_y))
            
        pygame.draw.lines(self.screen, COLORS["PATH"], False, points, 6) 

    def _draw_markers(self, start_pos, end_pos, current_knight_pos):
        """ Desenha Início, Fim e o Cavalo. """
        
        start_rect = pygame.Rect(start_pos[0] * CELL_SIZE, start_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        end_rect = pygame.Rect(end_pos[0] * CELL_SIZE, end_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, COLORS["START_BORDER"], start_rect, 5)
        pygame.draw.rect(self.screen, COLORS["END_BORDER"], end_rect, 5)
        
        if self.knight_image and current_knight_pos:
            knight_x = current_knight_pos[0] * CELL_SIZE + self.knight_image_offset
            knight_y = current_knight_pos[1] * CELL_SIZE + self.knight_image_offset
            self.screen.blit(self.knight_image, (knight_x, knight_y))

    def run(self, start_pos, end_pos, heuristic_options, search_function):
        """ Loop principal da visualização. """
        running = True
        
        heuristic_names = list(heuristic_options.keys())
        current_heuristic_index = 0
        current_heuristic_name = heuristic_names[current_heuristic_index]
        current_heuristic_func = heuristic_options[current_heuristic_name]
        
        search_generator = None
        search_state = {'open': set(), 'closed': set(), 'current': start_pos}
        final_path = None
        nodes_expanded = 0
        g_costs = {} 
        
        search_running = False
        show_g_map = False 
        
        animation_delay = 25 
        last_update_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()

            # --- Tratamento de Eventos ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not search_running:
                        print(f"Iniciando busca com {current_heuristic_name}...")
                        search_generator = search_function(
                            self.board, start_pos, end_pos, current_heuristic_func
                        )
                        search_running = True
                        final_path = None
                        nodes_expanded = 0
                        g_costs = {}
                        show_g_map = False
                        search_state = {'open': set(), 'closed': set(), 'current': start_pos}
                    
                    if event.key == pygame.K_r:
                        search_generator = None
                        search_state = {'open': set(), 'closed': set(), 'current': start_pos}
                        final_path = None
                        nodes_expanded = 0
                        g_costs = {}
                        search_running = False
                        show_g_map = False
                        print("--- RESETADO ---")
                    
                    if event.key == pygame.K_1 and not search_running:
                        current_heuristic_index = 0
                        current_heuristic_name = heuristic_names[current_heuristic_index]
                        current_heuristic_func = heuristic_options[current_heuristic_name]
                    
                    if event.key == pygame.K_2 and len(heuristic_names) > 1 and not search_running:
                        current_heuristic_index = 1
                        current_heuristic_name = heuristic_names[current_heuristic_index] 
                        current_heuristic_func = heuristic_options[current_heuristic_name]
                    
                    if event.key == pygame.K_g and final_path:
                        show_g_map = not show_g_map
                        print(f"Mapa de Custo G: {'Ligado' if show_g_map else 'Desligado'}")

            # --- Lógica de Busca (Passo a Passo) ---
            if search_running and search_generator and (current_time - last_update_time > animation_delay):
                try:
                    search_state = next(search_generator)
                    last_update_time = current_time
                except StopIteration as e:
                    try:
                        final_path, nodes_expanded, g_costs = e.value
                        if final_path:
                            path_cost = g_costs.get(final_path[-1], 0) # Pega o custo G do nó final
                            print(f"Caminho encontrado! {nodes_expanded} nós expandidos. Custo: {path_cost:.2f}")
                        else:
                            print("Caminho não encontrado.")
                    except ValueError:
                        print("Erro: O algoritmo A* não retornou os 3 valores esperados (path, nodes, g_costs).")
                        final_path, nodes_expanded = None, 0
                        g_costs = {}

                    search_running = False
                    search_generator = None

            # --- Lógica de Desenho (Camadas) ---
            
            # 1. Tabuleiro Base (Sempre o primeiro)
            self._draw_board() 
            
            # 2. Estado da Busca (Pontos verdes)
            if search_state and not show_g_map:
                self._draw_search_state(search_state)
            
            # 3. Caminho Final
            if final_path:
                self._draw_path(final_path)
            
            # 4. Mapa de Calor (se ativado)
            if final_path and show_g_map:
                self._draw_g_cost_map(g_costs, final_path)
            
            # 5. Marcadores (Início, Fim, Cavalo)
            knight_pos_to_draw = start_pos
            if final_path:
                knight_pos_to_draw = final_path[-1] 
            elif search_state:
                knight_pos_to_draw = search_state['current'] 
                
            self._draw_markers(start_pos, end_pos, knight_pos_to_draw)
            
            # 6. UI (Textos)
            # --- MUDANÇA: Posições 'y' ajustadas para baixo (645 e 670) ---
            ui_y1 = SCREEN_WIDTH + 5  # Posição Y da primeira linha da UI (645)
            ui_y2 = SCREEN_WIDTH + 30 # Posição Y da segunda linha da UI (670)

            self._draw_text(f"Heurística: {current_heuristic_name}", (10, ui_y1), self.font_main)
            self._draw_text(f"Nós Expandidos: {nodes_expanded}", (350, ui_y1), self.font_main)
            
            self._draw_text("[1] H0 (Dijkstra)  [2] H2 (Cavalo)", (10, ui_y2), self.font_stats)
            
            # Monta o texto de comandos dinamicamente
            commands_text = "[ESPAÇO] Iniciar  [R] Resetar"
            if final_path:
                commands_text += "  [G] Custo G"
            self._draw_text(commands_text, (350, ui_y2), self.font_stats)
            
            # --- Atualização da Tela ---
            pygame.display.flip()
            self.clock.tick(60) 

        pygame.quit()