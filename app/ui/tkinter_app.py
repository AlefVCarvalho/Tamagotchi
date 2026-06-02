import os
import sys
import math
import random
import tkinter as tk
from tkinter import messagebox, ttk

from app.core.pet_party import (
    PetParty, ALL_SCENARIO_KEYS, SKIN_LEVEL_UNLOCK, SKIN_COIN_PRICE
)
from app.core.shop import Shop
from app.core.save_manager import SaveManager
from app.core.minigames import open_minigame_selector


WINDOW_WIDTH  = 1000
WINDOW_HEIGHT = 560

GAME_AREA_WIDTH  = 620
GAME_AREA_HEIGHT = 460

PET_AREA_MARGIN  = 55
PET_SIZE_FALLBACK = 70

UI_BG        = "#FFF0F6"
UI_BORDER    = "#F7BBD5"
SELECTED_PINK = "#FF4FA3"
UI_BTN       = "#E8799F"   # rosa escuro para botões e cabeçalhos

CANVAS_NAME_OUTLINE = "#000000"
CANVAS_NAME_NORMAL  = "#FFFFFF"

SCENARIOS = {
    "Casa": {
        "key": "casa",
        "display_name": "Casa",
        "background": "assets/backgrounds/casa.png",
        "fallback_color": "#f5deb3",
        "fallback_pet": "🐣",
        "description": "Um lugar confortável para descansar.",
    },
    "Piscina": {
        "key": "piscina",
        "display_name": "Piscina",
        "background": "assets/backgrounds/piscina.png",
        "fallback_color": "#87ceeb",
        "fallback_pet": "🐧",
        "description": "Um cenário divertido e refrescante.",
    },
    "Zoo": {
        "key": "zoo",
        "display_name": "Zoo",
        "background": "assets/backgrounds/zoo.png",
        "fallback_color": "#98fb98",
        "fallback_pet": "🐵",
        "description": "Um passeio cheio de animais.",
    },
    "Palco de Show": {
        "key": "palco",
        "display_name": "Palco de Show",
        "background": "assets/backgrounds/palco.png",
        "fallback_color": "#dda0dd",
        "fallback_pet": "🎤",
        "description": "Luzes, música e muita animação.",
    },
}

# Mapa scenario_key → nome de exibição
SCENARIO_KEY_TO_NAME = {v["key"]: k for k, v in SCENARIOS.items()}

# Informações de desbloqueio legíveis para a UI
SKIN_UNLOCK_INFO = {
    "casa":    {"type": "level", "req": SKIN_LEVEL_UNLOCK["casa"],    "label": f"Nível {SKIN_LEVEL_UNLOCK['casa']}"},
    "piscina": {"type": "level", "req": SKIN_LEVEL_UNLOCK["piscina"], "label": f"Nível {SKIN_LEVEL_UNLOCK['piscina']}"},
    "zoo":     {"type": "coins", "req": SKIN_COIN_PRICE["zoo"],       "label": f"{SKIN_COIN_PRICE['zoo']} 💰"},
    "palco":   {"type": "coins", "req": SKIN_COIN_PRICE["palco"],     "label": f"{SKIN_COIN_PRICE['palco']} 💰"},
}

