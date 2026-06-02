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

XP_PER_LEVEL = 100

# ---------------------------------------------------------------------------
# Configuração de visuais alternativos por cenário
# ---------------------------------------------------------------------------
# Visuais desbloqueados por NÍVEL (casa e piscina)
SKIN_LEVEL_UNLOCK = {
    "casa":    5,    # nível 5 desbloqueia visual alternativo da Casa
    "piscina": 8,    # nível 8 desbloqueia visual alternativo da Piscina
}

# Visuais comprados com MOEDAS (zoo e palco)
SKIN_COIN_PRICE = {
    "zoo":   60,
    "palco": 80,
}

ALL_SCENARIO_KEYS = ["casa", "piscina", "zoo", "palco"]


class PetParty:
    def __init__(self):
        self.pets = [Pet(cfg["name"]) for cfg in PET_CONFIG]
        self.current_pet_index = 0

        # Progresso global do jogador
        self.money = 25
        self.xp    = 0
        self.level = 0

        # Visuais alternativos desbloqueados: {pet_asset_key: set(scenario_keys)}
        self._alt_unlocked: dict[str, set] = {}

        # Visuais alternativos equipados: {pet_asset_key: set(scenario_keys)}
        # Um visual equipado substitui o padrão quando o pet está no cenário correspondente
        self._alt_equipped: dict[str, set] = {}

    # ------------------------------------------------------------------
    # Nível e XP
    # ------------------------------------------------------------------
    def add_xp(self, amount):
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
        return self.xp, self._xp_for_next_level()

    # ------------------------------------------------------------------
    # Desbloqueio de pets
    # ------------------------------------------------------------------
    def unlock_level_for(self, index):
        return PET_CONFIG[index]["unlock_level"]

    def is_unlocked(self, index):
        return self.level >= PET_CONFIG[index]["unlock_level"]

    def next_unlock(self):
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
    # Visuais alternativos
    # ------------------------------------------------------------------
    def _key(self, pet):
        return pet.asset_key

    def alt_is_unlocked(self, pet, scenario_key: str) -> bool:
        """Retorna True se o visual alternativo desse cenário está desbloqueado para o pet."""
        unlocked = self._alt_unlocked.get(self._key(pet), set())
        return scenario_key in unlocked

    def alt_is_equipped(self, pet, scenario_key: str) -> bool:
        equipped = self._alt_equipped.get(self._key(pet), set())
        return scenario_key in equipped

    def alt_unlock(self, pet, scenario_key: str):
        k = self._key(pet)
        self._alt_unlocked.setdefault(k, set()).add(scenario_key)

    def alt_equip(self, pet, scenario_key: str):
        k = self._key(pet)
        self._alt_equipped.setdefault(k, set()).add(scenario_key)

    def alt_unequip(self, pet, scenario_key: str):
        k = self._key(pet)
        self._alt_equipped.get(k, set()).discard(scenario_key)

    def alt_unlock_by_level(self):
        """Chama após subir de nível para desbloquear visuais de nível."""
        for pet in self.pets:
            for sc_key, req_lvl in SKIN_LEVEL_UNLOCK.items():
                if self.level >= req_lvl and not self.alt_is_unlocked(pet, sc_key):
                    self.alt_unlock(pet, sc_key)

    def alt_buy(self, pet, scenario_key: str) -> tuple[bool, str]:
        """Tenta comprar visual com moedas. Retorna (sucesso, mensagem)."""
        price = SKIN_COIN_PRICE.get(scenario_key)
        if price is None:
            return False, "Visual não encontrado."
        if self.alt_is_unlocked(pet, scenario_key):
            return False, "Visual já desbloqueado."
        if self.money < price:
            return False, f"Moedas insuficientes. Custo: {price} 💰"
        self.money -= price
        self.alt_unlock(pet, scenario_key)
        return True, f"Visual de {scenario_key.capitalize()} desbloqueado para {pet.name}!"

    def get_active_skin_key(self, pet, scenario_key: str) -> str:
        """
        Retorna o sufixo de arquivo a usar para o pet no cenário dado.
        Se o visual alternativo estiver equipado → '{asset_key}_{scenario_key}_alternative'
        Caso contrário                           → '{asset_key}_{scenario_key}'
        """
        if self.alt_is_equipped(pet, scenario_key):
            return f"{pet.asset_key}_{scenario_key}_alternative"
        return f"{pet.asset_key}_{scenario_key}"

    # ------------------------------------------------------------------
    # Serialização
    # ------------------------------------------------------------------
    def to_dict(self):
        return {
            "money": self.money,
            "xp":    self.xp,
            "level": self.level,
            "current_pet_index": self.current_pet_index,
            "pets":  [pet.to_dict() for pet in self.pets],
            "alt_unlocked": {k: list(v) for k, v in self._alt_unlocked.items()},
            "alt_equipped":  {k: list(v) for k, v in self._alt_equipped.items()},
        }

    @classmethod
    def from_dict(cls, data):
        party = cls()

        party.money = data.get("money", 25)
        party.xp    = data.get("xp",    0)
        party.level = data.get("level", 0)

        saved_pets = data.get("pets", [])
        for index, pet_data in enumerate(saved_pets):
            if index < len(party.pets):
                party.pets[index] = Pet.from_dict(pet_data)

        party.current_pet_index = data.get("current_pet_index", 0)
        if not (0 <= party.current_pet_index < len(party.pets)):
            party.current_pet_index = 0

        raw_unlocked = data.get("alt_unlocked", {})
        party._alt_unlocked = {k: set(v) for k, v in raw_unlocked.items()}

        raw_equipped = data.get("alt_equipped", {})
        party._alt_equipped = {k: set(v) for k, v in raw_equipped.items()}

        # Re-aplica desbloqueios por nível (garante consistência após updates)
        party.alt_unlock_by_level()

        return party