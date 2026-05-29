import json
import os
from json import JSONDecodeError

from app.core.pet_party import PetParty


SAVE_DIR = "saves"
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")


class SaveManager:
    @staticmethod
    def save_game(party):
        os.makedirs(SAVE_DIR, exist_ok=True)

        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(party.to_dict(), file, indent=4, ensure_ascii=False)

    @staticmethod
    def load_game():
        if not os.path.exists(SAVE_FILE):
            return None

        if os.path.getsize(SAVE_FILE) == 0:
            return None

        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if "pets" not in data:
                return None

            return PetParty.from_dict(data)

        except JSONDecodeError:
            return None

        except KeyError:
            return None

    @staticmethod
    def has_save():
        return os.path.exists(SAVE_FILE) and os.path.getsize(SAVE_FILE) > 0

    @staticmethod
    def delete_save():
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)