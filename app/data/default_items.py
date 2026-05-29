from app.core.items import Item


DEFAULT_ITEMS = [
    Item(
        name="Ração simples",
        price=5,
        hunger_effect=30,
        happiness_effect=3,
        description="Comida básica. Recupera bem a fome."
    ),
    Item(
        name="Bolo",
        price=12,
        hunger_effect=18,
        happiness_effect=28,
        description="Doce gostoso. Aumenta bastante a felicidade."
    ),
    Item(
        name="Suco energético",
        price=15,
        hunger_effect=8,
        energy_effect=35,
        description="Recupera bastante energia."
    ),
    Item(
        name="Remédio",
        price=20,
        health_effect=45,
        cures_disease=True,
        description="Cura doenças e recupera bastante saúde."
    ),
    Item(
        name="Brinquedo",
        price=18,
        happiness_effect=35,
        energy_effect=-3,
        description="Aumenta bastante a felicidade."
    ),
    Item(
        name="Poção de Recuperação Total",
        price=80,
        full_restore=True,
        description="Restaura todos os status para 100 e cura doenças."
    ),
]