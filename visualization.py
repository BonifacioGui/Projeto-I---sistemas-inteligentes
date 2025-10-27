"""
visualization_final_v8.py
Visualizador A* com tabuleiro maior e toggles separados para listas.
- DURANTE busca: Azul (Aberta), Verde Musgo (Fechada).
- APÓS busca: Terreno + Caminho.
    - Tecla [V] mostra/oculta área Verde Musgo (Fechada Final).
    - Tecla [O] mostra/oculta área Azul Claro (Aberta Final).
- Mantém Heatmap G, Gráfico, Sidebar.
"""

import pygame
import math
import os
import time

# Layout
BOARD_PIXEL = 720
SIDEBAR_WIDTH = 260
SCREEN_WIDTH = BOARD_PIXEL + SIDEBAR_WIDTH
SCREEN_HEIGHT = 740
GRID_SIZE = 8
CELL_SIZE = BOARD_PIXEL // GRID_SIZE # Agora 90

# --- Paleta de Cores ---
PALETTE = {
    # Cores de Terreno
    'terrain_road': (192, 192, 192), # Cinza
    'terrain_land': (210, 180, 140), # Marrom Claro
    'terrain_mud': (139, 69, 19),    # Marrom Escuro
    'terrain_block': (60, 0, 0),     # Vermelho-sangue/Preto

    # Cores da Busca (Preenchimento Sólido)
    'open_fill': (135, 206, 250),    # Azul Céu Claro
    'closed_fill': (85, 107, 47),     # Verde Musgo Escuro (DarkOliveGreen)

    # Cores do Resultado
    'path': (255, 255, 0),        # Amarelo Brilhante
    'start_border': (0, 255, 0),    # Verde Brilhante
    'end_border': (255, 0, 0),      # Vermelho Brilhante

    # UI & Gráfico
    'panel': (37, 41, 47),        # Fundo do Sidebar
    'grid_line': (60, 60, 60),    # Linhas da grade escuras
    'text': (230, 234, 240),      # Texto claro (sidebar)
    'text_dark': (0, 0, 0),       # Texto escuro (heatmap/gráfico)
    'muted': (150, 155, 165),    # Texto secundário
    'accent': (255, 200, 80),    # Destaque
    'bg_chart': (245, 245, 245), # Fundo claro gráfico
    'bar_h1': (255, 160, 122),    # Cor barra H1
    'bar_h2': (120, 220, 140),    # Cor barra H2
}

# Paths
DEFAULT_KNIGHT_PATHS = ['assets/knight.png', 'knight.png', './knight.png']


