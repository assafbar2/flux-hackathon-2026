from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import brief, chat, setup


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


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
