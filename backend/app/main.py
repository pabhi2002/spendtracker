import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine, Base
from .routers import expenses, summary

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Spend Tracker API",
    description="A mini expense tracking API with summary insights",
    version="1.0.0",
)

# CORS — allow the frontend (served from file:// or any origin in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses.router)
app.include_router(summary.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "spend-tracker"}


# Serve the frontend as static files at /ui
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/ui", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
