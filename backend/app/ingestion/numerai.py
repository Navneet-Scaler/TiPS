"""Tier 1 connector: Numerai's public tournament GraphQL API (no auth).
Numerai runs a continuous, real-money data science tournament - this pulls
the live round info directly rather than hand-writing a static description."""

import logging
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.numerai")

API_URL = "https://api-tournament.numer.ai/"
OPPORTUNITY_URL = "https://numer.ai/tournament"


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://numer.ai").first()
    if not source:
        source = Source(name="Numerai", type="api", url="https://numer.ai", tier="tier1")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()

    if db.query(Opportunity).filter(Opportunity.url == OPPORTUNITY_URL).first():
        return {"status": "already tracked"}

    try:
        resp = httpx.post(
            API_URL,
            json={"query": "{rounds(tournament:8,number:0){number openTime resolveTime}}"},
            timeout=15,
        )
        resp.raise_for_status()
        rounds = resp.json().get("data", {}).get("rounds", [])
    except Exception as exc:
        logger.warning("Numerai fetch failed: %s", exc)
        return {"error": str(exc)}

    if not rounds:
        return {"status": "no active round"}

    current = rounds[0]
    added = safe_add(db, Opportunity(
        title=f"Numerai Tournament - Round {current.get('number')}",
        summary="Continuous real-money data science tournament predicting stock market signals from obfuscated data.",
        url=OPPORTUNITY_URL,
        category="Competitions",
        subcategory="ML Competition",
        tier="tier1",
        domain="Finance / Quant",
        organization="Numerai",
        geography="Global",
        is_remote=True,
        is_paid=True,
        is_rolling=True,
        published_at=now,
        discovered_at=now,
        updated_at=now,
        score=0.7,
        source_id=source.id,
    ))

    source.last_fetched_at = now
    db.commit()
    return {"added": added, "round": current.get("number")}
