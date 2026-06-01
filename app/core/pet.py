import random
import unicodedata

from app.core.disease import DiseaseSystem


class Pet:
    def __init__(self, name):
        self.name = name
        self.asset_key = self.generate_asset_key(name)

        self.hunger = 80
        self.happiness = 75
        self.energy = 75
        self.hygiene = 75
        self.health = 100

        self.age = 0

        self.sick = False
        self.disease_name = None

        self.collapsed = False

        self.inventory = []

        self.scenario = "Casa"

    def generate_asset_key(self, name):
        normalized = unicodedata.normalize("NFD", name)
        without_accents = "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )
        return without_accents.lower().replace(" ", "")

    def feed(self):
        self.hunger += 30
        self.happiness += 4
        self.health += 2
        self.pass_time()
        return f"{self.name} foi alimentado."

    def sleep(self):
        self.energy += 35
        self.health += 5
        self.hunger -= 4
        self.pass_time()
        return f"{self.name} descansou bastante."

    def bath(self):
        self.hygiene += 35
        self.happiness += 2
        self.health += 3
        self.pass_time()
        return f"{self.name} tomou banho."

    def use_medicine(self):
        if not self.sick:
            return f"{self.name} não está doente."
        self.sick = False
        self.disease_name = None
        self.health += 40
        self.limit_attributes()
        self.update_condition()
        return f"{self.name} foi tratado e está melhor."

    def use_item(self, item):
        if item.full_restore:
            self.full_restore()
            return f"{self.name} usou {item.name} e recuperou todos os status!"

        self.hunger += item.hunger_effect
        self.happiness += item.happiness_effect
        self.energy += item.energy_effect
        self.hygiene += item.hygiene_effect
        self.health += item.health_effect

        if item.cures_disease:
            self.sick = False
            self.disease_name = None

        self.pass_time()
        return f"{self.name} usou {item.name}."

    def full_restore(self):
        self.hunger = 100
        self.happiness = 100
        self.energy = 100
        self.hygiene = 100
        self.health = 100
        self.sick = False
        self.disease_name = None
        self.collapsed = False
        self.limit_attributes()

    def change_scenario(self, scenario):
        valid_scenarios = ["Casa", "Piscina", "Zoo", "Palco de Show"]
        if scenario not in valid_scenarios:
            return "Cenário inválido."
        self.scenario = scenario
        return f"Cenário alterado para {scenario}."

    def pass_time(self):
        self.age += 1

        self.hunger -= random.randint(1, 4)
        self.energy -= random.randint(1, 3)
        self.hygiene -= random.randint(1, 3)
        self.happiness -= random.randint(1, 3)

        DiseaseSystem.check_disease(self)

        self.limit_attributes()
        self.update_condition()

    def limit_attributes(self):
        self.hunger = max(0, min(100, self.hunger))
        self.happiness = max(0, min(100, self.happiness))
        self.energy = max(0, min(100, self.energy))
        self.hygiene = max(0, min(100, self.hygiene))
        self.health = max(0, min(100, self.health))

    def update_condition(self):
        critical_status = [
            self.hunger,
            self.happiness,
            self.energy,
            self.hygiene,
            self.health,
        ]
        if any(value <= 0 for value in critical_status):
            self.collapsed = True
            return
        if self.collapsed and all(value >= 20 for value in critical_status):
            self.collapsed = False

    def get_mood(self):
        if self.collapsed:
            return "desmaiado"
        if self.sick:
            return f"doente: {self.disease_name}"
        if self.hunger < 25:
            return "com fome"
        if self.energy < 25:
            return "cansado"
        if self.hygiene < 25:
            return "sujo"
        if self.happiness > 75:
            return "muito feliz"
        if self.happiness < 30:
            return "triste"
        return "normal"

    def to_dict(self):
        return {
            "name": self.name,
            "asset_key": self.asset_key,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "hygiene": self.hygiene,
            "health": self.health,
            "age": self.age,
            "sick": self.sick,
            "disease_name": self.disease_name,
            "collapsed": self.collapsed,
            "inventory": self.inventory,
            "scenario": self.scenario,
        }

    @classmethod
    def from_dict(cls, data):
        pet = cls(data.get("name", "Pet"))
        pet.asset_key = data.get("asset_key", pet.generate_asset_key(pet.name))
        pet.hunger = data.get("hunger", 80)
        pet.happiness = data.get("happiness", 75)
        pet.energy = data.get("energy", 75)
        pet.hygiene = data.get("hygiene", 75)
        pet.health = data.get("health", 100)
        pet.age = data.get("age", 0)
        pet.sick = data.get("sick", False)
        pet.disease_name = data.get("disease_name", None)
        pet.collapsed = data.get("collapsed", False)
        pet.inventory = data.get("inventory", [])
        pet.scenario = data.get("scenario", "Casa")
        pet.limit_attributes()
        pet.update_condition()
        return pet
