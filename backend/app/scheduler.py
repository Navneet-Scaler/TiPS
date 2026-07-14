import logging

from apscheduler.schedulers.background import BackgroundScheduler

from .database import SessionLocal
from .ingestion.orchestrator import run_all

logger = logging.getLogger("tips.scheduler")

scheduler = BackgroundScheduler()


def ingestion_job():
    db = SessionLocal()
    try:
        results = run_all(db)
        logger.info("Ingestion run complete: %s", results)
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(ingestion_job, "interval", minutes=30, id="rss_ingestion", replace_existing=True)
    scheduler.start()