class Visualizer:
    def __init__(self, board, *, fps=60):
        pygame.init(); pygame.font.init()
        pygame.display.set_caption('A* — Tactical Knight')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock(); self.board = board; self.fps = fps

        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 26, bold=True)
        self.main_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)
        self.chart_font = pygame.font.SysFont('Arial', 16)

        # Load knight image
        self.knight_img = None
        for p in DEFAULT_KNIGHT_PATHS:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    target = CELL_SIZE - 20 # Ajusta padding
                    self.knight_img = pygame.transform.smoothscale(img, (target, target))
                    break
                except Exception as e: print(f"Erro imagem {p}: {e}"); self.knight_img = None

        # Terrain color map
        self.cost_to_color = {
            board.costs['Estrada']: PALETTE['terrain_road'], board.costs['Terra']: PALETTE['terrain_land'],
            board.costs['Lama']: PALETTE['terrain_mud'], board.costs['Barreira']: PALETTE['terrain_block'], }

        # State initialization
        self.reset_state()

    def reset_state(self):
        self.open_set=set(); self.closed_set=set(); self.current=None; self.final_path=None
        self.g_costs={}; self.nodes_expanded=0; self.search_running=False; self.search_generator=None
        self.results={}; self.start_pos=None; self.end_pos=None; self.current_heuristic_name=''
        self.animation_start=None; self.show_g_map=False; self.view_mode='search'
        # --- NOVO: Estados para os Toggles ---
        self.show_closed_list_toggle = False
        self.show_open_list_toggle = False # Novo toggle para Aberta
        self.last_closed_set = set()
        self.last_open_set = set()           # Novo para armazenar Aberta final

    # ------------------------------- Drawing Helpers -------------------------------
    def _draw_text(self, text, pos, font, color):
        surf = font.render(text, True, color); self.screen.blit(surf, pos)

    def _draw_text_center(self, text, center_pos, font, color):
         surf = font.render(text, True, color); rect = surf.get_rect(center=center_pos)
         self.screen.blit(surf, rect)

    def _get_terrain_color(self, pos):
        cost = self.board.get_cost(pos)
        return self.cost_to_color.get(cost, (255, 255, 255))

    # --- MUDANÇA: Função unificada de desenho ---
    def _draw_board_and_search_state(self):
        """ Desenha o tabuleiro. Aplica cores da busca SE apropriado (dinâmico ou toggle). """
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                pos = (x, y)
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                # 1. Desenha a cor base do terreno PRIMEIRO
                base_color = self._get_terrain_color(pos)
                pygame.draw.rect(self.screen, base_color, rect)

                # 2. Desenha cores da busca POR CIMA, se aplicável
                draw_color = None
                # Se busca rodando (dinâmico)
                if self.search_running:
                    if pos in self.closed_set and pos != self.start_pos and pos != self.end_pos:
                        draw_color = PALETTE['closed_fill'] # Verde Musgo
                    elif pos in self.open_set and pos != self.start_pos and pos != self.end_pos:
                        draw_color = PALETTE['open_fill']   # Azul Claro
                # Se busca parada (toggles)
                else:
                    # Desenha Fechada (Verde Musgo) se V ligado
                    if self.show_closed_list_toggle and pos in self.last_closed_set and pos != self.start_pos and pos != self.end_pos:
                         draw_color = PALETTE['closed_fill']
                    # Desenha Aberta (Azul Claro) se O ligado (sobrescreve Verde se ambos ligados)
                    if self.show_open_list_toggle and pos in self.last_open_set and pos != self.start_pos and pos != self.end_pos:
                         draw_color = PALETTE['open_fill']

                # Aplica a cor da busca se uma foi definida
                if draw_color:
                    pygame.draw.rect(self.screen, draw_color, rect)

                # Grade desenhada depois para ficar por cima de tudo

    def _draw_grid(self):
        color = PALETTE['grid_line']
        for y in range(GRID_SIZE + 1): pygame.draw.line(self.screen, color, (0, y*CELL_SIZE), (BOARD_PIXEL, y*CELL_SIZE), 1)
        for x in range(GRID_SIZE + 1): pygame.draw.line(self.screen, color, (x*CELL_SIZE, 0), (x*CELL_SIZE, BOARD_PIXEL), 1)

    def _draw_path(self):
        if not self.final_path or len(self.final_path) < 2: return
        points = [(p[0]*CELL_SIZE+CELL_SIZE//2, p[1]*CELL_SIZE+CELL_SIZE//2) for p in self.final_path]
        pygame.draw.lines(self.screen, PALETTE['path'], False, points, 6) # Amarelo

    def _draw_g_heatmap(self):
        if not self.final_path or not self.g_costs: return
        path_g = [self.g_costs.get(p,0) for p in self.final_path if p in self.g_costs]; max_g = max(path_g) if path_g else 1
        for pos in self.final_path:
            g = self.g_costs.get(pos, 0); ratio = min(1.0, g / max_g) if max_g > 0 else 0
            r, g_col, b = 255, 255 - int(255 * ratio), 0
            r,g_col,b = max(0,min(255,r)), max(0,min(255,g_col)), max(0,min(255,b))
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA); s.fill((r, g_col, b, 170))
            self.screen.blit(s, (pos[0]*CELL_SIZE, pos[1]*CELL_SIZE))
            center = (pos[0]*CELL_SIZE+CELL_SIZE//2, pos[1]*CELL_SIZE+CELL_SIZE//2)
            self._draw_text_center(f"{g:.1f}", center, self.small_font, PALETTE['text_dark'])
            pygame.draw.rect(self.screen, PALETTE['grid_line'], (pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    def _draw_markers_and_knight(self, t):
        pad = 5
        if self.start_pos: start_r = pygame.Rect(self.start_pos[0]*CELL_SIZE, self.start_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE); pygame.draw.rect(self.screen, PALETTE['start_border'], start_r, pad)
        if self.end_pos: end_r = pygame.Rect(self.end_pos[0]*CELL_SIZE, self.end_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE); pygame.draw.rect(self.screen, PALETTE['end_border'], end_r, pad)
        knight_pos = None
        if self.final_path and self.animation_start: elapsed=time.time()-self.animation_start; step_t=0.18; steps=len(self.final_path); idx = max(0, min(steps - 1, int(elapsed // step_t))); knight_pos = self.final_path[idx]
        elif self.current: knight_pos = self.current
        elif self.start_pos: knight_pos = self.start_pos
        if knight_pos: self._blit_knight_at(knight_pos)

    def _blit_knight_at(self, pos):
        if not pos: return
        cx, cy = pos[0]*CELL_SIZE+CELL_SIZE//2, pos[1]*CELL_SIZE+CELL_SIZE//2
        if self.knight_img: rect = self.knight_img.get_rect(center=(cx, cy)); self.screen.blit(self.knight_img, rect.topleft)
        else: pygame.draw.circle(self.screen, PALETTE['accent'], (cx,cy), CELL_SIZE//4); pygame.draw.circle(self.screen, (255,255,255), (cx,cy), CELL_SIZE//12)

    # --- Sidebar UI (Atualizada com tecla O) ---
    def _draw_sidebar(self):
        pygame.draw.rect(self.screen, PALETTE['panel'], (BOARD_PIXEL, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        x0, y = BOARD_PIXEL + 20, 20
        self._draw_text('A* Tactical Knight', (x0, y), self.title_font, PALETTE['text']); y += 35
        self._draw_text('Visualização e comparação', (x0, y), self.small_font, PALETTE['muted']); y += 15
        self._draw_text('de heurísticas A*', (x0, y), self.small_font, PALETTE['muted'])
        y_info, line_h, section_sp = 120, 20, 35
        info = [('Heurística', self.current_heuristic_name), ('Nó Atual', str(self.current) if self.current else '-'),
                ('Nós Expandidos', str(self.nodes_expanded)),
                ('Custo Final', f"{self.g_costs.get(self.final_path[-1],0):.2f}" if self.final_path and self.g_costs else '-'),
                ('Comp. Caminho', str(len(self.final_path)-1) if self.final_path else '-'), ]
        for label, value in info:
            self._draw_text(label + ':', (x0, y_info), self.small_font, PALETTE['muted'])
            self._draw_text(value, (x0+5, y_info+line_h), self.main_font, PALETTE['text']); y_info += section_sp
        y_ctrls = y_info + 40
        self._draw_text('Controles', (x0, y_ctrls), self.main_font, PALETTE['accent']); y_ctrls += 30
        ctrl_sp = 25
        # --- MUDANÇA: Adiciona tecla O ---
        controls = ['[1] H1 (Cheby)   [2] H2 (Cavalo)', '[ESPAÇO]        - Iniciar Busca',
                    '[N]                  - Novo Tabuleiro Aleatório',
                    '[G]                  - Mapa de Custo G',
                    '[V]                  - Mostrar Exploração (Verde)',
                    '[O]                  - Mostrar Candidatos (Azul)', # Nova tecla
                    '[C]                  - Ver Gráfico Comp.',
                    '[R]                  - Reset / Voltar', '[ESC]             - Voltar ao Tabuleiro', ]
        for c_text in controls: self._draw_text(c_text, (x0, y_ctrls), self.small_font, PALETTE['muted']); y_ctrls += ctrl_sp

    # --- Gráfico (sem mudanças) ---
    def _draw_chart_view(self, heuristic_options):
        # (Código do gráfico permanece o mesmo da versão anterior)
        self.screen.fill(PALETTE['bg_chart']); title_y, sub_y = 40, 80
        self._draw_text_center('Comparação de Eficiência', (SCREEN_WIDTH / 2, title_y), self.title_font, PALETTE['text_dark'])
        self._draw_text_center('Nós Expandidos (Menor é Melhor)', (SCREEN_WIDTH / 2, sub_y), self.main_font, PALETTE['text_dark'])
        names=list(heuristic_options.keys()); results_data={n: self.results.get(n,{}) for n in names}
        have_data=all(isinstance(r,dict) and r.get('nodes',0)>0 for r in results_data.values())
        if not have_data:
            self._draw_text_center("Execute AMBAS as heurísticas ([1], [2]) para comparar.", (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50), self.main_font, PALETTE['text_dark'])
            self._draw_text_center('[R] Voltar', (SCREEN_WIDTH/2, SCREEN_HEIGHT - 60), self.main_font, PALETTE['text_dark']); return
        nodes=[results_data[n].get('nodes',0) for n in names]; max_n=max(nodes) if nodes else 1
        bar_w, bar_h, base_y, n_bars = 180, 280, sub_y + 280 + 80, len(names)
        total_w = n_bars*bar_w; total_sp=100; chart_w=total_w+(n_bars-1)*total_sp
        start_x=(SCREEN_WIDTH-chart_w)/2; colors=[PALETTE.get('bar_h1'), PALETTE.get('bar_h2')]
        for i, n in enumerate(names):
            bx=start_x+i*(bar_w+total_sp); node_val=results_data[n].get('nodes',0)
            bh=(node_val/max_n)*bar_h if max_n>0 else 0; by=base_y-bh; color=colors[i%len(colors)]
            pygame.draw.rect(self.screen, color, (bx, by, bar_w, bh), border_radius=6)
            self._draw_text_center(str(node_val), (bx+bar_w/2, by-20), self.main_font, PALETTE['text_dark'])
            self._draw_text_center(n, (bx+bar_w/2, base_y+25), self.chart_font, PALETTE['text_dark'])
            info_y, info_sp = base_y + 50, 20
            details = [ f"Tempo: {results_data[n].get('time', 0):.1f} ms", f"Custo: {results_data[n].get('cost', 0):.2f}", f"H Ini: {results_data[n].get('initial_h', 0):.2f}" ]
            for j, d in enumerate(details): self._draw_text_center(d, (bx+bar_w/2, info_y+j*info_sp), self.small_font, PALETTE['text_dark'])
        if len(names)==2:
             res1, res2 = results_data[names[0]], results_data[names[1]]
             win_n=names[0] if res1.get('nodes', float('inf')) < res2.get('nodes', float('inf')) else names[1]
             los_n=names[1] if win_n == names[0] else names[0]; conc1, conc2 = "", ""
             if res1.get('nodes',0)==res2.get('nodes',0): conc1="Mesma eficiência."
             else:
                 diff=abs(res1.get('nodes',0)-res2.get('nodes',0)); los_nodes=results_data[los_n].get('nodes',1)
                 perc=(diff/los_nodes)*100 if los_nodes>0 else 0; conc1=f"{win_n} mais eficiente."
                 conc2=f"({perc:.1f}% redução vs {los_n})."
             conc1_y = info_y + len(details) * info_sp + 40
             self._draw_text_center(conc1, (SCREEN_WIDTH/2, conc1_y), self.main_font, PALETTE['text_dark'])
             if conc2: self._draw_text_center(conc2, (SCREEN_WIDTH/2, conc1_y+25), self.chart_font, PALETTE['muted'])
        self._draw_text_center('[R] Voltar', (SCREEN_WIDTH/2, SCREEN_HEIGHT-60), self.main_font, PALETTE['text_dark'])


    # ------------------------------ Main loop ---------------------------------
    def run(self, start_pos, end_pos, heuristic_options, search_function):
        # Estado inicial do visualizador
        self.reset_state(); self.start_pos=start_pos; self.end_pos=end_pos

        # Dicionário onde vamos guardar métricas de cada heurística rodando (nodes, tempo, custo final, etc)
        self.results = {name: None for name in heuristic_options.keys()}

        #Lista com nomes das heurísticas, ex: ["H1 (Chebyshev)", "H2 (Cavalo)"]
        h_names=list(heuristic_options.keys())
        if len(h_names)<2: raise ValueError('>= 2 heurísticas')

        #Índice da heurística atualmente selecionada (Começa na primeira)
        curr_idx=0; self.current_heuristic_name=h_names[curr_idx]
        self.current_heuristic_func=heuristic_options[self.current_heuristic_name]

        #Variáveis de controle de animação e loop
        pulse_t, start_t = 0.0, 0; running = True; last_update_t = pygame.time.get_ticks()

        #Loop principal da aplicação (render + input + lógica de busca)
        while running:
            #clock.tick limita o FPS; dt é o tempo entre frames
            now = pygame.time.get_ticks(); dt = self.clock.tick(self.fps)/1000.0; pulse_t += dt

            # --- Event Handling ---
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False

                elif ev.type == pygame.KEYDOWN:
                    #Tecla R: resetar estado
                    if ev.key == pygame.K_r:
                        #Se estamos vendo o gráfico, "r" volta para o tabuleiro
                        if self.view_mode=='chart': self.view_mode='search'; print("Voltando.")
                        #Reset completo da simulação para o tabuleiro atual
                        else: self.reset_state(); self.start_pos=start_pos; self.end_pos=end_pos; self.results={n:None for n in h_names}; self.current_heuristic_name=h_names[0]; self.current_heuristic_func=heuristic_options[self.current_heuristic_name]; self.show_g_map=False; self.view_mode='search'; self.show_closed_list_toggle=False; self.show_open_list_toggle=False; print("--- RESETADO ---") # Reseta toggles

                    #Tecla ESC é outro modo de saur do gráfico.
                    elif ev.key == pygame.K_ESCAPE and self.view_mode == 'chart': self.view_mode = 'search'; print("Voltando.")

                    #As teclas abaixo só fazem sentido quando estamos no modo principal de busca
                    elif self.view_mode == 'search':

                        #N: gera um novo tabuleiro aleatório
                        if ev.key == pygame.K_n and not self.search_running:
                            # 1. Gera um novo layout de terreno
                            self.board.randomize()

                            # 2. Reseta o estado interno da busca
                            self.reset_state()

                            # 3. Mantém as mesmas posições inicial e final recebidas na chamada de run()
                            self.start_pos = start_pos
                            self.end_pos = end_pos

                            # 4. Mantém a heurística atualmente selecionada
                            self.current_heuristic_name = h_names[curr_idx]
                            self.current_heuristic_func = heuristic_options[self.current_heuristic_name]

                            # 5. Limpa resultados de execuções antigas, porque o mapa mudou
                            self.results = {name: None for name in heuristic_options.keys()}

                            # Garante que estamos no modo de busca normal e com todos os toggles limpos
                            self.view_mode = 'search'
                            self.show_g_map = False
                            self.show_closed_list_toggle = False
                            self.show_open_list_toggle = False

                            print("[N] Novo tabuleiro gerado.")

                        #Espaço: iniciar a busca A*
                        elif ev.key == pygame.K_SPACE and not self.search_running:
                            print(f"Iniciando: {self.current_heuristic_name}...");
                            start_t = time.time();

                            #Cria o gerador do A* com a heurística atual
                            self.search_generator = search_function(self.board, start_pos, end_pos, self.current_heuristic_func);

                            #Marca que a busca está acontecendo
                            self.search_running=True;

                            #Limpa dados visuais anteriores
                            self.final_path=None; self.g_costs={}; self.nodes_expanded=0; self.open_set=set(); self.closed_set=set(); self.current=start_pos; self.animation_start=None; self.show_g_map=False; self.show_closed_list_toggle=False; self.show_open_list_toggle=False

                        #[1] / [2]: trocar a heurística ativa ANTES de rodar
                        elif ev.key>=pygame.K_1 and ev.key<pygame.K_1+len(h_names) and not self.search_running:
                            curr_idx = ev.key - pygame.K_1
                            if 0 <= curr_idx < len(h_names): self.current_heuristic_name=h_names[curr_idx]; self.current_heuristic_func=heuristic_options[self.current_heuristic_name]; print(f"Heurística: {self.current_heuristic_name}")

                        #G: alternar axibição do mapa de custo G (heatmap)
                        elif ev.key == pygame.K_g and self.final_path: self.show_g_map = not self.show_g_map; print(f"Mapa G: {'On' if self.show_g_map else 'Off'}")

                        #V: alternar visualização da área explorada (closed_set final)
                        elif ev.key == pygame.K_v and not self.search_running and self.last_closed_set:
                             self.show_closed_list_toggle = not self.show_closed_list_toggle
                             print(f"Mostrar Exploração (Verde Musgo): {'Ligado' if self.show_closed_list_toggle else 'Desligado'}")

                        #O: alternar visualização da fronteira final (open_set final)
                        elif ev.key == pygame.K_o and not self.search_running and self.last_open_set:
                             self.show_open_list_toggle = not self.show_open_list_toggle
                             print(f"Mostrar Candidatos Finais (Azul): {'Ligado' if self.show_open_list_toggle else 'Desligado'}")

                        #C: ir para o modo gráfico comparativo (chart), caso já tivermos resultados das heurísticas
                        elif ev.key == pygame.K_c and all(r is not None for r in self.results.values()) and not self.search_running:
                             if all(isinstance(r, dict) and r.get('nodes', 0) > 0 for r in self.results.values()): self.view_mode = 'chart'; print("Gráfico.")
                             else: print("Execute ambas.")

            # --- Advance Search (execução incremental do A*) ---
            if self.search_running and self.search_generator and self.view_mode == 'search':

                #Throttle para não atualizar rápido demais
                if now - last_update_t > 50:
                    try:

                        #Pega o próximo "frame" da busca A*
                        state = next(self.search_generator)

                        #Atualiza conjuntos de abertos/fechados e nó atual
                        self.open_set=state.get('open',set()); self.closed_set=state.get('closed',set())
                        self.current=state.get('current',self.current);

                        #Contador de nós expandidos
                        self.nodes_expanded=len(self.closed_set)

                        last_update_t = now

                    except StopIteration as e:
                        #A busca terminou. Aqui nós colhemos os resultados finais
                        end_t = time.time(); exec_t = (end_t - start_t) * 1000
                        try:
                            path, nodes, g_costs, initial_h = e.value
                            self.final_path=path; self.nodes_expanded=nodes; self.g_costs=g_costs

                            #Guardar as versoes finais da open/closed da busca atual
                            self.last_closed_set = self.closed_set.copy()
                            self.last_open_set = self.open_set.copy()


                            #Calcula custo total do caminho encontrado
                            p_cost = 0
                            if path:
                                p_cost=g_costs.get(path[-1],0);
                                print(f"Fim: {nodes} nós. C:{p_cost:.2f}. H:{initial_h:.2f}. T:{exec_t:.2f} ms");
                                self.results[self.current_heuristic_name]={'nodes':nodes,'time':exec_t,'cost':p_cost,'initial_h':initial_h};
                                #Inicia animação do cavalo se tem caminho
                                self.animation_start=time.time() if path else None
                            else: print(f"Fim: Ñ enc. {nodes} nós. T:{exec_t:.2f} ms"); self.results[self.current_heuristic_name]={'nodes':nodes,'time':exec_t,'cost':float('inf'),'initial_h':initial_h}
                        except ValueError: print("Erro: A* ñ ret 4 val."); self.final_path=None; self.nodes_expanded=0; self.g_costs={}; self.results[self.current_heuristic_name]=None; self.last_closed_set = set(); self.last_open_set = set()
                        except Exception as ex: print(f"Erro: {ex}"); self.final_path=None; self.nodes_expanded=0; self.g_costs={}; self.results[self.current_heuristic_name]=None; self.last_closed_set = set(); self.last_open_set = set()

                        #Marca que terminou, a busca não está mais rodando
                        self.search_running=False;

                        #Não limpa open/closed aqui para permitir toggle imediato
                        self.search_generator=None


            # --- Draw Frame (renderização) ---
            if self.view_mode == 'search':
                # Ordem: Fundo -> Tabuleiro/Busca -> Grade -> Heatmap -> Caminho -> Marcadores -> Sidebar
                self.screen.fill(PALETTE.get('bg', (0,0,0)))
                self._draw_board_and_search_state() # Desenha terreno OU Azul/Verde OU toggles Verde/Azul
                self._draw_grid()
                if self.show_g_map and self.final_path: self._draw_g_heatmap()
                self._draw_path()
                self._draw_markers_and_knight(pulse_t)
                self._draw_sidebar()
            elif self.view_mode == 'chart':
                #Tabela de gráfico comparando heurísticas
                self._draw_chart_view(heuristic_options)

            pygame.display.flip()

        pygame.quit()