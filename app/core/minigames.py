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


def load_png(relative_path, subsample=1):
    """Carrega um PhotoImage PNG, retornando None se não existir."""
    path = resource_path(relative_path)
    if not os.path.exists(path):
        return None
    try:
        img = tk.PhotoImage(file=path)
        if subsample > 1:
            img = img.subsample(subsample, subsample)
        return img
    except tk.TclError:
        return None


# ---------------------------------------------------------------------------
# Configuração de dificuldade por jogo
# Cada entrada: (label_ui, multiplicador_recompensa, params_específicos)
# ---------------------------------------------------------------------------
DIFFICULTY_CONFIG = {
    "memory": {
        "fácil":  {"reward_mult": 1.0, "cols": 3, "rows": 4, "time_limit": 90},
        "médio":  {"reward_mult": 1.5, "cols": 4, "rows": 4, "time_limit": 60},
        "difícil":{"reward_mult": 2.2, "cols": 4, "rows": 6, "time_limit": 40},
    },
    "dino": {
        "fácil":  {"reward_mult": 1.0, "obs_density": 0.6, "survive_time": 12},
        "médio":  {"reward_mult": 1.5, "obs_density": 1.0, "survive_time": 18},
        "difícil":{"reward_mult": 2.2, "obs_density": 1.5, "survive_time": 25},
    },
    "flappy": {
        "fácil":  {"reward_mult": 1.0, "pipe_density": 0.7, "target_pipes": 8,  "time_limit": 120},
        "médio":  {"reward_mult": 1.5, "pipe_density": 1.0, "target_pipes": 12, "time_limit": 90},
        "difícil":{"reward_mult": 2.2, "pipe_density": 1.4, "target_pipes": 18, "time_limit": 60},
    },
    "crossroad": {
        "fácil":  {"reward_mult": 1.0, "speed_mult": 0.7, "extra_lanes": 0, "time_limit": 90},
        "médio":  {"reward_mult": 1.5, "speed_mult": 1.0, "extra_lanes": 1, "time_limit": 60},
        "difícil":{"reward_mult": 2.2, "speed_mult": 1.5, "extra_lanes": 2, "time_limit": 40},
    },
    "maze": {
        "fácil":  {"reward_mult": 1.0, "size": 8,  "time_limit": 120},
        "médio":  {"reward_mult": 1.5, "size": 12, "time_limit": 80},
        "difícil":{"reward_mult": 2.2, "size": 16, "time_limit": 50},
    },
}

BASE_REWARDS = {
    "memory":    {"win": {"coins": 18, "happiness": 12, "xp": 30}, "lose": {"coins": 5,  "happiness": 4, "xp": 8}},
    "dino":      {"win": {"coins": 15, "happiness": 10, "xp": 25}, "lose": {"coins": 4,  "happiness": 3, "xp": 6}},
    "flappy":    {"win": {"coins": 20, "happiness": 14, "xp": 35}, "lose": {"coins": 5,  "happiness": 4, "xp": 8}},
    "crossroad": {"win": {"coins": 14, "happiness": 10, "xp": 25}, "lose": {"coins": 4,  "happiness": 3, "xp": 6}},
    "maze":      {"win": {"coins": 22, "happiness": 16, "xp": 40}, "lose": {"coins": 6,  "happiness": 5, "xp": 10}},
}

DIFF_LABELS = ["fácil", "médio", "difícil"]
DIFF_COLORS = {"fácil": "#4caf50", "médio": "#ff9800", "difícil": "#e53935"}
DIFF_EMOJIS = {"fácil": "🟢", "médio": "🟡", "difícil": "🔴"}

DEFAULT_PINK_BG = "#FFF0F6"


def _scaled_reward(key, difficulty, won):
    base = BASE_REWARDS[key]["win" if won else "lose"]
    mult = DIFFICULTY_CONFIG[key][difficulty]["reward_mult"]
    return {k: max(1, int(v * mult)) for k, v in base.items()}

def _emoji_bar(value, emoji, step):
    """Converte valor numérico em fileira de emojis (arredondado pelo step)."""
    count = max(1, round(value / step))
    return emoji * count



