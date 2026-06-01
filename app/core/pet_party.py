from app.core.pet import Pet


# Ordem e nível de desbloqueio de cada pet
PET_CONFIG = [
    {"name": "Han",      "unlock_level": 0},
    {"name": "Hyunjin",  "unlock_level": 1},
    {"name": "Félix",    "unlock_level": 3},
    {"name": "Seungmin", "unlock_level": 6},
    {"name": "IN",       "unlock_level": 10},
    {"name": "Changbin", "unlock_level": 15},
    {"name": "BangChan", "unlock_level": 20},
    {"name": "LeeKnow",  "unlock_level": 30},
]

# XP necessária para cada nível (nível N requer XP_PER_LEVEL * N)
XP_PER_LEVEL = 100


class PetParty:
    def __init__(self):
        self.pets = [Pet(cfg["name"]) for cfg in PET_CONFIG]
        self.current_pet_index = 0

        # Progresso global do jogador
        self.money = 25
        self.xp = 0
        self.level = 0

    # ------------------------------------------------------------------
    # Nível e XP
    # ------------------------------------------------------------------
    def add_xp(self, amount):
        """Adiciona XP e sobe de nível se necessário. Retorna True se subiu de nível."""
        self.xp += amount
        leveled_up = False
        while self.xp >= self._xp_for_next_level():
            self.xp -= self._xp_for_next_level()
            self.level += 1
            leveled_up = True
        return leveled_up

    def _xp_for_next_level(self):
        return XP_PER_LEVEL * (self.level + 1)

    def xp_progress(self):
        """Retorna (xp_atual, xp_necessaria) para o próximo nível."""
        return self.xp, self._xp_for_next_level()

    # ------------------------------------------------------------------
    # Desbloqueio de pets
    # ------------------------------------------------------------------
    def unlock_level_for(self, index):
        return PET_CONFIG[index]["unlock_level"]

    def is_unlocked(self, index):
        return self.level >= PET_CONFIG[index]["unlock_level"]

    def next_unlock(self):
        """Retorna (nome, nível) do próximo pet a ser desbloqueado, ou None."""
        for i, cfg in enumerate(PET_CONFIG):
            if self.level < cfg["unlock_level"]:
                return cfg["name"], cfg["unlock_level"]
        return None

    # ------------------------------------------------------------------
    # Pet selecionado
    # ------------------------------------------------------------------
    def get_current_pet(self):
        return self.pets[self.current_pet_index]

    def select_pet(self, index):
        if 0 <= index < len(self.pets) and self.is_unlocked(index):
            self.current_pet_index = index
            return True
        return False

    # ------------------------------------------------------------------
    # Serialização
    # ------------------------------------------------------------------
    def to_dict(self):
        return {
            "money": self.money,
            "xp": self.xp,
            "level": self.level,
            "current_pet_index": self.current_pet_index,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data):
        party = cls()

        party.money = data.get("money", 25)
        party.xp = data.get("xp", 0)
        party.level = data.get("level", 0)

        saved_pets = data.get("pets", [])
        for index, pet_data in enumerate(saved_pets):
            if index < len(party.pets):
                party.pets[index] = Pet.from_dict(pet_data)

        party.current_pet_index = data.get("current_pet_index", 0)
        if not (0 <= party.current_pet_index < len(party.pets)):
            party.current_pet_index = 0

        return party
