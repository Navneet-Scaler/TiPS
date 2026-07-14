"""Tier 1 connector: OpenReview public search API (no auth for reads).
Surfaces open calls and discussion threads that mention active collaboration -
the plan calls this out as a gap most opportunity boards miss entirely."""

import logging
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..classify import classify_research_subcategory
from ..models import Opportunity, Source
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.openreview")

API_URL = "https://api2.openreview.net/notes/search"
SEARCH_TERMS = ["call for papers", "seeking collaborators", "call for reviewers"]


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://openreview.net").first()
    if not source:
        source = Source(name="OpenReview", type="api", url="https://openreview.net", tier="tier1")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    results = {}

    with httpx.Client() as client:
        for term in SEARCH_TERMS:
            new_count = 0
            try:
                resp = client.get(API_URL, params={"term": term, "type": "terms", "content": "all", "group": "all"}, timeout=10)
                resp.raise_for_status()
                notes = resp.json().get("notes", [])
            except Exception as exc:
                logger.warning("OpenReview search failed for '%s': %s", term, exc)
                results[term] = f"error: {exc}"
                continue

            for note in notes[:20]:
                note_id = note.get("id")
                if not note_id:
                    continue
                url = f"https://openreview.net/forum?id={note_id}"
                if db.query(Opportunity).filter(Opportunity.url == url).first():
                    continue

                content = note.get("content", {})
                title = (content.get("title") or {}).get("value") if isinstance(content.get("title"), dict) else content.get("title")
                title = title or "OpenReview thread"
                abstract = content.get("abstract")
                summary = (abstract or {}).get("value") if isinstance(abstract, dict) else abstract

                added = safe_add(db, Opportunity(
                    title=title,
                    summary=(summary or "")[:800] or None,
                    url=url,
                    category="Research",
                    subcategory=classify_research_subcategory(title, summary or "") or "Seeking Collaborators",
                    organization="OpenReview",
                    geography="Global",
                    published_at=now,
                    discovered_at=now,
                    updated_at=now,
                    score=0.6,
                    source_id=source.id,
                ))
                if added:
                    new_count += 1

            results[term] = new_count

    source.last_fetched_at = now
    db.commit()
    return results
