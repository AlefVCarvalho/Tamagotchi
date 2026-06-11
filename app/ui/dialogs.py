import os
import tkinter as tk
from tkinter import messagebox, ttk

from app.core.pet_party import ALL_SCENARIO_KEYS
from app.ui.config import (
    SCENARIO_EMOJI,
    SCENARIO_KEY_TO_NAME,
    SELECTED_PINK,
    SKIN_UNLOCK_INFO,
    UI_BG,
    UI_BORDER,
    UI_BTN,
)
from app.ui.utils import resource_path


class DialogsMixin:
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

        header = tk.Frame(win, bg=UI_BG)
        header.pack(fill="x", padx=16, pady=(14, 4))

        tk.Label(
            header,
            text="🎨  Troca de Visual",
            font=("Arial", 16, "bold"),
            bg=UI_BG,
            fg="#880E4F",
        ).pack(side="left")

        self._skin_money_lbl = tk.Label(
            header,
            text=f"💰 {self.party.money}",
            font=("Arial", 11, "bold"),
            bg=UI_BG,
            fg="#AD1457",
        )
        self._skin_money_lbl.pack(side="right")

        info = tk.Label(
            win,
            text=(
                "O cenário é global. Equipar um visual não troca o fundo; "
                "ele só aparece quando o cenário global correspondente estiver ativo."
            ),
            font=("Arial", 9),
            bg=UI_BG,
            fg="#880E4F",
            wraplength=450,
            justify="center",
        )
        info.pack(fill="x", padx=16, pady=(0, 6))

        pet_frame = tk.Frame(win, bg=UI_BG)
        pet_frame.pack(fill="x", padx=16, pady=(0, 6))

        tk.Label(
            pet_frame,
            text="Pet:",
            font=("Arial", 10, "bold"),
            bg=UI_BG,
            fg="#880E4F",
        ).pack(side="left", padx=(0, 6))

        unlocked_pets = [(i, pet) for i, pet in enumerate(self.party.pets) if self.party.is_unlocked(i)]
        pet_names = [p.name for _, p in unlocked_pets]
        pet_indices = [i for i, _ in unlocked_pets]

        selected_var = tk.StringVar(value=self.pet.name)
        pet_menu = ttk.Combobox(
            pet_frame,
            textvariable=selected_var,
            values=pet_names,
            state="readonly",
            width=14,
        )
        pet_menu.pack(side="left")

        current_scenario = self.party.get_current_scenario()
        current_scenario_key = self.party.get_current_scenario_key()
        tk.Label(
            pet_frame,
            text=f"Cenário atual: {current_scenario}",
            font=("Arial", 9, "bold"),
            bg=UI_BG,
            fg=SELECTED_PINK,
        ).pack(side="right")

        scroll_outer = tk.Frame(win, bg=UI_BG)
        scroll_outer.pack(fill="both", expand=True, padx=12, pady=4)

        scroll_canvas = tk.Canvas(scroll_outer, bg=UI_BG, highlightthickness=0, width=460)
        scrollbar = tk.Scrollbar(scroll_outer, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        cards_frame = tk.Frame(scroll_canvas, bg=UI_BG)
        win_id = scroll_canvas.create_window((0, 0), window=cards_frame, anchor="nw")

        def _on_cards_configure(_event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        def _on_canvas_configure(event):
            scroll_canvas.itemconfig(win_id, width=event.width)

        cards_frame.bind("<Configure>", _on_cards_configure)
        scroll_canvas.bind("<Configure>", _on_canvas_configure)

        def _on_wheel(event):
            scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        scroll_canvas.bind_all("<MouseWheel>", _on_wheel)
        win.protocol("WM_DELETE_WINDOW", lambda: (scroll_canvas.unbind_all("<MouseWheel>"), win.destroy()))

        self._skin_win_pet_idx = pet_indices[pet_names.index(self.pet.name) if self.pet.name in pet_names else 0]

        def _rebuild_cards():
            for widget in cards_frame.winfo_children():
                widget.destroy()

            idx = self._skin_win_pet_idx
            pet = self.party.pets[idx]

            for sc_key in ALL_SCENARIO_KEYS:
                sc_display = SCENARIO_KEY_TO_NAME.get(sc_key, sc_key.capitalize())
                emoji = SCENARIO_EMOJI.get(sc_key, "🎨")
                info_data = SKIN_UNLOCK_INFO[sc_key]
                unlocked = self.party.alt_is_unlocked(pet, sc_key)
                equipped = self.party.alt_is_equipped(pet, sc_key)
                visible_now = equipped and sc_key == current_scenario_key

                card = tk.Frame(cards_frame, bg=UI_BORDER, bd=0)
                card.pack(fill="x", padx=8, pady=6)

                inner = tk.Frame(card, bg=UI_BG, padx=10, pady=8)
                inner.pack(fill="x", padx=2, pady=2)

                row1 = tk.Frame(inner, bg=UI_BG)
                row1.pack(fill="x")

                tk.Label(
                    row1,
                    text=f"{emoji}  Visual de {sc_display}",
                    font=("Arial", 11, "bold"),
                    bg=UI_BG,
                    fg="#880E4F",
                    anchor="w",
                ).pack(side="left")

                if visible_now:
                    status_text = "✅ Visível agora"
                    status_color = SELECTED_PINK
                elif equipped:
                    status_text = "✅ Equipado"
                    status_color = "#2e7d32"
                elif unlocked:
                    status_text = "Desbloqueado"
                    status_color = "#2e7d32"
                else:
                    status_text = f"🔒 {info_data['label']}"
                    status_color = "#888888"

                tk.Label(
                    row1,
                    text=status_text,
                    font=("Arial", 9),
                    bg=UI_BG,
                    fg=status_color,
                    anchor="e",
                ).pack(side="right")

                asset_name = f"{pet.asset_key}_{sc_key}_alternative.png"
                tk.Label(
                    inner,
                    text=f"📁 assets/pets/{asset_name}",
                    font=("Arial", 8),
                    bg=UI_BG,
                    fg="#aaaaaa",
                    anchor="w",
                ).pack(fill="x", pady=(2, 1))

                tk.Label(
                    inner,
                    text=f"Aparece no cenário global: {sc_display}",
                    font=("Arial", 8),
                    bg=UI_BG,
                    fg="#777777",
                    anchor="w",
                ).pack(fill="x", pady=(0, 6))

                preview_path = resource_path(f"assets/pets/{asset_name}")
                preview_img = None
                if os.path.exists(preview_path):
                    try:
                        raw = tk.PhotoImage(file=preview_path)
                        w_img, h_img = raw.width(), raw.height()
                        sub = max(1, max(w_img, h_img) // 80)
                        preview_img = raw.subsample(sub, sub) if sub > 1 else raw
                    except tk.TclError:
                        preview_img = None

                preview_row = tk.Frame(inner, bg=UI_BG)
                preview_row.pack(fill="x", pady=(0, 4))

                if preview_img:
                    lbl_img = tk.Label(preview_row, image=preview_img, bg=UI_BG)
                    lbl_img.image = preview_img
                    lbl_img.pack(side="left", padx=(0, 10))
                else:
                    tk.Label(
                        preview_row,
                        text="🖼️\n(sem prévia)",
                        font=("Arial", 9),
                        bg=UI_BG,
                        fg="#bbbbbb",
                        width=8,
                        height=3,
                        relief="groove",
                    ).pack(side="left", padx=(0, 10))

                btn_frame = tk.Frame(preview_row, bg=UI_BG)
                btn_frame.pack(side="right", anchor="center")

                if not unlocked:
                    if info_data["type"] == "coins":
                        btn_text = f"Comprar  {info_data['label']}"
                        btn_color = "#ff9800"
                        btn_cmd = lambda p=pet, sk=sc_key: _buy_skin(p, sk)
                    else:
                        btn_text = f"Nível {info_data['req']} necessário"
                        btn_color = UI_BTN
                        btn_cmd = None

                    tk.Button(
                        btn_frame,
                        text=btn_text,
                        font=("Arial", 9, "bold"),
                        bg=btn_color,
                        fg="white",
                        activebackground="#e65100" if info_data["type"] == "coins" else UI_BORDER,
                        relief="flat",
                        cursor="hand2" if btn_cmd else "arrow",
                        state="normal" if btn_cmd else "disabled",
                        command=btn_cmd,
                    ).pack(pady=2)
                else:
                    if equipped:
                        tk.Button(
                            btn_frame,
                            text="✅ Equipado  (remover)",
                            font=("Arial", 9, "bold"),
                            bg="#388e3c",
                            fg="white",
                            activebackground="#1b5e20",
                            relief="flat",
                            cursor="hand2",
                            command=lambda p=pet, sk=sc_key: _unequip_skin(p, sk),
                        ).pack(pady=2)
                    else:
                        tk.Button(
                            btn_frame,
                            text="Equipar visual",
                            font=("Arial", 9, "bold"),
                            bg=SELECTED_PINK,
                            fg="white",
                            activebackground="#880E4F",
                            relief="flat",
                            cursor="hand2",
                            command=lambda p=pet, sk=sc_key: _equip_skin(p, sk),
                        ).pack(pady=2)

        def _buy_skin(pet, sc_key):
            success, msg = self.party.alt_buy(pet, sc_key)
            messagebox.showinfo("Visual", msg)
            if success:
                self._skin_money_lbl.config(text=f"💰 {self.party.money}")
                self.load_scene_assets()
                self.update_screen()
                self.autosave()
                _rebuild_cards()

        def _equip_skin(pet, sc_key):
            self.party.alt_equip(pet, sc_key)
            self.load_scene_assets()
            self.update_screen()
            self.autosave()
            _rebuild_cards()

        def _unequip_skin(pet, sc_key):
            self.party.alt_unequip(pet, sc_key)
            self.load_scene_assets()
            self.update_screen()
            self.autosave()
            _rebuild_cards()

        def _on_pet_change(_event=None):
            name = selected_var.get()
            if name in pet_names:
                self._skin_win_pet_idx = pet_indices[pet_names.index(name)]
                _rebuild_cards()

        pet_menu.bind("<<ComboboxSelected>>", _on_pet_change)

        _rebuild_cards()

        win.update_idletasks()
        content_h = cards_frame.winfo_reqheight() + 160
        screen_h = win.winfo_screenheight()
        final_h = min(content_h, int(screen_h * 0.88))
        win.geometry(f"500x{final_h}")

    # ──────────────────────────────────────────────────────────────────
    # Loja e inventário
    # ──────────────────────────────────────────────────────────────────
    def open_shop(self):
        w = tk.Toplevel(self.root)
        w.title("Loja")
        w.geometry("460x520")
        w.resizable(False, False)
        w.configure(bg=UI_BG)

        tk.Label(
            w,
            text=f"Loja — Moedas: {self.party.money}",
            font=("Arial", 15, "bold"),
            bg=UI_BG,
            fg=UI_BTN,
        ).pack(pady=10)

        for index, item in enumerate(self.shop.list_items()):
            tk.Button(
                w,
                text=f"{item.name} - {item.price} moedas\n{item.description}",
                width=48,
                height=3,
                bg=UI_BTN,
                fg="white",
                activebackground=UI_BORDER,
                activeforeground="white",
                relief="flat",
                command=lambda i=index: self.buy_item(i, w),
            ).pack(pady=4)

    def buy_item(self, item_index, window):
        success, message = self.shop.buy_item(self.party, self.pet, item_index)
        if not success:
            messagebox.showwarning("Compra", message)
            window.destroy()
            return

        messagebox.showinfo("Compra", message)
        window.destroy()
        self.refresh_after_action(gain_xp=0)

    def open_inventory(self):
        w = tk.Toplevel(self.root)
        w.title("Inventário")
        w.geometry("380x420")
        w.resizable(False, False)
        w.configure(bg=UI_BG)

        tk.Label(
            w,
            text="Inventário",
            font=("Arial", 16, "bold"),
            bg=UI_BG,
            fg=UI_BTN,
        ).pack(pady=10)

        if not self.pet.inventory:
            tk.Label(w, text="Inventário vazio.", font=("Arial", 13), bg=UI_BG).pack(pady=20)
            return

        for item_name in list(self.pet.inventory):
            tk.Button(
                w,
                text=f"Usar {item_name}",
                width=34,
                height=2,
                bg=UI_BTN,
                fg="white",
                activebackground=UI_BORDER,
                activeforeground="white",
                relief="flat",
                command=lambda n=item_name: self.use_inventory_item(n, w),
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
