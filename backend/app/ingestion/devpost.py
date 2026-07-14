"""Tier 1 connector: Devpost's public hackathon search API (no auth).
Returns real, currently-open hackathons directly - title, deadline window,
prize money, and a working URL - which is exactly the "opportunity only"
bar the Competitions tab needs to clear."""

import logging
from datetime import datetime

import httpx
from dateutil import parser as date_parser
from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .sources import DEVPOST_SEARCH_TERMS
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.devpost")

API_URL = "https://devpost.com/api/hackathons"


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://devpost.com").first()
    if not source:
        source = Source(name="Devpost", type="api", url="https://devpost.com", tier="tier1")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def _parse_deadline(date_range: str):
    if not date_range or " - " not in date_range:
        return None
    end_part = date_range.split(" - ")[-1]
    try:
        return date_parser.parse(end_part, fuzzy=True)
    except (ValueError, OverflowError):
        return None


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    results = {}
    seen_ids = set()

    with httpx.Client() as client:
        for term in DEVPOST_SEARCH_TERMS:
            new_count = 0
            try:
                resp = client.get(API_URL, params={"status[]": "open", "search": term}, timeout=15)
                resp.raise_for_status()
                hackathons = resp.json().get("hackathons", [])
            except Exception as exc:
                logger.warning("Devpost fetch failed for '%s': %s", term, exc)
                results[term] = f"error: {exc}"
                continue

            for h in hackathons:
                hid = h.get("id")
                if hid in seen_ids:
                    continue
                seen_ids.add(hid)

                url = h.get("url")
                if not url or db.query(Opportunity).filter(Opportunity.url == url).first():
                    continue

                deadline = _parse_deadline(h.get("submission_period_dates"))
                location = (h.get("displayed_location") or {}).get("location", "Online")
                prizes = h.get("prizes_counts", {}) or {}

                added = safe_add(db, Opportunity(
                    title=h.get("title", "Untitled hackathon"),
                    summary=f"Hosted by {h.get('organization_name', 'Devpost')}. {h.get('registrations_count', 0)} registered.",
                    url=url,
                    category="Competitions",
                    subcategory="Hackathon",
                    organization=h.get("organization_name") or "Devpost",
                    geography=location,
                    is_remote=location.lower() in ("online", "anywhere"),
                    is_paid=(prizes.get("cash", 0) or 0) > 0,
                    deadline=deadline,
                    is_rolling=deadline is None,
                    published_at=now,
                    discovered_at=now,
                    updated_at=now,
                    score=0.8,
                    source_id=source.id,
                ))
                if added:
                    new_count += 1

            results[term] = new_count

    source.last_fetched_at = now
    db.commit()
    return results
