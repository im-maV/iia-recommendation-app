# api/routes/recommendations.py
from pydantic import BaseModel
from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from api.db import users
from api.schemas.game_schema import Game
import time

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationRequest(BaseModel):
    games: list[Game]

@router.post("/")
def get_recommendations(body: RecommendationRequest):
    time.sleep(3)
    return body