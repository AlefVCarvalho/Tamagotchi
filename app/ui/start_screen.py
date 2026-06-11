import tkinter as tk

from app.ui.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    START_BACKGROUND,
    UI_BG,
    UI_BTN,
    UI_BORDER,
    SELECTED_PINK,
)
from app.ui.utils import load_photo


class StartScreen:
    def __init__(self, root, has_save, on_new_game, on_continue, on_delete_save):
        self.root = root
        self.has_save = has_save
        self.on_new_game = on_new_game
        self.on_continue = on_continue
        self.on_delete_save = on_delete_save
        self.bg_image = None

        self.frame = tk.Frame(root, bg=UI_BG)
        self.frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.frame,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0,
            bg=UI_BG,
        )
        self.canvas.pack(fill="both", expand=True)

        self._draw_background()
        self._draw_menu()

    def destroy(self):
        self.frame.destroy()

    def _draw_background(self):
        self.bg_image = load_photo(START_BACKGROUND)
        if self.bg_image:
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        else:
            self.canvas.create_rectangle(
                0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
                fill=UI_BG, outline=""
            )
            self.canvas.create_text(
                WINDOW_WIDTH // 2,
                115,
                text="Skz Mini Tamagotchi",
                font=("Arial", 34, "bold"),
                fill=SELECTED_PINK,
            )
            self.canvas.create_text(
                WINDOW_WIDTH // 2,
                160,
                text="Crie assets/backgrounds/start.png para personalizar esta tela.",
                font=("Arial", 13),
                fill="#880E4F",
            )

    def _draw_menu(self):
        panel = tk.Frame(self.canvas, bg=UI_BG, padx=22, pady=18)
        self.canvas.create_window(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 105,
            window=panel,
            anchor="center",
        )

        title = tk.Label(
            panel,
            text="Menu Inicial",
            font=("Arial", 18, "bold"),
            bg=UI_BG,
            fg="#880E4F",
        )
        title.pack(pady=(0, 10))

        tk.Button(
            panel,
            text="Novo jogo",
            width=24,
            height=2,
            bg=SELECTED_PINK,
            fg="white",
            activebackground="#e0006e",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.on_new_game,
        ).pack(pady=5)

        continue_state = "normal" if self.has_save else "disabled"
        tk.Button(
            panel,
            text="Continuar" if self.has_save else "Continuar (sem save)",
            width=24,
            height=2,
            bg=UI_BTN,
            fg="white",
            disabledforeground="#f5d6e1",
            activebackground=UI_BORDER,
            activeforeground="white",
            relief="flat",
            cursor="hand2" if self.has_save else "arrow",
            state=continue_state,
            command=self.on_continue,
        ).pack(pady=5)

        tk.Button(
            panel,
            text="Apagar save",
            width=24,
            height=2,
            bg="#AD1457",
            fg="white",
            disabledforeground="#f5d6e1",
            activebackground="#880E4F",
            activeforeground="white",
            relief="flat",
            cursor="hand2" if self.has_save else "arrow",
            state=continue_state,
            command=self.on_delete_save,
        ).pack(pady=5)
