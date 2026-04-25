from fastapi import APIRouter
from fastapi.responses import JSONResponse
from data.utils import get_allgames

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/")
def get_games():
    games =  get_allgames()
    return games

