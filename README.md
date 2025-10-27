# Projeto-I---sistemas-inteligentes

# Caminho Tático com Cavalo no Xadrez

## 🧠 Visão Geral
Este projeto implementa uma busca A* para encontrar o caminho de **menor custo total** que um **Cavalo de xadrez** precisa percorrer entre duas posições em um tabuleiro 8×8 com terrenos de custo diferente.

Além do algoritmo, o projeto inclui uma **visualização interativa em Pygame**, que mostra:
- o tabuleiro e os terrenos,
- a busca acontecendo passo a passo,
- o caminho final encontrado,
- métricas de desempenho das heurísticas.

O trabalho faz parte da disciplina de **Sistemas Inteligentes** e tem foco em heurísticas admissíveis e comparação de eficiência entre heurísticas.

---

## ♟️ Regras do Problema
- Peça usada: **Cavalo** (movimentos em “L”: (±1, ±2) e (±2, ±1)).
- Tabuleiro: 8×8.
- Cada casa tem um **custo de terreno**:
  - Estrada → custo baixo (0.5)
  - Terra → custo normal (1.0)
  - Lama → custo alto (5.0)
  - Barreira → custo infinito (intransitável)
- Objetivo: sair de uma posição inicial até uma posição final com **menor custo acumulado (G)**.
- A* minimiza `F(n) = G(n) + H(n)`:
  - `G(n)` = custo real já percorrido
  - `H(n)` = estimativa do custo restante até o objetivo (heurística)

---

## 🧮 Heurísticas implementadas
As heurísticas ficam em `heuristics.py`.

### H1 — Chebyshev (`h1_chebyshev`)
Heurística mais simples.
- Usa `max(dx, dy)` entre o ponto atual e o destino.
- Multiplica pela menor unidade de custo do tabuleiro.
- É **admissível** (nunca superestima o custo real).

### H2 — Distância de Cavalo (`h2_knight_distance`)
Heurística mais informativa.
- Calcula o **número mínimo de movimentos de cavalo** entre duas casas usando BFS.
- Multiplica esse número pelo menor custo de terreno.
- Também é **admissível**.

As duas heurísticas serão comparadas em termos de:
- nós expandidos,
- custo do caminho final,
- tempo de execução.

---

## 🗂 Estrutura do Código

### `main.py`
Ponto de entrada do programa.  
- Cria o tabuleiro.
- Registra as heurísticas disponíveis (`H1`, `H2`).
- Inicializa o visualizador.
- Define origem e destino do cavalo.

### `board.py`
Representa o tabuleiro 8×8:
- Mapa de terrenos e custos.
- Função `is_valid()` para impedir passar por barreiras.
- Função `get_cost()` para saber o custo de entrar numa célula.
- Guarda também `min_cost` (menor custo possível), usado nas heurísticas.

### `a_star.py`
Implementa o algoritmo **A\***:
- Controla lista aberta/fechada, custo `g`, heuristic `h`, custo total `f = g + h`.
- Respeita os movimentos de cavalo.
- É implementado como um **gerador**: vai emitindo estado parcial da busca passo a passo. Isso alimenta a animação.

Retorno final do A*:
- caminho encontrado,
- número de nós expandidos,
- mapa de custos `g_costs`,
- valor inicial da heurística.

### `heuristics.py`
Contém as heurísticas H1 e H2 (e código auxiliar como BFS para o cavalo).

### `visualization.py`
Interface gráfica (Pygame):
- Desenha o tabuleiro com cores diferentes por tipo de terreno.
- Mostra visualmente:
  - lista aberta (azul),
  - lista fechada (verde),
  - caminho final (amarelo),
  - heatmap do custo G.
- Mostra também um gráfico comparando heurísticas (quantos nós cada uma expandiu, etc).
- Permite controlar tudo via teclado.

---

## 🛠 Requisitos

### 1. Python
O projeto foi feito para rodar com **Python 3.x** (3.10+ é uma boa escolha).

Confirma a versão no teu sistema:
```bash
python --version
```
ou
```bash
python3 --version
```

### 2. Criar um ambiente virtual (recomendado)
No terminal, dentro da pasta do projeto:

```bash
python -m venv venv
```

Ativar:

- Linux / Mac:
  ```bash
  source venv/bin/activate
  ```

- Windows (PowerShell):
  ```powershell
  venv\Scripts\Activate.ps1
  ```

### 3. Dependências Python
Hoje precisamos basicamente de:
- `pygame`

Instala com:
```bash
pip install pygame
```

Se você quiser deixar isso fixo num `requirements.txt`, você pode criar um arquivo com:
```text
pygame
```
E depois rodar:
```bash
pip install -r requirements.txt
```

---

## ▶️ Como executar

Depois de instalar as dependências, estando na raiz do projeto:

```bash
python main.py
```

ou, dependendo do seu sistema:

```bash
python3 main.py
```

Isso vai abrir uma janela gráfica (Pygame) chamada `A* — Tactical Knight`.

Dentro dessa janela você já vai ver:
- O tabuleiro.
- A sidebar com informações.
- A posição inicial e final do cavalo.

---

## ⌨️ Controles dentro da interface

Quando a janela do Pygame estiver aberta:

### Escolha de heurística
- **[1]** → Seleciona H1 (Chebyshev)
- **[2]** → Seleciona H2 (Distância de Cavalo)

> Observação: você só pode trocar de heurística quando não tem busca em andamento.

### Rodar a busca A\*
- **[ESPAÇO]** → inicia a busca com a heurística atual  
  - Durante a busca:
    - Azul claro = Lista Aberta (candidatos a expandir)
    - Verde musgo = Lista Fechada (já explorados)
  - O cavalo vai sendo mostrado avançando.

Quando a busca termina:
- O caminho ótimo fica em **amarelo**.
- A posição inicial ganha uma borda verde.
- A posição final ganha uma borda vermelha.

### Analisar resultados após a busca
Essas teclas funcionam depois que a busca terminou:

- **[G]** → liga/desliga o mapa de calor do custo acumulado `G`.  
- **[V]** → mostra/esconde a área explorada final (**lista fechada**) em verde.  
- **[O]** → mostra/esconde os candidatos finais (**lista aberta**) em azul.  
- **[C]** → abre a tela de comparação das heurísticas.  
- **[R]** → reseta tudo e volta pro começo.
- **[ESC]** → sai da tela de gráfico e volta pro tabuleiro.

Para fechar o programa completamente: só fechar a janela ou apertar o X.
