class KNNRecommender:
    def __init__(self):
        # TODO: inicializar dados/modelo
        pass

    def recommend(self, ratings, top_n=10):
        # Mock: retorna recomendações estáticas para integração
        return [
            {
                "game_id": i+1,
                "title": f"Game {i+1}",
                "score": 0.9 - i*0.05,
                "score_content": 0.9 - i*0.05,
                "score_collaborative": 0.8 - i*0.04
            }
            for i in range(top_n)
        ]
