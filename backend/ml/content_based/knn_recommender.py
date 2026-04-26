"""
KNN Content-Based Recommender
==============================
Sistema de recomendação baseado em conteúdo usando TF-IDF e similaridade de cosseno.

Referências:
- Géron, A. Hands-On Machine Learning with Scikit-Learn & TensorFlow. O'Reilly, 2017.
- Abu-Mostafa, Y. et al. Learning from Data. AMLBook, 2012.
- Russell, S., Norvig, P. Artificial Intelligence - A Modern Approach (4th ed). Pearson, 2021.
"""

import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict
import os
import sys



BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_games(filepath: str) -> pd.DataFrame:
    """
    Carrega os jogos do arquivo JSON e retorna um DataFrame.

    Cada jogo possui:
        - id
        - name
        - genre: Survival Horror, RPG, Shooter, Simulation, Survival, Souls-like
        - perspective: First-Person, Third-Person, 2D
        - category: Singleplayer, Multiplayer, Co-op

    Args:
        filepath: caminho para o arquivo games.json

    Returns:
        DataFrame com os 50 jogos
    """
    with open(filepath, "r", encoding="utf-8") as f:
        games = json.load(f)
    return pd.DataFrame(games)


def build_feature_string(game: pd.Series) -> str:
    """
    (Funçao auxiliar) Concatena as 3 características de um jogo 
    em uma única string.

    Essa string será usada pelo TF-IDF para gerar o vetor do jogo.
    Repetimos cada característica para dar mais peso relativo caso necessário.

    Exemplo:
        genre="Shooter", perspective="First-Person", category="Multiplayer"
        → "Shooter First-Person Multiplayer"

    Args:
        game: linha do DataFrame (um jogo)

    Returns:
        String com as características concatenadas
    """
    return f"{game['genre']} {game['perspective']} {game['category']}"




def build_tfidf_matrix(games_df: pd.DataFrame):
    """
    Aplica TF-IDF sobre as caracteristicas dos jogos para gerar vetores numericos.

    TF-IDF (Term Frequency - Inverse Document Frequency):
        - TF: frequencia do termo no documento (aqui, documento é a string com as caracteristicas do jogo)
        - IDF: penaliza termos que aparecem em muitos jogos 

    Resultado: cada jogo vira um vetor numerico onde caracteristicas raras/distintivas
    tem pesos maiores, capturando melhor a identidade de cada jogo.

    Args:
        games_df: DataFrame com os 50 jogos

    Returns:
        tfidf_matrix: matriz esparsa (n_jogos x n_termos_unicos, i.e: 50x12)
        vectorizer: objeto TfidfVectorizer treinado (necessario para vetorizar o usuário)
    """
    
    games_df = games_df.copy()
    games_df["features"] = games_df.apply(build_feature_string, axis=1)


    # TF-IDF com analise de palavras individuais 
    vectorizer = CountVectorizer(binary=True, analyzer="word", token_pattern=r"[^\s]+")
    #vectorizer = TfidfVectorizer(analyzer="word", token_pattern=r"[^\s]+")
    tfidf_matrix = vectorizer.fit_transform(games_df["features"])

    print(f"[TF-IDF] Vocabulário gerado: {vectorizer.get_feature_names_out()}")
    print(f"[TF-IDF] Dimensão da matriz: {tfidf_matrix.shape}  (jogos x termos únicos)")

    return tfidf_matrix, vectorizer, games_df


