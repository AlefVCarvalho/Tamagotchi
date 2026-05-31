import os
import sys
import tkinter as tk
from tkinter import messagebox
import random
import time


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


REWARDS = {
    "memory": {
        "win": {"coins": 18, "happiness": 12},
        "lose": {"coins": 5, "happiness": 4},
    },
    "dino": {
        "win": {"coins": 15, "happiness": 10},
        "lose": {"coins": 4, "happiness": 3},
    },
    "flappy": {
        "win": {"coins": 20, "happiness": 14},
        "lose": {"coins": 5, "happiness": 4},
    },
    "crossroad": {
        "win": {"coins": 14, "happiness": 10},
        "lose": {"coins": 4, "happiness": 3},
    },
    "maze": {
        "win": {"coins": 22, "happiness": 16},
        "lose": {"coins": 6, "happiness": 5},
    },
}


def open_minigame_selector(parent, pet, on_finish):
    """
    Abre a janela de seleção de minijogos.
    on_finish(moedas_ganhas) é chamado ao fechar.
    """
    win = tk.Toplevel(parent)
    win.title("Minijogos")
    win.geometry("420x460")
    win.resizable(False, False)
    win.grab_set()

    tk.Label(win, text="Escolha um Minijogo",
             font=("Arial", 16, "bold")).pack(pady=12)
    tk.Label(win,
             text=f"Moedas de {pet.name}: {pet.money}",
             font=("Arial", 11)).pack(pady=2)

    icon_path = resource_path(f"assets/icons/{pet.asset_key}_icon.png")
    pet_icon = None

    if os.path.exists(icon_path):
        try:
            pet_icon = tk.PhotoImage(file=icon_path)
        except tk.TclError:
            pet_icon = None

    if pet_icon:
        icon_label = tk.Label(win, image=pet_icon)
        icon_label.image = pet_icon
        icon_label.pack(pady=6)
    else:
        tk.Label(win, text=pet.name, font=("Arial", 13, "bold")).pack(pady=6)

    games = [
        ("🃏 Jogo da Memória",  "memory"),
        ("🦕 Dino Run",         "dino"),
        ("🐦 Flappy Bird",      "flappy"),
        ("🚗 Crossroad",        "crossroad"),
        ("🌀 Labirinto",        "maze"),
    ]

    for label, key in games:
        r = REWARDS[key]
        desc = (
            f"{label}\n"
            f"Vitória: +{r['win']['coins']} moedas / +{r['win']['happiness']} felicidade\n"
            f"Derrota: +{r['lose']['coins']} moedas / +{r['lose']['happiness']} felicidade"
        )
        tk.Button(
            win,
            text=desc,
            width=38,
            height=2,
            font=("Arial", 10),
            command=lambda k=key: _launch(win, k, pet, on_finish)
        ).pack(pady=5)


def _launch(selector_win, key, pet, on_finish):
    selector_win.destroy()
    launchers = {
        "memory":    MemoryGame,
        "dino":      DinoGame,
        "flappy":    FlappyGame,
        "crossroad": CrossroadGame,
        "maze":      MazeGame,
    }
    launchers[key](pet, on_finish)