# ---------------------------------------------------------------------------
# Tela 1 — Seletor de minijogo
# ---------------------------------------------------------------------------
def open_minigame_selector(parent, pet, party, on_finish):
    win = tk.Toplevel(parent)
    win.title("Minijogos")
    win.resizable(False, False)
    win.grab_set()
    win.configure(bg="#FFF0F6")

    # Cabeçalho fixo
    header = tk.Frame(win, bg="#FFF0F6")
    header.pack(fill="x", pady=(14, 4))
    tk.Label(header, text="🎮  Minijogos", font=("Arial", 18, "bold"),
             bg="#FFF0F6", fg="#C2185B").pack()
    tk.Label(header, text=f"💰  Moedas: {party.money}", font=("Arial", 11),
             bg="#FFF0F6", fg="#AD1457").pack()

    # Ícone do pet
    icon_path = resource_path(f"assets/icons/{pet.asset_key}_icon.png")
    pet_icon = None
    if os.path.exists(icon_path):
        try:
            pet_icon = tk.PhotoImage(file=icon_path)
        except tk.TclError:
            pass
    if pet_icon:
        lbl = tk.Label(header, image=pet_icon, bg="#FFF0F6", bd=0, highlightthickness=0)
        lbl.image = pet_icon
        lbl.pack(pady=4)
    else:
        tk.Label(header, text=pet.name, font=("Arial", 13, "bold"),
                 bg="#FFF0F6", fg="#C2185B").pack(pady=4)

    games = [
        ("🃏  Jogo da Memória", "memory"),
        ("🦕  Dino Run",        "dino"),
        ("🐦  Flappy Bird",     "flappy"),
        ("🚗  Crossroad",       "crossroad"),
        ("🌀  Labirinto",       "maze"),
    ]

    for label, key in games:
        btn = tk.Button(
            win, text=label,
            font=("Arial", 13, "bold"),
            bg="#F8BBD0", fg="#880E4F",
            activebackground="#F48FB1", activeforeground="#880E4F",
            relief="flat", bd=0,
            cursor="hand2",
            width=30, height=2,
            command=lambda k=key, w=win: _open_difficulty(w, k, pet, party, on_finish)
        )
        btn.pack(fill="x", padx=24, pady=6)

    win.update_idletasks()
    win.geometry(f"{win.winfo_reqwidth() + 40}x{min(win.winfo_reqheight() + 20, 680)}")


# ---------------------------------------------------------------------------
# Tela 2 — Seletor de dificuldade
# ---------------------------------------------------------------------------
def _open_difficulty(selector_win, key, pet, party, on_finish):
    selector_win.destroy()

    game_names = {
        "memory": "🃏 Jogo da Memória",
        "dino":   "🦕 Dino Run",
        "flappy": "🐦 Flappy Bird",
        "crossroad": "🚗 Crossroad",
        "maze":   "🌀 Labirinto",
    }

    win = tk.Toplevel()
    win.title("Dificuldade")
    win.resizable(False, False)
    win.grab_set()
    win.configure(bg="#FFF0F6")

    # ── Cabeçalho fixo ──
    header_frame = tk.Frame(win, bg="#FFF0F6")
    header_frame.pack(fill="x")
    tk.Label(header_frame, text=game_names[key], font=("Arial", 16, "bold"),
             bg="#FFF0F6", fg="#C2185B").pack(pady=(14, 4))
    tk.Label(header_frame, text="Escolha a dificuldade:", font=("Arial", 11),
             bg="#FFF0F6", fg="#AD1457").pack(pady=(0, 10))

    # ── Área rolável ──
    scroll_canvas = tk.Canvas(win, bg="#FFF0F6", highlightthickness=0,
                               width=520)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=scroll_canvas.yview)
    scroll_canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    scroll_canvas.pack(side="left", fill="both", expand=True)

    scroll_frame = tk.Frame(scroll_canvas, bg="#FFF0F6")
    scroll_win_id = scroll_canvas.create_window((0, 0), window=scroll_frame,
                                                 anchor="nw")

    def _on_frame_configure(e):
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

    def _on_canvas_configure(e):
        scroll_canvas.itemconfig(scroll_win_id, width=e.width)

    scroll_frame.bind("<Configure>", _on_frame_configure)
    scroll_canvas.bind("<Configure>", _on_canvas_configure)

    # Scroll com mouse wheel
    def _on_mousewheel(e):
        scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    win.protocol("WM_DELETE_WINDOW", lambda: (
        scroll_canvas.unbind_all("<MouseWheel>"), win.destroy()
    ))

    for diff in DIFF_LABELS:
        cfg = DIFFICULTY_CONFIG[key][diff]
        wr = _scaled_reward(key, diff, True)
        lr = _scaled_reward(key, diff, False)

        params_text = _diff_params_text(key, cfg)

        frame = tk.Frame(scroll_frame, bg=DIFF_COLORS[diff], bd=0)
        frame.pack(fill="x", padx=18, pady=8)

        inner = tk.Frame(frame, bg="#FFF0F6", padx=10, pady=8)
        inner.pack(fill="x", padx=2, pady=2)

        header = tk.Frame(inner, bg="#FFF0F6")
        header.pack(fill="x")
        tk.Label(header, text=f"{DIFF_EMOJIS[diff]}  {diff.capitalize()}",
                 font=("Arial", 13, "bold"), bg="#FFF0F6",
                 fg=DIFF_COLORS[diff], anchor="w").pack(side="left")

        tk.Label(inner, text=params_text, font=("Arial", 9),
                 bg="#FFF0F6", fg="#880E4F", anchor="w", justify="left").pack(fill="x", pady=(2, 4))

        win_coins_bar = _emoji_bar(wr['coins'],    "💰", 5)
        win_happy_bar = _emoji_bar(wr['happiness'], "😊", 4)
        win_xp_bar    = _emoji_bar(wr['xp'],        "⭐", 10)
        lose_coins_bar = _emoji_bar(lr['coins'],    "💰", 5)
        lose_happy_bar = _emoji_bar(lr['happiness'],"😊", 4)
        lose_xp_bar    = _emoji_bar(lr['xp'],       "⭐", 10)

        tk.Label(inner, text="🏆 Vitória", font=("Arial", 9, "bold"),
                 bg="#FFF0F6", fg="#4caf50", anchor="w").pack(fill="x", pady=(4,0))
        tk.Label(inner, text=f"  {win_coins_bar}  {win_happy_bar}  {win_xp_bar}",
                 font=("Arial", 10), bg="#FFF0F6", fg="#880E4F",
                 anchor="w", justify="left").pack(fill="x")
        tk.Label(inner, text="💀 Derrota", font=("Arial", 9, "bold"),
                 bg="#FFF0F6", fg="#e53935", anchor="w").pack(fill="x", pady=(2,0))
        tk.Label(inner, text=f"  {lose_coins_bar}  {lose_happy_bar}  {lose_xp_bar}",
                 font=("Arial", 10), bg="#FFF0F6", fg="#880E4F",
                 anchor="w", justify="left").pack(fill="x")

        tk.Button(
            inner, text="▶  Jogar",
            font=("Arial", 11, "bold"),
            bg=DIFF_COLORS[diff], fg="white",
            activebackground="#880E4F", activeforeground="white",
            relief="flat", cursor="hand2",
            command=lambda d=diff, w=win: _launch(w, key, d, pet, party, on_finish)
        ).pack(anchor="e", pady=(6, 0))


    # Calcula altura necessária e limita a 90% da tela
    win.update_idletasks()
    content_h = scroll_frame.winfo_reqheight() + header_frame.winfo_reqheight() + 20
    screen_h  = win.winfo_screenheight()
    final_h   = min(content_h, int(screen_h * 0.88))
    win.geometry(f"560x{final_h}")


