# api/routes/users.py

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
import uuid
from api.db import users
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])



class UserCreate(BaseModel):
    name: str

@router.get("/register")
def get_register():
    return {"message": "Envie seu nome via POST"}


@router.post("/register")
def register(data: UserCreate):
    user_id = str(uuid.uuid4())

    user = {
        "id": user_id,
        "name": data.name,
        "games": [],
        "ratings": {}
    }

    users[user_id] = user
    return user
    


@router.get("/profile")
def get_profile(user_id: str):
    if user_id not in users:
        return RedirectResponse(url="/users/register")

    return {
        "message": "Envie jogos e notas",
        "example": {
            "games": ["Zelda", "FIFA"],
            "ratings": {"Zelda": 5, "FIFA": 3}
        }
    }


@router.post("/profile")
def set_profile(user_id: str, data: dict):
    if user_id not in users:
        return RedirectResponse(url="/users/register")

    users[user_id]["games"] = data.get("games", [])
    users[user_id]["ratings"] = data.get("ratings", {})

    return RedirectResponse(
        url=f"/recommendations?user_id={user_id}",
        status_code=303
    )