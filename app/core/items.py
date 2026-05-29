class Item:
    def __init__(
        self,
        name,
        price,
        hunger_effect=0,
        happiness_effect=0,
        energy_effect=0,
        hygiene_effect=0,
        health_effect=0,
        cures_disease=False,
        full_restore=False,
        description=""
    ):
        self.name = name
        self.price = price

        self.hunger_effect = hunger_effect
        self.happiness_effect = happiness_effect
        self.energy_effect = energy_effect
        self.hygiene_effect = hygiene_effect
        self.health_effect = health_effect

        self.cures_disease = cures_disease
        self.full_restore = full_restore

        self.description = description

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "hunger_effect": self.hunger_effect,
            "happiness_effect": self.happiness_effect,
            "energy_effect": self.energy_effect,
            "hygiene_effect": self.hygiene_effect,
            "health_effect": self.health_effect,
            "cures_disease": self.cures_disease,
            "full_restore": self.full_restore,
            "description": self.description,
        }