# ---------------------------------------------------------------------------
# Utilitário: janela base de minijogo
# ---------------------------------------------------------------------------
class BaseGame:
    def __init__(self, title, width, height, pet, on_finish, key):
        self.pet = pet
        self.on_finish = on_finish
        self.key = key
        self.finished = False

        self.pet_icon = self._load_pet_icon(subsample=2)
        self.pet_icon_big = self._load_pet_icon(subsample=1)

        self.win = tk.Toplevel()
        self.win.title(title)
        self.win.geometry(f"{width}x{height}")
        self.win.resizable(False, False)
        self.win.grab_set()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_pet_icon(self, subsample=1):
        icon_path = resource_path(f"assets/icons/{self.pet.asset_key}_icon.png")

        if not os.path.exists(icon_path):
            return None

        try:
            image = tk.PhotoImage(file=icon_path)

            if subsample > 1:
                image = image.subsample(subsample, subsample)

            return image

        except tk.TclError:
            return None

    def _draw_player_icon(self, canvas, x, y, fallback="●"):
        if self.pet_icon:
            return canvas.create_image(x, y, image=self.pet_icon, anchor="center")

        return canvas.create_text(
            x,
            y,
            text=fallback,
            font=("Arial", 24),
            anchor="center"
        )

    def _coords_player_icon(self, canvas, item, x, y):
        canvas.coords(item, x, y)

    def _reward(self, won):
        if self.finished:
            return

        self.finished = True

        result_key = "win" if won else "lose"
        reward = REWARDS[self.key][result_key]

        coins = reward["coins"]
        happiness = reward["happiness"]

        self.pet.money += coins
        self.pet.happiness += happiness

        self.pet.energy -= 4
        self.pet.hunger -= 2

        self.pet.limit_attributes()

        self.win.destroy()

        result = "Vitória!" if won else "Derrota!"

        try:
            self.on_finish(coins, result, happiness)
        except TypeError:
            self.on_finish(coins, result)

    def _on_close(self):
        if not self.finished:
            self._reward(False)

