from pydantic import BaseModel

class Game(BaseModel):
    id: str
    name: str
    genre: str
    perspective: str
    category: str