SCENARIO_EMOJI = {"casa": "🏠", "piscina": "🏊", "zoo": "🦁", "palco": "🎤"}


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class TamagotchiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skz Mini Tamagotchi")

        try:
            self.root.iconbitmap(resource_path("assets/icon.ico"))
        except Exception:
            pass

        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.shop  = Shop()
        self.party = SaveManager.load_game()
        if self.party is None:
            self.party = PetParty()

        self.pet = self.party.get_current_pet()

        self.background_image      = None
        self.background_canvas_item = None

        self.pet_states = {}
        self._init_pet_states()

        self.pet_images  = {}
        self.status_bars = {}

        self.setup_styles()
        self.create_widgets()
        self.load_scene_assets()
        self.update_screen()
        self.animate_pet()

    # ──────────────────────────────────────────────────────────────────
    # Init helpers
    # ──────────────────────────────────────────────────────────────────
    def _init_pet_states(self):
        n = len(self.party.pets)
        section_w = GAME_AREA_WIDTH // max(n, 1)
        for i, pet in enumerate(self.party.pets):
            start_x = section_w * i + section_w // 2
            start_x = max(PET_AREA_MARGIN, min(GAME_AREA_WIDTH - PET_AREA_MARGIN, start_x))
            self.pet_states[i] = {
                "x": start_x,
                "y": GAME_AREA_HEIGHT // 2,
                "vx": random.choice([-2, -1, 1, 2]),
                "vy": random.choice([-1, 1]),
                "walk_phase": random.uniform(0, 6.28),
                "frames_until_change": random.randint(35, 90),
                "canvas_pet": None,
                "canvas_shadow": None,
                "canvas_highlight": None,
                "canvas_name": None,
                "canvas_name_outline": [],
            }

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("default")

        self.style.configure(
            "TNotebook",
            background=UI_BG,
            borderwidth=0
        )

        self.style.configure(
            "TNotebook.Tab",
            background="#F8BBD0",
            foreground="#880E4F",
            padding=(12, 6),
            borderwidth=0
        )

        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#FF4FA3"), ("active", "#F48FB1")],
            foreground=[("selected", "white")]
        )
        for name, color in [
            ("green",  "#4caf50"),
            ("yellow", "#ffc107"),
            ("red",    "#f44336"),
            ("blue",   "#2196f3"),
        ]:
            self.style.configure(
                f"{name}.Horizontal.TProgressbar",
                troughcolor="#dddddd", background=color,
                thickness=18 if name != "blue" else 12
            )

    # ──────────────────────────────────────────────────────────────────
    # Widget creation
    # ──────────────────────────────────────────────────────────────────
    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg=UI_BG)
        self.main_frame.pack(fill="both", expand=True)

        self.game_frame = tk.Frame(self.main_frame, bg=UI_BG, padx=15, pady=15)
        self.game_frame.pack(side="left", fill="both")

        self.side_frame = tk.Frame(self.main_frame, width=350, bg=UI_BG, padx=18, pady=15)
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        self.create_game_area()
        self.create_side_panel()

    def create_game_area(self):
        self.canvas = tk.Canvas(
            self.game_frame,
            width=GAME_AREA_WIDTH, height=GAME_AREA_HEIGHT,
            highlightthickness=0, bg="#000000"
        )
        self.canvas.pack()

    def create_side_panel(self):
        tk.Label(
            self.side_frame, text="Mini Tamagotchi",
            font=("Arial", 20, "bold"), bg=UI_BG, fg=UI_BTN
        ).pack(pady=5)

        self.tabs = ttk.Notebook(self.side_frame, style="TNotebook")
        self.tabs.pack(fill="both", expand=True, pady=5)

        self.status_tab   = tk.Frame(self.tabs, bg=UI_BG)
        self.actions_tab  = tk.Frame(self.tabs, bg=UI_BG)
        self.scenario_tab = tk.Frame(self.tabs, bg=UI_BG)
        self.pets_tab     = tk.Frame(self.tabs, bg=UI_BG)

        self.tabs.add(self.status_tab,   text="Status")
        self.tabs.add(self.actions_tab,  text="Ações")
        self.tabs.add(self.scenario_tab, text="Cenário")
        self.tabs.add(self.pets_tab,     text="Pets")

        self.create_status_tab()
        self.create_actions_tab()
        self.create_scenario_tab()
        self.create_pets_tab()

    # ── Status tab ──
    def create_status_tab(self):
        self.level_frame = tk.Frame(self.status_tab, bg=UI_BG)
        self.level_frame.pack(fill="x", padx=8, pady=(8, 2))

        self.level_label = tk.Label(
            self.level_frame, text="", font=("Arial", 11, "bold"), bg=UI_BG, anchor="w"
        )
        self.level_label.pack(side="left")

        self.money_label = tk.Label(
            self.level_frame, text="", font=("Arial", 11), bg=UI_BG, anchor="e"
        )
        self.money_label.pack(side="right")

        self.xp_bar = ttk.Progressbar(
            self.status_tab, orient="horizontal", length=280,
            mode="determinate", maximum=100, style="blue.Horizontal.TProgressbar"
        )
        self.xp_bar.pack(fill="x", padx=8, pady=(0, 4))

        self.xp_label = tk.Label(
            self.status_tab, text="", font=("Arial", 8), bg=UI_BG, fg="#555555"
        )
        self.xp_label.pack()

        tk.Frame(self.status_tab, height=1, bg=UI_BORDER).pack(fill="x", padx=8, pady=4)

        self.pet_label = tk.Label(
            self.status_tab, text="", font=("Arial", 18, "bold"),
            bg=UI_BG, fg="#C2185B"
        )
        self.pet_label.pack(pady=(4, 2))

        self.info_label = tk.Label(
            self.status_tab, text="", font=("Arial", 10), bg=UI_BG, justify="center"
        )
        self.info_label.pack(pady=3)

        self.status_frame = tk.Frame(self.status_tab, bg=UI_BG)
        self.status_frame.pack(fill="both", expand=True, pady=2, padx=8)

        for lbl, key in [("Fome","hunger"),("Felicidade","happiness"),
                          ("Energia","energy"),("Higiene","hygiene"),("Saúde","health")]:
            self.create_status_bar(lbl, key)

    def create_status_bar(self, label_text, key):
        frame = tk.Frame(self.status_frame, bg=UI_BG)
        frame.pack(fill="x", pady=2)

        top = tk.Frame(frame, bg=UI_BG)
        top.pack(fill="x")

        tk.Label(top, text=label_text, font=("Arial", 10, "bold"),
                 bg=UI_BG, anchor="w").pack(side="left")

        val_lbl = tk.Label(top, text="100/100", width=8,
                           font=("Arial", 9), bg=UI_BG, anchor="e")
        val_lbl.pack(side="right")

        bar = ttk.Progressbar(frame, orient="horizontal", length=280,
                              mode="determinate", maximum=100,
                              style="green.Horizontal.TProgressbar")
        bar.pack(fill="x", pady=2)

        self.status_bars[key] = {"progress": bar, "value_label": val_lbl}

    # ── Actions tab ──
    def create_actions_tab(self):
        tk.Label(self.actions_tab, text="Ações do Pet",
                 font=("Arial", 15, "bold"), bg=UI_BG, fg=UI_BTN).pack(pady=12)
        tk.Label(self.actions_tab, text="Escolha uma ação para o pet selecionado.",
                 font=("Arial", 10), bg=UI_BG, wraplength=280).pack(pady=4)

        for text, cmd in [
            ("🍗 Alimentar",  self.feed_pet),
            ("💤 Dormir",     self.sleep_pet),
            ("🛁 Banho",      self.bath_pet),
            ("🎮 Minijogos",  self.open_minigames),
            ("🛒 Loja",       self.open_shop),
            ("🎒 Inventário", self.open_inventory),
            ("💾 Salvar",     self.save_game),
        ]:
            tk.Button(self.actions_tab, text=text, width=26, height=2,
                      bg=UI_BTN, fg="white", activebackground=UI_BORDER,
                      activeforeground="white", relief="flat",
                      command=cmd).pack(pady=5)

    # ── Scenario tab ──
    def create_scenario_tab(self):
        tk.Label(self.scenario_tab, text="Trocar Cenário",
                 font=("Arial", 15, "bold"), bg=UI_BG, fg=UI_BTN).pack(pady=12)
        tk.Label(self.scenario_tab,
                 text="Cada pet pode estar em um cenário diferente.",
                 font=("Arial", 10), bg=UI_BG, wraplength=280).pack(pady=4)

        for text, scenario in [
            ("🏠 Casa",          "Casa"),
            ("🏊 Piscina",       "Piscina"),
            ("🦁 Zoo",           "Zoo"),
            ("🎤 Palco de Show", "Palco de Show"),
        ]:
            tk.Button(self.scenario_tab, text=text, width=26, height=2,
                      bg=UI_BTN, fg="white", activebackground=UI_BORDER,
                      activeforeground="white", relief="flat",
                      command=lambda s=scenario: self.change_scenario(s)).pack(pady=7)

    # ── Pets tab ──
    def create_pets_tab(self):
        tk.Label(self.pets_tab, text="Selecionar Pet",
                 font=("Arial", 15, "bold"), bg=UI_BG, fg=UI_BTN).pack(pady=(10, 2))
        tk.Label(
            self.pets_tab,
            text="Clique em um pet para ver seus\nstatus e realizar ações nele.\n"
                 "O pet selecionado fica destacado\nem rosa no cenário.",
            font=("Arial", 10), bg=UI_BG, justify="center"
        ).pack(pady=2)

        # ── Botão de troca de visual ──
        tk.Button(
            self.pets_tab,
            text="🎨  Trocar Visual",
            font=("Arial", 10, "bold"),
            bg=SELECTED_PINK, fg="white",
            activebackground="#e0006e", activeforeground="white",
            relief="flat", cursor="hand2",
            width=24, height=2,
            command=self.open_skin_window
        ).pack(pady=(6, 4))

        tk.Frame(self.pets_tab, height=2, bg=UI_BORDER).pack(fill="x", pady=6, padx=10)

        self.pet_buttons = []
        grid = tk.Frame(self.pets_tab, bg=UI_BG)
        grid.pack(pady=4)

        for index, pet in enumerate(self.party.pets):
            unlock_lvl = self.party.unlock_level_for(index)
            label = pet.name if self.party.is_unlocked(index) else f"🔒 Nv.{unlock_lvl}"

            btn = tk.Button(
                grid, text=label, width=13, height=2, font=("Arial", 10),
                command=lambda i=index: self.select_pet(i)
            )
            btn.grid(row=index // 2, column=index % 2, padx=5, pady=4)
            self.pet_buttons.append(btn)

        self.update_pet_buttons()

    def update_pet_buttons(self):
        selected = self.party.current_pet_index
        for i, btn in enumerate(self.pet_buttons):
            unlocked  = self.party.is_unlocked(i)
            unlock_lvl = self.party.unlock_level_for(i)

            btn.config(text=self.party.pets[i].name if unlocked else f"🔒 Nv.{unlock_lvl}")

            if i == selected and unlocked:
                btn.config(bg=SELECTED_PINK, activebackground=SELECTED_PINK,
                           fg="white", relief="sunken", font=("Arial", 10, "bold"))
            elif unlocked:
                btn.config(bg=UI_BTN, activebackground=UI_BORDER,
                           fg="white", relief="flat", font=("Arial", 10))
            else:
                btn.config(bg=UI_BTN, activebackground=UI_BORDER,
                           fg="white", relief="flat", font=("Arial", 10))

    # ──────────────────────────────────────────────────────────────────
    # JANELA DE TROCA DE VISUAL
    # ──────────────────────────────────────────────────────────────────
    def open_skin_window(self):
        """Abre a janela de gerenciamento de visuais alternativos."""
        win = tk.Toplevel(self.root)
        win.title("🎨 Troca de Visual")
        win.configure(bg=UI_BG)
        win.resizable(False, False)
        win.grab_set()

        # ── Cabeçalho ──
        header = tk.Frame(win, bg=UI_BG)
        header.pack(fill="x", padx=16, pady=(14, 4))

        tk.Label(header, text="🎨  Troca de Visual",
                 font=("Arial", 16, "bold"), bg=UI_BG, fg="#880E4F").pack(side="left")

        self._skin_money_lbl = tk.Label(
            header, text=f"💰 {self.party.money}",
            font=("Arial", 11, "bold"), bg=UI_BG, fg="#AD1457"
        )
        self._skin_money_lbl.pack(side="right")

        # ── Seletor de pet (dropdown) ──
        pet_frame = tk.Frame(win, bg=UI_BG)
        pet_frame.pack(fill="x", padx=16, pady=(0, 6))

        tk.Label(pet_frame, text="Pet:", font=("Arial", 10, "bold"),
                 bg=UI_BG, fg="#880E4F").pack(side="left", padx=(0, 6))

        unlocked_pets = [
            (i, pet) for i, pet in enumerate(self.party.pets)
            if self.party.is_unlocked(i)
        ]
        pet_names = [p.name for _, p in unlocked_pets]
        pet_indices = [i for i, _ in unlocked_pets]

        selected_var = tk.StringVar(value=self.pet.name)
        pet_menu = ttk.Combobox(
            pet_frame, textvariable=selected_var,
            values=pet_names, state="readonly", width=14
        )
        pet_menu.pack(side="left")

        # ── Área de scroll com cards de visual ──
        scroll_outer = tk.Frame(win, bg=UI_BG)
        scroll_outer.pack(fill="both", expand=True, padx=12, pady=4)

        scroll_canvas = tk.Canvas(scroll_outer, bg=UI_BG, highlightthickness=0, width=460)
        scrollbar = tk.Scrollbar(scroll_outer, orient="vertical",
                                  command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        cards_frame = tk.Frame(scroll_canvas, bg=UI_BG)
        win_id = scroll_canvas.create_window((0, 0), window=cards_frame, anchor="nw")

        def _on_cards_configure(e):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        def _on_canvas_configure(e):
            scroll_canvas.itemconfig(win_id, width=e.width)

        cards_frame.bind("<Configure>", _on_cards_configure)
        scroll_canvas.bind("<Configure>", _on_canvas_configure)

        def _on_wheel(e):
            scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        scroll_canvas.bind_all("<MouseWheel>", _on_wheel)
        win.protocol("WM_DELETE_WINDOW", lambda: (
            scroll_canvas.unbind_all("<MouseWheel>"), win.destroy()
        ))

        # Referência ao pet atualmente exibido na janela
        self._skin_win_pet_idx = pet_indices[
            pet_names.index(self.pet.name) if self.pet.name in pet_names else 0
        ]

        def _rebuild_cards():
            """Reconstrói os cards de visual para o pet selecionado."""
            for w in cards_frame.winfo_children():
                w.destroy()

            idx = self._skin_win_pet_idx
            pet = self.party.pets[idx]

            for sc_key in ALL_SCENARIO_KEYS:
                sc_display = SCENARIO_KEY_TO_NAME.get(sc_key, sc_key.capitalize())
                emoji = SCENARIO_EMOJI.get(sc_key, "🎨")
                info  = SKIN_UNLOCK_INFO[sc_key]
                unlocked = self.party.alt_is_unlocked(pet, sc_key)
                equipped  = self.party.alt_is_equipped(pet, sc_key)

                # ── Card de visual ──
                card = tk.Frame(cards_frame, bg=UI_BORDER, bd=0)
                card.pack(fill="x", padx=8, pady=6)

                inner = tk.Frame(card, bg=UI_BG, padx=10, pady=8)
                inner.pack(fill="x", padx=2, pady=2)

                # Cabeçalho do card
                row1 = tk.Frame(inner, bg=UI_BG)
                row1.pack(fill="x")

                tk.Label(
                    row1,
                    text=f"{emoji}  Visual de {sc_display}",
                    font=("Arial", 11, "bold"), bg=UI_BG, fg="#880E4F", anchor="w"
                ).pack(side="left")

                # Badge de status
                if unlocked:
                    status_text = "✅ Desbloqueado"
                    status_color = "#2e7d32"
                else:
                    status_text = f"🔒 {info['label']}"
                    status_color = "#888888"

                tk.Label(
                    row1, text=status_text,
                    font=("Arial", 9), bg=UI_BG, fg=status_color, anchor="e"
                ).pack(side="right")

                # Nome do arquivo de asset
                asset_name = f"{pet.asset_key}_{sc_key}_alternative.png"
                tk.Label(
                    inner,
                    text=f"📁 assets/pets/{asset_name}",
                    font=("Arial", 8), bg=UI_BG, fg="#aaaaaa", anchor="w"
                ).pack(fill="x", pady=(2, 6))

                # Pré-visualização da imagem (se disponível)
                preview_path = resource_path(f"assets/pets/{asset_name}")
                preview_img  = None
                if os.path.exists(preview_path):
                    try:
                        raw = tk.PhotoImage(file=preview_path)
                        # Reduz para caber no card (máx 80×80 visual)
                        w_img, h_img = raw.width(), raw.height()
                        sub = max(1, max(w_img, h_img) // 80)
                        preview_img = raw.subsample(sub, sub) if sub > 1 else raw
                    except tk.TclError:
                        preview_img = None

                preview_row = tk.Frame(inner, bg=UI_BG)
                preview_row.pack(fill="x", pady=(0, 4))

                if preview_img:
                    lbl_img = tk.Label(preview_row, image=preview_img, bg=UI_BG)
                    lbl_img.image = preview_img  # evita GC
                    lbl_img.pack(side="left", padx=(0, 10))
                else:
                    tk.Label(preview_row, text="🖼️\n(sem prévia)",
                             font=("Arial", 9), bg=UI_BG, fg="#bbbbbb",
                             width=8, height=3, relief="groove").pack(side="left", padx=(0, 10))

                # Botões de ação
                btn_frame = tk.Frame(preview_row, bg=UI_BG)
                btn_frame.pack(side="right", anchor="center")

                if not unlocked:
                    # Botão de desbloqueio
                    if info["type"] == "coins":
                        btn_text  = f"Comprar  {info['label']}"
                        btn_color = "#ff9800"
                        btn_cmd   = lambda p=pet, sk=sc_key: _buy_skin(p, sk)
                    else:
                        btn_text  = f"Nível {info['req']} necessário"
                        btn_color = UI_BTN
                        btn_cmd   = None

                    tk.Button(
                        btn_frame, text=btn_text,
                        font=("Arial", 9, "bold"),
                        bg=btn_color, fg="white",
                        activebackground="#e65100" if info["type"] == "coins" else UI_BORDER,
                        relief="flat", cursor="hand2" if btn_cmd else "arrow",
                        state="normal" if btn_cmd else "disabled",
                        command=btn_cmd
                    ).pack(pady=2)

                else:
                    # Equipado / Desequipado
                    if equipped:
                        tk.Button(
                            btn_frame, text="✅ Equipado  (remover)",
                            font=("Arial", 9, "bold"),
                            bg="#388e3c", fg="white",
                            activebackground="#1b5e20",
                            relief="flat", cursor="hand2",
                            command=lambda p=pet, sk=sc_key: _unequip_skin(p, sk)
                        ).pack(pady=2)
                    else:
                        tk.Button(
                            btn_frame, text="Equipar visual",
                            font=("Arial", 9, "bold"),
                            bg=SELECTED_PINK, fg="white",
                            activebackground="#880E4F",
                            relief="flat", cursor="hand2",
                            command=lambda p=pet, sk=sc_key: _equip_skin(p, sk)
                        ).pack(pady=2)

        # ── Acções dos botões ──
        def _buy_skin(pet, sc_key):
            success, msg = self.party.alt_buy(pet, sc_key)
            messagebox.showinfo("Visual", msg)
            if success:
                self._skin_money_lbl.config(text=f"💰 {self.party.money}")
                self.update_screen()
                _rebuild_cards()

        def _equip_skin(pet, sc_key):
            self.party.alt_equip(pet, sc_key)
            self.load_scene_assets()
            self.update_screen()
            _rebuild_cards()

        def _unequip_skin(pet, sc_key):
            self.party.alt_unequip(pet, sc_key)
            self.load_scene_assets()
            self.update_screen()
            _rebuild_cards()

        def _on_pet_change(event=None):
            name = selected_var.get()
            if name in pet_names:
                self._skin_win_pet_idx = pet_indices[pet_names.index(name)]
                _rebuild_cards()

        pet_menu.bind("<<ComboboxSelected>>", _on_pet_change)

        # Build inicial
        _rebuild_cards()

        # Ajusta tamanho da janela após render
        win.update_idletasks()
        content_h = cards_frame.winfo_reqheight() + 130
        screen_h  = win.winfo_screenheight()
        final_h   = min(content_h, int(screen_h * 0.88))
        win.geometry(f"490x{final_h}")

    # ──────────────────────────────────────────────────────────────────
    # Asset loading
    # ──────────────────────────────────────────────────────────────────
    def load_image(self, relative_path):
        path = resource_path(relative_path)
        if not os.path.exists(path):
            return None
        try:
            return tk.PhotoImage(file=path)
        except tk.TclError:
            return None

    def load_scene_assets(self):
        scenario_data = SCENARIOS.get(self.pet.scenario, SCENARIOS["Casa"])
        self.background_image = self.load_image(scenario_data["background"])

        self.pet_images = {}
        for i, pet in enumerate(self.party.pets):
            if not self.party.is_unlocked(i):
                self.pet_images[i] = None
                continue

            sc_data     = SCENARIOS.get(pet.scenario, SCENARIOS["Casa"])
            scenario_key = sc_data["key"]
            pet_key      = pet.asset_key

            if pet.collapsed:
                img = (self.load_image(f"assets/pets/{pet_key}_desmaio.png")
                       or self.load_image("assets/pets/pet_desmaio.png"))
            elif pet.sick:
                img = (self.load_image(f"assets/pets/{pet_key}_doente.png")
                       or self.load_image("assets/pets/pet_doente.png")
                       or self.load_image(f"assets/pets/{pet_key}_{scenario_key}.png"))
            else:
                # Usa visual alternativo se equipado para esse cenário
                skin_file = self.party.get_active_skin_key(pet, scenario_key)
                img = (self.load_image(f"assets/pets/{skin_file}.png")
                       or self.load_image(f"assets/pets/{pet_key}_{scenario_key}.png"))

            self.pet_images[i] = img

        self.draw_scene()

    # ──────────────────────────────────────────────────────────────────
    # Scene drawing
    # ──────────────────────────────────────────────────────────────────
    def draw_scene(self):
        self.canvas.delete("all")

        scenario_data = SCENARIOS.get(self.pet.scenario, SCENARIOS["Casa"])

        if self.background_image:
            self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        else:
            self.canvas.create_rectangle(
                0, 0, GAME_AREA_WIDTH, GAME_AREA_HEIGHT,
                fill=scenario_data["fallback_color"], outline=""
            )
            self.canvas.create_text(
                GAME_AREA_WIDTH // 2, 50,
                text=scenario_data["display_name"],
                font=("Arial", 28, "bold"), fill="#303030"
            )
            self.canvas.create_text(
                GAME_AREA_WIDTH // 2, 88,
                text=scenario_data["description"],
                font=("Arial", 12), fill="#303030"
            )

        selected_index = self.party.current_pet_index

        draw_order = sorted(range(len(self.party.pets)),
                            key=lambda i: self.pet_states[i]["y"])

        for i in draw_order:
            pet   = self.party.pets[i]
            state = self.pet_states[i]
            px, py = state["x"], state["y"]
            is_selected = (i == selected_index)
            unlocked    = self.party.is_unlocked(i)

            if not unlocked:
                state["canvas_highlight"] = None
                state["canvas_shadow"]    = None
                state["canvas_pet"]       = None
                state["canvas_name_outline"] = []
                state["canvas_name"]      = None
                continue

            if is_selected:
                state["canvas_highlight"] = self.canvas.create_oval(
                    px - 44, py + 52, px + 44, py + 68,
                    fill=SELECTED_PINK, outline="", stipple="gray50"
                )
            else:
                state["canvas_highlight"] = None

            state["canvas_shadow"] = self.canvas.create_oval(
                px - 35, py + 56, px + 35, py + 68,
                fill="#000000", outline="", stipple="gray50"
            )

            img = self.pet_images.get(i)
            if img:
                state["canvas_pet"] = self.canvas.create_image(
                    px, py, image=img, anchor="center"
                )
            else:
                state["canvas_pet"] = self.canvas.create_text(
                    px, py, text=self.get_fallback_pet_visual_for(pet),
                    font=("Arial", PET_SIZE_FALLBACK), anchor="center"
                )

            name_color = SELECTED_PINK if is_selected else CANVAS_NAME_NORMAL
            name_y     = py - 65

            state["canvas_name_outline"] = []
            for ox, oy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
                item = self.canvas.create_text(
                    px + ox, name_y + oy,
                    text=pet.name, font=("Arial", 13, "bold"),
                    fill=CANVAS_NAME_OUTLINE
                )
                state["canvas_name_outline"].append(item)

            state["canvas_name"] = self.canvas.create_text(
                px, name_y, text=pet.name,
                font=("Arial", 13, "bold"), fill=name_color
            )

        self.canvas.create_rectangle(
            0, GAME_AREA_HEIGHT - 34, GAME_AREA_WIDTH, GAME_AREA_HEIGHT,
            fill="#000000", outline="", stipple="gray50"
        )
        self.canvas.create_text(
            15, GAME_AREA_HEIGHT - 18,
            text=f"Cenário: {self.pet.scenario}  |  Visualizando: {self.pet.name}",
            font=("Arial", 11, "bold"), fill="#ffffff", anchor="w"
        )

    # ──────────────────────────────────────────────────────────────────
    # Animation
    # ──────────────────────────────────────────────────────────────────
    def animate_pet(self):
        draw_order = sorted(range(len(self.party.pets)),
                            key=lambda i: self.pet_states[i]["y"])

        for i in draw_order:
            pet   = self.party.pets[i]
            state = self.pet_states[i]

            if not self.party.is_unlocked(i):
                continue

            if not pet.collapsed:
                state["walk_phase"] += 0.25
                vertical_bob = math.sin(state["walk_phase"]) * 5

                state["x"] += state["vx"]
                state["y"] += state["vy"]

                min_x, max_x = PET_AREA_MARGIN, GAME_AREA_WIDTH - PET_AREA_MARGIN
                min_y, max_y = 130, GAME_AREA_HEIGHT - 90

                if state["x"] <= min_x or state["x"] >= max_x: state["vx"] *= -1
                if state["y"] <= min_y or state["y"] >= max_y: state["vy"] *= -1

                state["x"] = max(min_x, min(max_x, state["x"]))
                state["y"] = max(min_y, min(max_y, state["y"]))

                state["frames_until_change"] -= 1
                if state["frames_until_change"] <= 0:
                    state["vx"] = random.choice([-2, -1, 1, 2])
                    state["vy"] = random.choice([-1, 0, 1])
                    if state["vy"] == 0 and random.random() < 0.5:
                        state["vy"] = random.choice([-1, 1])
                    state["frames_until_change"] = random.randint(35, 90)

                display_y = state["y"] + vertical_bob
            else:
                display_y = state["y"]

            px = state["x"]

            if state["canvas_highlight"]:
                self.canvas.coords(state["canvas_highlight"],
                    px - 44, state["y"] + 52, px + 44, state["y"] + 68)
            if state["canvas_shadow"]:
                self.canvas.coords(state["canvas_shadow"],
                    px - 35, state["y"] + 56, px + 35, state["y"] + 68)
            if state["canvas_pet"]:
                self.canvas.coords(state["canvas_pet"], px, display_y)

            if state.get("canvas_name_outline"):
                name_y  = display_y - 68
                offsets = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
                for item, (ox, oy) in zip(state["canvas_name_outline"], offsets):
                    self.canvas.coords(item, px + ox, name_y + oy)

            if state["canvas_name"]:
                self.canvas.coords(state["canvas_name"], px, display_y - 68)

            for item_key in ("canvas_highlight", "canvas_shadow", "canvas_pet",
                             "canvas_name_outline", "canvas_name"):
                items = state.get(item_key)
                if isinstance(items, list):
                    for it in items: self.canvas.tag_raise(it)
                elif items:
                    self.canvas.tag_raise(items)

        self.root.after(35, self.animate_pet)

    # ──────────────────────────────────────────────────────────────────
    # Fallbacks
    # ──────────────────────────────────────────────────────────────────
    def get_fallback_pet_visual_for(self, pet):
        if pet.collapsed: return "😵"
        if pet.sick:      return "🤒"
        return {
            "felix": "🐱", "bangchan": "🐺", "hyunjin": "🦙",
            "han": "🐿️", "changbin": "🐷", "leeknow": "🐰",
            "in": "🦊", "seungmin": "🐶",
        }.get(pet.asset_key, "🐣")

    # ──────────────────────────────────────────────────────────────────
    # Screen update
    # ──────────────────────────────────────────────────────────────────
    def get_progress_style(self, value):
        if value >= 60: return "green.Horizontal.TProgressbar"
        if value >= 30: return "yellow.Horizontal.TProgressbar"
        return "red.Horizontal.TProgressbar"

    def update_status_bar(self, key, value):
        bd = self.status_bars[key]
        bd["progress"]["value"] = value
        bd["progress"].configure(style=self.get_progress_style(value))
        bd["value_label"].config(text=f"{value}/100")

    def update_screen(self):
        xp_cur, xp_next = self.party.xp_progress()
        xp_pct = int((xp_cur / xp_next) * 100) if xp_next else 0
        self.level_label.config(text=f"⭐ Nível {self.party.level}")
        self.money_label.config(text=f"💰 {self.party.money}")
        self.xp_bar["value"] = xp_pct
        self.xp_label.config(text=f"XP: {xp_cur} / {xp_next}")

        self.pet_label.config(text=self.pet.name)

        if self.pet.collapsed:
            estado = "Incapacitado"
        elif self.pet.sick:
            estado = "Doente"
        else:
            estado = "Normal"

        self.info_label.config(
            text=estado,
            font=("Arial", 10),
            fg="#666666"
        )

        for key in ("hunger", "happiness", "energy", "hygiene", "health"):
            self.update_status_bar(key, getattr(self.pet, key))

    def refresh_after_action(self, gain_xp=10):
        leveled_up = False
        if gain_xp:
            leveled_up = self.party.add_xp(gain_xp)
        self.pet.update_condition()
        self.load_scene_assets()
        self.update_screen()
        self.update_pet_buttons()
        if leveled_up:
            self._on_level_up()

    def _on_level_up(self):
        # Desbloqueia visuais por nível
        self.party.alt_unlock_by_level()

        next_info = self.party.next_unlock()
        msg = f"Você chegou ao Nível {self.party.level}! 🎉"
        for i in range(len(self.party.pets)):
            if self.party.unlock_level_for(i) == self.party.level:
                msg += f"\n\n{self.party.pets[i].name} foi desbloqueado!"
        for sc_key, req in SKIN_LEVEL_UNLOCK.items():
            if req == self.party.level:
                sc_name = SCENARIO_KEY_TO_NAME.get(sc_key, sc_key.capitalize())
                msg += f"\n\n🎨 Visual de {sc_name} desbloqueado para todos os pets!"
        if next_info:
            name, lvl = next_info
            msg += f"\n\nPróximo pet: {name} no Nível {lvl}."
        messagebox.showinfo("Nível Up!", msg)

    # ──────────────────────────────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────────────────────────────
    def feed_pet(self):
        messagebox.showinfo("Ação", self.pet.feed())
        self.refresh_after_action(gain_xp=8)

    def sleep_pet(self):
        messagebox.showinfo("Ação", self.pet.sleep())
        self.refresh_after_action(gain_xp=5)

    def bath_pet(self):
        messagebox.showinfo("Ação", self.pet.bath())
        self.refresh_after_action(gain_xp=5)

    def open_minigames(self):
        if self.pet.energy < 10:
            messagebox.showwarning("Minijogos",
                f"{self.pet.name} está cansado demais para jogar!")
            return
        open_minigame_selector(self.root, self.pet, self.party, self._on_minigame_finish)

    def _on_minigame_finish(self, coins, result, happiness=0, xp=0):
        leveled_up = self.party.add_xp(xp) if xp else False
        self.pet.update_condition()
        self.load_scene_assets()
        self.update_screen()
        self.update_pet_buttons()
        messagebox.showinfo("Minijogo",
            f"{result}\n+{coins} moedas!\n+{happiness} felicidade\n+{xp} XP")
        if leveled_up:
            self._on_level_up()

    def change_scenario(self, scenario):
        self.pet.change_scenario(scenario)
        self.load_scene_assets()
        self.update_screen()

    def open_shop(self):
        w = tk.Toplevel(self.root)
        w.title("Loja")
        w.geometry("460x520")
        w.resizable(False, False)
        w.configure(bg=UI_BG)

        tk.Label(w, text=f"Loja — Moedas: {self.party.money}",
                 font=("Arial", 15, "bold"), bg=UI_BG, fg=UI_BTN).pack(pady=10)

        for index, item in enumerate(self.shop.list_items()):
            tk.Button(
                w,
                text=f"{item.name} - {item.price} moedas\n{item.description}",
                width=48, height=3,
                bg=UI_BTN, fg="white", activebackground=UI_BORDER,
                activeforeground="white", relief="flat",
                command=lambda i=index: self.buy_item(i, w)
            ).pack(pady=4)

    def buy_item(self, item_index, window):
        item = self.shop.list_items()[item_index]
        if self.party.money < item.price:
            messagebox.showwarning("Compra", "Moedas insuficientes.")
            window.destroy()
            return
        self.party.money -= item.price
        self.pet.inventory.append(item.name)
        messagebox.showinfo("Compra", f"{self.pet.name} comprou {item.name}.")
        window.destroy()
        self.refresh_after_action(gain_xp=0)

    def open_inventory(self):
        w = tk.Toplevel(self.root)
        w.title("Inventário")
        w.geometry("380x420")
        w.resizable(False, False)
        w.configure(bg=UI_BG)

        tk.Label(w, text="Inventário", font=("Arial", 16, "bold"),
                 bg=UI_BG, fg=UI_BTN).pack(pady=10)

        if not self.pet.inventory:
            tk.Label(w, text="Inventário vazio.", font=("Arial", 13),
                     bg=UI_BG).pack(pady=20)
            return

        for item_name in self.pet.inventory:
            tk.Button(
                w, text=f"Usar {item_name}", width=34, height=2,
                bg=UI_BTN, fg="white", activebackground=UI_BORDER,
                activeforeground="white", relief="flat",
                command=lambda n=item_name: self.use_inventory_item(n, w)
            ).pack(pady=5)

    def use_inventory_item(self, item_name, window):
        item = self.shop.get_item_by_name(item_name)
        if item is None:
            messagebox.showwarning("Erro", "Item não encontrado.")
            return
        message = self.pet.use_item(item)
        if item_name in self.pet.inventory:
            self.pet.inventory.remove(item_name)
        messagebox.showinfo("Inventário", message)
        window.destroy()
        self.refresh_after_action(gain_xp=3)

    def save_game(self):
        SaveManager.save_game(self.party)
        messagebox.showinfo("Salvar", "Jogo salvo com sucesso.")

    def select_pet(self, index):
        if not self.party.is_unlocked(index):
            unlock_lvl = self.party.unlock_level_for(index)
            messagebox.showinfo(
                "Pet bloqueado",
                f"{self.party.pets[index].name} será desbloqueado no Nível {unlock_lvl}.\n"
                f"Seu nível atual: {self.party.level}."
            )
            return
        self.party.select_pet(index)
        self.pet = self.party.get_current_pet()
        self.load_scene_assets()
        self.update_screen()
        self.update_pet_buttons()