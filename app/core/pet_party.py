from app.core.pet import Pet


PET_NAMES = [
    "Félix",
    "BangChan",
    "Hyunjin",
    "Han",
    "Changbin",
    "LeeKnow",
    "IN",
    "Seungmin",
]


class PetParty:
    def __init__(self):
        self.pets = [Pet(name) for name in PET_NAMES]
        self.current_pet_index = 0

    def get_current_pet(self):
        return self.pets[self.current_pet_index]

    def select_pet(self, index):
        if 0 <= index < len(self.pets):
            self.current_pet_index = index
            return True

        return False

    def to_dict(self):
        return {
            "current_pet_index": self.current_pet_index,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data):
        party = cls()

        saved_pets = data.get("pets", [])

        for index, pet_data in enumerate(saved_pets):
            if index < len(party.pets):
                party.pets[index] = Pet.from_dict(pet_data)

        party.current_pet_index = data.get("current_pet_index", 0)

        if party.current_pet_index < 0 or party.current_pet_index >= len(party.pets):
            party.current_pet_index = 0

        return party