"""
evaluation.py — Métricas de avaliação do sistema de recomendação KNN
=====================================================================
Responsabilidade ÚNICA deste módulo: calcular métricas de qualidade
das recomendações dado um conjunto de usuários e um KNNRecommender.

IMPORTANTE — Por que não usamos train/test split clássico:
    O KNN content-based não aprende parâmetros dos dados de treino.
    Ele constrói vetores fixos (One-Hot Encoding via CountVectorizer)
    e calcula similaridade de cosseno. Portanto, overfitting/underfitting
    no sentido clássico não se aplica ao modelo em si.

    O que avaliamos é a QUALIDADE DAS RECOMENDAÇÕES usando a matriz
    de utilidade como ground truth — simulando usuários reais.

Estratégia — Hold-out por usuário (Leave-Some-Out):
    Para cada usuário:
        - Jogos com rating >= threshold  → "jogos relevantes"
        - Esconde 20% desses jogos       → conjunto de teste (ground truth)
        - Usa o restante para perfil     → conjunto de "treino"
        - Mede se os jogos escondidos aparecem nas top-K recomendações

NOTA — Cross-validation e escolha do melhor K estão em cross_validation.py.
    Este módulo exporta apenas as funções de divisão e métricas.

Referências:
    - Géron, A. Hands-On ML, cap. 3 — Avaliação de modelos
    - Abu-Mostafa et al. Learning from Data, cap. 4 — Validação
"""

import math
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple

from knn_recommender import KNNRecommender


# =============================================================================
# PASSO 1 — Divisão hold-out por usuário
# =============================================================================

def split_user_ratings(
    user_row: pd.Series,
    relevance_threshold: float = 4.0,
    test_ratio: float = 0.2,
    random_state: int = 42,
) -> Tuple[List[Dict], List[str]]:
    """
    Divide os ratings de um usuário em perfil (treino) e ground truth (teste).

    Estratégia:
        1. Filtra apenas jogos avaliados (não nulos)
        2. Dos jogos com nota >= threshold, sorteia test_ratio% como teste
        3. O restante (incluindo jogos com nota baixa) constrói o perfil

    Por que random_state único por usuário?
        Evita que todos os usuários escondam sempre o mesmo "slot" de jogo,
        o que causaria viés sistemático nas métricas.
        Convenção: passe (base_seed + user_idx) ao chamar esta função.

    Args:
        user_row           : linha da matriz de utilidade (ratings de 1 usuário)
        relevance_threshold: nota mínima para jogo "relevante" (default 4)
        test_ratio         : proporção dos relevantes a esconder (default 20%)
        random_state       : semente aleatória — use seed único por usuário

    Returns:
        train_ratings: lista de dicts {"id": ..., "rating": ...} para o perfil
        test_game_ids: lista de IDs escondidos (ground truth)
    """
    rng = np.random.RandomState(random_state)

    all_rated = {
        str(game_id): rating
        for game_id, rating in user_row.items()
        if pd.notna(rating)
    }

    if len(all_rated) < 2:
        return [], []   # avaliações insuficientes — pula usuário

    relevant_ids = [
        gid for gid, r in all_rated.items()
        if r >= relevance_threshold
    ]

    if len(relevant_ids) < 2:
        return [], []   # precisa de >= 2 relevantes para esconder ao menos 1

    n_test   = max(1, math.ceil(len(relevant_ids) * test_ratio))
    test_ids = list(rng.choice(relevant_ids, size=n_test, replace=False))
    test_set = set(test_ids)

    train_ratings = [
        {"id": gid, "rating": int(r)}
        for gid, r in all_rated.items()
        if gid not in test_set
    ]

    return train_ratings, test_ids


# =============================================================================
# PASSO 2 — Métricas de avaliação
# =============================================================================

def precision_at_k(
    recommended_ids: List[str],
    relevant_ids: List[str],
    k: int,
) -> float:
    """
    Precision@K: fração dos K recomendados que são relevantes.

        Precision@K = |relevantes ∩ top-K| / K

    Exemplo: K=10, 3 acertos → Precision@10 = 0.30
    """
    if k <= 0:
        return 0.0
    top_k        = set(recommended_ids[:k])
    relevant_set = set(relevant_ids)
    return len(top_k & relevant_set) / k


def recall_at_k(
    recommended_ids: List[str],
    relevant_ids: List[str],
    k: int,
) -> float:
    """
    Recall@K: fração dos relevantes que o sistema encontrou no top-K.

        Recall@K = |relevantes ∩ top-K| / |relevantes|

    Exemplo: 5 relevantes, 2 encontrados → Recall@K = 0.40
    """
    if not relevant_ids:
        return 0.0
    top_k        = set(recommended_ids[:k])
    relevant_set = set(relevant_ids)
    return len(top_k & relevant_set) / len(relevant_set)


