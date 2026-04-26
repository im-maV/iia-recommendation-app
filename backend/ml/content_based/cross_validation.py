"""
cross_validation.py — Validação Cruzada K-Fold para KNN Recommender
=====================================================================
Encontra o melhor valor de K testando múltiplos valores via K-Fold
Cross-Validation sobre os usuários da matriz de utilidade.

POR QUE NÃO USAMOS sklearn.model_selection.KFold:
    KFold do sklearn divide amostras independentes para modelos com
    interface fit/predict (ex: regressão, SVM). Aqui, o KNNRecommender
    não aprende dos usuários de treino — cada usuário é avaliado de forma
    completamente independente. Portanto:
      - Os usuários do fold de "treino" NÃO alimentam o modelo
      - cross_val_score do sklearn exigiria fit/predict compatível
      - A divisão manual em folds é equivalente e mais transparente
    O que os folds fazem aqui é apenas garantir que TODOS os 100 usuários
    sejam usados como conjunto de teste exatamente uma vez.

ESTRUTURA DOS FOLDS (5 folds, 100 usuários):
    Fold 1: usuários 0-19  → avaliados como teste
    Fold 2: usuários 20-39 → avaliados como teste
    ...
    Fold 5: usuários 80-99 → avaliados como teste

ESTRATÉGIA DENTRO DE CADA USUÁRIO DE TESTE:
    - Jogos com rating >= threshold (>=4)  → relevantes
    - 20% dos relevantes escondidos        → ground truth
    - 80% restantes + notas baixas         → constroem o perfil
    - Sistema recomenda top-K              → comparamos com ground truth

MÉDIA ENTRE FOLDS:
    Ponderada pelo número de usuários válidos em cada fold.
    Folds com mais usuários (após descarte por dados insuficientes)
    têm mais peso — evita distorção por folds com poucos usuários válidos.

Referências:
    - Géron, A. Hands-On ML, cap. 3 — Validação cruzada
    - Abu-Mostafa et al. Learning from Data, cap. 4 — Cross-validation
    - Russell & Norvig, AIMA 4th ed., cap. 19 — Avaliação de modelos
"""

import json
import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple

