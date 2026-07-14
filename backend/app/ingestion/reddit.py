"""Tier 5 connector: Reddit's public JSON endpoints (no auth required).
One connector covers every subreddit in REDDIT_SUBREDDITS -
this is where hidden opportunities surface before they're posted anywhere formal."""

import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from ..classify import (
    classify,
    classify_competition_subcategory,
    classify_research_subcategory,
    gate_category,
    is_funded,
    score,
)
from ..models import Opportunity, Source
from .sources import REDDIT_SUBREDDITS
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.reddit")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) tips-opportunity-radar/0.1"}


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://www.reddit.com").first()
    if not source:
        source = Source(name="Reddit", type="reddit", url="https://www.reddit.com", tier="tier5")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def fetch_subreddit(client: httpx.Client, subreddit: str) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
    resp = client.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json().get("data", {}).get("children", [])


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    results = {}

    with httpx.Client() as client:
        for subreddit in REDDIT_SUBREDDITS:
            new_count = 0
            try:
                posts = fetch_subreddit(client, subreddit)
            except Exception as exc:
                logger.warning("Reddit fetch failed for r/%s: %s", subreddit, exc)
                results[f"r/{subreddit}"] = f"error: {exc}"
                continue

            for post in posts:
                p = post.get("data", {})
                permalink = p.get("permalink")
                if not permalink:
                    continue
                url = f"https://www.reddit.com{permalink}"
                if db.query(Opportunity).filter(Opportunity.url == url).first():
                    continue

                title = p.get("title", "Untitled")
                summary = (p.get("selftext") or "")[:800]
                created = datetime.fromtimestamp(p.get("created_utc", now.timestamp()), tz=timezone.utc).replace(tzinfo=None)
                recency_days = max((now - created).total_seconds() / 86400, 0)
                category = gate_category(classify(title, summary), title, summary)

                subcategory = None
                if category == "Research":
                    subcategory = classify_research_subcategory(title, summary)
                elif category == "Competitions":
                    subcategory = classify_competition_subcategory(title, summary)

                added = safe_add(db, Opportunity(
                    title=title,
                    summary=summary or None,
                    url=url,
                    category=category,
                    subcategory=subcategory,
                    organization=f"r/{subreddit}",
                    geography="Global",
                    is_paid=is_funded(title, summary),
                    published_at=created,
                    discovered_at=now,
                    updated_at=now,
                    score=score(recency_days),
                    source_id=source.id,
                ))
                if added:
                    new_count += 1

            results[f"r/{subreddit}"] = new_count

    source.last_fetched_at = now
    db.commit()
    return results
