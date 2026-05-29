import os
import sys
import math
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from app.core.pet_party import PetParty
from app.core.shop import Shop
from app.core.save_manager import SaveManager


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 560

GAME_AREA_WIDTH = 620
GAME_AREA_HEIGHT = 460

PET_AREA_MARGIN = 55
PET_SIZE_FALLBACK = 70


SCENARIOS = {
    "Casa": {
        "key": "casa",
        "display_name": "Casa",
        "background": "assets/backgrounds/casa.png",
        "pet_image": "assets/pets/pet_casa.png",
        "fallback_color": "#f5deb3",
        "fallback_pet": "🐣",
        "description": "Um lugar confortável para descansar.",
    },
    "Piscina": {
        "key": "piscina",
        "display_name": "Piscina",
        "background": "assets/backgrounds/piscina.png",
        "pet_image": "assets/pets/pet_piscina.png",
        "fallback_color": "#87ceeb",
        "fallback_pet": "🐧",
        "description": "Um cenário divertido e refrescante.",
    },
    "Zoo": {
        "key": "zoo",
        "display_name": "Zoo",
        "background": "assets/backgrounds/zoo.png",
        "pet_image": "assets/pets/pet_zoo.png",
        "fallback_color": "#98fb98",
        "fallback_pet": "🐵",
        "description": "Um passeio cheio de animais.",
    },
    "Palco de Show": {
        "key": "palco",
        "display_name": "Palco de Show",
        "background": "assets/backgrounds/palco.png",
        "pet_image": "assets/pets/pet_palco.png",
        "fallback_color": "#dda0dd",
        "fallback_pet": "🎤",
        "description": "Luzes, música e muita animação.",
    },
}