from knn_recommender import KNNRecommender
from evaluation import (
    split_user_ratings,
    precision_at_k,
    recall_at_k,
    ndcg_at_k,
    f1_at_k,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
sys.path.append(BASE_DIR)
sys.path.append(ROOT_DIR)


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

K_VALUES    = [3, 5, 7, 9, 11, 13, 15, 17, 19, 21]
N_FOLDS     = 5
TEST_RATIO  = 0.2    # 20% dos ratings relevantes de cada usuário → teste
REL_THRESH  = 4.0    # nota mínima para considerar jogo "relevante"
BEST_K_PATH = Path("data/best_k.json")


# =============================================================================
# PASSO 1 — Divisão dos usuários em K folds
# =============================================================================

def build_user_folds(
    utility_matrix: pd.DataFrame,
    n_folds: int = N_FOLDS,
    random_state: int = 42,
) -> List[List[int]]:
    """
    Divide os índices dos usuários em n_folds grupos de tamanho igual.

    A divisão é ALEATÓRIA com seed fixo para reprodutibilidade.
    Aleatoriedade evita viés de ordenação (usuários gerados em sequência
    podem ter padrões sistemáticos de ratings).

    Args:
        utility_matrix: DataFrame 100×50 com ratings
        n_folds       : número de folds (default 5 → grupos de 20 usuários)
        random_state  : semente para reprodutibilidade

    Returns:
        Lista de n_folds listas com os índices dos usuários de cada fold
        Ex: [[3,17,42,...], [1,8,23,...], ...]
    """
    rng           = np.random.RandomState(random_state)
    user_indices  = np.arange(len(utility_matrix))
    rng.shuffle(user_indices)

    folds = [fold.tolist() for fold in np.array_split(user_indices, n_folds)]

    print(f"[CV] {len(utility_matrix)} usuários divididos em {n_folds} folds:")
    for i, fold in enumerate(folds):
        print(f"     Fold {i+1}: {len(fold)} usuários")

    return folds


# =============================================================================
# PASSO 2 — Avaliação de um único fold para um valor de K
# =============================================================================

def evaluate_fold(
    recommender: KNNRecommender,
    utility_matrix: pd.DataFrame,
    name_to_id: Dict[str, str],
    test_user_indices: List[int],
    k: int,
    relevance_threshold: float = REL_THRESH,
    test_ratio: float = TEST_RATIO,
    random_state: int = 42,
) -> Dict:
    """
    Avalia as recomendações para os usuários de teste de um fold.

    MAPEAMENTO DE IDs:
        A matriz de utilidade usa nomes de jogos como colunas
        (ex: "Rust", "PUBG: BATTLEGROUNDS").
        O KNNRecommender indexa por ID numérico do Steam (ex: "252490").
        Por isso, antes de chamar recommend(), convertemos:
            nome_coluna → id_numerico  (via name_to_id)
        E depois de receber as recomendações, convertemos de volta:
            id_numerico → nome  (para comparar com test_ids que são nomes)

    Para cada usuário do fold:
        1. split_user_ratings → train_ratings com nomes como game_id
        2. Converte nomes → IDs numéricos para o recommend()
        3. recommend(k=k) → lista de dicts com "name" e "id"
        4. Extrai nomes das recomendações → compara com test_ids (nomes)
        5. Calcula métricas

    A média das métricas dentro do fold é PONDERADA pelo número de
    jogos de teste de cada usuário (n_test).

    Args:
        recommender       : instância treinada de KNNRecommender (fit() já chamado)
        utility_matrix    : matriz de utilidade completa (colunas = nomes dos jogos)
        name_to_id        : dict {nome_jogo: id_numerico_steam}
        test_user_indices : índices dos usuários deste fold de teste
        k                 : valor de K a avaliar
        relevance_threshold: nota mínima para relevância
        test_ratio        : proporção de ratings relevantes escondidos
        random_state      : semente base (incrementada por user_idx)

    Returns:
        Dict com métricas ponderadas do fold e contagens de usuários
    """
    precision_list, recall_list, ndcg_list, f1_list = [], [], [], []
    n_test_list = []
    skipped = 0

    for user_idx in test_user_indices:
        user_row  = utility_matrix.iloc[user_idx]
        user_seed = random_state + user_idx

        # test_ids e train_ratings usam NOMES como game_id (colunas da matriz)
        train_ratings, test_ids = split_user_ratings(
            user_row,
            relevance_threshold=relevance_threshold,
            test_ratio=test_ratio,
            random_state=user_seed,
        )

        if not train_ratings or not test_ids:
            skipped += 1
            continue

        # Converte train_ratings de {nome → rating} para {id_numerico → rating}
        # O recommend() espera id numérico para indexar no games_df
        train_ratings_by_id = []
        for entry in train_ratings:
            game_id = name_to_id.get(entry["id"])
            if game_id is not None:
                train_ratings_by_id.append({"id": game_id, "rating": entry["rating"]})

        if not train_ratings_by_id:
            skipped += 1
            continue

        try:
            # recommend() retorna lista de dicts com "name", "id", "score", etc.
            # Passamos k explicitamente pois o CV testa vários valores de K
            recs = recommender.recommend(train_ratings_by_id, k=k)

            # Extrai NOMES para comparar com test_ids (que são nomes da matriz)
            recommended_names = [str(r["name"]) for r in recs]
        except Exception as e:
            print(f"[CV] ERRO ao recomendar para user_idx={user_idx}: {e}")
            skipped += 1
            continue

        precision_list.append(precision_at_k(recommended_names, test_ids, k))
        recall_list.append(recall_at_k(recommended_names, test_ids, k))
        ndcg_list.append(ndcg_at_k(recommended_names, test_ids, k))
        f1_list.append(f1_at_k(recommended_names, test_ids, k))
        n_test_list.append(len(test_ids))

    n_valid = len(precision_list)

    if n_valid == 0:
        print(f"[CV] AVISO: fold zerado — {len(test_user_indices)} usuários descartados.")
        print(f"           Causas possíveis:")
        print(f"             (1) threshold={relevance_threshold} alto demais para a escala da matriz")
        print(f"             (2) mapeamento nome→id falhou (cheque name_to_id)")
        print(f"             (3) usuários têm < 2 jogos com rating >= threshold")
        return {
            "precision": 0.0, "recall": 0.0, "ndcg": 0.0, "f1": 0.0,
            "n_users": 0, "skipped": skipped,
        }

    weights = np.array(n_test_list, dtype=float)

    return {
        "precision": float(np.average(precision_list, weights=weights)),
        "recall":    float(np.average(recall_list,    weights=weights)),
        "ndcg":      float(np.average(ndcg_list,      weights=weights)),
        "f1":        float(np.average(f1_list,        weights=weights)),
        "n_users":   n_valid,
        "skipped":   skipped,
    }


# =============================================================================
# PASSO 3 — Cross-validation completa para todos os K
# =============================================================================

def run_cross_validation(
    recommender: KNNRecommender,
    utility_matrix: pd.DataFrame,
    k_values: List[int] = None,
    n_folds: int = N_FOLDS,
    relevance_threshold: float = REL_THRESH,
    test_ratio: float = TEST_RATIO,
    primary_metric: str = "ndcg",
    random_state: int = 42,
) -> Tuple[int, pd.DataFrame]:
    """
    Executa K-Fold Cross-Validation para cada valor de K e retorna o melhor.

    Fluxo:
        1. Divide usuários em n_folds grupos aleatórios (feito uma única vez)
        2. Para cada valor de K:
              Para cada fold → avalia os usuários do fold com aquele K
              Média PONDERADA das métricas entre folds (peso = n_users válidos)
        3. Escolhe o K com maior primary_metric médio

    A média entre folds é ponderada pelo número de usuários válidos em cada
    fold — folds com mais usuários (após descartes) têm mais peso.

    Args:
        recommender        : instância treinada de KNNRecommender
        utility_matrix     : DataFrame 100×50 com ratings
        k_values           : valores de K a testar
        n_folds            : número de folds (default 5)
        relevance_threshold: nota mínima para jogos relevantes
        test_ratio         : proporção de ratings relevantes usados como teste
        primary_metric     : métrica para escolher o melhor K
        random_state       : semente aleatória

    Returns:
        best_k     : melhor valor de K encontrado
        results_df : DataFrame completo com métricas por K e por fold
    """
    if k_values is None:
        k_values = K_VALUES

    # Mapeamento nome_do_jogo → id_numerico_steam
    # A matriz tem colunas com nomes; o recommend() espera IDs numéricos.
    # Construímos o dict uma única vez a partir do games_df do recommender.
    name_to_id: Dict[str, str] = {
        str(row["name"]): str(row["id"])
        for _, row in recommender.games_df.iterrows()
    }
    n_mapeados = sum(1 for col in utility_matrix.columns if col in name_to_id)
    print(f"[CV] Mapeamento nome→id: {n_mapeados}/{len(utility_matrix.columns)} "
          f"colunas da matriz encontradas no catálogo.")
    if n_mapeados == 0:
        raise ValueError(
            "Nenhuma coluna da matriz bate com os nomes em games_df. "
            "Verifique se a matriz usa nomes exatamente iguais ao campo 'name' dos jogos."
        )

    folds    = build_user_folds(utility_matrix, n_folds, random_state)
    all_rows = []

    print(f"\n{'='*65}")
    print(f"CROSS-VALIDATION — {n_folds} folds × {len(k_values)} valores de K")
    print(f"Métrica principal    : {primary_metric.upper()}@K")
    print(f"K testados           : {k_values}")
    print(f"Threshold relevância : rating >= {relevance_threshold}")
    print(f"Test ratio/usuário   : {int(test_ratio*100)}% dos ratings relevantes")
    print(f"Média entre folds    : ponderada por n_users válidos")
    print(f"{'='*65}\n")

    for k in k_values:
        fold_results = []

        for fold_idx, test_indices in enumerate(folds):
            fold_result = evaluate_fold(
                recommender=recommender,
                utility_matrix=utility_matrix,
                name_to_id=name_to_id,
                test_user_indices=test_indices,
                k=k,
                relevance_threshold=relevance_threshold,
                test_ratio=test_ratio,
                random_state=random_state,
            )
            fold_results.append(fold_result)

            all_rows.append({
                "k":         k,
                "fold":      fold_idx + 1,
                "precision": round(fold_result["precision"], 4),
                "recall":    round(fold_result["recall"],    4),
                "ndcg":      round(fold_result["ndcg"],      4),
                "f1":        round(fold_result["f1"],        4),
                "n_users":   fold_result["n_users"],
                "skipped":   fold_result["skipped"],
            })

        # ── Média PONDERADA entre folds (peso = n_users válidos) ──────────
        fold_weights = np.array([m["n_users"] for m in fold_results], dtype=float)

        if fold_weights.sum() == 0:
            mean_p, mean_r, mean_ndcg, mean_f1 = 0.0, 0.0, 0.0, 0.0
        else:
            mean_p    = float(np.average([m["precision"] for m in fold_results], weights=fold_weights))
            mean_r    = float(np.average([m["recall"]    for m in fold_results], weights=fold_weights))
            mean_ndcg = float(np.average([m["ndcg"]      for m in fold_results], weights=fold_weights))
            mean_f1   = float(np.average([m["f1"]        for m in fold_results], weights=fold_weights))

        all_rows.append({
            "k":         k,
            "fold":      "MÉDIA",
            "precision": round(mean_p,    4),
            "recall":    round(mean_r,    4),
            "ndcg":      round(mean_ndcg, 4),
            "f1":        round(mean_f1,   4),
            "n_users":   int(fold_weights.sum()),
            "skipped":   sum(m["skipped"] for m in fold_results),
        })

        print(f"K={k:2d} | Precision={mean_p:.4f} | Recall={mean_r:.4f} "
              f"| NDCG={mean_ndcg:.4f} | F1={mean_f1:.4f}")

    results_df = pd.DataFrame(all_rows)

    # Escolhe o melhor K pelas linhas de média
    summary  = results_df[results_df["fold"] == "MÉDIA"].copy()
    best_idx = summary[primary_metric].idxmax()
    best_k   = int(summary.loc[best_idx, "k"])
    best_score = summary.loc[best_idx, primary_metric]

    print(f"\n{'='*65}")
    print(f"MELHOR K ENCONTRADO : {best_k}")
    print(f"  {primary_metric.upper()}@{best_k} = {best_score:.4f}")
    print(f"{'='*65}\n")

    return best_k, results_df


# =============================================================================
# PASSO 4 — Persistência e leitura do melhor K
# =============================================================================

def save_best_k(
    best_k: int,
    results_df: pd.DataFrame,
    path: Path = BEST_K_PATH,
) -> None:
    """
    Salva o melhor K e resumo dos resultados em disco (data/best_k.json).
    Lido pelo train.py no startup do servidor FastAPI.

    Formato:
    {
        "best_k": 11,
        "k_values": [7, 9, 11, ...],
        "cv_results": {
            "7":  {"precision": 0.32, "recall": 0.28, "ndcg": 0.41, "f1": 0.30},
            ...
        }
    }
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    summary = results_df[results_df["fold"] == "MÉDIA"].set_index("k")
    cv_summary = {
        str(int(k)): {
            "precision": float(row["precision"]),
            "recall":    float(row["recall"]),
            "ndcg":      float(row["ndcg"]),
            "f1":        float(row["f1"]),
        }
        for k, row in summary.iterrows()
    }

    path.write_text(json.dumps({
        "best_k":     best_k,
        "k_values":   K_VALUES,
        "cv_results": cv_summary,
    }, indent=2))

    print(f"[CV] Resultados salvos em: {path}")


def load_best_k(path: Path = BEST_K_PATH, default_k: int = 10) -> int:
    """
    Lê o melhor K salvo em disco.
    Chamado pelo train.py no startup do servidor FastAPI.

    Returns:
        Melhor K salvo, ou default_k se o arquivo não existir.
    """
    if not path.exists():
        print(f"[CV] {path} não encontrado. Usando K padrão: {default_k}")
        return default_k

    data   = json.loads(path.read_text())
    best_k = data.get("best_k", default_k)
    print(f"[CV] Melhor K carregado do disco: {best_k}")
    return best_k


# =============================================================================
# ENTRYPOINT
# python cross_validation.py
# =============================================================================

if __name__ == "__main__":

    GAMES_PATH   = os.path.join(BASE_DIR, "..", "..", "data", "50_games.json")
    UTILITY_PATH = os.path.join(BASE_DIR, "..", "..", "data", "utility_matrix.csv")

    if not os.path.exists(UTILITY_PATH):
        print(f"[ERRO] Matriz de utilidade não encontrada: {UTILITY_PATH}")
        sys.exit(1)

    print("[CV] Carregando dados e modelo...")
    # KNNRecommender sem k fixo — o k será passado em cada chamada de recommend()
    recommender = KNNRecommender()
    recommender.fit()

    utility_matrix = pd.read_csv(UTILITY_PATH, index_col=0)
    print(f"[CV] Matriz carregada: {utility_matrix.shape[0]} usuários × "
          f"{utility_matrix.shape[1]} jogos")

    best_k, results_df = run_cross_validation(
        recommender=recommender,
        utility_matrix=utility_matrix,
        k_values=K_VALUES,
        n_folds=N_FOLDS,
        relevance_threshold=REL_THRESH,
        test_ratio=TEST_RATIO,
        primary_metric="ndcg",
        random_state=42,
    )

    save_best_k(best_k, results_df)

    print("\nRESUMO FINAL — médias ponderadas entre folds por K:")
    summary = results_df[results_df["fold"] == "MÉDIA"][
        ["k", "precision", "recall", "ndcg", "f1", "n_users"]
    ].reset_index(drop=True)
    print(summary.to_string(index=False))
    print(f"\nExecute o servidor FastAPI — ele usará K={best_k} automaticamente.")