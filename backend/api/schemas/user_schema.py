from pydantic import BaseModel
from typing import List

class UserRating(BaseModel):
    game_id: int
    rating: int

class UserProfileRequest(BaseModel):
    ratings: List[UserRating]

class UserProfileResponse(BaseModel):
    user_id: int
