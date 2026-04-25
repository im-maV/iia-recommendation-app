from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.routes import recommendations, users, games
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(recommendations.router)
app.include_router(games.router)


@app.get("/")
def root():
    return RedirectResponse(url="/users/register")

@app.get("/recommendations/health")
def health_check():
    return {"status": "ok"}
