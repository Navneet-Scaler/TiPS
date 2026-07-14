"""Tier 1 connector: Unstop's public opportunity search API (no auth).
Unstop is India's largest hackathon/competition aggregator - real open
listings with actual registration deadlines, not a static directory page."""

import logging
import re
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..classify import classify_ai_domain
from ..models import Opportunity, Source
from .sources import UNSTOP_SEARCH_TERMS
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.unstop")

API_URL = "https://unstop.com/api/public/opportunity/search-result"


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://unstop.com").first()
    if not source:
        source = Source(name="Unstop", type="api", url="https://unstop.com", tier="tier1")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()


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
    results = {}
    seen_ids = set()

    with httpx.Client() as client:
        for term in UNSTOP_SEARCH_TERMS:
            new_count = 0
            try:
                resp = client.get(
                    API_URL,
                    params={"opportunity": "hackathons", "oppstatus": "open", "search": term},
                    timeout=15,
                )
                resp.raise_for_status()
                items = resp.json().get("data", {}).get("data", [])
            except Exception as exc:
                logger.warning("Unstop fetch failed for '%s': %s", term, exc)
                results[term] = f"error: {exc}"
                continue

            for item in items:
                item_id = item.get("id")
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)

                public_url = item.get("public_url") or item.get("seo_url")
                if not public_url:
                    continue
                url = public_url if public_url.startswith("http") else f"https://unstop.com/{public_url}"
                if db.query(Opportunity).filter(Opportunity.url == url).first():
                    continue

                festival = item.get("festival") or {}
                regn = festival.get("regnRequirements") or {}
                deadline = _parse_iso(regn.get("end_regn_dt"))
                organization = (item.get("organisation") or {}).get("name", "Unstop")
                region = item.get("region", "")
                is_remote = region.lower() in ("online", "remote", "")
                title = item.get("title", "Untitled hackathon")
                summary = _strip_html(item.get("details", ""))[:500] or None

                added = safe_add(db, Opportunity(
                    title=title,
                    summary=summary,
                    url=url,
                    category="Competitions",
                    subcategory="Hackathon",
                    tier="tier1",
                    domain=classify_ai_domain(title, summary or ""),
                    organization=organization,
                    geography="India" if not is_remote else "Global",
                    is_remote=is_remote,
                    is_paid=bool(item.get("isPaid")),
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