def resource_path(relative_path):
    """
    Ajuda o app a encontrar imagens tanto rodando pelo Python
    quanto depois de empacotado com PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class TamagotchiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Tamagotchi")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.shop = Shop()
        self.party = SaveManager.load_game()

        if self.party is None:
            self.party = PetParty()

        self.pet = self.party.get_current_pet()

        self.background_image = None
        self.pet_image = None
        self.background_canvas_item = None
        self.pet_canvas_item = None
        self.shadow_canvas_item = None
        self.pet_name_canvas_item = None

        self.pet_x = GAME_AREA_WIDTH // 2
        self.pet_y = GAME_AREA_HEIGHT // 2
        self.pet_vx = random.choice([-2, -1, 1, 2])
        self.pet_vy = random.choice([-1, 1])
        self.walk_phase = 0
        self.frames_until_direction_change = 45

        self.status_bars = {}

        self.setup_styles()
        self.create_widgets()
        self.load_scene_assets()
        self.update_screen()
        self.animate_pet()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("default")

        self.style.configure(
            "green.Horizontal.TProgressbar",
            troughcolor="#dddddd",
            background="#4caf50",
            thickness=18
        )

        self.style.configure(
            "yellow.Horizontal.TProgressbar",
            troughcolor="#dddddd",
            background="#ffc107",
            thickness=18
        )

        self.style.configure(
            "red.Horizontal.TProgressbar",
            troughcolor="#dddddd",
            background="#f44336",
            thickness=18
        )

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg="#202020")
        self.main_frame.pack(fill="both", expand=True)

        self.game_frame = tk.Frame(self.main_frame, bg="#202020", padx=15, pady=15)
        self.game_frame.pack(side="left", fill="both")

        self.side_frame = tk.Frame(self.main_frame, width=350, bg="#f2f2f2", padx=18, pady=15)
        self.side_frame.pack(side="right", fill="y")
        self.side_frame.pack_propagate(False)

        self.create_game_area()
        self.create_side_panel()

    def create_game_area(self):
        self.canvas = tk.Canvas(
            self.game_frame,
            width=GAME_AREA_WIDTH,
            height=GAME_AREA_HEIGHT,
            highlightthickness=0,
            bg="#000000"
        )
        self.canvas.pack()

    def create_side_panel(self):
        self.title_label = tk.Label(
            self.side_frame,
            text="Mini Tamagotchi",
            font=("Arial", 20, "bold"),
            bg="#f2f2f2"
        )
        self.title_label.pack(pady=5)

        self.tabs = ttk.Notebook(self.side_frame)
        self.tabs.pack(fill="both", expand=True, pady=5)

        self.status_tab = tk.Frame(self.tabs, bg="#f2f2f2")
        self.actions_tab = tk.Frame(self.tabs, bg="#f2f2f2")
        self.scenario_tab = tk.Frame(self.tabs, bg="#f2f2f2")

        self.tabs.add(self.status_tab, text="Status")
        self.tabs.add(self.actions_tab, text="Ações")
        self.tabs.add(self.scenario_tab, text="Cenário")

        self.create_status_tab()
        self.create_actions_tab()
        self.create_scenario_tab()

    def create_status_tab(self):
        self.pet_label = tk.Label(
            self.status_tab,
            text="",
            font=("Arial", 13, "bold"),
            bg="#f2f2f2",
            wraplength=300
        )
        self.pet_label.pack(pady=8)

        self.info_label = tk.Label(
            self.status_tab,
            text="",
            font=("Arial", 10),
            bg="#f2f2f2",
            justify="center"
        )
        self.info_label.pack(pady=5)

        self.status_frame = tk.Frame(self.status_tab, bg="#f2f2f2")
        self.status_frame.pack(fill="x", pady=10, padx=8)

        self.create_status_bar("Fome", "hunger")
        self.create_status_bar("Felicidade", "happiness")
        self.create_status_bar("Energia", "energy")
        self.create_status_bar("Higiene", "hygiene")
        self.create_status_bar("Saúde", "health")

        separator = tk.Frame(self.status_tab, height=2, bg="#cccccc")
        separator.pack(fill="x", pady=8)

        self.create_pet_selector(parent=self.status_tab)

    def create_actions_tab(self):
        actions_title = tk.Label(
            self.actions_tab,
            text="Ações do Pet",
            font=("Arial", 15, "bold"),
            bg="#f2f2f2"
        )
        actions_title.pack(pady=12)

        actions_description = tk.Label(
            self.actions_tab,
            text="Escolha uma ação para o pet selecionado.",
            font=("Arial", 10),
            bg="#f2f2f2",
            wraplength=280
        )
        actions_description.pack(pady=4)

        buttons = [
            ("🍗 Alimentar", self.feed_pet),
            ("🎾 Brincar", self.play_pet),
            ("💤 Dormir", self.sleep_pet),
            ("🛁 Banho", self.bath_pet),
            ("💼 Trabalhar", self.work),
            ("🛒 Loja", self.open_shop),
            ("🎒 Inventário", self.open_inventory),
            ("💾 Salvar", self.save_game),
        ]

        for text, command in buttons:
            button = tk.Button(
                self.actions_tab,
                text=text,
                width=26,
                height=2,
                command=command
            )
            button.pack(pady=5)

    def create_scenario_tab(self):
        scenario_title = tk.Label(
            self.scenario_tab,
            text="Trocar Cenário",
            font=("Arial", 15, "bold"),
            bg="#f2f2f2"
        )
        scenario_title.pack(pady=12)

        scenario_description = tk.Label(
            self.scenario_tab,
            text="Cada pet pode estar em um cenário diferente.",
            font=("Arial", 10),
            bg="#f2f2f2",
            wraplength=280
        )
        scenario_description.pack(pady=4)

        scenario_buttons = [
            ("🏠 Casa", "Casa"),
            ("🏊 Piscina", "Piscina"),
            ("🦁 Zoo", "Zoo"),
            ("🎤 Palco de Show", "Palco de Show"),
        ]

        for text, scenario in scenario_buttons:
            button = tk.Button(
                self.scenario_tab,
                text=text,
                width=26,
                height=2,
                command=lambda selected=scenario: self.change_scenario(selected)
            )
            button.pack(pady=7)
    def create_status_bar(self, label_text, key):
        frame = tk.Frame(self.status_frame, bg="#f2f2f2")
        frame.pack(fill="x", pady=5)

        top_line = tk.Frame(frame, bg="#f2f2f2")
        top_line.pack(fill="x")

        label = tk.Label(
            top_line,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg="#f2f2f2",
            anchor="w"
        )
        label.pack(side="left")

        value_label = tk.Label(
            top_line,
            text="100/100",
            width=8,
            font=("Arial", 9),
            bg="#f2f2f2",
            anchor="e"
        )
        value_label.pack(side="right")

        progress = ttk.Progressbar(
            frame,
            orient="horizontal",
            length=280,
            mode="determinate",
            maximum=100,
            style="green.Horizontal.TProgressbar"
        )
        progress.pack(fill="x", pady=2)

        self.status_bars[key] = {
            "progress": progress,
            "value_label": value_label,
        }

    def load_image(self, relative_path):
        path = os.path.abspath(relative_path)

        if not os.path.exists(path):
            return None

        try:
            return tk.PhotoImage(file=path)
        except tk.TclError:
            return None

    def load_scene_assets(self):
        scenario_data = SCENARIOS.get(self.pet.scenario, SCENARIOS["Casa"])

        self.background_image = self.load_image(scenario_data["background"])

        scenario_key = scenario_data["key"]
        pet_key = self.pet.asset_key

        if self.pet.collapsed:
            self.pet_image = (
                self.load_image(f"assets/pets/{pet_key}_desmaio.png")
                or self.load_image("assets/pets/pet_desmaio.png")
            )
        elif self.pet.sick:
            self.pet_image = (
                self.load_image(f"assets/pets/{pet_key}_doente.png")
                or self.load_image("assets/pets/pet_doente.png")
                or self.load_image(f"assets/pets/{pet_key}_{scenario_key}.png")
            )
        else:
            self.pet_image = self.load_image(f"assets/pets/{pet_key}_{scenario_key}.png")

        self.draw_scene()

    def draw_scene(self):
        self.canvas.delete("all")

        scenario_data = SCENARIOS.get(self.pet.scenario, SCENARIOS["Casa"])

        if self.background_image:
            self.background_canvas_item = self.canvas.create_image(
                0,
                0,
                image=self.background_image,
                anchor="nw"
            )
        else:
            self.canvas.create_rectangle(
                0,
                0,
                GAME_AREA_WIDTH,
                GAME_AREA_HEIGHT,
                fill=scenario_data["fallback_color"],
                outline=""
            )

            self.canvas.create_text(
                GAME_AREA_WIDTH // 2,
                50,
                text=scenario_data["display_name"],
                font=("Arial", 28, "bold"),
                fill="#303030"
            )

            self.canvas.create_text(
                GAME_AREA_WIDTH // 2,
                88,
                text=scenario_data["description"],
                font=("Arial", 12),
                fill="#303030"
            )

        self.shadow_canvas_item = self.canvas.create_oval(
            self.pet_x - 35,
            self.pet_y + 34,
            self.pet_x + 35,
            self.pet_y + 45,
            fill="#000000",
            outline="",
            stipple="gray50"
        )

        if self.pet_image:
            self.pet_canvas_item = self.canvas.create_image(
                self.pet_x,
                self.pet_y,
                image=self.pet_image,
                anchor="center"
            )
        else:
            self.pet_canvas_item = self.canvas.create_text(
                self.pet_x,
                self.pet_y,
                text=self.get_fallback_pet_visual(),
                font=("Arial", PET_SIZE_FALLBACK),
                anchor="center"
            )

        self.pet_name_canvas_item = self.canvas.create_text(
            self.pet_x,
            self.pet_y - 65,
            text=self.pet.name,
            font=("Arial", 13, "bold"),
            fill="#ffffff"
        )

        self.canvas.create_rectangle(
            0,
            GAME_AREA_HEIGHT - 34,
            GAME_AREA_WIDTH,
            GAME_AREA_HEIGHT,
            fill="#000000",
            outline="",
            stipple="gray50"
        )

        self.canvas.create_text(
            15,
            GAME_AREA_HEIGHT - 18,
            text=f"Cenário: {self.pet.scenario}",
            font=("Arial", 11, "bold"),
            fill="#ffffff",
            anchor="w"
        )

    def get_fallback_pet_visual(self):
        if self.pet.collapsed:
            return "😵"

        if self.pet.sick:
            return "🤒"

        fallback_by_pet = {
            "felix": "🐱",
            "bangchan": "🐺",
            "hyunjin": "🦙",
            "han": "🐿️",
            "changbin": "🐷",
            "leeknow": "🐰",
            "in": "🦊",
            "seungmin": "🐶",
        }

        return fallback_by_pet.get(self.pet.asset_key, "🐣")

    def animate_pet(self):
        if not self.pet.collapsed:
            self.walk_phase += 0.25
            vertical_bob = math.sin(self.walk_phase) * 5

            self.pet_x += self.pet_vx
            self.pet_y += self.pet_vy

            min_x = PET_AREA_MARGIN
            max_x = GAME_AREA_WIDTH - PET_AREA_MARGIN
            min_y = 130
            max_y = GAME_AREA_HEIGHT - 90

            if self.pet_x <= min_x or self.pet_x >= max_x:
                self.pet_vx *= -1

            if self.pet_y <= min_y or self.pet_y >= max_y:
                self.pet_vy *= -1

            self.pet_x = max(min_x, min(max_x, self.pet_x))
            self.pet_y = max(min_y, min(max_y, self.pet_y))

            self.frames_until_direction_change -= 1

            if self.frames_until_direction_change <= 0:
                self.randomize_pet_direction()
                self.frames_until_direction_change = random.randint(35, 90)

            display_y = self.pet_y + vertical_bob
        else:
            display_y = self.pet_y

        if self.shadow_canvas_item:
            self.canvas.coords(
                self.shadow_canvas_item,
                self.pet_x - 38,
                self.pet_y + 38,
                self.pet_x + 38,
                self.pet_y + 48
            )

        if self.pet_canvas_item:
            self.canvas.coords(
                self.pet_canvas_item,
                self.pet_x,
                display_y
            )

        if self.pet_name_canvas_item:
            self.canvas.coords(
                self.pet_name_canvas_item,
                self.pet_x,
                display_y - 68
            )

        self.root.after(35, self.animate_pet)

    def randomize_pet_direction(self):
        possible_speeds = [-2, -1, 1, 2]

        self.pet_vx = random.choice(possible_speeds)
        self.pet_vy = random.choice([-1, 0, 1])

        if self.pet_vy == 0 and random.random() < 0.5:
            self.pet_vy = random.choice([-1, 1])

    def get_progress_style(self, value):
        if value >= 60:
            return "green.Horizontal.TProgressbar"

        if value >= 30:
            return "yellow.Horizontal.TProgressbar"

        return "red.Horizontal.TProgressbar"

    def update_status_bar(self, key, value):
        bar_data = self.status_bars[key]
        progress = bar_data["progress"]
        value_label = bar_data["value_label"]

        progress["value"] = value
        progress.configure(style=self.get_progress_style(value))
        value_label.config(text=f"{value}/100")

    def update_screen(self):
        self.pet_label.config(
            text=f"{self.pet.name} - {self.pet.get_stage()} - {self.pet.get_mood()}"
        )

        self.info_label.config(
            text=(
                f"Idade: {self.pet.age} turnos\n"
                f"Moedas: {self.pet.money}\n"
                f"Doente: {'Sim' if self.pet.sick else 'Não'}\n"
                f"Estado: {'Desmaiado' if self.pet.collapsed else 'Ativo'}"
            )
        )

        self.update_status_bar("hunger", self.pet.hunger)
        self.update_status_bar("happiness", self.pet.happiness)
        self.update_status_bar("energy", self.pet.energy)
        self.update_status_bar("hygiene", self.pet.hygiene)
        self.update_status_bar("health", self.pet.health)

    def refresh_after_action(self):
        self.pet.update_condition()
        self.load_scene_assets()
        self.update_screen()

    def feed_pet(self):
        message = self.pet.feed()
        messagebox.showinfo("Ação", message)
        self.refresh_after_action()

    def play_pet(self):
        message = self.pet.play()
        messagebox.showinfo("Ação", message)
        self.refresh_after_action()

    def sleep_pet(self):
        message = self.pet.sleep()
        messagebox.showinfo("Ação", message)
        self.refresh_after_action()

    def bath_pet(self):
        message = self.pet.bath()
        messagebox.showinfo("Ação", message)
        self.refresh_after_action()

    def work(self):
        message = self.pet.work()
        messagebox.showinfo("Trabalho", message)
        self.refresh_after_action()

    def change_scenario(self, scenario):
        self.pet.change_scenario(scenario)
        self.load_scene_assets()
        self.update_screen()

    def open_shop(self):
        shop_window = tk.Toplevel(self.root)
        shop_window.title("Loja")
        shop_window.geometry("460x520")
        shop_window.resizable(False, False)

        label = tk.Label(
            shop_window,
            text=f"Loja - Moedas: {self.pet.money}",
            font=("Arial", 15, "bold")
        )
        label.pack(pady=10)

        for index, item in enumerate(self.shop.list_items()):
            text = f"{item.name} - {item.price} moedas\n{item.description}"

            button = tk.Button(
                shop_window,
                text=text,
                width=48,
                height=3,
                command=lambda i=index: self.buy_item(i, shop_window)
            )
            button.pack(pady=4)

    def buy_item(self, item_index, window):
        success, message = self.shop.buy_item(self.pet, item_index)

        if success:
            messagebox.showinfo("Compra", message)
        else:
            messagebox.showwarning("Compra", message)

        window.destroy()
        self.refresh_after_action()

    def open_inventory(self):
        inventory_window = tk.Toplevel(self.root)
        inventory_window.title("Inventário")
        inventory_window.geometry("380x420")
        inventory_window.resizable(False, False)

        title = tk.Label(
            inventory_window,
            text="Inventário",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)

        if not self.pet.inventory:
            label = tk.Label(
                inventory_window,
                text="Inventário vazio.",
                font=("Arial", 13)
            )
            label.pack(pady=20)
            return

        for item_name in self.pet.inventory:
            button = tk.Button(
                inventory_window,
                text=f"Usar {item_name}",
                width=34,
                height=2,
                command=lambda name=item_name: self.use_inventory_item(name, inventory_window)
            )
            button.pack(pady=5)

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
        self.refresh_after_action()

    def save_game(self):
        SaveManager.save_game(self.party)
        messagebox.showinfo("Salvar", "Jogo salvo com sucesso.")

    def select_pet(self, index):
        self.party.select_pet(index)
        self.pet = self.party.get_current_pet()

        self.pet_x = GAME_AREA_WIDTH // 2
        self.pet_y = GAME_AREA_HEIGHT // 2

        self.load_scene_assets()
        self.update_screen()

    def create_pet_selector(self, parent):
        selector_title = tk.Label(
            parent,
            text="Pets",
            font=("Arial", 15, "bold"),
            bg="#f2f2f2"
        )
        selector_title.pack(pady=3)

        selector_grid = tk.Frame(parent, bg="#f2f2f2")
        selector_grid.pack()

        for index, pet in enumerate(self.party.pets):
            button = tk.Button(
                selector_grid,
                text=pet.name,
                width=14,
                command=lambda i=index: self.select_pet(i)
            )
            button.grid(row=index // 2, column=index % 2, padx=4, pady=3)
