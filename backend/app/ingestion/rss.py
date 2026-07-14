import logging
from datetime import datetime, timezone

import feedparser
from sqlalchemy.orm import Session

from ..classify import classify, classify_research_subcategory, is_funded, score
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


def fetch_source(db: Session, source: Source, organization: str) -> int:
    parsed = feedparser.parse(source.url)
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
        category = classify(title, summary)

        opp = Opportunity(
            title=title,
            summary=summary[:1000] if summary else None,
            url=url,
            category=category,
            subcategory=classify_research_subcategory(title, summary) if category == "Research" else None,
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

    for source in db.query(Source).filter(Source.type == "rss", Source.active == True).all():  # noqa: E712
        meta = sources_by_url.get(source.url, {})
        organization = meta.get("organization", source.name)
        try:
            count = fetch_source(db, source, organization)
            results[source.name] = count
        except Exception as exc:  # keep ingestion resilient to a single bad feed
            logger.warning("Failed to fetch %s: %s", source.name, exc)
            results[source.name] = f"error: {exc}"

    return results
