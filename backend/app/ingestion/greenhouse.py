"""Tier 3 connector: Greenhouse job-board API (public JSON per company, no auth).
One connector, add a board token to GREENHOUSE_BOARDS to monitor another company's
career page - this is the pattern the plan calls out explicitly."""

import logging
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .sources import GREENHOUSE_BOARDS
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.greenhouse")


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://boards-api.greenhouse.io").first()
    if not source:
        source = Source(name="Greenhouse Career Pages", type="career_page", url="https://boards-api.greenhouse.io", tier="tier3")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    results = {}

    with httpx.Client() as client:
        for board in GREENHOUSE_BOARDS:
            token = board["token"]
            organization = board["organization"]
            new_count = 0
            try:
                resp = client.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
                    timeout=10,
                )
                resp.raise_for_status()
                jobs = resp.json().get("jobs", [])
            except Exception as exc:
                logger.warning("Greenhouse fetch failed for %s: %s", token, exc)
                results[organization] = f"error: {exc}"
                continue

            for job in jobs[:30]:
                url = job.get("absolute_url")
                if not url or db.query(Opportunity).filter(Opportunity.url == url).first():
                    continue

                location = (job.get("location") or {}).get("name", "Global")
                added = safe_add(db, Opportunity(
                    title=job.get("title", "Untitled role"),
                    summary=f"Open role at {organization}.",
                    url=url,
                    category="Career",
                    organization=organization,
                    geography=location,
                    is_remote="remote" in location.lower(),
                    is_paid=True,
                    published_at=now,
                    discovered_at=now,
                    updated_at=now,
                    score=0.5,
                    source_id=source.id,
                ))
                if added:
                    new_count += 1

            results[organization] = new_count

    source.last_fetched_at = now
    db.commit()
    return results