def _diff_params_text(key, cfg):
    """Gera linha de parâmetros legível para cada jogo."""
    if key == "memory":
        return f"Grade: {cfg['cols']}×{cfg['rows']}  |  Tempo: {cfg['time_limit']}s"
    if key == "dino":
        return f"Tempo para sobreviver: {cfg['survive_time']}s  |  Obstáculos: {'mais' if cfg['obs_density'] > 1 else 'normal' if cfg['obs_density'] == 1 else 'menos'}"
    if key == "flappy":
        return f"Canos para passar: {cfg['target_pipes']}  |  Tempo: {cfg['time_limit']}s"
    if key == "crossroad":
        lv = cfg['extra_lanes']
        return f"Tempo: {cfg['time_limit']}s  |  Faixas extras: {lv}  |  Velocidade: {int(cfg['speed_mult']*100)}%"
    if key == "maze":
        return f"Grade: {cfg['size']}×{cfg['size']}  |  Tempo: {cfg['time_limit']}s"
    return ""


# ---------------------------------------------------------------------------
# Launch — instancia o jogo com dificuldade
# ---------------------------------------------------------------------------
def _launch(diff_win, key, difficulty, pet, party, on_finish):
    diff_win.destroy()
    cfg = DIFFICULTY_CONFIG[key][difficulty]
    launchers = {
        "memory":    MemoryGame,
        "dino":      DinoGame,
        "flappy":    FlappyGame,
        "crossroad": CrossroadGame,
        "maze":      MazeGame,
    }
    launchers[key](pet, party, difficulty, cfg, on_finish)


# ===========================================================================
# BASE GAME
# ===========================================================================
class BaseGame:
    def __init__(self, title, width, height, pet, party, difficulty, cfg, on_finish, key):
        self.pet = pet
        self.party = party
        self.difficulty = difficulty
        self.cfg = cfg
        self.on_finish = on_finish
        self.key = key
        self.finished = False

        self.pet_icon = self._load_pet_icon(subsample=2)
        self.pet_icon_big = self._load_pet_icon(subsample=1)

        self.win = tk.Toplevel()
        self.win.title(f"{title}  [{difficulty.capitalize()}]")
        self.win.geometry(f"{width}x{height}")
        self.win.resizable(False, False)
        self.win.grab_set()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_pet_icon(self, subsample=1):
        icon_path = resource_path(f"assets/icons/{self.pet.asset_key}_icon.png")
        if not os.path.exists(icon_path):
            return None
        try:
            img = tk.PhotoImage(file=icon_path)
            if subsample > 1:
                img = img.subsample(subsample, subsample)
            return img
        except tk.TclError:
            return None

    def _draw_player_icon(self, canvas, x, y, fallback="●"):
        if self.pet_icon:
            return canvas.create_image(x, y, image=self.pet_icon, anchor="center")
        return canvas.create_text(x, y, text=fallback, font=("Arial", 24), anchor="center")

    def _coords_player_icon(self, canvas, item, x, y):
        canvas.coords(item, x, y)

    def _reward(self, won):
        if self.finished:
            return
        self.finished = True

        reward = _scaled_reward(self.key, self.difficulty, won)
        coins, happiness, xp = reward["coins"], reward["happiness"], reward["xp"]

        self.party.money += coins
        self.pet.happiness += happiness
        self.pet.energy -= 4
        self.pet.hunger -= 2
        self.pet.limit_attributes()
        self.party.add_xp(xp)

        self.win.destroy()
        result = "Vitória! 🎉" if won else "Derrota! 😢"
        try:
            self.on_finish(coins, result, happiness, xp)
        except TypeError:
            self.on_finish(coins, result)

    def _on_close(self):
        if not self.finished:
            self._reward(False)


