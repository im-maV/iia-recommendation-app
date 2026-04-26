from fastapi import APIRouter
from data.utils import get_most_popular

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/")
def get_games():
    games = get_most_popular()
    return games
