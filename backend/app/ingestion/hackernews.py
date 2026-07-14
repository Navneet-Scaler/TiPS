"""Tier 5 connector: Hacker News via the Algolia HN Search API (official, public, no auth).
Searches recent stories for opportunity-shaped keywords."""

import logging
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..classify import classify, classify_competition_subcategory, gate_category, score
from ..models import Opportunity, Source
from .sources import HN_KEYWORDS
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.hackernews")

API_URL = "https://hn.algolia.com/api/v1/search_by_date"


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://news.ycombinator.com").first()
    if not source:
        source = Source(name="Hacker News", type="hackernews", url="https://news.ycombinator.com", tier="tier5")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    results = {}

    with httpx.Client() as client:
        for keyword in HN_KEYWORDS:
            new_count = 0
            try:
                resp = client.get(API_URL, params={"query": keyword, "tags": "story", "hitsPerPage": 15}, timeout=10)
                resp.raise_for_status()
                hits = resp.json().get("hits", [])
            except Exception as exc:
                logger.warning("HN fetch failed for '%s': %s", keyword, exc)
                results[keyword] = f"error: {exc}"
                continue

            for hit in hits:
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                if db.query(Opportunity).filter(Opportunity.url == url).first():
                    continue

                title = hit.get("title") or "Untitled"
                created_str = hit.get("created_at")
                try:
                    published_at = datetime.fromisoformat(created_str.replace("Z", "")) if created_str else now
                except ValueError:
                    published_at = now
                recency_days = max((now - published_at).total_seconds() / 86400, 0)
                category = gate_category(classify(title, ""), title, "")

                added = safe_add(db, Opportunity(
                    title=title,
                    summary=f"Discussed on Hacker News — {hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments.",
                    url=url,
                    category=category,
                    subcategory=classify_competition_subcategory(title, "") if category == "Competitions" else None,
                    organization="Hacker News",
                    geography="Global",
                    published_at=published_at,
                    discovered_at=now,
                    updated_at=now,
                    score=score(recency_days),
                    source_id=source.id,
                ))
                if added:
                    new_count += 1

            results[keyword] = new_count

    source.last_fetched_at = now
    db.commit()
    return results
