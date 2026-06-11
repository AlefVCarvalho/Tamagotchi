# Configurações de balanceamento novas da prioridade média.

# A cada 60 segundos os pets desbloqueados sofrem passagem de tempo real.
REAL_TIME_TICK_MS = 60_000

# Efeitos passivos aplicados depois da decadência normal de tempo.
# Valores positivos recuperam atributo; negativos desgastam atributo.
SCENARIO_PASSIVE_EFFECTS = {
    "Casa": {
        "energy": 1,
        "health": 1,
    },
    "Piscina": {
        "happiness": 2,
        "energy": -1,
    },
    "Zoo": {
        "happiness": 2,
        "hygiene": -1,
    },
    "Palco de Show": {
        "happiness": 2,
        "energy": -2,
    },
}

# Bônus por ação, dependentes do cenário global.
SCENARIO_ACTION_BONUSES = {
    "Casa": {
        "sleep": {"energy": 6, "health": 1},
    },
    "Piscina": {
        "bath": {"happiness": 5},
    },
    "Zoo": {
        "feed": {"happiness": 3},
    },
    "Palco de Show": {},
}

SCENARIO_ACTION_MESSAGES = {
    "Casa": {
        "sleep": "Bônus da Casa: descanso mais eficiente.",
    },
    "Piscina": {
        "bath": "Bônus da Piscina: banho mais divertido.",
    },
    "Zoo": {
        "feed": "Bônus do Zoo: passeio deixou o pet mais feliz.",
    },
}

# Bônus/penalidade aplicada ao terminar minijogo no cenário global correspondente.
SCENARIO_MINIGAME_BONUSES = {
    "Palco de Show": {
        "xp_percent": 0.15,
        "energy_cost": 2,
    }
}

SCENARIO_EFFECT_DESCRIPTIONS = {
    "Casa": "Tempo real: +energia/+saúde leve. Dormir recupera mais.",
    "Piscina": "Tempo real: +felicidade, -energia. Banho dá felicidade extra.",
    "Zoo": "Tempo real: +felicidade, -higiene. Alimentar dá felicidade extra.",
    "Palco de Show": "Tempo real: +felicidade, -energia. Minijogos dão +15% XP e gastam +2 energia.",
}