def ndcg_at_k(
    recommended_ids: List[str],
    relevant_ids: List[str],
    k: int,
) -> float:
    """
    NDCG@K (Normalized Discounted Cumulative Gain):
    Penaliza acertos que aparecem no final da lista — acertos no topo valem mais.

        DCG@K   = Σ  1 / log2(posição + 1)   para acertos nas posições 1..K
        NDCG@K  = DCG@K / DCG_ideal@K

    Valor entre 0.0 (péssimo) e 1.0 (perfeito).
    """
    relevant_set = set(relevant_ids)
    dcg = sum(
        1.0 / math.log2(i + 2)           # i+2: evita log2(1)=0
        for i, gid in enumerate(recommended_ids[:k])
        if gid in relevant_set
    )
    ideal_hits = min(len(relevant_ids), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))
    return dcg / idcg if idcg > 0 else 0.0


def f1_at_k(
    recommended_ids: List[str],
    relevant_ids: List[str],
    k: int,
) -> float:
    """
    F1@K: média harmônica entre Precision@K e Recall@K.
    Útil quando precisão e recall têm importância igual.
    """
    p = precision_at_k(recommended_ids, relevant_ids, k)
    r = recall_at_k(recommended_ids, relevant_ids, k)
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


# =============================================================================
# PASSO 3 — Avaliação final sobre todos os usuários
# =============================================================================

def evaluate(
    recommender: KNNRecommender,
    utility_matrix: pd.DataFrame,
    k: int = 10,
    relevance_threshold: float = 4.0,
    test_ratio: float = 0.2,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Avalia o sistema sobre todos os usuários da matriz de utilidade.

    Usado para avaliação final com o melhor K encontrado pelo cross_validation.py.
    A média das métricas é PONDERADA pelo número de jogos de teste de cada
    usuário — usuários com mais jogos escondidos têm mais peso.

    Args:
        recommender        : instância treinada de KNNRecommender
        utility_matrix     : DataFrame 100×50 com ratings dos usuários
        k                  : tamanho da lista de recomendação
        relevance_threshold: nota mínima para jogo relevante
        test_ratio         : proporção de relevantes usados como teste
        random_state       : semente base (incrementada por posição do usuário)

    Returns:
        DataFrame com métricas por usuário + linha de médias ponderadas
    """
    results = []

    for user_pos, (user_id, user_row) in enumerate(utility_matrix.iterrows()):
        user_seed = random_state + user_pos   # seed único por usuário

        train_ratings, test_ids = split_user_ratings(
            user_row, relevance_threshold, test_ratio, user_seed
        )

        if not train_ratings or not test_ids:
            continue

        try:
            recs            = recommender.recommend(train_ratings, k=k)
            recommended_ids = [str(r["name"]) for r in recs]  # lista de dicts → nomes
        except Exception as e:
            print(f"[Eval] ERRO ao recomendar para {user_id}: {e}")
            continue

        results.append({
            "user_id":     user_id,
            "n_train":     len(train_ratings),
            "n_test":      len(test_ids),
            "precision@k": precision_at_k(recommended_ids, test_ids, k),
            "recall@k":    recall_at_k(recommended_ids, test_ids, k),
            "ndcg@k":      ndcg_at_k(recommended_ids, test_ids, k),
            "f1@k":        f1_at_k(recommended_ids, test_ids, k),
        })

    if not results:
        raise ValueError("Nenhum usuário com dados suficientes para avaliação.")

    df      = pd.DataFrame(results)
    weights = df["n_test"].values   # média ponderada pelo tamanho do ground truth

    summary_vals = {
        col: float(np.average(df[col].values, weights=weights))
        for col in ["precision@k", "recall@k", "ndcg@k", "f1@k"]
    }
    summary_vals.update({
        "user_id": "MÉDIA_PONDERADA",
        "n_train": float(df["n_train"].mean()),
        "n_test":  float(df["n_test"].mean()),
    })

    print(f"\n{'='*52}")
    print(f"AVALIAÇÃO FINAL  (K={k}, threshold={relevance_threshold})")
    print(f"{'='*52}")
    print(f"Usuários avaliados : {len(df)}")
    print(f"Precision@{k:<3}      : {summary_vals['precision@k']:.4f}")
    print(f"Recall@{k:<6}      : {summary_vals['recall@k']:.4f}")
    print(f"NDCG@{k:<8}      : {summary_vals['ndcg@k']:.4f}")
    print(f"F1@{k:<10}      : {summary_vals['f1@k']:.4f}")
    print(f"{'='*52}\n")

    return pd.concat(
        [df, pd.DataFrame([summary_vals])],
        ignore_index=True,
    )