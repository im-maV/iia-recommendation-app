"""
Configurações do módulo de filtragem colaborativa.

Centraliza os perfis de usuário, parâmetros das distribuições de notas
e constantes de geração da matriz de utilidade.

Sobre os perfis:
    Cada perfil representa um arquétipo de jogador real.
    - genre/perspective/category: None significa "aceita qualquer valor"
    - Perfis com múltiplos gêneros simulam jogadores eclético
    - n: número de usuários deste perfil (soma deve ser N_USERS)

Sobre as distribuições:
    - high   → jogo bate bem com o perfil → nota 4-5
    - medium → jogo bate parcialmente     → nota 3-4
    - low    → jogo não combina           → nota 1-2
"""

# CAMINHOS
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_PATH = os.path.join(BASE_DIR, "50_games.json")
MATRIX_PATH = os.path.join(BASE_DIR, "utility_matrix.csv")


# PARÂMETROS GERAIS
SEED = 42
RATING_RATE = 0.65
N_USERS = 100
N_GAMES = 50
RATING_SCALE = (1, 5)

# PERFIS DE USUÁRIO
PROFILES = [
    {
        # Fã de RPGs de ação — gosta tanto de RPG quanto de Souls-like
        "name": "Action RPG Fan",
        "genre": ["RPG", "Souls-like"],
        "perspective": ["Third-Person"],
        "category": ["Singleplayer"],
        "n": 17,
    },
    {
        # Fã de survival — gosta de desafio em grupo ou solo
        "name": "Survival Fan",
        "genre": ["Survival", "Survival Horror"],
        "perspective": None,
        "category": None,  # aceita qualquer categoria
        "n": 16,
    },
    {
        # Shooter competitivo — foca em multiplayer first-person
        "name": "Competitive Shooter",
        "genre": ["Shooter"],
        "perspective": ["First-Person"],
        "category": ["Multiplayer"],
        "n": 17,
    },
    {
        # Generalista multiplayer — joga de tudo desde que seja online
        "name": "Multiplayer Generalist",
        "genre": None,
        "perspective": None,
        "category": ["Multiplayer", "Co-op"],
        "n": 15,
    },
    {
        # Fã de Souls — aceita 2D e Third-Person
        "name": "Souls Enjoyer",
        "genre": ["Souls-like", "RPG"],
        "perspective": ["Third-Person", "2D"],
        "category": ["Singleplayer"],
        "n": 13,
    },
    {
        # Fã de simulação — aceita qualquer perspectiva e categoria
        "name": "Simulation Fan",
        "genre": ["Simulation"],
        "perspective": None,
        "category": None,
        "n": 12,
    },
    {
        # Casual — sem preferência forte, avalia tudo de forma moderada
        "name": "Casual Gamer",
        "genre": None,
        "perspective": None,
        "category": None,
        "n": 10,
    },
]


# DISTRIBUIÇÕES DE NOTA POR AFINIDADE
DISTRIBUTIONS = {
    "high": {"loc": 4.5, "scale": 0.5},
    "medium": {"loc": 3.5, "scale": 0.7},
    "low": {"loc": 2.2, "scale": 1.0},
}


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
