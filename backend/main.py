from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.routes import recommendations, users, games
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from data.data_loader import get_utility_matrix


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] Inicializando server...")
    app.state.utility_matrix = get_utility_matrix()
    print(f"[startup] Matriz carregada: {app.state.utility_matrix.shape}")
    # app.state.knn_recommender =
    yield
    print("[shutdown] Encerrando server.")


app = FastAPI(
    title="Game Recommender API",
    description="Sistema de recomendação de jogos - (content-based: KNN + TF-IDF)",
    lifespan=lifespan,
)

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
