"""
visualization.py (v14 - Lado-a-Lado Corrigido e Melhorado)

Funcionalidades Atualizadas:
- Correção do KeyError ao iniciar/retomar busca.
- Layout aprimorado com separador visual mais forte.
- Tela ligeiramente mais alta.
- Sidebar com melhor clareza e espaçamento.
- [N] para Novo Tabuleiro Aleatório.
- [ESPAÇO] inicia/pausa/retoma AMBAS as buscas.
- [V] / [O] / [G] mostram o estado final de AMBAS as buscas.
- Caminho final (amarelo) desenhado em "L"s.
- Células e Bordas do caminho final destacadas.
"""

import pygame
import math
import os
import time

# --- MUDANÇA: Layout com Separador Mais Forte e Tela Mais Alta ---
BOARD_PIXEL = 480
SEPARATOR_WIDTH = 20 # Mais largo
SIDEBAR_WIDTH = 300
SCREEN_WIDTH = BOARD_PIXEL * 2 + SEPARATOR_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = 650 # Mais alta
GRID_SIZE = 8
CELL_SIZE = BOARD_PIXEL // GRID_SIZE # 60
BOARD_OFFSET_X = BOARD_PIXEL + SEPARATOR_WIDTH
SIDEBAR_START_X = BOARD_PIXEL * 2 + SEPARATOR_WIDTH

# --- Paleta de Cores (COM DESTAQUE MAGENTA NA BORDA) ---
PALETTE = {
    # Cores de Terreno
    'terrain_road': (192, 192, 192), # Cinza
    'terrain_land': (210, 180, 140), # Marrom Claro
    'terrain_mud': (139, 69, 19),     # Marrom Escuro
    'terrain_block': (60, 0, 0),     # Vermelho-sangue/Preto

    # Cores da Busca (Preenchimento Sólido)
    'open_fill': (135, 206, 250),     # Azul Céu Claro
    'closed_fill': (85, 107, 47),    # Verde Musgo Escuro (DarkOliveGreen)

    # Cores do Resultado
    'path': (255, 255, 0),         # Amarelo Brilhante (para as linhas em L)
    'start_border': (0, 255, 0),     # Verde Brilhante
    'end_border': (255, 0, 0),       # Vermelho Brilhante

    'path_fill_color': (255, 255, 0), # Amarelo para o preenchimento
    'path_fill_alpha': 150,           # Opacidade do preenchimento

    'path_border_color': (255, 0, 255), # MAGENTA BRILHANTE (era marrom escuro)
    'path_border_width': 3,             # Espessura da borda

    # UI & Gráfico
    'panel': (37, 41, 47),         # Fundo do Sidebar
    'grid_line': (60, 60, 60),     # Linhas da grade escuras
    'text': (230, 234, 240),      # Texto claro (sidebar)
    'text_dark': (0, 0, 0),        # Texto escuro (heatmap/gráfico/labels/separador)
    'muted': (150, 155, 165),      # Texto secundário
    'accent': (255, 200, 80),      # Destaque
    'bg_chart': (245, 245, 245),   # Fundo claro gráfico
    'bar_h1': (255, 160, 122),     # Cor barra H1
    'bar_h2': (120, 220, 140),     # Cor barra H2
}

# Paths
DEFAULT_KNIGHT_PATHS = ['assets/knight.png', 'knight.png', './knight.png']