def build_user_profile(
    user_ratings: List[Dict],
    games_df: pd.DataFrame,
    tfidf_matrix: np.ndarray,
    rating_scale_mid: float = 3.0,
) -> np.ndarray:
    """
    Constro o vetor de perfil do usuario a partir dos jogos que ele avaliou

    Estrategia:
        Ratings são centralizados em torno do ponto médio da escala (3.0)
        antes de serem usados como peso. Isso garante que:
 
            rating 5 → peso +2.0  → puxa o perfil PARA essas características
            rating 4 → peso +1.0  → influência positiva moderada
            rating 3 → peso  0.0  → neutro, não influencia o perfil
            rating 2 → peso -1.0  → puxa o perfil PARA LONGE dessas características
            rating 1 → peso -2.0  → afasta fortemente o perfil dessas características
 
        perfil = Σ (centered_rating_i x vetor_i)
                 normalizado para norma unitaria
 
    Referência: Géron, Hands-On ML, cap. 3 — Content-Based Filtering.

    Args:
        user_ratings: lista de dicts com chaves id e rating
            Ex: [{"id": "730", "rating": 5}, {"id": "550", "rating": 3}]
        games_df: DataFrame com os 50 jogos (necessário para mapear id → indice)
        tfidf_matrix: matriz TF-IDF dos jogos (output do build_tfidf_matrix)

    Returns:
        user_vector: vetor numpy de dimensão (1 x n_termos) representando o perfil
    """
    # Mapeia game_id → índice na matriz TF-IDF
    id_to_index = {str(game_id): idx for idx, game_id in enumerate(games_df["id"])}
 
    weighted_sum = np.zeros(tfidf_matrix.shape[1])
    games_used = []
    skipped = []
 
    for entry in user_ratings:
        game_id = str(entry["id"])
        rating  = entry.get("rating", rating_scale_mid)
 
        if game_id not in id_to_index:
            skipped.append(game_id)
            continue
 
        # Centraliza o rating: transforma 1-5 em -2 a +2
        centered_weight = rating - rating_scale_mid
 
        idx         = id_to_index[game_id]
        game_vector = tfidf_matrix[idx].toarray().flatten()
 
        weighted_sum += centered_weight * game_vector
        games_used.append((game_id, rating, centered_weight))
 
    if skipped:
        print(f"[Perfil] Jogos não encontrados no catálogo (ignorados): {skipped}")
 
    if len(games_used) == 0:
        raise ValueError("Nenhum jogo válido encontrado nos ratings do usuário.")
 
    # Normaliza o vetor resultante (norma L2 = 1)
    # Necessário pois a soma pode resultar em vetores de magnitudes muito diferentes
    norm = np.linalg.norm(weighted_sum)
    if norm > 0:
        user_vector = weighted_sum / norm
    else:
        # Todos os ratings eram 3 (neutros) — perfil zerado, sem preferência clara
        print("[Perfil] AVISO: todos os ratings são neutros (=3). Perfil sem direção clara.")
        user_vector = weighted_sum
 
    print(f"[Perfil] Jogos usados (id, rating, peso_centralizado):")
    for gid, r, w in games_used:
        print(f"         id={gid}  rating={r}  peso={w:+.1f}")
 
    return user_vector.reshape(1, -1)




def build_user_profile_positive_only(
    user_ratings: List[Dict],
    games_df: pd.DataFrame,
    tfidf_matrix: np.ndarray,
    min_rating: float = 3.0,
) -> np.ndarray:
    """
    Constroi o vetor de perfil do usuário usando APENAS jogos com rating >= min_rating.

    Estratégia:
        - Jogos com rating < min_rating são ignorados (peso = 0).
        - Jogos com rating >= min_rating entram com um peso positivo,
          por exemplo: peso = rating - (min_rating - 1)

          Ex. se min_rating = 3:
              rating 5 -> peso = 3
              rating 4 -> peso = 2
              rating 3 -> peso = 1
              rating 2 -> ignorado
              rating 1 -> ignorado

        Perfil = Σ (peso_i * vetor_i)/ Σ (peso_i), normalizado para norma unitaria.

    Args:
        user_ratings: lista de dicts com chaves id e rating
        games_df: DataFrame com os jogos (para mapear id -> índice)
        tfidf_matrix: matriz TF-IDF dos jogos

    Returns:
        user_vector: vetor numpy (1 x n_termos) representando o perfil
    """
    # Mapeia game_id -> indice na matriz TF-IDF
    id_to_index = {str(game_id): idx for idx, game_id in enumerate(games_df["id"])}

    weighted_sum = np.zeros(tfidf_matrix.shape[1])
    sum_weights = 0.0
    games_used = []
    skipped = []
    ignored_low = []

    for entry in user_ratings:
        game_id = str(entry["id"])
        rating = entry.get("rating", min_rating)

        if game_id not in id_to_index:
            skipped.append(game_id)
            continue

        # Ignora ratings abaixo do limiar
        if rating < min_rating:
            ignored_low.append((game_id, rating))
            continue

        # Ex.: min_rating = 3 -> pesos: 3->1, 4->2, 5->3
        weight = rating - (min_rating - 1)

        idx = id_to_index[game_id]
        game_vector = tfidf_matrix[idx].toarray().flatten()

        weighted_sum += weight * game_vector
        sum_weights += weight
        games_used.append((game_id, rating, weight))

    if skipped:
        print(f"[Perfil] Jogos não encontrados no catálogo (ignorados): {skipped}")
    if ignored_low:
        print(f"[Perfil] Jogos ignorados por rating baixo (<{min_rating}): {ignored_low}")

    if len(games_used) == 0:
        raise ValueError("Nenhum jogo com rating >= min_rating encontrado para o usuário.")
    
    if sum_weights > 0:
        user_vector = weighted_sum / sum_weights
    else:
        print("[Perfil] AVISO: soma de pesos zerada.")
        user_vector = weighted_sum

    # Normaliza o vetor resultante (norma L2 = 1)
    norm = np.linalg.norm(weighted_sum)
    if norm > 0:
        user_vector = weighted_sum / norm
    else:
        print("[Perfil] AVISO: vetor resultante zerado. Verifique os ratings/TF-IDF.")
        user_vector = weighted_sum

    print(f"[Perfil] Jogos usados (id, rating, peso_positivo):")
    for gid, r, w in games_used:
        print(f"         id={gid}  rating={r}  peso={w:.1f}")

    print("[Perfil]")
    return user_vector.reshape(1, -1)



