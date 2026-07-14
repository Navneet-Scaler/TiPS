"""Tier 1 connector: Hugging Face's public Spaces API (no auth).
Chatbot Arena, MTEB, Open LLM Leaderboard, and dozens of other AI/ML
leaderboards are literally hosted as HF Spaces - this pulls them directly
rather than hand-curating each one, and picks up new leaderboards as they
appear without any code change."""

import logging
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..classify import classify_ai_domain
from ..models import Opportunity, Source
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.huggingface_spaces")

API_URL = "https://huggingface.co/api/spaces"
SEARCH_TERMS = ["leaderboard", "benchmark", "arena"]


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://huggingface.co/spaces").first()
    if not source:
        source = Source(name="Hugging Face Spaces", type="api", url="https://huggingface.co/spaces", tier="tier1")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    results = {}
    seen_ids = set()

    with httpx.Client() as client:
        for term in SEARCH_TERMS:
            new_count = 0
            try:
                resp = client.get(API_URL, params={"search": term, "limit": 20, "sort": "likes"}, timeout=15)
                resp.raise_for_status()
                spaces = resp.json()
            except Exception as exc:
                logger.warning("HF Spaces fetch failed for '%s': %s", term, exc)
                results[term] = f"error: {exc}"
                continue

            for space in spaces:
                space_id = space.get("id")
                if not space_id or space_id in seen_ids:
                    continue
                seen_ids.add(space_id)
                if space.get("private"):
                    continue

                url = f"https://huggingface.co/spaces/{space_id}"
                if db.query(Opportunity).filter(Opportunity.url == url).first():
                    continue

                title = space_id.split("/")[-1].replace("-", " ").title()
                summary = f"Community leaderboard/benchmark space - {space.get('likes', 0)} likes."

                added = safe_add(db, Opportunity(
                    title=title,
                    summary=summary,
                    url=url,
                    category="Competitions",
                    subcategory="ML Competition",
                    tier="tier1",
                    domain=classify_ai_domain(title, summary) or "Data Science",
                    organization=space_id.split("/")[0],
                    geography="Global",
                    is_remote=True,
                    is_paid=False,
                    is_rolling=True,
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