# ===========================================================================
# 1. JOGO DA MEMÓRIA
# ===========================================================================
class MemoryGame(BaseGame):
    EMOJIS = ["🐱","🐶","🐸","🐧","🦊","🐺","🐷","🐮"]

    def __init__(self, pet, on_finish):
        super().__init__("🃏 Jogo da Memória", 420, 480, pet, on_finish, "memory")

        self.cards_val = self.EMOJIS * 2
        random.shuffle(self.cards_val)

        self.buttons = []
        self.flipped = []       # índices virados agora
        self.matched = set()
        self.locked = False

        tk.Label(self.win, text="Encontre os pares!", font=("Arial",13,"bold")).pack(pady=6)
        if self.pet_icon_big:
            icon_label = tk.Label(self.win, image=self.pet_icon_big)
            icon_label.image = self.pet_icon_big
            icon_label.pack(pady=4)
        else:
            tk.Label(
                self.win,
                text=self.pet.name,
                font=("Arial", 12, "bold")
            ).pack(pady=4)
        self.info = tk.Label(self.win, text="", font=("Arial",10))
        self.info.pack()

        grid = tk.Frame(self.win)
        grid.pack(pady=8)

        for i in range(16):
            btn = tk.Button(grid, text="?", width=4, height=2,
                            font=("Arial",16),
                            command=lambda idx=i: self._flip(idx))
            btn.grid(row=i//4, column=i%4, padx=4, pady=4)
            self.buttons.append(btn)

        self._update_info()

    def _update_info(self):
        pairs = len(self.matched) // 2
        self.info.config(text=f"Pares encontrados: {pairs}/8")

    def _flip(self, idx):
        if self.locked or idx in self.matched or idx in self.flipped:
            return
        self.buttons[idx].config(text=self.cards_val[idx], state="disabled")
        self.flipped.append(idx)

        if len(self.flipped) == 2:
            self.locked = True
            self.win.after(700, self._check)

    def _check(self):
        a, b = self.flipped
        if self.cards_val[a] == self.cards_val[b]:
            self.matched.add(a)
            self.matched.add(b)
            self._update_info()
            if len(self.matched) == 16:
                self._reward(True)
                return
        else:
            self.buttons[a].config(text="?", state="normal")
            self.buttons[b].config(text="?", state="normal")
        self.flipped.clear()
        self.locked = False


# ===========================================================================
# 2. DINO RUN
# ===========================================================================
class DinoGame(BaseGame):
    W, H = 480, 280

    def __init__(self, pet, on_finish):
        super().__init__("🦕 Dino Run", 480, 320, pet, on_finish, "dino")

        self.canvas = tk.Canvas(self.win, width=self.W, height=self.H, bg="#e8e8e8")
        self.canvas.pack()

        tk.Label(self.win, text="ESPAÇO para pular  |  Sobreviva 15 segundos!",
                 font=("Arial",9)).pack(pady=4)

        # dino
        self.dino_x = 60
        self.dino_y = self.H - 50
        self.dino_vy = 0
        self.on_ground = True

        # obstáculos
        self.obstacles = []
        self.obs_speed = 5
        self.frame_count = 0
        self.next_obs = 60

        self.start_time = time.time()
        self.target = 15  # segundos

        self.score_text = self.canvas.create_text(
            self.W - 10, 10, anchor="ne",
            text="0s / 15s", font=("Arial", 11, "bold"), fill="#333"
        )

        # chão
        self.canvas.create_line(0, self.H - 30, self.W, self.H - 30, fill="#888", width=2)

        # dino (retângulo verde simples)
        self.dino = self._draw_player_icon(
            self.canvas,
            self.dino_x + 15,
            self.dino_y - 15,
            fallback="🦕"
        )

        self.win.bind("<space>", self._jump)
        self.win.focus_set()
        self._loop()

    def _jump(self, event=None):
        if self.on_ground:
            self.dino_vy = -14
            self.on_ground = False

    def _loop(self):
        if self.finished:
            return

        elapsed = time.time() - self.start_time
        self.canvas.itemconfig(self.score_text,
                               text=f"{int(elapsed)}s / {self.target}s")

        if elapsed >= self.target:
            self._reward(True)
            return

        # gravidade
        self.dino_vy += 1
        self.dino_y += self.dino_vy
        ground = self.H - 50
        if self.dino_y >= ground:
            self.dino_y = ground
            self.dino_vy = 0
            self.on_ground = True

        self._coords_player_icon(
            self.canvas,
            self.dino,
            self.dino_x + 15,
            self.dino_y - 15
        )

        # obstáculos
        self.frame_count += 1
        if self.frame_count >= self.next_obs:
            h = random.randint(20, 50)
            obs = self.canvas.create_rectangle(
                self.W, self.H - 30 - h,
                self.W + 18, self.H - 30,
                fill="#e53935", outline="#b71c1c"
            )
            self.obstacles.append(obs)
            self.frame_count = 0
            self.next_obs = random.randint(45, 100)
            self.obs_speed = min(10, 5 + int(elapsed / 5))

        dead = False
        for obs in list(self.obstacles):
            coords = self.canvas.coords(obs)
            if not coords:
                continue
            self.canvas.move(obs, -self.obs_speed, 0)
            coords = self.canvas.coords(obs)
            if coords[2] < 0:
                self.canvas.delete(obs)
                self.obstacles.remove(obs)
                continue
            # colisão simples
            dx1, dy1, dx2, dy2 = coords
            if (dx1 < self.dino_x + 28 and dx2 > self.dino_x + 2 and
                    dy1 < self.dino_y and dy2 > self.dino_y - 28):
                dead = True

        if dead:
            self._reward(False)
            return

        self.win.after(30, self._loop)


# ===========================================================================
# 3. FLAPPY BIRD
# ===========================================================================
class FlappyGame(BaseGame):
    W, H = 380, 480
    GAP = 130
    PIPE_W = 40
    PIPE_SPEED = 3

    def __init__(self, pet, on_finish):
        super().__init__("🐦 Flappy Bird", 380, 520, pet, on_finish, "flappy")

        self.canvas = tk.Canvas(self.win, width=self.W, height=self.H, bg="#87ceeb")
        self.canvas.pack()
        tk.Label(self.win, text="ESPAÇO ou clique para bater as asas  |  Passe 10 canos!",
                 font=("Arial", 9)).pack(pady=4)

        self.bird_x = 80
        self.bird_y = self.H // 2
        self.bird_vy = 0

        self.pipes = []
        self.score = 0
        self.target = 10
        self.frame = 0
        self.next_pipe = 80

        # chão
        self.ground = self.canvas.create_rectangle(
            0, self.H - 20, self.W, self.H, fill="#8d6e3f", outline=""
        )

        # pássaro
        self.bird = self._draw_player_icon(
            self.canvas,
            self.bird_x,
            self.bird_y,
            fallback="🐦"
        )
        self.score_txt = self.canvas.create_text(
            10, 10, anchor="nw",
            text="0 / 10", font=("Arial", 13, "bold"), fill="white"
        )

        self.win.bind("<space>", self._flap)
        self.canvas.bind("<Button-1>", self._flap)
        self.win.focus_set()
        self._loop()

    def _flap(self, event=None):
        self.bird_vy = -8

    def _loop(self):
        if self.finished:
            return

        # física do pássaro
        self.bird_vy += 0.5
        self.bird_y += self.bird_vy
        self._coords_player_icon(
            self.canvas,
            self.bird,
            self.bird_x,
            self.bird_y
        )

        # morreu: chão ou teto
        if self.bird_y >= self.H - 32 or self.bird_y <= 0:
            self._reward(False)
            return

        # gera canos
        self.frame += 1
        if self.frame >= self.next_pipe:
            gap_y = random.randint(80, self.H - 120)
            top = self.canvas.create_rectangle(
                self.W, 0,
                self.W + self.PIPE_W, gap_y,
                fill="#4caf50", outline="#2e7d32"
            )
            bot = self.canvas.create_rectangle(
                self.W, gap_y + self.GAP,
                self.W + self.PIPE_W, self.H - 20,
                fill="#4caf50", outline="#2e7d32"
            )
            self.pipes.append({"top": top, "bot": bot, "gap_y": gap_y, "passed": False})
            self.frame = 0
            self.next_pipe = random.randint(70, 110)

        # move canos
        for p in list(self.pipes):
            self.canvas.move(p["top"], -self.PIPE_SPEED, 0)
            self.canvas.move(p["bot"], -self.PIPE_SPEED, 0)
            cx = self.canvas.coords(p["top"])
            if not cx:
                self.pipes.remove(p)
                continue

            pipe_x1, _, pipe_x2, _ = cx
            # pontuação
            if not p["passed"] and pipe_x2 < self.bird_x - 14:
                p["passed"] = True
                self.score += 1
                self.canvas.itemconfig(self.score_txt, text=f"{self.score} / {self.target}")
                if self.score >= self.target:
                    self._reward(True)
                    return

            # colisão
            if pipe_x1 < self.bird_x + 12 and pipe_x2 > self.bird_x - 12:
                gap_y = p["gap_y"]
                if self.bird_y - 12 < gap_y or self.bird_y + 12 > gap_y + self.GAP:
                    self._reward(False)
                    return

            # remove fora da tela
            if pipe_x2 < 0:
                self.canvas.delete(p["top"])
                self.canvas.delete(p["bot"])
                self.pipes.remove(p)

        self.canvas.tag_raise(self.bird)
        self.canvas.tag_raise(self.score_txt)
        self.win.after(30, self._loop)


# ===========================================================================
# 4. CROSSROAD (tipo Frogger)
# ===========================================================================
class CrossroadGame(BaseGame):
    W, H = 420, 420
    CELL = 42
    COLS = 10
    ROWS = 10

    def __init__(self, pet, on_finish):
        super().__init__("🚗 Crossroad", 420, 460, pet, on_finish, "crossroad")

        self.canvas = tk.Canvas(self.win, width=self.W, height=self.H, bg="#558b2f")
        self.canvas.pack()
        tk.Label(self.win, text="Setas para mover  |  Chegue ao outro lado 3 vezes!",
                 font=("Arial", 9)).pack(pady=4)

        self.px = 5
        self.py = 9  # linha de baixo
        self.lives = 3
        self.wins = 0
        self.target = 3

        # faixas de carro: linha → (direção, velocidade, gap_min)
        self.lanes = {
            2: {"dir": 1,  "speed": 2.5, "cars": []},
            3: {"dir": -1, "speed": 3.0, "cars": []},
            5: {"dir": 1,  "speed": 2.0, "cars": []},
            6: {"dir": -1, "speed": 3.5, "cars": []},
            8: {"dir": 1,  "speed": 2.8, "cars": []},
        }
        for row, lane in self.lanes.items():
            self._spawn_cars(row, lane)

        self.info_txt = self.canvas.create_text(
            5, 5, anchor="nw",
            text="", font=("Arial", 11, "bold"), fill="white"
        )
        self._draw_all()
        self.win.bind("<Up>",    lambda e: self._move(0, -1))
        self.win.bind("<Down>",  lambda e: self._move(0, 1))
        self.win.bind("<Left>",  lambda e: self._move(-1, 0))
        self.win.bind("<Right>", lambda e: self._move(1, 0))
        self.win.focus_set()
        self._loop()

    def _spawn_cars(self, row, lane):
        lane["cars"].clear()
        x = 0 if lane["dir"] == 1 else self.W
        while x < self.W if lane["dir"] == 1 else x > 0:
            gap = random.randint(80, 160)
            x += gap * lane["dir"]
            lane["cars"].append(float(x))
            if lane["dir"] == 1 and x > self.W + 200:
                break
            if lane["dir"] == -1 and x < -200:
                break

    def _draw_all(self):
        self.canvas.delete("all")

        # fundo
        for r in range(self.ROWS):
            color = "#37474f" if r in self.lanes else "#558b2f"
            self.canvas.create_rectangle(
                0, r * self.CELL, self.W, (r + 1) * self.CELL,
                fill=color, outline=""
            )

        # calçadas (linha 0 e 9)
        for r in [0, 9]:
            self.canvas.create_rectangle(
                0, r * self.CELL, self.W, (r + 1) * self.CELL,
                fill="#8d6e3f", outline=""
            )

        # carros
        for row, lane in self.lanes.items():
            for cx in lane["cars"]:
                x1 = cx
                x2 = cx + 36 * lane["dir"]
                rx1, rx2 = (min(x1, x2), max(x1, x2))
                ry1 = row * self.CELL + 5
                ry2 = (row + 1) * self.CELL - 5
                self.canvas.create_rectangle(rx1, ry1, rx2, ry2,
                                             fill="#e53935", outline="#b71c1c")

        # jogador
        player_x = self.px * self.CELL + self.CELL // 2
        player_y = self.py * self.CELL + self.CELL // 2

        self._draw_player_icon(
            self.canvas,
            player_x,
            player_y,
            fallback="🐾"
        )

        self.info_txt = self.canvas.create_text(
            5, 2, anchor="nw",
            text=f"Chegadas: {self.wins}/{self.target}  Vidas: {'❤️' * self.lives}",
            font=("Arial", 10, "bold"), fill="white"
        )

    def _move(self, dx, dy):
        nx = max(0, min(self.COLS - 1, self.px + dx))
        ny = max(0, min(self.ROWS - 1, self.py + dy))
        self.px, self.py = nx, ny
        self._draw_all()

        if self.py == 0:
            self.wins += 1
            if self.wins >= self.target:
                self._reward(True)
                return
            self.py = 9
            self._draw_all()

    def _loop(self):
        if self.finished:
            return

        for row, lane in self.lanes.items():
            for i in range(len(lane["cars"])):
                lane["cars"][i] += lane["speed"] * lane["dir"]
                # reposiciona ao sair da tela
                if lane["dir"] == 1 and lane["cars"][i] > self.W + 50:
                    lane["cars"][i] = -50.0
                elif lane["dir"] == -1 and lane["cars"][i] < -86:
                    lane["cars"][i] = float(self.W + 50)

        # colisão
        if self.py in self.lanes:
            lane = self.lanes[self.py]
            px_center = self.px * self.CELL + 21
            for cx in lane["cars"]:
                x1 = min(cx, cx + 36 * lane["dir"])
                x2 = max(cx, cx + 36 * lane["dir"])
                if x1 + 4 < px_center < x2 - 4:
                    self.lives -= 1
                    self.px, self.py = 5, 9
                    if self.lives <= 0:
                        self._reward(False)
                        return
                    break

        self._draw_all()
        self.win.after(60, self._loop)


# ===========================================================================
# 5. LABIRINTO
# ===========================================================================
class MazeGame(BaseGame):
    CELL = 40
    COLS = 10
    ROWS = 10

    def __init__(self, pet, on_finish):
        W = self.CELL * self.COLS
        H = self.CELL * self.ROWS
        super().__init__("🌀 Labirinto", W, H + 40, pet, on_finish, "maze")

        self.canvas = tk.Canvas(self.win, width=W, height=H, bg="#1a1a2e")
        self.canvas.pack()
        tk.Label(self.win, text="Setas para mover  |  Chegue ao 🏁!",
                 font=("Arial", 9)).pack(pady=4)

        self.maze = self._generate_maze()
        self.px, self.py = 0, 0

        self._draw_maze()

        self.win.bind("<Up>",    lambda e: self._move(0, -1))
        self.win.bind("<Down>",  lambda e: self._move(0, 1))
        self.win.bind("<Left>",  lambda e: self._move(-1, 0))
        self.win.bind("<Right>", lambda e: self._move(1, 0))
        self.win.focus_set()

    def _generate_maze(self):
        """Gera labirinto com DFS recursivo. maze[y][x] = set de direções abertas."""
        cols, rows = self.COLS, self.ROWS
        visited = [[False] * cols for _ in range(rows)]
        walls = {(y, x): {"N", "S", "E", "W"} for y in range(rows) for x in range(cols)}

        def dfs(y, x):
            visited[y][x] = True
            dirs = [("N", -1, 0), ("S", 1, 0), ("E", 0, 1), ("W", 0, -1)]
            random.shuffle(dirs)
            for d, dy, dx in dirs:
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols and not visited[ny][nx]:
                    # remove parede entre (y,x) e (ny,nx)
                    walls[(y, x)].discard(d)
                    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}[d]
                    walls[(ny, nx)].discard(opp)
                    dfs(ny, nx)

        dfs(0, 0)
        return walls

    def _draw_maze(self):
        self.canvas.delete("all")
        C = self.CELL

        for y in range(self.ROWS):
            for x in range(self.COLS):
                x1, y1 = x * C, y * C
                x2, y2 = x1 + C, y1 + C
                walls = self.maze[(y, x)]

                # fundo da célula
                color = "#16213e"
                if (x, y) == (self.COLS - 1, self.ROWS - 1):
                    color = "#1b5e20"  # meta
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                lw = 2
                lc = "#7e57c2"
                if "N" in walls:
                    self.canvas.create_line(x1, y1, x2, y1, fill=lc, width=lw)
                if "S" in walls:
                    self.canvas.create_line(x1, y2, x2, y2, fill=lc, width=lw)
                if "W" in walls:
                    self.canvas.create_line(x1, y1, x1, y2, fill=lc, width=lw)
                if "E" in walls:
                    self.canvas.create_line(x2, y1, x2, y2, fill=lc, width=lw)

        # meta
        gx = (self.COLS - 1) * C + C // 2
        gy = (self.ROWS - 1) * C + C // 2
        self.canvas.create_text(gx, gy, text="🏁", font=("Arial", 18))

        # jogador
        player_x = self.px * C + C // 2
        player_y = self.py * C + C // 2

        self._draw_player_icon(
            self.canvas,
            player_x,
            player_y,
            fallback="🐾"
        )

    def _move(self, dx, dy):
        dirs_map = {(0, -1): "N", (0, 1): "S", (1, 0): "E", (-1, 0): "W"}
        d = dirs_map.get((dx, dy))
        if d and d not in self.maze[(self.py, self.px)]:
            self.px += dx
            self.py += dy
            self._draw_maze()
            if self.px == self.COLS - 1 and self.py == self.ROWS - 1:
                self._reward(True)