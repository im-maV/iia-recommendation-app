from pydantic import BaseModel
from typing import List, Optional

class RecommendationItem(BaseModel):
    game_id: int
    title: str
    genre: str
    perspective: str
    category: str

class RecommendationRequest(BaseModel):
    ratings: List[dict]
    top_n: int = 10
    alpha: float = 0.5

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
