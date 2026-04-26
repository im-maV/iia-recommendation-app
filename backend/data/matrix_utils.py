"""
Matriz de Utilidade
===================
Estratégia:
    Simula o comportamento de usuários reais via perfis definidos em config.py.
    A nota depende de quantas características do jogo batem com o perfil,
    com ruído gaussiano para realismo. A matriz é esparsa (~65% preenchida).
"""

import numpy as np
import pandas as pd

from data.config import (
    PROFILES,
    DISTRIBUTIONS,
    SEED,
    RATING_RATE,
    RATING_SCALE,
    GAMES_PATH,
    MATRIX_PATH,
)


def calculate_affinity(game: dict, profile: dict) -> str:
    """
    Calcula afinidade entre um jogo e um perfil contando características
    compatíveis (genre, perspective, category).

    Retorna 'high' (3 matches), 'medium' (2), ou 'low' (0-1).
    """
    matches = 0

    if profile["genre"] is None or game["genre"] in profile["genre"]:
        matches += 1
    if profile["perspective"] is None or game["perspective"] in profile["perspective"]:
        matches += 1
    if profile["category"] is None or game["category"] in profile["category"]:
        matches += 1

    if matches == 3:
        return "high"
    elif matches == 2:
        return "medium"
    else:
        return "low"


def generate_rating(affinity: str, rng: np.random.Generator) -> int:
    """
    Gera uma nota inteira (dentro de RATING_SCALE) via distribuição gaussiana
    com base no nível de afinidade.
    """
    params = DISTRIBUTIONS[affinity]
    rating_float = rng.normal(loc=params["loc"], scale=params["scale"])
    return int(np.clip(round(rating_float), *RATING_SCALE))


def load_games(path: str = GAMES_PATH) -> pd.DataFrame:
    """
    Carrega a lista de jogos a partir de CSV ou JSON.
    Espera as colunas: 'name', 'genre', 'perspective', 'category'.
    """
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".json"):
        df = pd.read_json(path)
    else:
        raise ValueError(f"Formato não suportado: '{path}'. Use .csv ou .json")

    expected_columns = {"name", "genre", "perspective", "category"}
    missing = expected_columns - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no arquivo de jogos: {missing}")

    return df.reset_index(drop=True)


def generate_utility_matrix(
    games: pd.DataFrame,
    rating_rate: float = RATING_RATE,
    seed: int = SEED,
) -> pd.DataFrame:
    """
    Gera a matriz de utilidade (usuários × jogos) com notas inteiras de 1 a 5.

    Retorna DataFrame com shape (100, 50):
        Índice  : 'User_001' ... 'User_100'
        Colunas : nomes dos jogos
    """
    rng = np.random.default_rng(seed)

    game_names = games["name"].tolist()
    n_games = len(game_names)
    n_users = sum(p["n"] for p in PROFILES)

    matrix = np.full((n_users, n_games), np.nan)
    user_idx = 0

    for profile in PROFILES:
        for _ in range(profile["n"]):
            n_to_rate = int(round(rating_rate * n_games))
            rated_games = rng.choice(n_games, size=n_to_rate, replace=False)

            for g_idx in rated_games:
                game = games.iloc[g_idx]
                affinity = calculate_affinity(game, profile)
                rating = generate_rating(affinity, rng)
                matrix[user_idx, g_idx] = rating

            user_idx += 1

    user_index = [f"User_{i+1:03d}" for i in range(n_users)]
    return pd.DataFrame(matrix, index=user_index, columns=game_names)


def matrix_summary(df: pd.DataFrame) -> None:
    """Imprime um resumo da matriz: shape, esparsidade, distribuição de notas."""
    total = df.size
    filled = df.count().sum()
    sparsity = 1 - (filled / total)

    print("=" * 45)
    print("          UTILITY MATRIX SUMMARY")
    print("=" * 45)
    print(f"  Shape          : {df.shape[0]} users × {df.shape[1]} games")
    print(f"  Filled cells   : {filled} / {total}")
    print(f"  Sparsity       : {sparsity:.1%}")
    print(f"  Min rating     : {df.min().min():.0f}")
    print(f"  Max rating     : {df.max().max():.0f}")
    print(f"  Overall mean   : {df.stack().mean():.2f}")
    print("=" * 45)
    print("\nTop 5 highest-rated games (by mean):")
    print(df.mean().sort_values(ascending=False).head(5).to_string())


def save_matrix(df: pd.DataFrame, path: str = MATRIX_PATH) -> None:
    """Salva a matriz em CSV, mantendo NaN como células vazias."""
    df.to_csv(path, index=True)
    print(f"[matrix_utils] Matriz salva em: {path}")
