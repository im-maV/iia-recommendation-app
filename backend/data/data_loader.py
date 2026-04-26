# TODO: Funções para carregar games.json e utility_matrix.csv
"""
Fluxo:
    1. Verifica se utility_matrix.csv existe em data/
    2. Se sim  → carrega e retorna o DataFrame
    3. Se não  → gera a partir de 50_games.json, salva e retorna

Assim o resto do projeto (rotas, ML) nunca precisa se preocupar
com a existência ou geração da matriz — basta chamar get_utility_matrix().
"""

import os
import logging

import pandas as pd

from data.config import GAMES_PATH, MATRIX_PATH
from data.matrix_utils import load_games, generate_utility_matrix, save_matrix

logger = logging.getLogger(__name__)

# Cache em memória: evita ler o CSV a cada requisição
_cached_matrix: pd.DataFrame | None = None


def get_utility_matrix(force_regenerate: bool = False) -> pd.DataFrame:
    """
    Retorna a matriz de utilidade (usuários × jogos).

    Parâmetros
    ----------
    force_regenerate : bool
        Se True, ignora o CSV existente e gera uma nova matriz.
        Útil para testes ou após atualização do dataset de jogos.

    Retorna
    -------
    pd.DataFrame
        Matriz com shape (100, 50), índice 'User_001'...'User_100',
        colunas com nomes dos jogos. NaN = jogo não avaliado.
    """
    global _cached_matrix

    if _cached_matrix is not None and not force_regenerate:
        logger.debug("[data_loader] Retornando matriz do cache em memória.")
        return _cached_matrix

    if not force_regenerate and os.path.exists(MATRIX_PATH):
        logger.info("[data_loader] Carregando matriz existente: %s", MATRIX_PATH)
        _cached_matrix = _load_from_csv(MATRIX_PATH)
    else:
        reason = (
            "force_regenerate=True" if force_regenerate else "arquivo não encontrado"
        )
        logger.info("[data_loader] Gerando nova matriz (%s)...", reason)
        _cached_matrix = _generate_and_save()

    return _cached_matrix


def invalidate_cache() -> None:
    """
    Limpa o cache em memória.
    Chame isso se regenerar a matriz manualmente via endpoint admin.
    """
    global _cached_matrix
    _cached_matrix = None
    logger.info("[data_loader] Cache da matriz invalidado.")


def _load_from_csv(path: str) -> pd.DataFrame:
    """Carrega a matriz do CSV, usando a primeira coluna como índice."""
    df = pd.read_csv(path, index_col=0)
    logger.info(
        "[data_loader] Matriz carregada: %d usuários × %d jogos.",
        df.shape[0],
        df.shape[1],
    )
    return df


def _generate_and_save() -> pd.DataFrame:
    """Gera a matriz do zero e a persiste em CSV."""
    if not os.path.exists(GAMES_PATH):
        raise FileNotFoundError(
            f"[data_loader] Arquivo de jogos não encontrado: {GAMES_PATH}\n"
            "Certifique-se de que '50_games.json' está na pasta data/."
        )

    games = load_games(GAMES_PATH)
    df = generate_utility_matrix(games)
    save_matrix(df, MATRIX_PATH)

    logger.info(
        "[data_loader] Matriz gerada e salva: %d usuários × %d jogos.",
        df.shape[0],
        df.shape[1],
    )
    return df
