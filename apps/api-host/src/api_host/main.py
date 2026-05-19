from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api_host.api.podcast_routes import router as podcast_router

app = FastAPI(
    title="PodCraft AI API Host",
    version="0.1.0",
)

app.include_router(podcast_router)
app.mount("/generated", StaticFiles(directory="generated"), name="generated")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