# ===========================================================================
# 1. JOGO DA MEMÓRIA
# ===========================================================================
class MemoryGame(BaseGame):
    # 18 figuras disponíveis (memory_fig1 … memory_fig18)
    ALL_FIGS = [f"assets/minigames/memory_fig{i}.png" for i in range(1, 19)]

    def __init__(self, pet, party, difficulty, cfg, on_finish):
        self.cols = cfg["cols"]
        self.rows = cfg["rows"]
        self.time_limit = cfg["time_limit"]
        total_cards = self.cols * self.rows          # sempre par por construção
        n_pairs = total_cards // 2

        # Tamanho de célula adaptativo
        cell = min(80, max(52, 360 // max(self.cols, self.rows)))
        self.cell_size = cell
        W = self.cols * cell + 24
        H = self.rows * cell + 80   # espaço para barra de info

        super().__init__("🃏 Jogo da Memória", W, H,
                         pet, party, difficulty, cfg, on_finish, "memory")

        self.win.configure(bg=DEFAULT_PINK_BG)

        self.bg_img = load_png("assets/minigames/memory_background.png")

        FALLBACK_EMOJIS = ["🐱","🐶","🐸","🐧","🦊","🐺","🐷","🐮",
                           "🐯","🐻","🦁","🐨","🦄","🐙","🦋","🐢","🦀","🦜"]
        self.fig_images = []
        for i in range(n_pairs):
            img = load_png(self.ALL_FIGS[i % len(self.ALL_FIGS)])
            self.fig_images.append(img)
        self.fig_fallbacks = FALLBACK_EMOJIS[:n_pairs]

        indices = list(range(n_pairs)) * 2  # sempre par
        random.shuffle(indices)
        self.card_ids = indices

        self.buttons = []
        self.card_imgs = []
        self.flipped = []
        self.matched = set()
        self.locked = False
        self.time_left = self.time_limit

        # --- UI ---
        top = tk.Frame(self.win, bg="#FFF0F6")
        top.pack(fill="x", pady=4, padx=8)

        self.info_lbl = tk.Label(top, text="", font=("Arial", 10, "bold"),
                                  bg="#FFF0F6", fg="#C2185B", anchor="w")
        self.info_lbl.pack(side="left")

        self.timer_lbl = tk.Label(top, text="", font=("Arial", 10, "bold"),
                                   bg="#FFF0F6", fg="#AD1457", anchor="e")
        self.timer_lbl.pack(side="right")

        self.canvas = tk.Canvas(self.win, width=W - 4, height=self.rows * cell,
                                bg="#FFF0F6", highlightthickness=0)
        self.canvas.pack(padx=2, pady=4)

        if self.bg_img:
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        self.grid_frame = tk.Frame(self.canvas, bg="#FFF0F6")
        self.canvas.create_window(4, 4, anchor="nw", window=self.grid_frame)

        for i in range(total_cards):
            btn = tk.Button(
                self.grid_frame,
                text="?",
                width=max(3, cell // 16), height=max(1, cell // 32),
                font=("Arial", max(10, cell // 6), "bold"),
                bg="#F8BBD0", fg="#AD1457",
                activebackground="#F48FB1",
                relief="flat", bd=1,
                command=lambda idx=i: self._flip(idx)
            )
            btn.grid(row=i // self.cols, column=i % self.cols, padx=2, pady=2)
            self.buttons.append(btn)
            self.card_imgs.append(None)

        self._update_info()
        self._tick()

    def _update_info(self):
        pairs_found = len(self.matched) // 2
        total_pairs = len(self.card_ids) // 2
        self.info_lbl.config(text=f"🃏 {pairs_found}/{total_pairs} pares")
        color = "#AD1457" if self.time_left > 15 else "#e53935"
        self.timer_lbl.config(text=f"⏱ {self.time_left}s", fg=color)

    def _tick(self):
        if self.finished:
            return
        self._update_info()
        if self.time_left <= 0:
            self._reward(False)
            return
        self.time_left -= 1
        self.win.after(1000, self._tick)

    def _flip(self, idx):
        if self.locked or idx in self.matched or idx in self.flipped:
            return
        fig_idx = self.card_ids[idx]
        img = self.fig_images[fig_idx]
        if img:
            self.buttons[idx].config(image=img, text="")
            self.buttons[idx].image = img
        else:
            self.buttons[idx].config(text=self.fig_fallbacks[fig_idx % len(self.fig_fallbacks)],
                                      image="")
        self.buttons[idx].config(state="disabled", bg="#533483")
        self.flipped.append(idx)

        if len(self.flipped) == 2:
            self.locked = True
            self.win.after(750, self._check)

    def _check(self):
        a, b = self.flipped
        if self.card_ids[a] == self.card_ids[b]:
            self.matched.add(a)
            self.matched.add(b)
            self.buttons[a].config(bg="#1b5e20")
            self.buttons[b].config(bg="#1b5e20")
            self._update_info()
            if len(self.matched) >= len(self.card_ids):
                self._reward(True)
                return
        else:
            self.buttons[a].config(text="?", image="", bg="#FFF0F6", state="normal")
            self.buttons[b].config(text="?", image="", bg="#FFF0F6", state="normal")
            self.card_imgs[a] = None
            self.card_imgs[b] = None
        self.flipped.clear()
        self.locked = False


# ===========================================================================
# 2. DINO RUN
# ===========================================================================
class DinoGame(BaseGame):
    W, H = 520, 300

    def __init__(self, pet, party, difficulty, cfg, on_finish):
        super().__init__("🦕 Dino Run", self.W + 120, self.H + 180,
                         pet, party, difficulty, cfg, on_finish, "dino")

        self.survive_time = cfg["survive_time"]
        self.obs_density  = cfg["obs_density"]

        # Assets
        self.bg_img  = load_png("assets/minigames/dino_background.png")
        self.obs_img = load_png("assets/minigames/dino_obstacle.png")
        # Mantém referências para evitar GC
        self._obs_img_refs = []

        self.canvas = tk.Canvas(self.win, width=self.W, height=self.H,
                                bg=DEFAULT_PINK_BG, highlightthickness=0)
        self.canvas.pack()
        tk.Label(self.win, text="ESPAÇO para pular  |  Sobreviva!",
                 font=("Arial", 9), bg="#FFF0F6", fg="#AD1457").pack(fill="x")

        self.win.configure(bg="#FFF0F6")

        # Fundo
        if self.bg_img:
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        else:
            self.canvas.create_rectangle(0, 0, self.W, self.H, fill=DEFAULT_PINK_BG, outline="")

        # Chão
        self.canvas.create_line(0, self.H - 30, self.W, self.H - 30, fill="#5d4037", width=3)

        self.dino_x  = 70
        self.dino_y  = self.H - 50
        self.dino_vy = 0
        self.on_ground = True

        self.obstacles = []    # cada obs: {"item": canvas_id, "img_ref": img}
        self.obs_speed = 5
        self.frame_count = 0
        self.next_obs = int(60 / self.obs_density)

        self.start_time = time.time()

        self.score_text = self.canvas.create_text(
            self.W - 10, 10, anchor="ne",
            text=f"0s / {self.survive_time}s",
            font=("Arial", 12, "bold"), fill="#FFF0F6"
        )

        self.dino_item = self._draw_player_icon(
            self.canvas, self.dino_x + 15, self.dino_y - 15, fallback="🦕"
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
                               text=f"{int(elapsed)}s / {self.survive_time}s")

        if elapsed >= self.survive_time:
            self._reward(True)
            return

        # Física
        self.dino_vy += 1
        self.dino_y  += self.dino_vy
        ground = self.H - 50
        if self.dino_y >= ground:
            self.dino_y = ground
            self.dino_vy = 0
            self.on_ground = True

        self._coords_player_icon(self.canvas, self.dino_item,
                                  self.dino_x + 15, self.dino_y - 15)

        # Spawn de obstáculos
        self.frame_count += 1
        if self.frame_count >= self.next_obs:
            h = random.randint(22, 52)
            img = load_png("assets/minigames/dino_obstacle.png")
            if img:
                obs_item = self.canvas.create_image(
                    self.W + 10, self.H - 30 - h // 2,
                    image=img, anchor="center"
                )
                ref = img
            else:
                obs_item = self.canvas.create_rectangle(
                    self.W, self.H - 30 - h, self.W + 20, self.H - 30,
                    fill="#e53935", outline="#b71c1c"
                )
                ref = None
            self.obstacles.append({"item": obs_item, "img_ref": ref, "h": h})
            self.frame_count = 0
            gap_min = max(30, int(45 / self.obs_density))
            gap_max = max(50, int(90 / self.obs_density))
            self.next_obs = random.randint(gap_min, gap_max)
            self.obs_speed = min(12, 5 + int(elapsed / 4))

        dead = False
        for obs in list(self.obstacles):
            self.canvas.move(obs["item"], -self.obs_speed, 0)
            coords = self.canvas.coords(obs["item"])
            if not coords:
                self.obstacles.remove(obs)
                continue
            cx = coords[0] if obs["img_ref"] else coords[2]  # imagem: x centro; rect: x2
            if (obs["img_ref"] and cx < -20) or (not obs["img_ref"] and coords[2] < 0):
                self.canvas.delete(obs["item"])
                self.obstacles.remove(obs)
                continue
            # Colisão (bounding box aproximada)
            ox = coords[0] - 10 if obs["img_ref"] else coords[0]
            ox2 = coords[0] + 10 if obs["img_ref"] else coords[2]
            oy = self.H - 30 - obs["h"]
            if (ox < self.dino_x + 28 and ox2 > self.dino_x + 2 and
                    oy < self.dino_y and self.H - 30 > self.dino_y - 28):
                dead = True

        if dead:
            self._reward(False)
            return

        self.canvas.tag_raise(self.dino_item)
        self.canvas.tag_raise(self.score_text)
        self.win.after(30, self._loop)


# ===========================================================================
# 3. FLAPPY BIRD
# ===========================================================================
class FlappyGame(BaseGame):
    W, H   = 400, 500
    GAP    = 130
    PIPE_W = 44

    def __init__(self, pet, party, difficulty, cfg, on_finish):
        super().__init__("🐦 Flappy Bird", self.W + 140, self.H + 180,
                         pet, party, difficulty, cfg, on_finish, "flappy")

        self.target_pipes = cfg["target_pipes"]
        self.pipe_density = cfg["pipe_density"]
        self.time_limit   = cfg["time_limit"]
        self.PIPE_SPEED   = int(3 * self.pipe_density)

        self.bg_img   = load_png("assets/minigames/flappy_background.png")
        self.pipe_img = load_png("assets/minigames/flappy_obstacle.png")

        self.win.configure(bg="#FFF0F6")

        self.canvas = tk.Canvas(self.win, width=self.W, height=self.H,
                                bg=DEFAULT_PINK_BG, highlightthickness=0)
        self.canvas.pack()

        info_bar = tk.Frame(self.win, bg="#FFF0F6", height=40)
        info_bar.pack(fill="x")
        self.time_lbl = tk.Label(info_bar, text="", font=("Arial", 9),
                                  bg="#FFF0F6", fg="#ffd700")
        self.time_lbl.pack(side="left", padx=8)
        tk.Label(info_bar, text="ESPAÇO ou clique para bater asas",
                 font=("Arial", 9), bg="#FFF0F6", fg="#AD1457").pack(side="right", padx=8)

        if self.bg_img:
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        # Chão
        self.canvas.create_rectangle(0, self.H - 20, self.W, self.H,
                                      fill="#8d6e3f", outline="")

        self.bird_x  = 80
        self.bird_y  = self.H // 2
        self.bird_vy = 0

        self.pipes   = []
        self.score   = 0
        self.frame   = 0
        self.next_pipe = 80
        self.time_left = self.time_limit

        self.bird = self._draw_player_icon(self.canvas, self.bird_x, self.bird_y, fallback="🐦")

        self.score_txt = self.canvas.create_text(
            10, 10, anchor="nw",
            text=f"0 / {self.target_pipes}", font=("Arial", 14, "bold"), fill="white"
        )

        self.win.bind("<space>", self._flap)
        self.canvas.bind("<Button-1>", self._flap)
        self.win.focus_set()
        self._tick_timer()
        self._loop()

    def _flap(self, event=None):
        self.bird_vy = -8

    def _tick_timer(self):
        if self.finished:
            return
        color = "#ffd700" if self.time_left > 15 else "#e53935"
        self.time_lbl.config(text=f"⏱ {self.time_left}s", fg=color)
        if self.time_left <= 0:
            self._reward(False)
            return
        self.time_left -= 1
        self.win.after(1000, self._tick_timer)

    def _loop(self):
        if self.finished:
            return

        self.bird_vy += 0.5
        self.bird_y  += self.bird_vy
        self._coords_player_icon(self.canvas, self.bird, self.bird_x, self.bird_y)

        if self.bird_y >= self.H - 32 or self.bird_y <= 0:
            self._reward(False)
            return

        # Spawn de canos
        self.frame += 1
        gap_base = int(90 / self.pipe_density)
        if self.frame >= self.next_pipe:
            gap_y = random.randint(80, self.H - 130)
            if self.pipe_img:
                top_item = self.canvas.create_image(
                    self.W, gap_y // 2, image=self.pipe_img, anchor="center"
                )
                bot_item = self.canvas.create_image(
                    self.W, gap_y + self.GAP + (self.H - gap_y - self.GAP) // 2,
                    image=self.pipe_img, anchor="center"
                )
            else:
                top_item = self.canvas.create_rectangle(
                    self.W, 0, self.W + self.PIPE_W, gap_y,
                    fill="#4caf50", outline="#2e7d32"
                )
                bot_item = self.canvas.create_rectangle(
                    self.W, gap_y + self.GAP, self.W + self.PIPE_W, self.H - 20,
                    fill="#4caf50", outline="#2e7d32"
                )
            self.pipes.append({
                "top": top_item, "bot": bot_item,
                "gap_y": gap_y, "passed": False,
                "has_img": bool(self.pipe_img)
            })
            self.frame = 0
            self.next_pipe = random.randint(max(50, gap_base - 20), gap_base + 20)

        # Move e verifica canos
        for p in list(self.pipes):
            self.canvas.move(p["top"], -self.PIPE_SPEED, 0)
            self.canvas.move(p["bot"], -self.PIPE_SPEED, 0)
            cx = self.canvas.coords(p["top"])
            if not cx:
                self.pipes.remove(p)
                continue

            if p["has_img"]:
                pipe_x1 = cx[0] - self.PIPE_W // 2
                pipe_x2 = cx[0] + self.PIPE_W // 2
            else:
                pipe_x1, _, pipe_x2, _ = cx

            if not p["passed"] and pipe_x2 < self.bird_x - 14:
                p["passed"] = True
                self.score += 1
                self.canvas.itemconfig(self.score_txt,
                                        text=f"{self.score} / {self.target_pipes}")
                if self.score >= self.target_pipes:
                    self._reward(True)
                    return

            if pipe_x1 < self.bird_x + 12 and pipe_x2 > self.bird_x - 12:
                gap_y = p["gap_y"]
                if self.bird_y - 12 < gap_y or self.bird_y + 12 > gap_y + self.GAP:
                    self._reward(False)
                    return

            if pipe_x2 < 0:
                self.canvas.delete(p["top"])
                self.canvas.delete(p["bot"])
                self.pipes.remove(p)

        self.canvas.tag_raise(self.bird)
        self.canvas.tag_raise(self.score_txt)
        self.win.after(30, self._loop)


# ===========================================================================
# 4. CROSSROAD
# ===========================================================================
class CrossroadGame(BaseGame):
    CELL = 42
    COLS = 10
    ROWS = 10
    W    = CELL * COLS
    H    = CELL * ROWS

    # Faixas base
    BASE_LANES = {
        2: {"dir":  1, "speed": 2.5},
        3: {"dir": -1, "speed": 3.0},
        5: {"dir":  1, "speed": 2.0},
        6: {"dir": -1, "speed": 3.5},
        8: {"dir":  1, "speed": 2.8},
    }
    # Faixas extras (adicionadas conforme dificuldade)
    EXTRA_LANES = [
        {4: {"dir":  1, "speed": 2.2}},
        {7: {"dir": -1, "speed": 3.8}},
    ]

    def __init__(self, pet, party, difficulty, cfg, on_finish):
        super().__init__("🚗 Crossroad", self.W + 140, self.H + 180,
                         pet, party, difficulty, cfg, on_finish, "crossroad")

        self.speed_mult = cfg["speed_mult"]
        self.time_limit = cfg["time_limit"]
        self.time_left  = self.time_limit

        # Assets
        self.bg_img  = load_png("assets/minigames/cross_background.png")
        self.road_img = load_png("assets/minigames/cross_road.png")
        self.car_img  = load_png("assets/minigames/cross_obstacle.png")

        self.win.configure(bg="#FFF0F6")

        self.canvas = tk.Canvas(self.win, width=self.W, height=self.H,
                                bg=DEFAULT_PINK_BG, highlightthickness=0)
        self.canvas.pack()

        info_bar = tk.Frame(self.win, bg="#FFF0F6", height=50)
        info_bar.pack(fill="x")
        self.info_lbl = tk.Label(info_bar, text="", font=("Arial", 10, "bold"),
                                  bg="#FFF0F6", fg="#AD1457")
        self.info_lbl.pack(side="left", padx=8)
        self.timer_lbl = tk.Label(info_bar, text="", font=("Arial", 10, "bold"),
                                   bg="#FFF0F6", fg="#ffd700")
        self.timer_lbl.pack(side="right", padx=8)
        tk.Label(info_bar, text="Setas para mover  |  Chegue ao outro lado 3×!",
                 font=("Arial", 9), bg="#FFF0F6", fg="#aaaaaa").pack()

        # Monta faixas com extras
        self.lanes = {}
        for row, lane_cfg in self.BASE_LANES.items():
            self.lanes[row] = {
                "dir": lane_cfg["dir"],
                "speed": lane_cfg["speed"] * self.speed_mult,
                "cars": []
            }
        for i in range(min(cfg["extra_lanes"], len(self.EXTRA_LANES))):
            for row, lane_cfg in self.EXTRA_LANES[i].items():
                self.lanes[row] = {
                    "dir": lane_cfg["dir"],
                    "speed": lane_cfg["speed"] * self.speed_mult,
                    "cars": []
                }

        self.px = 5
        self.py = 9
        self.lives  = 3
        self.wins   = 0
        self.target = 3

        for row, lane in self.lanes.items():
            self._spawn_cars(row, lane)

        self._draw_all()

        self.win.bind("<Up>",    lambda e: self._move(0, -1))
        self.win.bind("<Down>",  lambda e: self._move(0, 1))
        self.win.bind("<Left>",  lambda e: self._move(-1, 0))
        self.win.bind("<Right>", lambda e: self._move(1, 0))
        self.win.focus_set()
        self._tick_timer()
        self._loop()

    def _tick_timer(self):
        if self.finished:
            return
        color = "#ffd700" if self.time_left > 15 else "#e53935"
        self.timer_lbl.config(text=f"⏱ {self.time_left}s", fg=color)
        if self.time_left <= 0:
            self._reward(False)
            return
        self.time_left -= 1
        self.win.after(1000, self._tick_timer)

    def _spawn_cars(self, row, lane):
        lane["cars"].clear()
        x = 0.0 if lane["dir"] == 1 else float(self.W)
        while True:
            gap = random.randint(70, 150)
            x += gap * lane["dir"]
            lane["cars"].append(x)
            if lane["dir"] == 1 and x > self.W + 200:
                break
            if lane["dir"] == -1 and x < -200:
                break

    def _draw_all(self):
        self.canvas.delete("all")

        if self.bg_img:
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        else:
            for r in range(self.ROWS):
                color = "#37474f" if r in self.lanes else DEFAULT_PINK_BG
                self.canvas.create_rectangle(
                    0, r * self.CELL, self.W, (r + 1) * self.CELL,
                    fill=color, outline=""
                )
            for r in [0, 9]:
                self.canvas.create_rectangle(
                    0, r * self.CELL, self.W, (r + 1) * self.CELL,
                    fill="#8d6e3f", outline=""
                )

        for row, lane in self.lanes.items():
            for cx in lane["cars"]:
                rx1 = min(cx, cx + 36 * lane["dir"])
                rx2 = max(cx, cx + 36 * lane["dir"])
                ry1 = row * self.CELL + 5
                ry2 = (row + 1) * self.CELL - 5
                if self.car_img:
                    self.canvas.create_image(
                        (rx1 + rx2) / 2, (ry1 + ry2) / 2,
                        image=self.car_img, anchor="center"
                    )
                else:
                    self.canvas.create_rectangle(rx1, ry1, rx2, ry2,
                                                  fill="#e53935", outline="#b71c1c")

        player_x = self.px * self.CELL + self.CELL // 2
        player_y = self.py * self.CELL + self.CELL // 2
        self._draw_player_icon(self.canvas, player_x, player_y, fallback="🐾")

        self.info_lbl.config(
            text=f"Chegadas: {self.wins}/{self.target}  Vidas: {'❤️' * self.lives}"
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
                if lane["dir"] == 1 and lane["cars"][i] > self.W + 50:
                    lane["cars"][i] = -50.0
                elif lane["dir"] == -1 and lane["cars"][i] < -86:
                    lane["cars"][i] = float(self.W + 50)

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

    def __init__(self, pet, party, difficulty, cfg, on_finish):
        self.COLS = cfg["size"]
        self.ROWS = cfg["size"]
        self.time_limit = cfg["time_limit"]

        # Tamanho de célula adaptativo para caber na tela
        max_px = 480
        self.CELL = max(20, max_px // self.COLS)
        W = self.CELL * self.COLS
        H = self.CELL * self.ROWS

        super().__init__("🌀 Labirinto", W, H + 50,
                         pet, party, difficulty, cfg, on_finish, "maze")

        self.win.configure(bg="#FFF0F6")

        self.bg_img = load_png("assets/minigames/maze_background.png")

        self.canvas = tk.Canvas(self.win, width=W, height=H,
                                bg=DEFAULT_PINK_BG, highlightthickness=0)
        self.canvas.pack()

        info_bar = tk.Frame(self.win, bg="#FFF0F6", height=50)
        info_bar.pack(fill="x")
        tk.Label(info_bar, text="Setas para mover  |  Chegue ao 🏁",
                 font=("Arial", 9), bg="#FFF0F6", fg="#aaaaaa").pack(side="left", padx=8)
        self.timer_lbl = tk.Label(info_bar, text="", font=("Arial", 10, "bold"),
                                   bg="#FFF0F6", fg="#AD1457")
        self.timer_lbl.pack(side="right", padx=8)

        self.time_left = self.time_limit
        self.px, self.py = 0, 0
        self.maze = self._generate_maze()

        self._draw_maze()

        self.win.bind("<Up>",    lambda e: self._move(0, -1))
        self.win.bind("<Down>",  lambda e: self._move(0, 1))
        self.win.bind("<Left>",  lambda e: self._move(-1, 0))
        self.win.bind("<Right>", lambda e: self._move(1, 0))
        self.win.focus_set()
        self._tick()

    def _tick(self):
        if self.finished:
            return
        color = "#ffd700" if self.time_left > 15 else "#e53935"
        self.timer_lbl.config(text=f"⏱ {self.time_left}s", fg=color)
        if self.time_left <= 0:
            self._reward(False)
            return
        self.time_left -= 1
        self.win.after(1000, self._tick)

    def _generate_maze(self):
        cols, rows = self.COLS, self.ROWS
        visited = [[False] * cols for _ in range(rows)]
        walls = {(y, x): {"N", "S", "E", "W"}
                 for y in range(rows) for x in range(cols)}

        def dfs(y, x):
            visited[y][x] = True
            dirs = [("N", -1, 0), ("S", 1, 0), ("E", 0, 1), ("W", 0, -1)]
            random.shuffle(dirs)
            for d, dy, dx in dirs:
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols and not visited[ny][nx]:
                    walls[(y, x)].discard(d)
                    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}[d]
                    walls[(ny, nx)].discard(opp)
                    dfs(ny, nx)

        sys_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(sys_limit, cols * rows * 4))
        dfs(0, 0)
        sys.setrecursionlimit(sys_limit)
        return walls

    def _draw_maze(self):
        self.canvas.delete("all")
        C = self.CELL

        if self.bg_img:
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        for y in range(self.ROWS):
            for x in range(self.COLS):
                x1, y1 = x * C, y * C
                x2, y2 = x1 + C, y1 + C
                walls = self.maze[(y, x)]

                color = "#1b5e20" if (x, y) == (self.COLS - 1, self.ROWS - 1) else "#FFF0F6"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                lw = max(1, C // 16)
                lc = "#7e57c2"
                if "N" in walls:
                    self.canvas.create_line(x1, y1, x2, y1, fill=lc, width=lw)
                if "S" in walls:
                    self.canvas.create_line(x1, y2, x2, y2, fill=lc, width=lw)
                if "W" in walls:
                    self.canvas.create_line(x1, y1, x1, y2, fill=lc, width=lw)
                if "E" in walls:
                    self.canvas.create_line(x2, y1, x2, y2, fill=lc, width=lw)

        # Meta
        gx = (self.COLS - 1) * C + C // 2
        gy = (self.ROWS - 1) * C + C // 2
        fsize = max(10, C - 8)
        self.canvas.create_text(gx, gy, text="🏁", font=("Arial", fsize))

        # Jogador
        px = self.px * C + C // 2
        py = self.py * C + C // 2
        self._draw_player_icon(self.canvas, px, py, fallback="🐾")

    def _move(self, dx, dy):
        dirs_map = {(0, -1): "N", (0, 1): "S", (1, 0): "E", (-1, 0): "W"}
        d = dirs_map.get((dx, dy))
        if d and d not in self.maze[(self.py, self.px)]:
            self.px += dx
            self.py += dy
            self._draw_maze()
            if self.px == self.COLS - 1 and self.py == self.ROWS - 1:
                self._reward(True)
