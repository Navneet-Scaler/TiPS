import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import feedparser
import httpx
from sqlalchemy.orm import Session

from ..classify import (
    classify,
    classify_competition_subcategory,
    classify_dilution_type,
    classify_research_subcategory,
    classify_startup_subcategory,
    gate_category,
    is_funded,
    score,
)
from ..models import Opportunity, Source
from .sources import RSS_SOURCES
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.rss")


def ensure_sources(db: Session):
    for entry in RSS_SOURCES:
        existing = db.query(Source).filter(Source.url == entry["url"]).first()
        if not existing:
            db.add(Source(name=entry["name"], type="rss", url=entry["url"], tier="tier2"))
    db.commit()


def _parse_time(struct_time):
    if not struct_time:
        return None
    return datetime(*struct_time[:6], tzinfo=timezone.utc).replace(tzinfo=None)


def _download_feed(url: str):
    """Standalone, thread-safe fetch - downloading is the slow network part,
    kept separate from feedparser.parse() (pure CPU) so every feed's request
    can happen concurrently instead of one at a time."""
    try:
        resp = httpx.get(url, timeout=15, follow_redirects=True, headers={"User-Agent": "tips-opportunity-radar/0.1"})
        resp.raise_for_status()
        return resp.content
    except Exception as exc:
        logger.warning("Failed to download feed %s: %s", url, exc)
        return None


def fetch_source(db: Session, source: Source, organization: str, raw_feed) -> int:
    if raw_feed is None:
        return 0
    parsed = feedparser.parse(raw_feed)
    new_count = 0
    now = datetime.utcnow()

    for entry in parsed.entries[:40]:
        url = entry.get("link")
        if not url:
            continue
        if db.query(Opportunity).filter(Opportunity.url == url).first():
            continue

        title = entry.get("title", "Untitled")
        summary = entry.get("summary", "")
        published_at = _parse_time(entry.get("published_parsed")) or _parse_time(entry.get("updated_parsed")) or now

        recency_days = max((now - published_at).total_seconds() / 86400, 0)
        category = gate_category(classify(title, summary), title, summary)

        subcategory = None
        dilution_type = None
        if category == "Research":
            subcategory = classify_research_subcategory(title, summary)
        elif category == "Competitions":
            subcategory = classify_competition_subcategory(title, summary)
        elif category == "Startup":
            subcategory = classify_startup_subcategory(title, summary)
            dilution_type = classify_dilution_type(title, summary)

        opp = Opportunity(
            title=title,
            summary=summary[:1000] if summary else None,
            url=url,
            category=category,
            subcategory=subcategory,
            dilution_type=dilution_type,
            organization=organization,
            geography="Global",
            is_paid=is_funded(title, summary),
            published_at=published_at,
            discovered_at=now,
            updated_at=now,
            score=score(recency_days),
            source_id=source.id,
        )
        if safe_add(db, opp):
            new_count += 1

    source.last_fetched_at = now
    db.commit()
    return new_count


def run_ingestion(db: Session) -> dict:
    ensure_sources(db)
    results = {}
    sources_by_url = {s["url"]: s for s in RSS_SOURCES}

    sources = db.query(Source).filter(Source.type == "rss", Source.active == True).all()  # noqa: E712
    urls = [s.url for s in sources]

    # Downloading is the slow network part - do every feed concurrently
    # instead of one at a time, then parse+store sequentially as before.
    raw_feeds = {}
    if urls:
        with ThreadPoolExecutor(max_workers=12) as pool:
            for url, content in zip(urls, pool.map(_download_feed, urls)):
                raw_feeds[url] = content

    for source in sources:
        meta = sources_by_url.get(source.url, {})
        organization = meta.get("organization", source.name)
        try:
            count = fetch_source(db, source, organization, raw_feeds.get(source.url))
            results[source.name] = count
        except Exception as exc:  # keep ingestion resilient to a single bad feed
            logger.warning("Failed to fetch %s: %s", source.name, exc)
            results[source.name] = f"error: {exc}"

    return results
