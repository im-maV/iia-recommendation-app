import pytest
from ml.content_based.knn_recommender import KNNRecommender

def test_knn_recommender():
    recommender = KNNRecommender()
    ratings = [{"game_id": 1, "rating": 5}, {"game_id": 2, "rating": 3}]
    result = recommender.recommend(ratings, top_n=2)
    assert isinstance(result, list)
    # assert len(result) == 2  # quando implementado
