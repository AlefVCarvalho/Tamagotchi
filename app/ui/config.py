from app.core.pet_party import SKIN_LEVEL_UNLOCK, SKIN_COIN_PRICE


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 560

GAME_AREA_WIDTH = 620
GAME_AREA_HEIGHT = 460

PET_AREA_MARGIN = 55
PET_SIZE_FALLBACK = 70

UI_BG = "#FFF0F6"
UI_BORDER = "#F7BBD5"
SELECTED_PINK = "#FF4FA3"
UI_BTN = "#E8799F"

CANVAS_NAME_OUTLINE = "#000000"
CANVAS_NAME_NORMAL = "#FFFFFF"

START_BACKGROUND = "assets/backgrounds/start.png"
START_BACKGROUND_WIDTH = WINDOW_WIDTH
START_BACKGROUND_HEIGHT = WINDOW_HEIGHT

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

SCENARIO_KEY_TO_NAME = {v["key"]: k for k, v in SCENARIOS.items()}

SKIN_UNLOCK_INFO = {
    "casa": {
        "type": "level",
        "req": SKIN_LEVEL_UNLOCK["casa"],
        "label": f"Nível {SKIN_LEVEL_UNLOCK['casa']}",
    },
    "piscina": {
        "type": "level",
        "req": SKIN_LEVEL_UNLOCK["piscina"],
        "label": f"Nível {SKIN_LEVEL_UNLOCK['piscina']}",
    },
    "zoo": {
        "type": "coins",
        "req": SKIN_COIN_PRICE["zoo"],
        "label": f"{SKIN_COIN_PRICE['zoo']} 💰",
    },
    "palco": {
        "type": "coins",
        "req": SKIN_COIN_PRICE["palco"],
        "label": f"{SKIN_COIN_PRICE['palco']} 💰",
    },
}

SCENARIO_EMOJI = {"casa": "🏠", "piscina": "🏊", "zoo": "🦁", "palco": "🎤"}
