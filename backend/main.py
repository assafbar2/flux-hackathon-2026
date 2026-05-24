import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from routes import action, brief, chat, setup


app = FastAPI(title="Flux API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(setup.router, prefix="/api")
app.include_router(brief.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(action.router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": os.getenv("FLUX_AGENT_MODE", "demo"),
        "version": "1.0.0",
    }


STATIC_DIR = Path(__file__).resolve().parent / "static"
ASSETS_DIR = STATIC_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/favicon.svg")
def serve_favicon() -> FileResponse:
    favicon_file = STATIC_DIR / "favicon.svg"
    if favicon_file.exists():
        return FileResponse(favicon_file, media_type="image/svg+xml")
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return FileResponse(__file__, media_type="text/plain")


@app.get("/{path:path}")
def serve_frontend(path: str) -> FileResponse:
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return FileResponse(__file__, media_type="text/plain")
    return FileResponse(index_file)