def find_knn_recommendations(
    user_vector: np.ndarray,
    tfidf_matrix,
    games_df: pd.DataFrame,
    user_ratings: List[Dict],
    k: int = 10,
) -> pd.DataFrame:
    """
    Encontra os K jogos mais similares ao perfil do usuário usando KNN
    com métrica de similaridade de cosseno.

    Similaridade de cosseno:
        sim(A, B) = (A · B) / (||A|| x ||B||)
        Valor entre 0 (nenhuma similaridade) e 1 (idênticos).

    Jogos já avaliados pelo usuário são excluídos dos resultados.

    Args:
        user_vector: vetor do perfil do usuário (1 x n_termos)
        tfidf_matrix: matriz TF-IDF dos jogos
        games_df: DataFrame com informações dos jogos
        user_ratings: jogos já avaliados (para excluir dos resultados)
        k: número de recomendações a retornar

    Returns:
        DataFrame com os K jogos recomendados e seus scores de similaridade
    """
    # IDs já avaliados pelo usuário — serão excluídos
    rated_ids = {str(entry["id"]) for entry in user_ratings}

    # Converte a matriz TF-IDF para array denso para o cálculo
    tfidf_dense = tfidf_matrix.toarray()

    # Calcula similaridade de cosseno entre perfil do usuário e todos os jogos
    similarities = cosine_similarity(user_vector, tfidf_dense).flatten()

    # Monta DataFrame com scores
    results = games_df.copy()
    results["similarity_score"] = similarities

    # Remove jogos já avaliados pelo usuário
    results = results[~results["id"].astype(str).isin(rated_ids)]

    # Ordena por similaridade decrescente e retorna top-K
    recommendations = (
        results
        .sort_values("similarity_score", ascending=False)
        .head(k)
        .reset_index(drop=True)
    )

    return recommendations[["id", "name", "genre", "perspective", "category", "similarity_score"]]




class KNNRecommender:
    """
    Singleton
    classe principal do sistema de recomendação KNN content-based.
    """

    def __init__(self, games_filepath: str, k: int = 15):
        self.games_filepath = games_filepath
        self.games_df = None
        self.tfidf_matrix = None
        self.vectorizer = None
        self._fitted = False
        self.k = k

    def fit(self):
        """Carrega os dados e treina o TF-IDF (base de conhecimento)"""
        self.games_df = load_games(self.games_filepath)
        self.tfidf_matrix, self.vectorizer, self.games_df = build_tfidf_matrix(self.games_df)
        self._fitted = True
        print(f"[KNNRecommender] Pronto. {len(self.games_df)} jogos carregados.")
        return self

    def recommend(self, user_ratings: List[Dict]) -> pd.DataFrame:
        """
        Recebe os ratings do usuário e retorna os K jogos mais recomendados.

        Args:
            user_ratings: lista de dicts com id e rating (1-5)

        Returns:
            DataFrame com top-K recomendações e scores de similaridade
        """
        k = self.k
        if not self._fitted:
            raise RuntimeError("Chame fit() antes de recommend().")

        user_vector = build_user_profile_positive_only(user_ratings, self.games_df, self.tfidf_matrix)
        recommendations = find_knn_recommendations(
            user_vector, self.tfidf_matrix, self.games_df, user_ratings, k=k
        )
        return recommendations



if __name__ == "__main__":
    GAMES_FILE_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../..", "data", "50_games.json")
    )
    if not os.path.exists(GAMES_FILE_PATH):
        print("arquivo nao encontrado: ", GAMES_FILE_PATH)
        sys.exit()

    # 1. Inicializa e treina o recomendador
    k_neighb = 25
    recommender = KNNRecommender(GAMES_FILE_PATH, k=k_neighb)
    recommender.fit()

    # 2. simulçao: dados mock
    user_ratings = [
        {"id": "227300",     "name": "Euro Truck Simulator 2",    "rating": 5},
        {"id": "292030", "name": "The Witcher 3: Wild Hunt",     "rating": 1},
        {"id": "814380",    "name": "Sekiro™: Shadows Die Twice - GOTY Edition", "rating": 1},
        {"id": "730",     "name": "Counter-Strike 2",  "rating": 5},
        {"id": "365670",     "name": "Blender",   "rating": 1},
    ]

    recommendations = recommender.recommend(user_ratings)

    print(f"\n=== TOP {k_neighb} JOGOS RECOMENDADOS ===")
    print(recommendations.to_string(index=False))
