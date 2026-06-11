import math
import random
import tkinter as tk

from app.ui.config import (
    CANVAS_NAME_NORMAL,
    CANVAS_NAME_OUTLINE,
    GAME_AREA_HEIGHT,
    GAME_AREA_WIDTH,
    PET_AREA_MARGIN,
    PET_SIZE_FALLBACK,
    SCENARIOS,
    SELECTED_PINK,
)
from app.ui.utils import load_photo


class SceneMixin:
    def _init_pet_states(self):
        self.pet_states = {}
        n = len(self.party.pets)
        section_w = GAME_AREA_WIDTH // max(n, 1)
        for i, _pet in enumerate(self.party.pets):
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

    def load_image(self, relative_path):
        return load_photo(relative_path)

    def _current_scenario_data(self):
        scenario_name = self.party.get_current_scenario()
        return SCENARIOS.get(scenario_name, SCENARIOS["Casa"])

    def load_scene_assets(self):
        scenario_data = self._current_scenario_data()
        scenario_key = scenario_data["key"]
        self.background_image = self.load_image(scenario_data["background"])

        self.pet_images = {}
        for i, pet in enumerate(self.party.pets):
            if not self.party.is_unlocked(i):
                self.pet_images[i] = None
                continue

            pet_key = pet.asset_key

            if pet.collapsed:
                img = (
                    self.load_image(f"assets/pets/{pet_key}_desmaio.png")
                    or self.load_image("assets/pets/pet_desmaio.png")
                )
            elif pet.sick:
                img = (
                    self.load_image(f"assets/pets/{pet_key}_doente.png")
                    or self.load_image("assets/pets/pet_doente.png")
                    or self.load_image(f"assets/pets/{pet_key}_{scenario_key}.png")
                )
            else:
                # O visual alternativo só aparece quando está equipado para o cenário global atual.
                skin_file = self.party.get_active_skin_key(pet, scenario_key)
                img = (
                    self.load_image(f"assets/pets/{skin_file}.png")
                    or self.load_image(f"assets/pets/{pet_key}_{scenario_key}.png")
                )

            self.pet_images[i] = img

        self.draw_scene()

    def draw_scene(self):
        self.canvas.delete("all")

        scenario_data = self._current_scenario_data()

        if self.background_image:
            self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        else:
            self.canvas.create_rectangle(
                0,
                0,
                GAME_AREA_WIDTH,
                GAME_AREA_HEIGHT,
                fill=scenario_data["fallback_color"],
                outline="",
            )
            self.canvas.create_text(
                GAME_AREA_WIDTH // 2,
                50,
                text=scenario_data["display_name"],
                font=("Arial", 28, "bold"),
                fill="#303030",
            )
            self.canvas.create_text(
                GAME_AREA_WIDTH // 2,
                88,
                text=scenario_data["description"],
                font=("Arial", 12),
                fill="#303030",
            )

        selected_index = self.party.current_pet_index
        draw_order = sorted(range(len(self.party.pets)), key=lambda i: self.pet_states[i]["y"])

        for i in draw_order:
            pet = self.party.pets[i]
            state = self.pet_states[i]
            px, py = state["x"], state["y"]
            is_selected = i == selected_index
            unlocked = self.party.is_unlocked(i)

            if not unlocked:
                state["canvas_highlight"] = None
                state["canvas_shadow"] = None
                state["canvas_pet"] = None
                state["canvas_name_outline"] = []
                state["canvas_name"] = None
                continue

            if is_selected:
                state["canvas_highlight"] = self.canvas.create_oval(
                    px - 44,
                    py + 52,
                    px + 44,
                    py + 68,
                    fill=SELECTED_PINK,
                    outline="",
                    stipple="gray50",
                )
            else:
                state["canvas_highlight"] = None

            state["canvas_shadow"] = self.canvas.create_oval(
                px - 35,
                py + 56,
                px + 35,
                py + 68,
                fill="#000000",
                outline="",
                stipple="gray50",
            )

            img = self.pet_images.get(i)
            if img:
                state["canvas_pet"] = self.canvas.create_image(px, py, image=img, anchor="center")
            else:
                state["canvas_pet"] = self.canvas.create_text(
                    px,
                    py,
                    text=self.get_fallback_pet_visual_for(pet),
                    font=("Arial", PET_SIZE_FALLBACK),
                    anchor="center",
                )

            name_color = SELECTED_PINK if is_selected else CANVAS_NAME_NORMAL
            name_y = py - 65

            state["canvas_name_outline"] = []
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                item = self.canvas.create_text(
                    px + ox,
                    name_y + oy,
                    text=pet.name,
                    font=("Arial", 13, "bold"),
                    fill=CANVAS_NAME_OUTLINE,
                )
                state["canvas_name_outline"].append(item)

            state["canvas_name"] = self.canvas.create_text(
                px,
                name_y,
                text=pet.name,
                font=("Arial", 13, "bold"),
                fill=name_color,
            )

        self.canvas.create_rectangle(
            0,
            GAME_AREA_HEIGHT - 34,
            GAME_AREA_WIDTH,
            GAME_AREA_HEIGHT,
            fill="#000000",
            outline="",
            stipple="gray50",
        )
        self.canvas.create_text(
            15,
            GAME_AREA_HEIGHT - 18,
            text=f"Cenário global: {self.party.get_current_scenario()}  |  Pet selecionado: {self.pet.name}",
            font=("Arial", 11, "bold"),
            fill="#ffffff",
            anchor="w",
        )

    def animate_pet(self):
        if not self.game_started:
            return

        draw_order = sorted(range(len(self.party.pets)), key=lambda i: self.pet_states[i]["y"])

        for i in draw_order:
            pet = self.party.pets[i]
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

                if state["x"] <= min_x or state["x"] >= max_x:
                    state["vx"] *= -1
                if state["y"] <= min_y or state["y"] >= max_y:
                    state["vy"] *= -1

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
                self.canvas.coords(
                    state["canvas_highlight"],
                    px - 44,
                    state["y"] + 52,
                    px + 44,
                    state["y"] + 68,
                )
            if state["canvas_shadow"]:
                self.canvas.coords(
                    state["canvas_shadow"],
                    px - 35,
                    state["y"] + 56,
                    px + 35,
                    state["y"] + 68,
                )
            if state["canvas_pet"]:
                self.canvas.coords(state["canvas_pet"], px, display_y)

            if state.get("canvas_name_outline"):
                name_y = display_y - 68
                offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
                for item, (ox, oy) in zip(state["canvas_name_outline"], offsets):
                    self.canvas.coords(item, px + ox, name_y + oy)

            if state["canvas_name"]:
                self.canvas.coords(state["canvas_name"], px, display_y - 68)

            for item_key in (
                "canvas_highlight",
                "canvas_shadow",
                "canvas_pet",
                "canvas_name_outline",
                "canvas_name",
            ):
                items = state.get(item_key)
                if isinstance(items, list):
                    for it in items:
                        self.canvas.tag_raise(it)
                elif items:
                    self.canvas.tag_raise(items)

        self._animation_after_id = self.root.after(35, self.animate_pet)

    def get_fallback_pet_visual_for(self, pet):
        if pet.collapsed:
            return "😵"
        if pet.sick:
            return "🤒"
        return {
            "felix": "🐱",
            "bangchan": "🐺",
            "hyunjin": "🦙",
            "han": "🐿️",
            "changbin": "🐷",
            "leeknow": "🐰",
            "in": "🦊",
            "seungmin": "🐶",
        }.get(pet.asset_key, "🐣")
