from pydantic import BaseModel
from fastapi import APIRouter, Request
from api.schemas.game_schema import RatedGame
import time

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationRequest(BaseModel):
    games: list[RatedGame]


@router.post("/")
def get_recommendations(body: RecommendationRequest, request: Request):
    user_ratings = [{"id": g.id, "rating": g.rating} for g in body.games]
    recommender = request.app.state.knn_recommender

    time.sleep(2)
    return recommender.recommend(user_ratings)
