"""Tier 1 connector: Zindi's public competitions API (no auth).
Zindi hosts real, prize-backed data science/ML competitions - many with an
explicit AI/geospatial/health focus - with structured deadlines and rewards."""

import logging
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..classify import classify_ai_domain
from ..models import Opportunity, Source
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.zindi")

API_URL = "https://api.zindi.africa/v1/competitions"


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://zindi.africa").first()
    if not source:
        source = Source(name="Zindi", type="api", url="https://zindi.africa", tier="tier1")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def _parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()

    try:
        resp = httpx.get(API_URL, params={"per_page": 100}, timeout=15)
        resp.raise_for_status()
        competitions = resp.json().get("data", [])
    except Exception as exc:
        logger.warning("Zindi fetch failed: %s", exc)
        source.last_fetched_at = now
        db.commit()
        return {"error": str(exc)}

    new_count = 0
    for comp in competitions:
        if not comp.get("open"):
            continue

        comp_id = comp.get("id")
        if not comp_id:
            continue
        url = f"https://zindi.africa/competitions/{comp_id}"
        if db.query(Opportunity).filter(Opportunity.url == url).first():
            continue

        title = comp.get("title", "Untitled competition")
        reward = comp.get("reward")
        summary = f"{comp.get('participations_count', 0)} participants. Reward: {reward or 'certificate/points only'}."

        added = safe_add(db, Opportunity(
            title=title,
            summary=summary,
            url=url,
            category="Competitions",
            subcategory="ML Competition",
            tier="tier1",
            domain=classify_ai_domain(title, summary) or "Data Science",
            organization=comp.get("organization") or "Zindi",
            geography="Global",
            is_remote=True,
            is_paid=bool(reward) and comp.get("reward_type") == "prize",
            deadline=_parse_iso(comp.get("end_time")),
            is_rolling=False,
            published_at=_parse_iso(comp.get("start_time")) or now,
            discovered_at=now,
            updated_at=now,
            score=0.8,
            source_id=source.id,
        ))
        if added:
            new_count += 1

    source.last_fetched_at = now
    db.commit()
    return {"competitions_added": new_count, "total_open": len([c for c in competitions if c.get("open")])}
