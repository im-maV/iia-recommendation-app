"""
Configurações do módulo de filtragem colaborativa.

Centraliza os perfis de usuário, parâmetros das distribuições de notas
e constantes de geração da matriz de utilidade.
"""

# PARÂMETROS GERAIS
SEED = 42
RATING_RATE = 0.65
N_USERS = 100
N_GAMES = 50
RATING_SCALE = (1, 5)

# PERFIS DE USUÁRIO
PROFILES = [
    {
        "name": "Solo RPG Player",
        "genre": ["RPG"],
        "perspective": ["Third Person"],
        "category": ["Singleplayer"],
        "n": 12,
    },
    {
        "name": "Co-op RPG",
        "genre": ["RPG"],
        "perspective": ["Third Person"],
        "category": ["Co-op"],
        "n": 10,
    },
    {
        "name": "Horror Enjoyer",
        "genre": ["Survival Horror"],
        "perspective": ["First-Person"],
        "category": ["Singleplayer"],
        "n": 10,
    },
    {
        "name": "Competitive Shooter",
        "genre": ["Shooter"],
        "perspective": ["First-Person"],
        "category": ["Multiplayer"],
        "n": 15,
    },
    {
        "name": "Co-op Shooter",
        "genre": ["Shooter"],
        "perspective": ["First-Person"],
        "category": ["Co-op"],
        "n": 10,
    },
    {
        "name": "Solo Survivor",
        "genre": ["Survival"],
        "perspective": ["Third Person"],
        "category": ["Singleplayer"],
        "n": 8,
    },
    {
        "name": "Group Survivor",
        "genre": ["Survival"],
        "perspective": ["Third Person"],
        "category": ["Co-op"],
        "n": 8,
    },
    {
        "name": "Souls Masochist",
        "genre": ["Souls-like"],
        "perspective": ["Third Person"],
        "category": ["Singleplayer"],
        "n": 10,
    },
    {
        "name": "Simulation Enjoyer",
        "genre": ["Simulation"],
        "perspective": ["Third Person"],
        "category": ["Singleplayer"],
        "n": 9,
    },
    {
        "name": "Multiplayer Generalist",
        "genre": None,
        "perspective": None,
        "category": ["Multiplayer"],
        "n": 8,
    },
]

# DISTRIBUIÇÕES DE NOTA POR AFINIDADE
DISTRIBUTIONS = {
    "high": {"loc": 4.3, "scale": 0.5},
    "medium": {"loc": 3.2, "scale": 0.7},
    "low": {"loc": 1.8, "scale": 0.6},
}

# CAMINHOS
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_PATH = os.path.join(BASE_DIR, "50_games.json")
MATRIX_PATH = os.path.join(BASE_DIR, "utility_matrix.csv")


# VALIDAÇÃO
def _validate_config() -> None:
    total = sum(p["n"] for p in PROFILES)
    assert (
        total == N_USERS
    ), f"[config.py] Sum of profile users is {total}, expected {N_USERS}."
    assert all(
        k in DISTRIBUTIONS for k in ("high", "medium", "low")
    ), "[config.py] DISTRIBUTIONS must contain 'high', 'medium' and 'low'."


_validate_config()
