import random


class DiseaseSystem:
    diseases = [
        "resfriado",
        "dor de barriga",
        "febre",
        "cansaço extremo",
    ]

    @staticmethod
    def check_disease(pet):
        if pet.collapsed:
            return

        if pet.sick:
            pet.health -= random.randint(1, 4)
            return

        risk = 0

        if pet.hygiene < 20:
            risk += 10

        if pet.hunger < 20:
            risk += 8

        if pet.energy < 15:
            risk += 6

        if pet.happiness < 15:
            risk += 5

        chance = random.randint(1, 100)

        if chance <= risk:
            pet.sick = True
            pet.disease_name = random.choice(DiseaseSystem.diseases)
            pet.health -= random.randint(3, 8)