class Visualizer:
    def __init__(self, board, *, fps=60):
        pygame.init(); pygame.font.init()
        pygame.display.set_caption('A* — Tactical Knight (Comparação Lado-a-Lado)')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock(); self.board = board; self.fps = fps

        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 26, bold=True)
        self.main_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)
        self.chart_font = pygame.font.SysFont('Arial', 16)
        self.label_font = pygame.font.SysFont('Arial', 20, bold=True) # Labels H1/H2

        # Load knight image
        self.knight_img = None
        for p in DEFAULT_KNIGHT_PATHS:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    target = CELL_SIZE - 15
                    if target > 0:
                        self.knight_img = pygame.transform.smoothscale(img, (target, target))
                    break
                except Exception as e: print(f"Erro imagem {p}: {e}"); self.knight_img = None

        # Terrain color map
        self.cost_to_color = {
            board.costs['Estrada']: PALETTE['terrain_road'], board.costs['Terra']: PALETTE['terrain_land'],
            board.costs['Lama']: PALETTE['terrain_mud'], board.costs['Barreira']: PALETTE['terrain_block'], }

        # Estado agora é por heurística
        self.reset_state()

    def reset_state(self, keep_results=False): # Adicionado keep_results
        """Reseta o estado dinâmico da busca."""
        self.open_sets = {}
        self.closed_sets = {}
        self.current_nodes = {}
        self.nodes_expanded = {}
        self.search_generators = {} # Limpa geradores
        self.search_running_flags = {} # Limpa flags de execução
        self.search_finished_flags = {} # Limpa flags de conclusão
        self.animation_starts = {}
        self.start_times = {}

        if not keep_results:
            self.results = {} # Limpa resultados apenas se não for para manter

        # Estados globais (geralmente definidos fora do reset, mas garantidos aqui)
        self.start_pos=getattr(self, 'start_pos', None)
        self.end_pos=getattr(self, 'end_pos', None)
        self.h_names = getattr(self, 'h_names', [])
        self.heuristic_funcs = getattr(self, 'heuristic_funcs', {})

        # Toggles
        self.show_g_map=False
        self.view_mode='search' # Sempre volta para a busca
        self.show_closed_list_toggle = False
        self.show_open_list_toggle = False

    # --- Funções de Desenho (sem alterações desde a v13) ---
    def _draw_text(self, text, pos, font, color):
        surf = font.render(text, True, color); self.screen.blit(surf, pos)

    def _draw_text_center(self, text, center_pos, font, color):
        surf = font.render(text, True, color); rect = surf.get_rect(center=center_pos)
        self.screen.blit(surf, rect)

    def _get_terrain_color(self, pos):
        cost = self.board.get_cost(pos)
        return self.cost_to_color.get(cost, (255, 255, 255))

    def _draw_board_and_search_state(self, offset_x, h_name):
        final_results = self.results.get(h_name)
        open_set_dyn = self.open_sets.get(h_name, set())
        closed_set_dyn = self.closed_sets.get(h_name, set())
        is_running = self.search_running_flags.get(h_name, False)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                pos = (x, y); rect = pygame.Rect(offset_x + x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                base_color = self._get_terrain_color(pos); pygame.draw.rect(self.screen, base_color, rect)
                draw_color = None
                if is_running:
                    if pos in closed_set_dyn and pos != self.start_pos and pos != self.end_pos: draw_color = PALETTE['closed_fill']
                    elif pos in open_set_dyn and pos != self.start_pos and pos != self.end_pos: draw_color = PALETTE['open_fill']
                elif final_results:
                    closed_set_final = final_results.get('closed_set', set())
                    if self.show_closed_list_toggle and pos in closed_set_final and pos != self.start_pos and pos != self.end_pos: draw_color = PALETTE['closed_fill']
                    open_set_final = final_results.get('open_set', set())
                    if self.show_open_list_toggle and pos in open_set_final and pos != self.start_pos and pos != self.end_pos: draw_color = PALETTE['open_fill']
                if draw_color: pygame.draw.rect(self.screen, draw_color, rect)

    def _draw_grid(self, offset_x):
        color = PALETTE['grid_line']; grid_height = BOARD_PIXEL
        for y in range(GRID_SIZE + 1): pygame.draw.line(self.screen, color, (offset_x, y*CELL_SIZE), (offset_x + BOARD_PIXEL, y*CELL_SIZE), 1)
        for x in range(GRID_SIZE + 1): pygame.draw.line(self.screen, color, (offset_x + x*CELL_SIZE, 0), (offset_x + x*CELL_SIZE, grid_height), 1)

    def _draw_path_highlight(self, offset_x, h_name):
        final_results = self.results.get(h_name);
        if not final_results or not final_results.get('path'): return
        final_path = final_results['path']; highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        fill_color = PALETTE['path_fill_color']; fill_alpha = PALETTE['path_fill_alpha']
        highlight_surface.fill((*fill_color, fill_alpha)); border_color = PALETTE['path_border_color']; border_width = PALETTE['path_border_width']
        for pos in final_path:
            if pos == self.start_pos or pos == self.end_pos: continue
            rect_pos = (offset_x + pos[0] * CELL_SIZE, pos[1] * CELL_SIZE)
            self.screen.blit(highlight_surface, rect_pos)
            pygame.draw.rect(self.screen, border_color, (*rect_pos, CELL_SIZE, CELL_SIZE), border_width)

    def _draw_path(self, offset_x, h_name):
        final_results = self.results.get(h_name);
        if not final_results or not final_results.get('path') or len(final_results['path']) < 2: return
        final_path = final_results['path']; path_color = PALETTE['path']; line_width = 4
        for i in range(len(final_path) - 1):
            p1 = final_path[i]; p2 = final_path[i+1]
            p1_center = (offset_x + p1[0] * CELL_SIZE + CELL_SIZE // 2, p1[1] * CELL_SIZE + CELL_SIZE // 2)
            p2_center = (offset_x + p2[0] * CELL_SIZE + CELL_SIZE // 2, p2[1] * CELL_SIZE + CELL_SIZE // 2)
            dx = p2[0] - p1[0]; dy = p2[1] - p1[1]; intermediate_point = p1_center
            if abs(dx) == 1 and abs(dy) == 2: intermediate_point = (p2_center[0], p1_center[1])
            elif abs(dx) == 2 and abs(dy) == 1: intermediate_point = (p1_center[0], p2_center[1])
            pygame.draw.line(self.screen, path_color, p1_center, intermediate_point, line_width)
            pygame.draw.line(self.screen, path_color, intermediate_point, p2_center, line_width)

    def _draw_g_heatmap(self, offset_x, h_name):
        final_results = self.results.get(h_name);
        if not self.show_g_map or not final_results or not final_results.get('path') or not final_results.get('g_costs'): return
        final_path = final_results['path']; g_costs = final_results['g_costs']
        path_g = [g_costs.get(p,0) for p in final_path if p in g_costs]; max_g = max(path_g) if path_g else 1
        for pos in final_path:
            g = g_costs.get(pos, 0); ratio = min(1.0, g / max_g) if max_g > 0 else 0
            r, g_col, b = 255, 255 - int(255 * ratio), 0; r,g_col,b = max(0,min(255,r)), max(0,min(255,g_col)), max(0,min(255,b))
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA); s.fill((r, g_col, b, 170))
            self.screen.blit(s, (offset_x + pos[0]*CELL_SIZE, pos[1]*CELL_SIZE))
            center = (offset_x + pos[0]*CELL_SIZE+CELL_SIZE//2, pos[1]*CELL_SIZE+CELL_SIZE//2)
            self._draw_text_center(f"{g:.1f}", center, self.small_font, PALETTE['text_dark'])

    def _draw_markers_and_knight(self, offset_x, h_name, t):
        pad = 3
        if self.start_pos: start_r = pygame.Rect(offset_x + self.start_pos[0]*CELL_SIZE, self.start_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE); pygame.draw.rect(self.screen, PALETTE['start_border'], start_r, pad)
        if self.end_pos: end_r = pygame.Rect(offset_x + self.end_pos[0]*CELL_SIZE, self.end_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE); pygame.draw.rect(self.screen, PALETTE['end_border'], end_r, pad)
        knight_pos = None; final_results = self.results.get(h_name); animation_start = self.animation_starts.get(h_name)
        if final_results and final_results.get('path') and animation_start:
            final_path = final_results['path']; elapsed=time.time()-animation_start; step_t=0.18; steps=len(final_path);
            idx = max(0, min(steps - 1, int(elapsed // step_t))); knight_pos = final_path[idx]
        elif self.search_running_flags.get(h_name, False): knight_pos = self.current_nodes.get(h_name)
        elif not self.search_finished_flags.get(h_name, False) and self.start_pos: knight_pos = self.start_pos
        if knight_pos: self._blit_knight_at(offset_x, knight_pos)

    def _blit_knight_at(self, offset_x, pos):
        if not pos: return
        cx, cy = offset_x + pos[0]*CELL_SIZE+CELL_SIZE//2, pos[1]*CELL_SIZE+CELL_SIZE//2
        if self.knight_img: rect = self.knight_img.get_rect(center=(cx, cy)); self.screen.blit(self.knight_img, rect.topleft)
        else: pygame.draw.circle(self.screen, PALETTE['accent'], (cx,cy), CELL_SIZE//4); pygame.draw.circle(self.screen, (255,255,255), (cx,cy), CELL_SIZE//12)

    def _draw_sidebar(self):
        sidebar_x = SIDEBAR_START_X; pygame.draw.rect(self.screen, PALETTE['panel'], (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        x0, y = sidebar_x + 20, 20; self._draw_text('A* Lado-a-Lado', (x0, y), self.title_font, PALETTE['text']); y += 45
        y_info_start = y; line_h = 22; section_sp = 28; info_block_height = 4 * section_sp + 10; separator_y = y_info_start + info_block_height + 15
        for i, h_name in enumerate(self.h_names):
            y_info = y_info_start + i * (info_block_height + 30); self._draw_text(h_name, (x0, y_info), self.label_font, PALETTE['accent']); y_info += 35
            current_results = self.results.get(h_name); costo_final = "-"; comp_caminho = "-"; nodes_str = "-"; status = "Pendente"
            if self.search_running_flags.get(h_name, False): status = "Buscando..."; nodes_str = str(self.nodes_expanded.get(h_name, 0))
            elif self.search_finished_flags.get(h_name, False):
                 status = "Concluído";
                 if current_results:
                     nodes_str = str(current_results.get('nodes', '-'))
                     if current_results.get('path'): path = current_results['path']; costo_final = f"{current_results.get('cost', 0):.2f}"; comp_caminho = str(len(path) - 1) if path else '0'
                     else: costo_final = "Ñ enc."; comp_caminho = "-"
            info = [('Status', status), ('Nós Expandidos', nodes_str), ('Custo Final', costo_final), ('Comp. Caminho', comp_caminho), ]
            label_x = x0; value_x = x0 + 150
            for label, value in info: self._draw_text(label + ':', (label_x, y_info), self.small_font, PALETTE['muted']); self._draw_text(value, (value_x, y_info), self.main_font, PALETTE['text']); y_info += section_sp
            if i == 0: pygame.draw.line(self.screen, PALETTE['grid_line'], (x0, separator_y), (sidebar_x + SIDEBAR_WIDTH - 20, separator_y), 1)
        y_ctrls = separator_y + info_block_height + 45; self._draw_text('Controles', (x0, y_ctrls), self.main_font, PALETTE['accent']); y_ctrls += 35; ctrl_sp = 28
        controls = ['[ESPAÇO] - Iniciar/Pausar Buscas', '[N]      - Novo Tabuleiro', '[G]      - Mapa de Custo G', '[V]      - Exploração Final', '[O]      - Candidatos Finais', '[C]      - Ver Gráfico', '[R]      - Reset Busca', '[ESC]    - Sair do Gráfico', ]
        for c_text in controls: self._draw_text(c_text, (x0, y_ctrls), self.small_font, PALETTE['muted']); y_ctrls += ctrl_sp

    def _draw_chart_view(self):
        heuristic_options = {name: func for name, func in self.heuristic_funcs.items()}
        self.screen.fill(PALETTE['bg_chart']); title_y, sub_y = 40, 80
        self._draw_text_center('Comparação de Eficiência', (SCREEN_WIDTH / 2, title_y), self.title_font, PALETTE['text_dark'])
        self._draw_text_center('Nós Expandidos (Menor é Melhor)', (SCREEN_WIDTH / 2, sub_y), self.main_font, PALETTE['text_dark'])
        names=self.h_names; results_data={n: self.results.get(n,{}) for n in names}
        have_data=all(isinstance(r,dict) and r.get('nodes',0)>0 for r in results_data.values())
        if not have_data: self._draw_text_center("Execute AMBAS as buscas ([ESPAÇO]) para comparar.", (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50), self.main_font, PALETTE['text_dark']); self._draw_text_center('[R] Voltar', (SCREEN_WIDTH/2, SCREEN_HEIGHT - 60), self.main_font, PALETTE['text_dark']); return
        nodes=[results_data[n].get('nodes',0) for n in names]; max_n=max(nodes) if nodes else 1
        bar_w = 180; max_bar_h = 280; n_bars = len(names); top_chart_margin = 120; bottom_chart_margin = 180; base_y = top_chart_margin + max_bar_h
        total_w = n_bars*bar_w; total_sp=100; chart_w=total_w+(n_bars-1)*total_sp; start_x=(SCREEN_WIDTH-chart_w)/2; colors=[PALETTE.get('bar_h1'), PALETTE.get('bar_h2')]
        for i, n in enumerate(names):
            bx=start_x+i*(bar_w+total_sp); node_val=results_data[n].get('nodes',0); bh=(node_val/max_n)*max_bar_h if max_n>0 else 0; by=base_y-bh; color=colors[i%len(colors)]
            pygame.draw.rect(self.screen, color, (bx, by, bar_w, bh), border_radius=6); self._draw_text_center(str(node_val), (bx+bar_w/2, by + 25), self.main_font, PALETTE['text_dark'])
            self._draw_text_center(n, (bx+bar_w/2, base_y+25), self.chart_font, PALETTE['text_dark']); info_y, info_sp = base_y + 55, 22
            details = [ f"Tempo: {results_data[n].get('time', 0):.1f} ms", f"Custo: {results_data[n].get('cost', 0):.2f}", f"H Ini: {results_data[n].get('initial_h', 0):.2f}" ];
            for j, d in enumerate(details): self._draw_text_center(d, (bx+bar_w/2, info_y+j*info_sp), self.small_font, PALETTE['text_dark'])
        if len(names)==2:
            res1, res2 = results_data[names[0]], results_data[names[1]]; win_n=names[0] if res1.get('nodes', float('inf')) < res2.get('nodes', float('inf')) else names[1]; los_n=names[1] if win_n == names[0] else names[0]; conc1, conc2 = "", ""
            if res1.get('nodes',0)==res2.get('nodes',0): conc1="Mesma eficiência."
            else: diff=abs(res1.get('nodes',0)-res2.get('nodes',0)); los_nodes=results_data[los_n].get('nodes',1); perc=(diff/los_nodes)*100 if los_nodes>0 else 0; conc1=f"{win_n} mais eficiente."; conc2=f"({perc:.1f}% redução vs {los_n})."
            conc1_y = info_y + len(details) * info_sp + 30; self._draw_text_center(conc1, (SCREEN_WIDTH/2, conc1_y), self.main_font, PALETTE['text_dark'])
            if conc2: self._draw_text_center(conc2, (SCREEN_WIDTH/2, conc1_y+25), self.chart_font, PALETTE['muted'])
        self._draw_text_center('[R] Voltar', (SCREEN_WIDTH/2, SCREEN_HEIGHT-60), self.main_font, PALETTE['text_dark'])

    # --- Main loop (LÓGICA DO K_SPACE CORRIGIDA) ---
    def run(self, start_pos, end_pos, heuristic_options, search_function):

        # Configuração inicial
        self.reset_state() # Garante estado limpo
        self.start_pos=start_pos; self.end_pos=end_pos
        self.heuristic_funcs = heuristic_options
        self.h_names = list(heuristic_options.keys())
        self.results = {name: None for name in self.h_names} # Garante que results exista
        if len(self.h_names) < 2: raise ValueError('Necessita de 2 heurísticas')

        # Loop principal
        running = True; last_update_t = pygame.time.get_ticks()

        while running:
            now = pygame.time.get_ticks(); dt = self.clock.tick(self.fps)/1000.0

            # --- Event Handling ---
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False
                elif ev.type == pygame.KEYDOWN:

                    if ev.key == pygame.K_r: # Reset (manter tabuleiro)
                        if self.view_mode=='chart': self.view_mode='search'; print("Voltando.")
                        else:
                            # Reseta estado dinâmico, mantém results
                            self.reset_state(keep_results=True)
                            self.start_pos = start_pos; self.end_pos = end_pos
                            self.heuristic_funcs = heuristic_options; self.h_names = list(heuristic_options.keys())
                            print("--- ESTADO DA BUSCA RESETADO (mesmo tabuleiro) ---")

                    elif ev.key == pygame.K_ESCAPE and self.view_mode == 'chart':
                        self.view_mode = 'search'; print("Voltando.")

                    elif self.view_mode == 'search':

                        if ev.key == pygame.K_n: # Novo Tabuleiro Aleatório
                             self.board.randomize()
                             self.reset_state(keep_results=False) # Limpa tudo
                             self.start_pos = start_pos; self.end_pos = end_pos
                             self.heuristic_funcs = heuristic_options; self.h_names = list(heuristic_options.keys())
                             self.results = {name: None for name in self.h_names} # Garante limpeza
                             print("[N] Novo tabuleiro gerado.")

                        # --- LÓGICA K_SPACE CORRIGIDA ---
                        elif ev.key == pygame.K_SPACE:
                            is_any_running = any(self.search_running_flags.values())
                            are_all_finished = all(self.search_finished_flags.get(h, False) for h in self.h_names)
                            # Verifica se os geradores *foram* inicializados alguma vez neste tabuleiro
                            were_generators_initialized = bool(self.search_generators)

                            if is_any_running:
                                print("Pausando buscas...")
                                for h_name in self.h_names:
                                    self.search_running_flags[h_name] = False # Pausa
                            else: # Nenhuma busca rodando no momento
                                # Se JÁ foram inicializados e NÃO terminaram, retoma
                                if were_generators_initialized and not are_all_finished:
                                    print("Retomando buscas...")
                                    for h_name in self.h_names:
                                        if not self.search_finished_flags.get(h_name, False):
                                            self.search_running_flags[h_name] = True
                                else: # Primeira execução OU reinício após todas terminarem (ou após R/N)
                                    print("Iniciando/Reiniciando ambas as buscas...");
                                    # --- Código de Inicialização ---
                                    # Garante que estados dinâmicos estejam limpos antes de (re)criar geradores
                                    self.open_sets = {}; self.closed_sets = {}; self.current_nodes = {}
                                    self.nodes_expanded = {}; self.search_generators = {}
                                    self.search_running_flags = {}; self.search_finished_flags = {}
                                    self.animation_starts = {}; self.start_times = {}

                                    self.start_pos = start_pos; self.end_pos = end_pos
                                    self.heuristic_funcs = heuristic_options; self.h_names = list(heuristic_options.keys())

                                    for h_name in self.h_names:
                                        # Recria o gerador
                                        self.search_generators[h_name] = search_function(
                                            self.board, start_pos, end_pos, self.heuristic_funcs[h_name]
                                        )
                                        # Define estado inicial
                                        self.search_running_flags[h_name] = True
                                        self.search_finished_flags[h_name] = False
                                        self.open_sets[h_name] = set([start_pos])
                                        self.closed_sets[h_name] = set()
                                        self.current_nodes[h_name] = start_pos
                                        self.nodes_expanded[h_name] = 0
                                        self.animation_starts[h_name] = None
                                        self.start_times[h_name] = time.time()
                                    # --- Fim Inicialização ---
                        # --- FIM LÓGICA K_SPACE ---

                        elif ev.key == pygame.K_g:
                            self.show_g_map = not self.show_g_map
                            print(f"Mapa G (Ambos): {'On' if self.show_g_map else 'Off'}")

                        elif ev.key == pygame.K_v:
                            self.show_closed_list_toggle = not self.show_closed_list_toggle
                            print(f"Mostrar Exploração Final (Ambos): {'Ligado' if self.show_closed_list_toggle else 'Desligado'}")

                        elif ev.key == pygame.K_o:
                            self.show_open_list_toggle = not self.show_open_list_toggle
                            print(f"Mostrar Candidatos Finais (Ambos): {'Ligado' if self.show_open_list_toggle else 'Desligado'}")

                        elif ev.key == pygame.K_c: # Ver gráfico
                            if all(self.search_finished_flags.get(h, False) for h in self.h_names):
                                 if all(r is not None and isinstance(r, dict) and r.get('nodes', -1) >= 0 for r in self.results.values()):
                                     self.view_mode = 'chart'; print("Gráfico.")
                                 else: print("Erro nos resultados para gerar gráfico.")
                            else: print("Aguarde ambas as buscas terminarem para comparar.")


            # --- Advance Search (Alternando entre H1 e H2) ---
            if self.view_mode == 'search' and any(self.search_running_flags.values()):

                if now - last_update_t > 30: # Ajuste o throttle
                    for h_name in self.h_names:
                        # Só avança se estiver rodando E o gerador existir
                        if self.search_running_flags.get(h_name, False) and h_name in self.search_generators:
                           try:
                                state = next(self.search_generators[h_name])
                                self.open_sets[h_name] = state.get('open', set())
                                self.closed_sets[h_name] = state.get('closed', set())
                                self.current_nodes[h_name] = state.get('current')
                                self.nodes_expanded[h_name] = len(self.closed_sets[h_name])

                           except StopIteration as e:
                                self.search_running_flags[h_name] = False
                                self.search_finished_flags[h_name] = True
                                end_t = time.time()
                                exec_t = (end_t - self.start_times.get(h_name, end_t)) * 1000

                                try:
                                    path, nodes, g_costs, initial_h = e.value
                                    p_cost = g_costs.get(path[-1], 0) if path else float('inf')
                                    print(f"Fim ({h_name}): {nodes} nós. C:{p_cost:.2f}. H:{initial_h:.2f}. T:{exec_t:.1f} ms")
                                    self.results[h_name] = {
                                        'nodes': nodes, 'time': exec_t, 'cost': p_cost, 'initial_h': initial_h,
                                        'path': path, 'g_costs': g_costs.copy(),
                                        'closed_set': self.closed_sets.get(h_name, set()).copy(),
                                        'open_set': self.open_sets.get(h_name, set()).copy()
                                    }
                                    if path: self.animation_starts[h_name] = time.time()
                                except ValueError: print(f"Erro ({h_name}): A* ñ ret 4 val."); self.results[h_name]=None
                                except Exception as ex: print(f"Erro ({h_name}): {ex}"); self.results[h_name]=None

                    last_update_t = now # Reseta throttle

            # --- Draw Frame ---
            if self.view_mode == 'search':
                self.screen.fill(PALETTE.get('bg_chart', (245,245,245)))

                # --- DESENHA H1 (Esquerda) ---
                h1_name = self.h_names[0]; offset1 = 0
                self._draw_board_and_search_state(offset1, h1_name); self._draw_path_highlight(offset1, h1_name)
                self._draw_grid(offset1); self._draw_g_heatmap(offset1, h1_name); self._draw_path(offset1, h1_name)
                self._draw_markers_and_knight(offset1, h1_name, now)
                self._draw_text_center(h1_name, (offset1 + BOARD_PIXEL // 2, BOARD_PIXEL + 25), self.label_font, PALETTE['text_dark'])

                # --- DESENHA SEPARADOR ---
                separator_x = BOARD_PIXEL + SEPARATOR_WIDTH // 2
                pygame.draw.line(self.screen, PALETTE['text_dark'], (separator_x, 10), (separator_x, BOARD_PIXEL + 45), 3)

                # --- DESENHA H2 (Direita) ---
                h2_name = self.h_names[1]; offset2 = BOARD_OFFSET_X
                self._draw_board_and_search_state(offset2, h2_name); self._draw_path_highlight(offset2, h2_name)
                self._draw_grid(offset2); self._draw_g_heatmap(offset2, h2_name); self._draw_path(offset2, h2_name)
                self._draw_markers_and_knight(offset2, h2_name, now)
                self._draw_text_center(h2_name, (offset2 + BOARD_PIXEL // 2, BOARD_PIXEL + 25), self.label_font, PALETTE['text_dark'])

                # --- DESENHA SIDEBAR ---
                self._draw_sidebar()

            elif self.view_mode == 'chart':
                self._draw_chart_view()

            pygame.display.flip()

        pygame.quit()