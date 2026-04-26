import pandas as pd
from typing import List, Dict
from knn_recommender import build_user_profile, find_knn_recommendations

def cross_validate_k(
    tfidf_matrix,
    games_df: pd.DataFrame,
    utility_matrix: pd.DataFrame,
    k_values: List[int] = None,
    n_folds: int = 5,
) -> Dict:
    """
    Usa cross-validation para encontrar o melhor valor de K.

    Estratégia Leave-One-Out simplificada:
        Para cada usuário da matriz de utilidade:
            1. Esconde um jogo que ele avaliou com nota ≥ 4 (jogo alvo)
            2. Constrói o perfil com os jogos restantes
            3. Verifica se o jogo alvo aparece no top-K recomendado
            4. Métrica: hit rate = proporção de acertos

    Args:
        tfidf_matrix: matriz TF-IDF dos jogos
        games_df: DataFrame com os 50 jogos
        utility_matrix: DataFrame 100x50 com ratings dos usuários
        k_values: lista de valores de K a testar (default: [3, 5, 7, 10, 15])
        n_folds: número de usuários a amostrar por fold

    Returns:
        Dict com hit_rate para cada K e o melhor K encontrado
    """
    if k_values is None:
        k_values = [3, 5, 7, 10, 15]

    id_to_index = {str(gid): idx for idx, gid in enumerate(games_df["id"])}
    results = {}

    for k in k_values:
        hits = 0
        total = 0

        # Amostra n_folds usuários aleatoriamente
        sampled_users = utility_matrix.sample(min(n_folds, len(utility_matrix)))

        for _, user_row in sampled_users.iterrows():
            # Pega jogos que o usuário avaliou com nota ≥ 4
            liked_games = [
                col for col in utility_matrix.columns
                if pd.notna(user_row[col]) and user_row[col] >= 4
            ]

            if len(liked_games) < 2:
                continue  # precisa de pelo menos 2 jogos para esconder um

            # Esconde um jogo (jogo alvo)
            target_game = liked_games[-1]
            training_games = liked_games[:-1]

            # Constrói ratings de treino
            training_ratings = [
                {"id": gid, "rating": int(user_row[gid])}
                for gid in training_games
                if str(gid) in id_to_index
            ]

            if not training_ratings:
                continue

            try:
                user_vector = build_user_profile(training_ratings, games_df, tfidf_matrix)
                recs = find_knn_recommendations(
                    user_vector, tfidf_matrix, games_df, training_ratings, k=k
                )

                # Verifica se o jogo alvo está no top-K
                recommended_ids = set(recs["id"].astype(str))
                if str(target_game) in recommended_ids:
                    hits += 1
                total += 1

            except ValueError:
                continue

        hit_rate = hits / total if total > 0 else 0.0
        results[k] = {"hit_rate": round(hit_rate, 4), "hits": hits, "total": total}
        print(f"[Cross-Val] K={k:2d} → Hit Rate: {hit_rate:.4f} ({hits}/{total})")

    best_k = max(results, key=lambda k: results[k]["hit_rate"])
    results["best_k"] = best_k
    print(f"\n[Cross-Val] Melhor K encontrado: {best_k}")

    return results



if __name__ == "main":
    # utility_matrix = pd.read_csv("data/utility_matrix.csv", index_col=0)
    # best_k = recommender.find_best_k(utility_matrix)
    # print(f"\nMelhor K: {best_k}")
    pass