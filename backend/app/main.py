import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, SessionLocal
from .routes.opportunities import router as opportunities_router
from .ingestion.orchestrator import run_all
from .scheduler import start_scheduler
from . import seed

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TIPS - Talent Intelligence & Personal Signals API")

allowed_origins = ["http://localhost:3000"]
extra_origins = os.environ.get("ALLOWED_ORIGINS", "")
if extra_origins:
    allowed_origins.extend(o.strip() for o in extra_origins.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(opportunities_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/ingest/run")
def trigger_ingestion():
    db = SessionLocal()
    try:
        results = run_all(db)
        return {"results": results}
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed.seed_if_empty(db)
    finally:
        db.close()
    start_scheduler()
